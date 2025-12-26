import asyncio
from utils import async_requests, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'LinodeS3'


def get_tags():
    return ['s3', 'bucket', 'subdomain', 'nolimit']


def get_description():
    return 'This module uses bruteforce name of bucket over <region>.linodeobjects.com to find interesting buckets'


def wordslist_for_check_module():
    return {
        'real': ['backstagecleaning', 'horizon-cleaning-services', 'patriot4'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]  # lowercase
    # https://www.linode.com/docs/products/storage/object-storage/guides/manage-buckets/
    import re
    filtered_words = []
    pattern = r"^(?!.*\.\.)(?!.*[-.]{2})(?!.*_$)(?!.*-$)(?!.*\.$)[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$"
    for word in words:
        if re.match(pattern, word):
            filtered_words.append(word)

    # https://www.linode.com/docs/products/storage/object-storage/#availability
    endpoints = [
        'us-east-1.linodeobjects.com',
        'ap-south-1.linodeobjects.com',
        'eu-central-1.linodeobjects.com',
        'us-southeast-1.linodeobjects.com',
    ]

    urls = []
    for endpoint in endpoints:
        urls.extend(compile_subdomain(endpoint, filtered_words, proto='https://'))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = [str(r.url) for r in responses if r.status_code != 404]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
