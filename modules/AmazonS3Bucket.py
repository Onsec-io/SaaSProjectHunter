import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'AmazonS3Bucket'


def get_version():
    return '1.1'


def get_description():
    return 'This module uses bruteforce name of bucket over endpoint s3.amazonaws.com to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['bussola', 'arrowheadclinicatlanta', 'exist'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    import re
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]  # lowercase
    urls = compile_url('s3.amazonaws.com/', words)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))

    founded_projects = []
    for r in responses:
        if r.status_code == 404:
            continue
        elif r.status_code == 403 and 'Access Denied' in r.text:
            founded_projects.append('{} ({})'.format(r.url, 'Access Denied'))
        elif r.status_code == 301:
            pattern = r"<Endpoint>(.*?)</Endpoint>"
            match = re.search(pattern, r.text)
            extracted_string = match.group(1)
            log.info('Found redirect: {} -> {}'.format(r.url, extracted_string))
            founded_projects.append('https://{}/ ({})'.format(extracted_string, 'Redirect found'))
        else:
            founded_projects.append(r.url)

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
