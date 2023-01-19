import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'DockerHubUsers'


def get_version():
    return '1.0'


def get_description():
    return 'This module uses bruteforce of API hub.docker.com/v2/users/<> to find users/orgs'


def wordslist_for_check_module():
    return {
        'real': ['bitnami', 'wallarm', 'bdfoster'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    urls = compile_url('hub.docker.com/v2/users/', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, http2=False))
    founded_projects = [str(r.url).replace('/v2/users/', '/u/') for r in responses if r.status_code != 404]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
