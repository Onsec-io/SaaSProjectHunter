import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'breezy'


def get_version():
    return '1.0'


def get_tags():
    return ['subdomain', 'hr']


def get_description():
    return 'This module uses bruteforce of breezy.hr subdomain-sites to find companies jobs and careers pages'


def wordslist_for_check_module():
    return {
        'real': ['mukuru', 'almentor', 'urrly'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set(words.lower() for words in words))
    domains = compile_subdomain('breezy.hr', words, proto='https://')
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(domains, method='HEAD'))
    founded_projects = []
    for r in responses:
            if r.status_code == 403:
                log.error('Your IP has been blocked: response code {} for {}'.format(r.status_code, r.url))
            elif r.status_code != 302:
                 founded_projects.append(r.url.host)
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
