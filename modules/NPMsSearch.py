import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'NPMsSearch'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses bruteforce of API api.npms.io'


def wordslist_for_check_module():
    return {
        'real': ['date', 'nodejs', 'sdv'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]
    urls = compile_url('api.npms.io/v2/search?q=', words)
    # urls += compile_url('api.npms.io/v2/search?q=author:', words)
    # urls += compile_url('api.npms.io/v2/search?q=scope:', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='GET'))
    founded_projects = [str(r.url) for r in responses if r.text != '{"total":0,"results":[]}']
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
