"""Tests for utils.py — thread-local infrastructure, helpers, compile functions, generator."""
import asyncio
import threading
import time
from unittest.mock import MagicMock, AsyncMock

import pytest

import logger
logger.init_logger(0, True)

import utils


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reinit_utils():
    """Re-initialise utils before every test so state doesn't leak."""
    utils.init(
        args_verbose=1,
        args_threads=8,
        args_user_agent='test-agent',
        args_limit_requests=100,
        args_proxies=None,
        args_tld=None,
        args_auto_resend=None,
    )
    yield
    utils.set_concurrent_mode(False)


# ---------------------------------------------------------------------------
# init()
# ---------------------------------------------------------------------------

class TestInit:
    def test_init_sets_globals(self):
        utils.init(2, 16, 'ua-string', 500, None, None, 5)
        assert utils.verbose == 2
        assert utils._default_threads == 16
        assert utils.header_useragent == {'user-agent': 'ua-string'}
        assert utils.limit_requests == 500
        assert utils.auto_resend == 5

    def test_init_creates_semaphore_with_thread_count(self):
        utils.init(0, 12, 'ua', 100)
        sem = utils._get_semaphore()
        assert sem._value == 12

    def test_init_resets_auto_resend_counter(self):
        utils._thread_local.auto_resend_counter = 99
        utils.init(0, 4, 'ua', 100)
        assert utils._get_auto_resend_counter() == 0

    def test_init_adds_custom_tlds(self):
        utils.init(0, 4, 'ua', 100, args_tld='co,kz')
        assert 'co' in utils.tlds
        assert 'kz' in utils.tlds
        # default ones still present
        assert 'com' in utils.tlds

    def test_init_does_not_duplicate_existing_tlds(self):
        utils.init(0, 4, 'ua', 100, args_tld='com,org')
        assert utils.tlds.count('com') == 1
        assert utils.tlds.count('org') == 1

    def test_init_loads_proxies(self):
        proxy_list = ['http://proxy1:8080', 'socks://proxy2:1080']
        utils.init(0, 4, 'ua', 100, args_proxies=proxy_list)
        assert utils.proxies == proxy_list


# ---------------------------------------------------------------------------
# Thread-local semaphore
# ---------------------------------------------------------------------------

class TestThreadLocalSemaphore:
    def test_get_semaphore_returns_asyncio_semaphore(self):
        sem = utils._get_semaphore()
        assert isinstance(sem, asyncio.Semaphore)

    def test_get_semaphore_creates_default_if_missing(self):
        # Remove semaphore from thread-local
        if hasattr(utils._thread_local, 'semaphore'):
            del utils._thread_local.semaphore
        sem = utils._get_semaphore()
        assert sem._value == utils._default_threads

    def test_semaphore_is_thread_local(self):
        """Two threads get independent semaphores."""
        main_sem = utils._get_semaphore()
        other_sem = [None]

        def worker():
            # New thread should create its own semaphore
            if hasattr(utils._thread_local, 'semaphore'):
                del utils._thread_local.semaphore
            other_sem[0] = utils._get_semaphore()

        t = threading.Thread(target=worker)
        t.start()
        t.join()
        assert other_sem[0] is not main_sem


# ---------------------------------------------------------------------------
# Rate tiers
# ---------------------------------------------------------------------------

