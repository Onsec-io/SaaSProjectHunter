import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Bubble'


def get_tags():
    return ['subdomain', 'nolimit', 'nocode']


def get_description():
    return 'This module uses bruteforce of bubbleapps.io subdomain to find no-code applications'


def wordslist_for_check_module():
    return {
        'real': ['newcrm', 'landingpage3', 'login-page-1'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('bubbleapps.io', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        # Bubble returns 400 for invalid app names, 200 for valid
        if r.status_code == 200:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} apps'.format(get_name(), len(founded_projects)))
    return founded_projects
