import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'GrayhatWarfare'


def get_tags():
    return ['limit', 'bucket']


def get_description():
    return 'This module uses GrayhatWarfare site for search files in open buckets'


def wordslist_for_check_module():
    return {
        'real': ['google', 'search', 'random'],
        'fake': ['micrrverv34', 'uenrf348', 'randomsearch938jf34']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set([item.lower() for item in words]))  # lowercase and unique
    params = ['/files?keywords={}'.format(word) for word in words]
    urls = compile_url('buckets.grayhatwarfare.com', params)
    log.debug('Compiled {} urls for request ({})'.format(len(urls), get_name()))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        if 'Results for ' in r.text and 'No results found' not in r.text:
            founded_projects.append(str(r.url))
    founded_projects = list(set(founded_projects))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
