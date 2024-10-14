import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'APKCombo'


def get_version():
    return '1.0'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses URL path enumeration at https://apkcombo.com/[search,developer]/<path> to search for apps and games (apk files)'


def wordslist_for_check_module():
    return {
        'real': ['pokemon', 'fibrum', 'foundation'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    headers = {'Accept-Encoding': ''}
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set([item.lower() for item in words]))  # lowercase and remove doubles
    urls = compile_url('apkcombo.com/search/', [f'%22{item.lower()}%22' for item in words])
    urls += compile_url('apkcombo.com/developer/', [item.upper() for item in words])
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='GET', additional_headers=headers))
    founded_projects = [str(r.url) for r in responses if r.status_code == 200 and ('content content-apps' in r.text or '<h1 class="title heading">Developer: ' in r.text)]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
