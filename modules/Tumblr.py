import asyncio
from utils import compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Tumblr'


def get_tags():
    return ['subdomain', 'limit', 'blog']


def get_description():
    return 'This module uses bruteforce of www.tumblr.com/@<blog> paths to find company blogs'


def wordslist_for_check_module():
    return {
        'real': ['staff', 'netflix', 'spotify'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-').lower() for item in words]
    # *.tumblr.com is WAF-blocked (403 "Please stop" / 429) for common UAs.
    # Unprefixed www.tumblr.com/<word> collides with app routes (/login, /explore).
    # /@<blog> returns 301/302 for existing blogs and 404 otherwise.
    urls = compile_url('www.tumblr.com/@', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = []
    for r in responses:
        if r.status_code not in (200, 301, 302):
            continue
        path = r.request.url.path
        if not path.startswith('/@'):
            continue
        founded_projects.append('https://www.tumblr.com/@{}'.format(path[2:]))
    log.info('{}: founded {} blogs'.format(get_name(), len(founded_projects)))
    return founded_projects
