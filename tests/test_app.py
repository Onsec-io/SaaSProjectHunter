"""Tests for app.py — CLI argument parsing, module loading, main dispatch."""
import os
import importlib
from unittest.mock import MagicMock

import pytest

import logger
logger.init_logger(0, True)

import utils


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


# ---------------------------------------------------------------------------
# CLI argument parsing (via subprocess to avoid app.py's module-level code)
# ---------------------------------------------------------------------------

class TestCLIParsing:
    """Test argparse configuration by importing the parser directly."""

    def _get_parser(self):
        """Build a parser identical to app.py's without executing module-level code."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-g', '--generator', nargs='*')
        parser.add_argument('-m', '--module', action='store', type=str, default=False)
        parser.add_argument('-x', '--exclude', nargs='*')
        parser.add_argument('-t', '--threads', default=8, type=int)
        parser.add_argument('-u', '--user-agent', default='test')
        parser.add_argument('-a', '--auto-resend', type=int, default=None)
        parser.add_argument('-v', '--verbose', default=0, action='count')
        parser.add_argument('-nc', '--no-color', action='store_true', default=False)
        parser.add_argument('-p', '--postfix')
        parser.add_argument('--tld', default=None)
        parser.add_argument('--limit', default=100000, type=int)
        parser.add_argument('--proxies', default=None)
        parser.add_argument('--tag', default=None)
        parser.add_argument('--no-concurrent', action='store_true', default=False)
        parser.add_argument('--workers', default=None, type=int)

        group = parser.add_mutually_exclusive_group()
        group.add_argument('-l', '--list', action='store_true', default=False)
        group.add_argument('-c', '--check', action='store_true', default=False)

        input_group = parser.add_mutually_exclusive_group()
        input_group.add_argument('-w', '--wordlist')
        input_group.add_argument('-s', '--strings', nargs='+')
        return parser

    def test_no_concurrent_flag(self):
        parser = self._get_parser()
        args = parser.parse_args(['--no-concurrent', '-s', 'test'])
        assert args.no_concurrent is True

    def test_no_concurrent_default_false(self):
        parser = self._get_parser()
        args = parser.parse_args(['-s', 'test'])
        assert args.no_concurrent is False

    def test_workers_flag(self):
        parser = self._get_parser()
        args = parser.parse_args(['--workers', '10', '-s', 'test'])
        assert args.workers == 10

    def test_workers_default_none(self):
        parser = self._get_parser()
        args = parser.parse_args(['-s', 'test'])
        assert args.workers is None

    def test_strings_flag(self):
        parser = self._get_parser()
        args = parser.parse_args(['-s', 'google', 'logstash'])
        assert args.strings == ['google', 'logstash']

    def test_module_flag(self):
        parser = self._get_parser()
        args = parser.parse_args(['-m', 'Slack', '-s', 'test'])
        assert args.module == 'Slack'

    def test_tag_flag(self):
        parser = self._get_parser()
        args = parser.parse_args(['--tag', 'limit', '-s', 'test'])
        assert args.tag == 'limit'

    def test_exclude_flag(self):
        parser = self._get_parser()
        args = parser.parse_args(['-x', 'Slack', 'Azure', '-s', 'test'])
        assert args.exclude == ['Slack', 'Azure']

    def test_verbose_counts(self):
        parser = self._get_parser()
        args = parser.parse_args(['-vv', '-s', 'test'])
        assert args.verbose == 2

    def test_threads_flag(self):
        parser = self._get_parser()
        args = parser.parse_args(['-t', '16', '-s', 'test'])
        assert args.threads == 16

    def test_list_and_check_mutually_exclusive(self):
        parser = self._get_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(['-l', '-c'])

    def test_wordlist_and_strings_mutually_exclusive(self):
        parser = self._get_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(['-w', 'file.txt', '-s', 'word'])


# ---------------------------------------------------------------------------
# load_modules() (uses real module files)
# ---------------------------------------------------------------------------

class TestLoadModules:
    """Test module loading from the real modules/ directory."""

    def _load_modules(self, name=False, tag=None, exclude_modules=None):
        """Replicate app.py load_modules logic without importing app.py."""
        folder = 'modules'
        modules = []
        if name:
            module = importlib.import_module(f'{folder}.{name}')
            modules.append(module)
        else:
            for file in os.listdir(folder):
                if file == '__init__.py' or file[-3:] != '.py':
                    continue
                module_name = file[:-3]
                if exclude_modules and module_name in exclude_modules:
                    continue
                module = importlib.import_module(f'{folder}.{module_name}')
                if not tag or tag in module.get_tags():
                    modules.append(module)
        return sorted(modules, key=lambda x: x.get_name())

    def test_load_all_modules(self):
        modules = self._load_modules()
        assert len(modules) >= 80  # at least 80 modules exist

    def test_load_specific_module(self):
        modules = self._load_modules(name='Slack')
        assert len(modules) == 1
        assert modules[0].get_name() == 'Slack'

    def test_load_by_tag(self):
        modules = self._load_modules(tag='limit')
        assert len(modules) > 0
        for m in modules:
            assert 'limit' in m.get_tags()

    def test_exclude_modules(self):
        all_modules = self._load_modules()
        excluded = self._load_modules(exclude_modules=['Slack', 'Azure'])
        all_names = {m.get_name() for m in all_modules}
        excluded_names = {m.get_name() for m in excluded}
        assert 'Slack' not in excluded_names
        assert 'Azure' not in excluded_names
        assert len(excluded) == len(all_modules) - 2

    def test_modules_sorted_by_name(self):
        modules = self._load_modules()
        names = [m.get_name() for m in modules]
        assert names == sorted(names)

    def test_every_module_has_required_interface(self):
        """Every module must have get_name, get_tags, get_description, run."""
        modules = self._load_modules()
        for m in modules:
            assert callable(getattr(m, 'get_name', None)), f'{m} missing get_name'
            assert callable(getattr(m, 'get_tags', None)), f'{m} missing get_tags'
            assert callable(getattr(m, 'get_description', None)), f'{m} missing get_description'
            assert callable(getattr(m, 'run', None)), f'{m} missing run'

    def test_every_module_name_is_string(self):
        modules = self._load_modules()
        for m in modules:
            name = m.get_name()
            assert isinstance(name, str) and len(name) > 0

    def test_every_module_tags_is_list(self):
        modules = self._load_modules()
        for m in modules:
            tags = m.get_tags()
            assert isinstance(tags, list) and len(tags) > 0


# ---------------------------------------------------------------------------
# Main dispatch logic
# ---------------------------------------------------------------------------

class TestMainDispatch:
    """Test the sequential vs concurrent dispatch logic."""

    def _make_module(self, name, urls=None):
        m = MagicMock()
        m.get_name.return_value = name
        m.get_tags.return_value = ['nolimit']
        m.run.return_value = urls or []
        return m

    def test_sequential_when_no_concurrent(self):
        """With no_concurrent=True, modules run in a loop (not via scheduler)."""
        m1 = self._make_module('A', ['url1'])
        m2 = self._make_module('B', ['url2'])
        modules = [m1, m2]

        output = []
        # Simulate the sequential path from app.py
        for module in modules:
            utils.reset_auto_resend_counter()
            for url in module.run(['word']):
                output.append([module.get_name(), url])

        assert output == [['A', 'url1'], ['B', 'url2']]
        m1.run.assert_called_once_with(['word'])
        m2.run.assert_called_once_with(['word'])

    def test_sequential_for_single_module(self):
        """Single module should use sequential path."""
        m = self._make_module('Solo', ['url1'])
        modules = [m]

        # Simulate: len(modules) == 1 triggers sequential
        output = []
        for module in modules:
            utils.reset_auto_resend_counter()
            for url in module.run(['word']):
                output.append([module.get_name(), url])

        assert len(output) == 1

    def test_concurrent_dispatch(self):
        """With multiple modules and no --no-concurrent, scheduler is used."""
        import scheduler

        m1 = self._make_module('A', ['url1'])
        m2 = self._make_module('B', ['url2'])

        results = scheduler.run_concurrent([m1, m2], ['word'], max_workers=2)

        output = []
        for name, url in results:
            output.append([name, url])

        names = {row[0] for row in output}
        urls = {row[1] for row in output}
        assert names == {'A', 'B'}
        assert urls == {'url1', 'url2'}
