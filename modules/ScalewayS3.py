import asyncio
from utils import async_requests, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'ScalewayS3'


def get_tags():
    return ['s3', 'bucket', 'subdomain', 'nolimit']


def get_description():
    return 'This module uses bruteforce name of bucket over endpoint <region>.scw.cloud to find interesting Object Storages'


def wordslist_for_check_module():
    return {
        'real': ['waldorfplumbing', 'spray-on-grass-auckland', 'website-cn'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    endpoints = [
        's3.nl-ams.scw.cloud',
        's3.pl-waw.scw.cloud',
        's3.fr-par.scw.cloud',
    ]
    urls = []
    for endpoint in endpoints:
        urls.extend(compile_subdomain(endpoint, words, proto='https://'))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = [str(r.url) for r in responses if r.status_code != 404]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
