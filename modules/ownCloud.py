import asyncio
from utils import compile_subdomain, async_requests, async_nslookup
import logger
log = logger.get_logger('logger')


def get_name():
    return 'ownCloud'


def get_version():
    return '1.0'


def get_tags():
    return ['subdomain']


def get_description():
    return 'This module uses bruteforce of owncloud.online subdomain-sites to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['instrumentsystems', 'cygnagroup', 'inventis'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    domains = compile_subdomain('owncloud.online', words, proto='https://')
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(domains, method='HEAD', http2=False))
    founded_projects = ['https://{}/'.format(r.url.host) for r in responses if r.status_code != 404 and r.status_code != 200]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
