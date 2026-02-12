import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logger
import utils

log = logger.get_logger('logger')

# Modules sharing a rate limit are grouped to run sequentially within the group.
# Groups targeting different services run concurrently via threads.
SERVICE_GROUPS = {
    'github': ['GithubSearch', 'GithubUsers', 'GithubGist'],
    'dockerhub': ['DockerHubSearch', 'DockerHubUsers'],
    'postman': ['PostmanSearch', 'PostmanUsers'],
    'npm': ['NPMjs', 'NPMsSearch'],
}

# Invert for fast lookup: module_name -> group_key
_MODULE_TO_GROUP = {}
for _group_key, _members in SERVICE_GROUPS.items():
    for _name in _members:
        _MODULE_TO_GROUP[_name] = _group_key


def group_modules(modules):
    """Group modules by shared service. Returns list of lists."""
    groups = {}
    ungrouped = []

    for module in modules:
        name = module.get_name()
        group_key = _MODULE_TO_GROUP.get(name)
        if group_key:
            groups.setdefault(group_key, []).append(module)
        else:
            ungrouped.append([module])

    return list(groups.values()) + ungrouped


def _get_rate_tier(modules):
    """Determine rate tier from module tags."""
    for module in modules:
        tags = module.get_tags()
        if 'limit' in tags:
            return 'limit'
        if 'dns' in tags:
            return 'dns'
    return 'nolimit'


_print_lock = threading.Lock()


def _run_group(group, words):
    """Worker function: runs a group of modules sequentially in its own thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    tier = _get_rate_tier(group)
    utils.set_rate_tier(tier)
    utils.set_request_delay(0.3 if tier == 'limit' else 0)
    utils.reset_auto_resend_counter()

    results = []
    try:
        for module in group:
            name = module.get_name()
            with _print_lock:
                print('Run {}'.format(name))
            try:
                for url in module.run(words):
                    results.append((name, url))
            except Exception as e:
                with _print_lock:
                    log.error('Module {} failed: {}'.format(name, e))
            with _print_lock:
                log.debug('Completed {}'.format(name))
    finally:
        loop.close()

    return results


def _run_check_group(group):
    """Worker function: runs check for a group of modules sequentially in its own thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    tier = _get_rate_tier(group)
    utils.set_rate_tier(tier)
    utils.set_request_delay(0.3 if tier == 'limit' else 0)
    utils.reset_auto_resend_counter()

    failed = []
    try:
        for module in group:
            try:
                if not utils.run_check_module(module):
                    failed.append(module.get_name())
            except Exception as e:
                failed.append(module.get_name())
                with _print_lock:
                    log.error('Check {} failed: {}'.format(module.get_name(), e))
    finally:
        loop.close()

    return failed


def check_concurrent(modules, max_workers=None):
    """Check modules concurrently, grouping by shared service."""
    groups = group_modules(modules)

    if max_workers is None:
        max_workers = min(len(groups), 20)

    log.info('Concurrent check: {} groups, {} workers'.format(len(groups), max_workers))

    utils.set_concurrent_mode(True)
    all_failed = []

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_run_check_group, group): group
                for group in groups
            }
            try:
                for future in as_completed(futures):
                    try:
                        failed = future.result()
                        all_failed.extend(failed)
                    except Exception as e:
                        group = futures[future]
                        names = [m.get_name() for m in group]
                        all_failed.extend(names)
                        log.error('Check group {} failed: {}'.format(names, e))
            except KeyboardInterrupt:
                print('\nStopping... waiting for running checks to finish')
                executor.shutdown(wait=False, cancel_futures=True)
    finally:
        utils.set_concurrent_mode(False)

    utils._print_check_summary(len(modules), all_failed)


def run_concurrent(modules, words, max_workers=None):
    """Run modules concurrently, grouping by shared service."""
    groups = group_modules(modules)

    if max_workers is None:
        max_workers = min(len(groups), 20)

    log.info('Concurrent mode: {} groups, {} workers'.format(len(groups), max_workers))

    utils.set_concurrent_mode(True)
    all_results = []

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_run_group, group, words): group
                for group in groups
            }
            try:
                for future in as_completed(futures):
                    try:
                        results = future.result()
                        all_results.extend(results)
                    except Exception as e:
                        group = futures[future]
                        names = [m.get_name() for m in group]
                        log.error('Group {} failed: {}'.format(names, e))
            except KeyboardInterrupt:
                print('\nStopping... waiting for running modules to finish')
                executor.shutdown(wait=False, cancel_futures=True)
    finally:
        utils.set_concurrent_mode(False)

    return all_results
