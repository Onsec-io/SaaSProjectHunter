import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'ReadTheDocs'


def get_version():
    return '1.2'


def get_tags():
    return ['subdomain', 'nolimit']


def get_description():
    return 'This module uses bruteforce of readthedocs.io subdomain-sites to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['pillow', 'pycord', 'netbox'],
        'fake': ['8457fj20d', 'uenrf348', 'betwinner']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    urls = compile_subdomain('readthedocs.io', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    internal_check = []
    for r in responses:
        if r.status_code == 302 and r.headers.get('content-length') == '0' and 'location' in r.headers:
            if '.readthedocs.io/en/latest/' in r.headers.get('location'):
                log.debug('Add to internal recheck: {}'.format(r.headers.get('location')))
                internal_check.append(r.headers.get('location'))
            else:
                founded_projects.append('https://{}/'.format(r.url.host))

    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(internal_check))
    founded_projects.extend(['https://{}/'.format(r.url.host) for r in responses if r.status_code != 404])
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
