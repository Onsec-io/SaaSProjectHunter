import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'DockerHubSearch'


def get_version():
    return '1.0'


def get_description():
    return 'This module uses bruteforce of API search to find repos/images'


def wordslist_for_check_module():
    return {
        'real': ['ubuntu', 'wallarm', 'alpine'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    if len(words) > 180:
        log.warning('The size of words is more than 180. API DockerHub: x-ratelimit-limit: 180. Launching the request using only the first 180 words.')
        words = words[:10]
    urls = compile_url('hub.docker.com/api/content/v1/products/search?page_size=1&q=', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get', http2=False, additional_headers={'Search-Version': 'v3'}))
    founded_projects = []
    for r in responses:
        if r.status_code != 200 or int(r.headers.get('x-ratelimit-remaining')) < 2:
            log.warning('Error usage {} module. Status code: {}, x-ratelimit-remaining - {}'.format(get_name(), r.status_code, r.headers.get('x-ratelimit-remaining')))
        if r.status_code == 200 and r.json()['count'] != 0:
            word_from_url = str(r.url).split('q=')[1]
            founded_projects.append('https://hub.docker.com/search?q={}'.format(word_from_url))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
