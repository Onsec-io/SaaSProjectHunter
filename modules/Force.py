import asyncio
from utils import compile_subdomain, async_nslookup
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Force'


def get_version():
    return '1.0'


def get_tags():
    return ['subdomain']


def get_description():
    return 'This module uses bruteforce of force.com subdomain to find login pages and public knowledge bases.'


def wordslist_for_check_module():
    return {
        'real': ['kmbl', 'digitalwellnessus', 'kukaprod'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set(item.lower() for item in words))  # lowercase and deduplicate
    domains = compile_subdomain('force.com', words, proto='')
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_nslookup(domains))
    founded_projects = ['https://{}/'.format(domain) for domain in responses if domain is not None]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
