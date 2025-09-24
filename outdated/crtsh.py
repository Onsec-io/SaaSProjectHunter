import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'crtsh'


def get_version():
    return '1.0'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses bruteforce of API search to find subdomains'


def wordslist_for_check_module():
    return {
        'real': ['onsec.io', 'crt', 'google.com'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    urls = compile_url('crt.sh?output=json&q=%.', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='head'))
    founded_projects = []
    for r in responses:
        if r.status_code == 200 and r.headers.get('content-length') != '2':
            founded_projects.append(r.url)
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
