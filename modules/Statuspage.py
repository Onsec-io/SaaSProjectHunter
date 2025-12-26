import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Statuspage'


def get_tags():
    return ['subdomain', 'nolimit', 'status']


def get_description():
    return 'This module uses bruteforce of statuspage.io subdomain to find status pages'


def wordslist_for_check_module():
    return {
        'real': ['releasy', 'exact', 'playvox-customer-ai'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('statuspage.io', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        # Statuspage returns 302 to www.statuspage.io for non-existent, 200 for existing
        if r.status_code == 200:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} status pages'.format(get_name(), len(founded_projects)))
    return founded_projects
