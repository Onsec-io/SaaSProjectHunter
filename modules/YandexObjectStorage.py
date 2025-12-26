import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'YandexObjectStorage'


def get_tags():
    return ['s3', 'bucket']


def get_description():
    return 'This module uses bruteforce name of bucket over endpoint storage.yandexcloud.net to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['kubium-storage', 'astrade', 'certificates-prod'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]  # lowercase
    urls = compile_url('storage.yandexcloud.net/', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='head'))

    founded_projects = []
    for r in responses:
        if r.status_code == 404:
            continue
        elif r.status_code == 403:
            founded_projects.append('{} ({})'.format(r.url, 'Access Denied'))
        else:
            founded_projects.append(str(r.url))

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
