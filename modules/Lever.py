import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Lever'


def get_version():
    return '1.0'


def get_tags():
    return ['hr']


def get_description():
    return 'This module uses bruteforce URL-path over lever.co/<path> to find companies jobs and careers pages'


def wordslist_for_check_module():
    return {
        'real': ['quantco-', 'finn', 'welocalize'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set(words.lower() for words in words))  # lowercase and remove doubles
    urls = compile_url('jobs.lever.co/', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='HEAD'))
    founded_projects = [r.url for r in responses if r.status_code != 404]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
