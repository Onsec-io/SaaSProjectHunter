import asyncio
import random
import re
from utils import async_requests, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'OVHCloudS3'


def get_version():
    return '1.0'


def get_tags():
    return ['s3', 'backet', 'subdomain', 'nolimit']


def get_description():
    return 'This module uses bruteforce name of bucket over endpoint <region>.<type>.cloud.ovh.net to find OVH Cloud Object Storage'


def wordslist_for_check_module():
    return {
        'real': ['mycity', 'scanr-data', 'newdoc-fiec-prod-container'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    endpoints = {  # https://help.ovhcloud.com/csm/en-au-public-cloud-storage-s3-location
        'cloud.ovh.net': [
            'sbg',
            'uk',
            'de',
            'waw',
            'bhs',
            'gra',
        ],
        'perf.cloud.ovh.net': [
            'gra',
            'sbg',
            'bhs',
        ],
        'io.cloud.ovh.net': [
            'gra',
            'sbg',
            'de',
            'bhs',
            'rbx',
            'waw',
            'uk',
        ]
    }

    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    urls = []
    for endpoint, regions in endpoints.items():
        for region in regions:
            urls += compile_subdomain('s3.{}.{}'.format(region, endpoint), words)

    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = [str(r.url) for r in responses if r.status_code != 404]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
