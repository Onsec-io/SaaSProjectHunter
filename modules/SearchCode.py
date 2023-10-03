import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'SearchCode'


def get_version():
    return '1.0'


def get_description():
    return 'This module uses searchcode.com API'


def wordslist_for_check_module():
    import time
    tmp = str(int(time.time()))
    return {
        'real': ['mlb.com', 'searchcode.com', 'true'],
        'fake': ['8457fj20d'+tmp, 'uenrf348'+tmp, '8rurur8ud'+tmp]
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [word.lower() for word in words]
    urls = compile_url('searchcode.com/api/codesearch_I/?per_page=1&q=', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        if r.status_code != 200:
            log.warning('Status code: {}'.format(r.status_code))
        elif r.json()['total'] > 0:
            founded_projects.append('https://searchcode.com/?q={}'.format(str(r.url).split('=')[-1]))

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
