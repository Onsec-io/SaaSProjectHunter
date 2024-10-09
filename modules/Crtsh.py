import asyncio
from utils import compile_url, async_requests
import logger
from utils import verbose, tlds
import xml.etree.ElementTree as ET
log = logger.get_logger('logger')


def get_name():
    return 'Crtsh'


def get_version():
    return '1.2'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses the crt.sh service to search for domain certificates'


def wordslist_for_check_module():
    return {
        'real': ['wallarm', 'chatgpt.com', 'google'],
        'fake': ['micraaaaaarverv34', 'uenrf348', 'sde2d23A']
    }


def run(words):
    founded_projects = []
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    domains = []
    for item in words:
        if '_' in item:
            item.replace('_', '.')
        if '.' not in item or not any(item.endswith(f'.{tld}') for tld in tlds):
            domains.extend(f"{item}.{domain}" for domain in tlds)
        else:
            domains.append(item)
    urls = compile_url('crt.sh/?output=json&q=', domains)
    log.debug('Compiled {} urls for request ({})'.format(len(urls), get_name()))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls))

    for r in responses:
        if r.status_code == 200:
            if 'Content-Length' in r.headers:
                if int(r.headers.get('Content-Length')) != 2:
                    founded_projects.append(str(r.url))
            else:
                founded_projects.append(str(r.url))
        else:
            log.error('Status code: {}'.format(r.status_code))

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
