import asyncio
from utils import async_nslookup, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'ServiceNow'


def get_tags():
    return ['dns', 'nolimit', 'itsm']


def get_description():
    return 'This module finds ServiceNow instances by resolving service-now.com subdomains (non-existent instances do not resolve)'


def wordslist_for_check_module():
    return {
        'real': ['nvidia', 'snowflake', 'adobe'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    subdomains = compile_subdomain('service-now.com', words, proto='')
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_nslookup(subdomains))
    founded_projects = ['https://{}/'.format(domain) for domain in responses if domain is not None]
    log.info('{}: founded {} instances'.format(get_name(), len(founded_projects)))
    return founded_projects
