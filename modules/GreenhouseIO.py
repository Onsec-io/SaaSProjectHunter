import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'GreenhouseIO'


def get_version():
    return '1.0'


def get_tags():
    return []


def get_description():
    return 'Search for boards by name on the greenhouse.io platform'


def wordslist_for_check_module():
    return {
        'real': ['cargurus', 'celonis', 'contentful'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    import re
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set(item.lower() for item in words))  # lowercase and deduplicate
    urls = compile_url('boards-api.greenhouse.io/v1/boards/', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        if r.status_code == 404:
            continue
        elif r.status_code == 200 or r.status_code == 204:
            founded_projects.append('{}/departments'.format(r.url))
        else:
            log.warning('Error {} for url {}'.format(r.status_code, r.url))

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
