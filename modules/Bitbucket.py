import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Bitbucket'


def get_version():
    return '1.0'


def get_description():
    return 'This module uses bruteforce of bitbucket.org URLs to find users and companies'


def wordslist_for_check_module():
    return {
        'real': ['multicoreware', 'lukaszlaba', 'HR_ELEKTRO'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set(['{}/'.format(w.lower().strip()) for w in words]))
    urls = compile_url('bitbucket.org/', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = [str(r.url) for r in responses if r.status_code != 404]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
