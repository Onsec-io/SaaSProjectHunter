import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'YouTrack'


def get_tags():
    return ['subdomain', 'nolimit', 'devtools']


def get_description():
    return 'This module uses bruteforce of youtrack.cloud subdomain-sites to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['system', 'cloud', 'track'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    urls = compile_subdomain('youtrack.cloud', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = ['https://{}/'.format(r.url.host) for r in responses
                        if
                        ((r.status_code == 200 or r.status_code == 502) and 'location' not in r.headers and 'content-length' not in r.headers)
                        or
                        (r.status_code == 302 and 'content-length' in r.headers and r.headers['content-length'] == '0')]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
