import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Zoho'


def get_tags():
    return ['subdomain', 'nolimit', 'support']


def get_description():
    return 'This module uses bruteforce of wiki.zoho.com and zohodesk.com subdomain-sites to find interesting projects (Wiki + Desk)'


def wordslist_for_check_module():
    return {
        'real': ['tanzaniatravel', 'palemonium', 'mano', 'nuisocial', 'manageengine'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    urls = compile_subdomain('wiki.zoho.com', words)  # search subdomains *.wiki.zoho.com
    urls += compile_subdomain('zohodesk.com', words)  # search subdomains *.zohodesk.com
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    founded_projects = []
    responses = loop.run_until_complete(async_requests(urls, method='GET', http2=False))
    for r in responses:
        if 'wiki.zoho.com' in str(r.url) and r.status_code != 404:
            founded_projects.append('https://{}/'.format(r.url.host))
        elif 'zohodesk.com' in str(r.url) and r.status_code == 301:
            founded_projects.append('https://{}/'.format(r.url.host))

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
