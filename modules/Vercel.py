import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Vercel'


def get_tags():
    return ['subdomain', 'nolimit', 'paas']


def get_description():
    return 'This module uses bruteforce of vercel.app subdomain to find deployed applications'


def wordslist_for_check_module():
    return {
        'real': ['nordstan', 'alnf', 'enginedj'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('vercel.app', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        # Vercel returns 404 with "DEPLOYMENT_NOT_FOUND" for non-existent deployments
        # Valid deployments return 200 or redirects
        if r.status_code != 404:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} apps'.format(get_name(), len(founded_projects)))
    return founded_projects
