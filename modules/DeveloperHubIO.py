import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'DeveloperHubIO'


def get_tags():
    return ['subdomain', 'nolimit', 'docs']


def get_description():
    return 'This module uses bruteforce of developerhub.io subdomain to find documentation portals'


def wordslist_for_check_module():
    return {
        'real': ['blink', 'payerdocs', 'wia'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('developerhub.io/robots.txt', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        if r.status_code != 200:
            continue
        text = r.text.lower().replace('\ufeff', '').strip()
        expected_sitemap = 'sitemap: https://{}/sitemap.xml'.format(r.url.host).lower()
        if expected_sitemap in text:
            founded_projects.append('https://{}/'.format(r.url.host))
    founded_projects = list(set(founded_projects))
    log.info('{}: founded {} docs'.format(get_name(), len(founded_projects)))
    return founded_projects
