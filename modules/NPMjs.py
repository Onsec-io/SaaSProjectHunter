import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'NPMjs'


def get_version():
    return '1.0'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses bruteforce URL-path over https://www.npmjs.com/<path> to find users and packages'


def wordslist_for_check_module():
    return {
        'real': ['nodejs', 'nodejs-foundation', 'ljharb'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]
    urls = compile_url('www.npmjs.com/~', words)
    urls += compile_url('www.npmjs.com/package/', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects = [str(r.url) for r in responses if r.status_code == 200]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
