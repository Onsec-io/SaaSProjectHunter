import asyncio
from utils import compile_url, async_requests
import re
import logger
log = logger.get_logger('logger')


def get_name():
    return 'CodebergSearch'


def get_version():
    return '1.0'


def get_description():
    return 'This module uses Codeberg search (Repositories/Users/Organizations) and extracts values from responses'


def wordslist_for_check_module():
    return {
        'real': ['google', 'search', 'random'],
        'fake': ['micrrverv34', 'uenrf348', 'randomsearch938jf34']
    }


def run(words):
    founded_projects = []
    paths = [
        'explore/repos?only_show_relevant=false&q=',
        'explore/users?q=',
        'explore/organizations?q=',
    ]
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set([item.lower() for item in words]))  # lowercase and unique
    params = ['/{}{}'.format(type_of_search, word) for word in words for type_of_search in paths]
    urls = compile_url('codeberg.org', params)
    log.debug('Compiled {} urls for request ({})'.format(len(urls), get_name()))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    for r in responses:
        if '<div class="flex-item-main">' in r.text:  # Counter--primary in response (html-code)
            founded_projects.append(str(r.url))
    founded_projects = list(set(founded_projects))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
