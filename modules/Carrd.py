import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Carrd'


def get_tags():
    return ['subdomain', 'nolimit', 'website']


def get_description():
    return 'This module uses bruteforce of carrd.co subdomain to find one-page sites'


def wordslist_for_check_module():
    return {
        'real': ['themakingof', 'startwith'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('carrd.co', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        # Carrd returns 404 for non-existent sites
        if r.status_code != 404:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
