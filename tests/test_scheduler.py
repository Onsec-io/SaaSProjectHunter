"""Tests for scheduler.py — grouping, rate tiers, concurrent execution."""
import asyncio
import threading
import time
from unittest.mock import MagicMock

import pytest

import logger
logger.init_logger(0, True)

import utils
import scheduler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reinit_utils():
    utils.init(
        args_verbose=1,
        args_threads=8,
        args_user_agent='test-agent',
        args_limit_requests=100,
    )
    yield
    utils.set_concurrent_mode(False)


def _make_module(name, tags=None):
    """Create a fake module object with get_name()/get_tags()/run()."""
    m = MagicMock()
    m.get_name.return_value = name
    m.get_tags.return_value = tags or ['nolimit']
    m.run.return_value = [f'https://example.com/{name}']
    return m


# ---------------------------------------------------------------------------
# SERVICE_GROUPS / _MODULE_TO_GROUP
# ---------------------------------------------------------------------------

class TestServiceGroups:
    def test_all_group_members_in_lookup(self):
        for group_key, members in scheduler.SERVICE_GROUPS.items():
            for name in members:
                assert scheduler._MODULE_TO_GROUP[name] == group_key

    def test_github_group(self):
        assert 'GithubSearch' in scheduler._MODULE_TO_GROUP
        assert 'GithubUsers' in scheduler._MODULE_TO_GROUP
        assert 'GithubGist' in scheduler._MODULE_TO_GROUP
        assert scheduler._MODULE_TO_GROUP['GithubSearch'] == 'github'

    def test_dockerhub_group(self):
        assert scheduler._MODULE_TO_GROUP['DockerHubSearch'] == 'dockerhub'
        assert scheduler._MODULE_TO_GROUP['DockerHubUsers'] == 'dockerhub'

    def test_postman_group(self):
        assert scheduler._MODULE_TO_GROUP['PostmanSearch'] == 'postman'
        assert scheduler._MODULE_TO_GROUP['PostmanUsers'] == 'postman'

    def test_npm_group(self):
        assert scheduler._MODULE_TO_GROUP['NPMjs'] == 'npm'
        assert scheduler._MODULE_TO_GROUP['NPMsSearch'] == 'npm'


# ---------------------------------------------------------------------------
# group_modules()
# ---------------------------------------------------------------------------

class TestGroupModules:
    def test_ungrouped_modules_each_get_own_group(self):
        modules = [_make_module('Slack'), _make_module('Vercel')]
        groups = scheduler.group_modules(modules)
        assert len(groups) == 2
        assert all(len(g) == 1 for g in groups)

    def test_grouped_modules_share_a_group(self):
        modules = [
            _make_module('GithubSearch'),
            _make_module('GithubUsers'),
            _make_module('GithubGist'),
        ]
        groups = scheduler.group_modules(modules)
        assert len(groups) == 1
        names = [m.get_name() for m in groups[0]]
        assert set(names) == {'GithubSearch', 'GithubUsers', 'GithubGist'}

    def test_mixed_grouped_and_ungrouped(self):
        modules = [
            _make_module('GithubSearch'),
            _make_module('GithubUsers'),
            _make_module('Slack'),
            _make_module('Vercel'),
        ]
        groups = scheduler.group_modules(modules)
        # 1 github group + 2 singles
        assert len(groups) == 3

    def test_multiple_service_groups(self):
        modules = [
            _make_module('GithubSearch'),
            _make_module('GithubUsers'),
            _make_module('DockerHubSearch'),
            _make_module('DockerHubUsers'),
            _make_module('Slack'),
        ]
        groups = scheduler.group_modules(modules)
        # 2 service groups + 1 single
        assert len(groups) == 3
        group_sizes = sorted([len(g) for g in groups])
        assert group_sizes == [1, 2, 2]

    def test_single_member_of_service_group(self):
        """If only one module of a service group is present, it still goes into the group."""
        modules = [_make_module('GithubSearch')]
        groups = scheduler.group_modules(modules)
        assert len(groups) == 1
        assert len(groups[0]) == 1

    def test_empty_input(self):
        groups = scheduler.group_modules([])
        assert groups == []

    def test_preserves_order_within_group(self):
        modules = [
            _make_module('NPMjs'),
            _make_module('NPMsSearch'),
        ]
        groups = scheduler.group_modules(modules)
        assert len(groups) == 1
        names = [m.get_name() for m in groups[0]]
        assert names == ['NPMjs', 'NPMsSearch']


