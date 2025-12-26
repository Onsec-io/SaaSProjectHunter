import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Glitch'


def get_tags():
    return ['subdomain', 'nolimit', 'hosting']


def get_description():
    return 'This module uses bruteforce of glitch.me subdomain to find hosted projects'


def wordslist_for_check_module():
    return {
        'real': ['typing-games', 'url-parts'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('glitch.me', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        # Glitch returns 410 Gone for non-existent projects, 308 for existing
        if r.status_code != 410:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} projects'.format(get_name(), len(founded_projects)))
    return founded_projects
