import asyncio
from utils import async_requests, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'GhostIO'


def get_version():
    return '1.0'


def get_tags():
    return []


def get_description():
    return 'This module uses bruteforce subdomain over ghost.io to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['ecoinometrics', 'onsec-io', 'takushiyoshida'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('ghost.io', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        if r.status_code == 302 and 'Location' in r.headers:
            if r.headers['Location'] != 'https://error.ghost.org/':
                founded_projects.append('{} -> {}'.format(str(r.url), str(r.headers['Location'])))

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