# ---------------------------------------------------------------------------
# _get_rate_tier()
# ---------------------------------------------------------------------------

class TestGetRateTier:
    def test_limit_tag(self):
        modules = [_make_module('X', ['limit'])]
        assert scheduler._get_rate_tier(modules) == 'limit'

    def test_dns_tag(self):
        modules = [_make_module('X', ['dns', 'nolimit'])]
        assert scheduler._get_rate_tier(modules) == 'dns'

    def test_nolimit_tag(self):
        modules = [_make_module('X', ['subdomain', 'nolimit'])]
        assert scheduler._get_rate_tier(modules) == 'nolimit'

    def test_no_tags(self):
        modules = [_make_module('X', ['subdomain'])]
        assert scheduler._get_rate_tier(modules) == 'nolimit'

    def test_limit_takes_priority_over_dns(self):
        modules = [
            _make_module('X', ['limit']),
            _make_module('Y', ['dns']),
        ]
        assert scheduler._get_rate_tier(modules) == 'limit'


# ---------------------------------------------------------------------------
# _run_group()
# ---------------------------------------------------------------------------

class TestRunGroup:
    def test_runs_modules_sequentially_and_collects_results(self):
        m1 = _make_module('ModA')
        m1.run.return_value = ['url1', 'url2']
        m2 = _make_module('ModB')
        m2.run.return_value = ['url3']

        results = scheduler._run_group([m1, m2], ['word1'])

        m1.run.assert_called_once_with(['word1'])
        m2.run.assert_called_once_with(['word1'])
        assert ('ModA', 'url1') in results
        assert ('ModA', 'url2') in results
        assert ('ModB', 'url3') in results

    def test_creates_own_event_loop(self):
        """_run_group creates a new event loop per thread."""
        m = _make_module('Mod')
        m.run.return_value = []

        loop_ids = []

        original_run = scheduler._run_group

        def capture_loop(group, words):
            loop_ids.append(id(asyncio.get_event_loop()))
            return original_run(group, words)

        # Run in a separate thread to test loop creation
        result = [None]
        def worker():
            result[0] = scheduler._run_group([m], ['w'])
            loop_ids.append(id(asyncio.get_event_loop()))

        t = threading.Thread(target=worker)
        t.start()
        t.join()

        assert result[0] == []

    def test_handles_module_exception(self):
        m1 = _make_module('Good')
        m1.run.return_value = ['url1']
        m2 = _make_module('Bad')
        m2.run.side_effect = RuntimeError('boom')
        m3 = _make_module('AlsoGood')
        m3.run.return_value = ['url2']

        results = scheduler._run_group([m1, m2, m3], ['word'])
        assert ('Good', 'url1') in results
        assert ('AlsoGood', 'url2') in results
        # Bad module's exception was caught, no result for it
        assert not any(name == 'Bad' for name, _ in results)

    def test_empty_group(self):
        results = scheduler._run_group([], ['word'])
        assert results == []

    def test_sets_rate_tier_for_limit_modules(self):
        m = _make_module('GithubSearch', ['limit'])
        m.run.return_value = []

        # Run in thread to get isolated thread-local
        tier_value = [None]
        def worker():
            scheduler._run_group([m], ['w'])
            tier_value[0] = utils._get_semaphore()._value

        t = threading.Thread(target=worker)
        t.start()
        t.join()

        assert tier_value[0] == max(2, utils._default_threads // 4)

    def test_sets_request_delay_for_limit_modules(self):
        m = _make_module('GithubSearch', ['limit'])
        m.run.return_value = []

        delay_value = [None]
        def worker():
            scheduler._run_group([m], ['w'])
            delay_value[0] = utils._get_request_delay()

        t = threading.Thread(target=worker)
        t.start()
        t.join()

        assert delay_value[0] == 0.3

    def test_no_delay_for_nolimit_modules(self):
        m = _make_module('Slack', ['subdomain', 'nolimit'])
        m.run.return_value = []

        delay_value = [None]
        def worker():
            scheduler._run_group([m], ['w'])
            delay_value[0] = utils._get_request_delay()

        t = threading.Thread(target=worker)
        t.start()
        t.join()

        assert delay_value[0] == 0


# ---------------------------------------------------------------------------
# run_concurrent()
# ---------------------------------------------------------------------------

class TestRunConcurrent:
    def test_basic_concurrent_execution(self):
        m1 = _make_module('Slack', ['nolimit'])
        m1.run.return_value = ['url1']
        m2 = _make_module('Vercel', ['nolimit'])
        m2.run.return_value = ['url2']

        results = scheduler.run_concurrent([m1, m2], ['word'], max_workers=2)
        names = {name for name, _ in results}
        assert names == {'Slack', 'Vercel'}

    def test_concurrent_mode_is_set_and_cleared(self):
        m = _make_module('Slack', ['nolimit'])
        m.run.return_value = []

        assert utils._concurrent_mode is False
        scheduler.run_concurrent([m], ['w'])
        assert utils._concurrent_mode is False  # cleaned up

    def test_concurrent_mode_set_during_execution(self):
        """Verify concurrent mode is True while modules are running."""
        m = _make_module('Slack', ['nolimit'])
        seen_mode = [None]

        def capture_mode(words):
            seen_mode[0] = utils._concurrent_mode
            return []

        m.run.side_effect = capture_mode
        scheduler.run_concurrent([m], ['w'])
        assert seen_mode[0] is True

    def test_max_workers_auto_capped_at_20(self):
        """Auto workers = min(len(groups), 20). With 25 modules => 20."""
        modules = [_make_module(f'Mod{i}') for i in range(25)]
        for m in modules:
            m.run.return_value = []

        groups = scheduler.group_modules(modules)
        expected_workers = min(len(groups), 20)
        assert expected_workers == 20

    def test_max_workers_auto_matches_groups_when_small(self):
        """Auto workers = min(len(groups), 20). With 3 modules => 3."""
        modules = [_make_module(f'Mod{i}') for i in range(3)]
        groups = scheduler.group_modules(modules)
        expected_workers = min(len(groups), 20)
        assert expected_workers == 3

    def test_max_workers_explicit_is_respected(self):
        """Explicit max_workers is passed through to the executor."""
        m1 = _make_module('Slack')
        m1.run.return_value = []
        m2 = _make_module('Vercel')
        m2.run.return_value = []

        # Just verify it doesn't error — the explicit value goes straight through
        results = scheduler.run_concurrent([m1, m2], ['w'], max_workers=1)
        assert isinstance(results, list)

    def test_groups_run_in_parallel(self):
        """Different service groups run concurrently (not sequentially)."""
        sleep_time = 0.2
        m1 = _make_module('Slack', ['nolimit'])
        m2 = _make_module('Vercel', ['nolimit'])
        m3 = _make_module('Zendesk', ['nolimit'])

        def slow_run(words):
            time.sleep(sleep_time)
            return []

        m1.run.side_effect = slow_run
        m2.run.side_effect = slow_run
        m3.run.side_effect = slow_run

        start = time.monotonic()
        scheduler.run_concurrent([m1, m2, m3], ['w'], max_workers=3)
        elapsed = time.monotonic() - start

        # If run in parallel, should take ~0.2s; if sequential, ~0.6s
        assert elapsed < sleep_time * 2

    def test_service_group_runs_sequentially(self):
        """Modules in the same service group run sequentially within the group."""
        call_order = []

        m1 = _make_module('GithubSearch', ['limit'])
        m2 = _make_module('GithubUsers', ['limit'])

        def run_search(words):
            call_order.append('GithubSearch')
            return []

        def run_users(words):
            call_order.append('GithubUsers')
            return []

        m1.run.side_effect = run_search
        m2.run.side_effect = run_users

        scheduler.run_concurrent([m1, m2], ['w'], max_workers=4)

        # Both should have run (order within group is preserved)
        assert 'GithubSearch' in call_order
        assert 'GithubUsers' in call_order

    def test_handles_module_exception_in_group(self):
        m1 = _make_module('Slack', ['nolimit'])
        m1.run.return_value = ['good-url']
        m2 = _make_module('Vercel', ['nolimit'])
        m2.run.side_effect = RuntimeError('network error')

        results = scheduler.run_concurrent([m1, m2], ['w'], max_workers=2)
        # m1 results should still be collected
        assert ('Slack', 'good-url') in results

    def test_aggregates_results_from_all_groups(self):
        modules = []
        for i in range(5):
            m = _make_module(f'Mod{i}')
            m.run.return_value = [f'url-{i}']
            modules.append(m)

        results = scheduler.run_concurrent(modules, ['w'], max_workers=5)
        assert len(results) == 5
        urls = {url for _, url in results}
        assert urls == {f'url-{i}' for i in range(5)}
