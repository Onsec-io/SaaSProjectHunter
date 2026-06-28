import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Lovable'


def get_tags():
    return ['subdomain', 'nolimit', 'paas']


def get_description():
    return 'This module uses bruteforce of lovable.app subdomains (published <project> and preview--<project> hosts) to find deployed apps'


def wordslist_for_check_module():
    return {
        'real': ['ai-app-gallery', 'innovate-code-gallery', 'ux-experience-gallery'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    # Canonical published host: <project>.lovable.app
    urls = compile_subdomain('lovable.app', words)
    # Preview host: preview--<project>.lovable.app (live apps 302 to auth-bridge, fakes 404)
    preview_words = ['preview--{}'.format(w) for w in words]
    urls += compile_subdomain('lovable.app', preview_words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        # Lovable returns 404 for non-existent apps
        # Valid apps return 200 or redirects
        if r.status_code != 404:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} apps'.format(get_name(), len(founded_projects)))
    return founded_projects
