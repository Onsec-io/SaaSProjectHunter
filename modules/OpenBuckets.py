import asyncio
from utils import compile_url, async_requests
import logger
import random
log = logger.get_logger('logger')


def get_name():
    return 'OpenBuckets'


def get_version():
    return '1.0'


def get_tags():
    return ['limit', 'backet']


def get_description():
    return 'This module uses OpenBuckets.io search (/?keyword=)'


def wordslist_for_check_module():
    tmp = random.randint(10, 100)
    return {
        'real': ['google', 'test', 'bucket'],
        'fake': [f'micraaaaaarverv{tmp}', f'uenrf{tmp}', f'sde2d{tmp}A']
    }


def run(words):
    founded_projects = []
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set([item.lower() for item in words]))  # lowercase and unique
    params = []
    params.extend(['/api/v2/ui/files?pageSize=0&start=0&keywords={}'.format(word) for word in words])
    params.extend(['/api/v2/ui/buckets?pageSize=0&start=0&keywords={}'.format(word) for word in words])
    urls = compile_url('darkone.openbuckets.io', params)
    log.debug('Compiled {} urls for request ({})'.format(len(urls), get_name()))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    headers = {'Accept': 'application/json', 'Referer': 'https://www.openbuckets.io/'}
    responses = loop.run_until_complete(async_requests(urls, method='get', additional_headers=headers))
    for r in responses:
        if r.status_code == 200:
            data = r.json()
            if data['meta']['results'] > 0 and 'keywords' in data['query']:
                if 'bucket' in data['meta']:
                    founded_projects.append('https://www.openbuckets.io/search?keyword={}&viewType=file'.format(data['query']['keywords']))
                else:
                    founded_projects.append('https://www.openbuckets.io/search?keyword={}&viewType=bucket'.format(data['query']['keywords']))
    founded_projects = list(set(founded_projects))
    log.info('{}: founded {} results'.format(get_name(), len(founded_projects)))
    return founded_projects