class TestRateTiers:
    def test_set_rate_tier_nolimit(self):
        utils.set_rate_tier('nolimit')
        sem = utils._get_semaphore()
        assert sem._value == utils._default_threads

    def test_set_rate_tier_limit(self):
        utils.init(0, 16, 'ua', 100)
        utils.set_rate_tier('limit')
        sem = utils._get_semaphore()
        assert sem._value == max(2, 16 // 4)

    def test_set_rate_tier_limit_minimum_is_2(self):
        utils.init(0, 4, 'ua', 100)
        utils.set_rate_tier('limit')
        sem = utils._get_semaphore()
        assert sem._value == 2

    def test_set_rate_tier_dns(self):
        utils.init(0, 8, 'ua', 100)
        utils.set_rate_tier('dns')
        sem = utils._get_semaphore()
        assert sem._value == 16

    def test_set_rate_tier_unknown_defaults_to_nolimit(self):
        utils.set_rate_tier('unknown_tier')
        sem = utils._get_semaphore()
        assert sem._value == utils._default_threads


# ---------------------------------------------------------------------------
# Request delay
# ---------------------------------------------------------------------------

class TestRequestDelay:
    def test_default_delay_is_zero(self):
        # Clear thread-local
        if hasattr(utils._thread_local, 'request_delay'):
            del utils._thread_local.request_delay
        assert utils._get_request_delay() == 0

    def test_set_and_get_delay(self):
        utils.set_request_delay(0.3)
        assert utils._get_request_delay() == 0.3

    def test_delay_is_thread_local(self):
        utils.set_request_delay(0.5)
        other_delay = [None]

        def worker():
            other_delay[0] = utils._get_request_delay()

        t = threading.Thread(target=worker)
        t.start()
        t.join()
        assert other_delay[0] == 0  # default, not 0.5


# ---------------------------------------------------------------------------
# Auto-resend counter (thread-local)
# ---------------------------------------------------------------------------

class TestAutoResendCounter:
    def test_reset(self):
        utils.reset_auto_resend_counter()
        assert utils._get_auto_resend_counter() == 0

    def test_increment(self):
        utils.reset_auto_resend_counter()
        utils._increment_auto_resend_counter()
        utils._increment_auto_resend_counter()
        assert utils._get_auto_resend_counter() == 2

    def test_counter_is_thread_local(self):
        utils.reset_auto_resend_counter()
        utils._increment_auto_resend_counter()
        utils._increment_auto_resend_counter()
        other_count = [None]

        def worker():
            other_count[0] = utils._get_auto_resend_counter()

        t = threading.Thread(target=worker)
        t.start()
        t.join()
        assert other_count[0] == 0  # default for new thread


# ---------------------------------------------------------------------------
# Concurrent mode
# ---------------------------------------------------------------------------

class TestConcurrentMode:
    def test_default_is_false(self):
        assert utils._concurrent_mode is False

    def test_set_concurrent_mode(self):
        utils.set_concurrent_mode(True)
        assert utils._concurrent_mode is True
        utils.set_concurrent_mode(False)
        assert utils._concurrent_mode is False

    def test_wait_user_input_returns_pass_in_concurrent_mode(self):
        utils.set_concurrent_mode(True)
        assert utils.wait_user_input() == 'pass'


# ---------------------------------------------------------------------------
# get_proxy()
# ---------------------------------------------------------------------------

class TestGetProxy:
    def test_returns_none_when_no_proxies(self):
        utils.proxies = None
        assert utils.get_proxy() is None

    def test_returns_proxy_by_index(self):
        utils.proxies = ['http://p1:8080', 'socks://p2:1080']
        assert utils.get_proxy(num=0) == 'http://p1:8080'
        assert utils.get_proxy(num=1) == 'socks://p2:1080'

    def test_returns_random_proxy(self):
        utils.proxies = ['http://p1:8080']
        assert utils.get_proxy() == 'http://p1:8080'

    def test_returns_none_for_invalid_proxy(self):
        utils.proxies = ['invalid-proxy']
        assert utils.get_proxy(num=0) is None


# ---------------------------------------------------------------------------
# generator()
# ---------------------------------------------------------------------------

class TestGenerator:
    def test_basic_generation(self):
        result = utils.generator(['Hello World'])
        assert 'helloworld' in result
        assert 'hello_world' in result
        assert 'hello-world' in result

    def test_filters_short_words(self):
        result = utils.generator(['ab', 'cd', 'longword'])
        # words <= 3 chars are filtered
        assert 'ab' not in result
        assert 'longword' in result

    def test_filters_blacklisted_words(self):
        result = utils.generator(['https://example.com'])
        assert 'http' not in result
        assert 'https' not in result
        assert 'com' not in result

    def test_deduplicates_and_lowercases(self):
        result = utils.generator(['HELLO', 'hello', 'Hello'])
        assert result.count('hello') == 1

    def test_splits_on_dot(self):
        result = utils.generator(['test.case'])
        assert 'testcase' in result
        assert 'test_case' in result
        assert 'test-case' in result

    def test_extracts_first_part_if_last_part_short(self):
        result = utils.generator(['example.io'])
        # 'io' has len < 5, so 'example' should be in result
        assert 'example' in result


# ---------------------------------------------------------------------------
# compile_subdomain()
# ---------------------------------------------------------------------------

class TestCompileSubdomain:
    def test_basic(self):
        urls = utils.compile_subdomain('example.com', ['test', 'demo'])
        assert 'https://test.example.com' in urls
        assert 'https://demo.example.com' in urls

    def test_custom_proto(self):
        urls = utils.compile_subdomain('example.com', ['test'], proto='http://')
        assert 'http://test.example.com' in urls

    def test_filters_invalid_characters(self):
        urls = utils.compile_subdomain('example.com', ['valid', 'inv@lid', 'al so'])
        hostnames = [u.split('://')[1].split('.')[0] for u in urls]
        assert 'valid' in hostnames
        assert 'inv@lid' not in hostnames
        assert 'al so' not in hostnames

    def test_lowercases_and_deduplicates(self):
        urls = utils.compile_subdomain('example.com', ['Test', 'TEST', 'test'])
        assert len(urls) == 1
        assert 'https://test.example.com' in urls


# ---------------------------------------------------------------------------
# compile_url()
# ---------------------------------------------------------------------------

class TestCompileUrl:
    def test_basic(self):
        urls = utils.compile_url('example.com', ['/path1', '/path2'])
        assert 'https://example.com/path1' in urls
        assert 'https://example.com/path2' in urls

    def test_custom_proto(self):
        urls = utils.compile_url('example.com', ['/p'], proto='http://')
        assert 'http://example.com/p' in urls

    def test_deduplicates(self):
        urls = utils.compile_url('example.com', ['/dup', '/dup', '/dup'])
        assert len(urls) == 1


# ---------------------------------------------------------------------------
# make_request() — async, uses httpx mock
# ---------------------------------------------------------------------------

class TestMakeRequest:
    def test_returns_response_on_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                utils.make_request(mock_client, 'https://example.com', 'head')
            )
            assert result[0] is None  # uuid
            assert result[1] == mock_response
        finally:
            loop.close()

    def test_returns_url_on_429(self):
        mock_response = MagicMock()
        mock_response.status_code = 429

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                utils.make_request(mock_client, 'https://example.com', 'head')
            )
            assert result == [None, 'https://example.com']
        finally:
            loop.close()

    def test_returns_url_on_503(self):
        mock_response = MagicMock()
        mock_response.status_code = 503

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                utils.make_request(mock_client, 'https://example.com', 'head')
            )
            assert result == [None, 'https://example.com']
        finally:
            loop.close()

    def test_preserves_uuid(self):
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                utils.make_request(mock_client, 'https://example.com', 'get', uuid='abc-123')
            )
            assert result[0] == 'abc-123'
            assert result[1] == mock_response
        finally:
            loop.close()

    def test_request_delay_is_applied(self):
        """When request delay is set, make_request sleeps before acquiring semaphore."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)

        utils.set_request_delay(0.05)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            start = time.monotonic()
            loop.run_until_complete(
                utils.make_request(mock_client, 'https://example.com', 'head')
            )
            elapsed = time.monotonic() - start
            assert elapsed >= 0.04  # allow small tolerance
        finally:
            utils.set_request_delay(0)
            loop.close()


# ---------------------------------------------------------------------------
# perform_request() dispatches correctly
# ---------------------------------------------------------------------------

class TestPerformRequest:
    def test_head_method(self):
        client = AsyncMock()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(utils.perform_request(client, 'http://x', 'head', None, None, None))
        client.head.assert_awaited_once()
        loop.close()

    def test_post_method(self):
        client = AsyncMock()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(utils.perform_request(client, 'http://x', 'post', {'key': 'val'}, None, None))
        client.post.assert_awaited_once()
        loop.close()

    def test_get_method(self):
        client = AsyncMock()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(utils.perform_request(client, 'http://x', 'get', None, None, None))
        client.get.assert_awaited_once()
        loop.close()
