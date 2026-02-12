import asyncio
from utils import compile_url, async_requests
import re
import logger
log = logger.get_logger('logger')


def get_name():
    return 'TruffleSecurity'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses Forager from TruffleSecurity to find leaked credentials'


def wordslist_for_check_module():
    return {
        'real': ['google', 'test', 'microsoft'],
        'fake': ['micraaaaaarverv34', 'uenrf348', 'sde2d23A']
    }


def run(words):
    founded_projects = []
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]  # lowercase
    words = [w for w in words if re.match(r'^[a-z0-9.-]+$', w)]  # valid hostnames only
    params = ['/api/v1/public/secrets/domain?domain={}&page_size=1&page=0'.format(word) for word in words]
    urls = compile_url('forager.trufflesecurity.com', params)
    log.debug('Compiled {} urls for request ({})'.format(len(urls), get_name()))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    for r in responses:
        if "total_count_items" in r.text:
            if '"total_count_items":0' not in r.text:
                match = re.search(r'domain=([^&]+)&', str(r.url))  # extract value of param `domain` from original URL
                if match.group(1) in words:
                    founded_projects.append('https://forager.trufflesecurity.com/explore?q={}'.format(match.group(1)))
        else:
            log.error('Error in response: {}\n{}'.format(r.url, r.text))
    founded_projects = list(set(founded_projects))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
