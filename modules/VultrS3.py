import asyncio
from utils import async_requests, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'VultrS3'


def get_version():
    return '1.2'


def get_tags():
    return ['s3', 'backet', 'subdomain', 'nolimit']


def get_description():
    return 'This module uses bruteforce name of bucket over <region>.vultrobjects.com to find interesting buckets'


def wordslist_for_check_module():
    return {
        'real': ['alicante', 'ndclibrary', 'outdoor-luxury'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('_', '-') for item in words]  # replace underscores with dashes

    # https://www.vultr.com/docs/vultr-object-storage
    endpoints = [
        'ams1.vultrobjects.com',
        'blr1.vultrobjects.com',
        'ewr1.vultrobjects.com',
        'sjc1.vultrobjects.com',
        'sgp1.vultrobjects.com',
        'del1.vultrobjects.com',
    ]

    urls = []
    for endpoint in endpoints:
        urls.extend(compile_subdomain(endpoint, words, proto='https://'))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = [str(r.url) for r in responses if r.status_code != 404 and r.status_code != 502]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
