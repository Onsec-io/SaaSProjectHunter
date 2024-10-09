import asyncio
from utils import compile_url, async_requests
import re
import logger
log = logger.get_logger('logger')


def get_name():
    return 'GithubGist'


def get_version():
    return '1.3'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses GitHub Gist search (/search?q=)'


def wordslist_for_check_module():
    return {
        'real': ['google', 'test', 'umputun'],
        'fake': ['micraaaaaarverv34', 'uenrf348', 'sde2d23A']
    }


def run(words):
    founded_projects = []
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]  # lowercase
    params = ['/search?q=%22{}%22'.format(word) for word in words]
    urls = compile_url('gist.github.com', params)
    log.debug('Compiled {} urls for request ({})'.format(len(urls), get_name()))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    for r in responses:
        if not "find any gists matching" in r.text:  # Counter--primary in response (html-code)
            match = re.search(r'q=%22([^&]+)%22', str(r.url))  # extract value of param `q` from original URL
            if match.group(1) in words:
                founded_projects.append('https://gist.github.com/search?q=%22{}%22'.format(match.group(1)))
    founded_projects = list(set(founded_projects))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
