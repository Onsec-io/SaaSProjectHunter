import asyncio
from utils import async_nslookup, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'AzureStorage'


def get_version():
    return '1.1'


def get_description():
    return 'This module uses bruteforce of subdomains by Azure Storage endpoints'


def wordslist_for_check_module():
    return {
        'real': ['stratasysstorage01', 'rcastoragev2', 'e2stdaccq001'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    domains = []
    endpoint = 'blob.core.windows.net'  # https://learn.microsoft.com/en-us/rest/api/storageservices/authorize-requests-to-azure-storage
    domains.extend(compile_subdomain(endpoint, words, proto=''))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_nslookup(domains))
    founded_projects = ['https://{}'.format(domain) for domain in responses if domain is not None]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
