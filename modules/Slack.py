import asyncio
import secrets
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Slack'


def get_tags():
    return ['subdomain', 'limit', 'collaboration']


def get_description():
    return 'This module uses bruteforce of slack.com subdomain-sites to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['friendsofredaxo', 'demo', 'cloud'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    canary = 'sphc{}'.format(secrets.token_hex(8))
    urls = compile_subdomain('slack.com', list(words) + [canary])
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    canary_host = '{}.slack.com'.format(canary)
    canary_status = None
    for r in responses:
        if r.url.host == canary_host:
            canary_status = r.status_code
            break
    # Existing workspaces answer 403 (WAF/login wall) or 200/302; non-existent
    # names answer 404. Treat 403 as a hit only while a random canary still 404s,
    # so a blanket WAF 403 cannot mark every word as a workspace.
    accept_403 = canary_status == 404
    if canary_status is None:
        log.warning('Slack canary request dropped; not treating 403 as a workspace')
    elif not accept_403:
        log.warning('Slack canary returned {}; suppressing 403 hits'.format(canary_status))
    founded_projects = []
    for r in responses:
        if r.url.host == canary_host:
            continue
        if r.status_code in (200, 302) or (r.status_code == 403 and accept_403):
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
