import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'APKCombo'


def get_version():
    return '1.3'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses URL path enumeration at https://apkcombo.com/[search,developer]/<path> to search for apps and games (apk files)'


def wordslist_for_check_module():
    return {
        'real': ['pokemon', 'FIBRUM', 'FunPlus International AG'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    founded_projects = []
    headers = {'Accept-Encoding': ''}
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set(['%22' + item.lower() + '%22' for item in words]))
    urls = compile_url('apkcombo.com/search/', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='GET', additional_headers=headers))
    for r in responses:
        if r.status_code == 200 and '<div class="content content-apps">' in r.text:
            founded_projects.append(str(r.url))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
