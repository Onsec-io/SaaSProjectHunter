import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Canny'


def get_tags():
    return ['subdomain', 'nolimit', 'feedback']


def get_description():
    return 'This module uses bruteforce of canny.io subdomain to find feedback portals'


def wordslist_for_check_module():
    return {
        'real': ['clickup', 'intercom', 'loom'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('canny.io', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        # Canny returns 200 for all requests, need to check body for "Company Not Found"
        if r.status_code == 200 and 'Company Not Found' not in r.text:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} portals'.format(get_name(), len(founded_projects)))
    return founded_projects
