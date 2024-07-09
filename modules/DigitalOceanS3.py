import asyncio
from utils import async_requests, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'DigitalOceanS3'


def get_version():
    return '1.0'


def get_tags():
    return ['s3', 'backet', 'subdomain', 'nolimit']


def get_description():
    return 'This module uses bruteforce name of bucket over <region>.digitaloceanspaces.com to find interesting buckets'


def wordslist_for_check_module():
    return {
        'real': ['keyword-research', 'jartec', '911-assets'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]  # lowercase

    # https://docs.digitalocean.com/products/spaces/details/availability/
    endpoints = [
        # 'nyc1.digitaloceanspaces.com',
        'nyc3.digitaloceanspaces.com',
        'ams3.digitaloceanspaces.com',
        'sfo3.digitaloceanspaces.com',
        'sgp1.digitaloceanspaces.com',
        # 'lon1.digitaloceanspaces.com',
        'fra1.digitaloceanspaces.com',
        # 'tor1.digitaloceanspaces.com',
        # 'blr1.digitaloceanspaces.com',
        'syd1.digitaloceanspaces.com',
    ]

    urls = []
    for endpoint in endpoints:
        urls.extend(compile_subdomain(endpoint, words, proto='https://'))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = [str(r.url) for r in responses if r.status_code != 404]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
