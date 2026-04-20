import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Ashby'


def get_tags():
    return ['limit', 'hr']


def get_description():
    return 'This module uses bruteforce on jobs.ashbyhq.com to find open positions at companies'


def wordslist_for_check_module():
    return {
        'real': ['airwallex', 'g2i', 'openai'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]
    urls = compile_url('jobs.ashbyhq.com/', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        slug = r.url.path.strip('/').lower()
        marker = '"hostedjobspageslug":"{}"'.format(slug)
        if r.status_code == 200 and slug and marker in r.text.lower():
            founded_projects.append(str(r.url))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
