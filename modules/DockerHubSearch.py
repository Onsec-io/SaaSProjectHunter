import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'DockerHubSearch'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses bruteforce of API search to find repos/images'


def wordslist_for_check_module():
    return {
        'real': ['ubuntu', 'docker', 'alpine'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    urls = compile_url('hub.docker.com/api/search/v3/catalog/search?size=0&query=', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        if r.status_code == 200 and r.json()['total'] != 0:
            word_from_url = str(r.url).split('query=')[1]
            founded_projects.append('https://hub.docker.com/search?q={}'.format(word_from_url))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
