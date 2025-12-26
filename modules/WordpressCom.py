import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'WordpressCom'


def get_tags():
    return ['subdomain', 'nolimit', 'blog']


def get_description():
    return 'This module uses bruteforce of wordpress.com subdomain to find blogs'


def wordslist_for_check_module():
    return {
        'real': ['blogsencastellano', 'networkn8', 'techcrunch'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('wordpress.com', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        # WordPress.com returns 302 redirect to typo page for non-existent blogs
        # Valid blogs return 200
        if r.status_code == 200:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} blogs'.format(get_name(), len(founded_projects)))
    return founded_projects
