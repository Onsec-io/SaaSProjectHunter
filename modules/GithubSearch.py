import asyncio
from utils import compile_url, async_requests
import re
import logger
log = logger.get_logger('logger')


def get_name():
    return 'GithubSearch'


def get_version():
    return '1.2'


def get_description():
    return 'This module uses GitHub search (/search/count) and extracts values from responses'


def wordslist_for_check_module():
    return {
        'real': ['google', 'search', 'random'],
        'fake': ['micrrverv34', 'uenrf348', 'randomsearch938jf34']
    }


def run(words):
    founded_projects = []
    types = [
        'repositories',
        'issues',
        'pullrequests',
        'discussions',
        'users',
        'commits',
        'registrypackages',
        'wikis',
        'topics',
        'marketplace',
    ]
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set([item.lower() for item in words]))  # lowercase and unique
    params = ['/search/count?q=%22{}%22&type={}'.format(word, type_of_search) for word in words for type_of_search in types]
    urls = compile_url('github.com', params)
    log.debug('Compiled {} urls for request ({})'.format(len(urls), get_name()))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    for r in responses:
        if 'Counter--primary' in r.text:  # Counter--primary in response (html-code)
            match = re.search(r'q=%22([^&]+)%22', str(r.url))  # extract value of param `q` from original URL
            if match.group(1) in words:
                founded_projects.append('https://github.com/search?q=%22{}%22'.format(match.group(1)))
    founded_projects = list(set(founded_projects))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
