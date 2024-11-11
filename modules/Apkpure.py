import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Apkpure'


def get_version():
    return '1.1'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses URL path enumeration at apkpure.net to search for apps and games (apk files)'


def wordslist_for_check_module():
    return {
        'real': ['pokemon', 'fibrum', 'foundation'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set([item.lower() for item in words]))  # lowercase and remove doubles
    urls = compile_url('apkpure.net/api/v1/search_suggestion_new?limit=1&key=', [f'{item.lower()}' for item in words])
    urls += compile_url('apkpure.net/developer/', [item.upper() for item in words])
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='HEAD', http2=False))
    founded_projects = []
    for r in responses:
        if (r.status_code == 200 and not r.headers.get('Content-Length', None)) or (r.headers.get('Content-Length') == 2):
            founded_projects.append(str(r.url))

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
