import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'BambooHR'


def get_tags():
    return ['subdomain', 'nolimit', 'hr']


def get_description():
    return 'This module uses bruteforce of bamboohr.com subdomain-sites to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['validic', 'hutchcc', 'watchguard'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set(words.lower() for words in words))
    domains = compile_subdomain('bamboohr.com/careers', words, proto='https://')
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(domains, method='HEAD'))
    founded_projects = [r.url for r in responses if r.status_code != 404 and r.status_code != 302]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
