import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Helpjuice'


def get_tags():
    return ['subdomain', 'nolimit', 'docs']


def get_description():
    return 'This module uses bruteforce of helpjuice.com subdomain to find public knowledge bases and help centers.'


def wordslist_for_check_module():
    return {
        'real': ['interfolio', 'ticketleap', 'ilab'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set(item.lower() for item in words))  # lowercase and deduplicate
    urls = compile_subdomain('helpjuice.com', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        if r.status_code == 404:
            continue
        elif r.status_code == 200:
            founded_projects.append('https://{}/'.format(r.url.host))
        else:
            log.warning('Error {} for url {}'.format(r.status_code, r.url))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
