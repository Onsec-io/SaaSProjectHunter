import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'SwaggerHub'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses bruteforce of search over parameters `onwer` and `query` (https://app.swaggerhub.com/apiproxy/specs)'


def wordslist_for_check_module():
    return {
        'real': ['root', 'cloud', 'TEST', 'microSOft'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [word.lower() for word in words]
    urls = compile_url('app.swaggerhub.com/apiproxy/specs?limit=1&owner=', words)
    urls += compile_url('app.swaggerhub.com/apiproxy/specs?limit=1&query=', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        if r.json()['totalCount'] > 0 and '&owner=' in str(r.url):
            founded_projects.append('https://app.swaggerhub.com/search?owner={}'.format(str(r.url).split('=')[-1]))
        elif r.json()['totalCount'] > 0 and '&query=' in str(r.url):
            founded_projects.append('https://app.swaggerhub.com/search?query={}'.format(str(r.url).split('=')[-1]))

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
