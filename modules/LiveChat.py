import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'LiveChat'


def get_tags():
    return ['subdomain', 'nolimit', 'support']


def get_description():
    return 'This module uses bruteforce of ladesk.com subdomain-sites to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['euroconnect', 'f45', 'darex'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set(words.lower() for words in words))
    domains = compile_subdomain('ladesk.com', words, proto='https://')
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(domains, method='HEAD'))
    founded_projects = ['https://{}/'.format(r.url.host) for r in responses if r.status_code != 404]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
