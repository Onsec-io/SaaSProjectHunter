import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Substack'


def get_tags():
    return ['subdomain', 'nolimit', 'newsletter']


def get_description():
    return 'This module uses bruteforce of substack.com subdomain to find company newsletters'


def wordslist_for_check_module():
    return {
        'real': ['platformer', 'simonowens', 'davidlebovitz'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('substack.com', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    redirect_urls = []
    for r in responses:
        # Substack returns 404 for non-existent newsletters, 200 for existing
        # 302 redirects need to be followed and checked (e.g., onsec-io -> onsecio -> 404)
        if r.status_code == 302 and 'location' in r.headers:
            redirect_urls.append(r.headers['location'])
        elif r.status_code != 404 and r.url.host != 'substack.com':
            founded_projects.append('https://{}/'.format(r.url.host))
    # Follow redirects and verify they don't lead to 404
    if redirect_urls:
        log.debug('Following {} redirects...'.format(len(redirect_urls)))
        redirect_responses = loop.run_until_complete(async_requests(redirect_urls))
        for r in redirect_responses:
            if r.status_code != 404 and r.url.host != 'substack.com':
                founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} newsletters'.format(get_name(), len(founded_projects)))
    return founded_projects
