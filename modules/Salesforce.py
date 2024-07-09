import asyncio
from utils import compile_subdomain, async_nslookup
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Salesforce'


def get_version():
    return '1.0'


def get_tags():
    return ['dns', 'subdomain', 'nolimit']


def get_description():
    return 'This module uses bruteforce of my.salesforce.com subdomain-sites to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['abbott', 'myaxabiz', 'marriottintl'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    domains = compile_subdomain('my.salesforce.com', words, proto='')
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_nslookup(domains))
    founded_projects = ['https://{}/'.format(domain) for domain in responses if domain is not None]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
