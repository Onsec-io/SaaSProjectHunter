import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Zendesk'


def get_version():
    return '1.1'


def get_description():
    return 'This module uses bruteforce of zendesk.com subdomain-sites to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['ubnt', 'cloud', 'demo'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    urls = compile_subdomain('zendesk.com', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = ['https://{}/'.format(r.url.host) for r in responses if r.headers.get(
        'content-length') == '0' and r.status_code == 301 and 'https://www.zendesk.com/app/help-center-closed' not in r.headers.get(
        'location')]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
