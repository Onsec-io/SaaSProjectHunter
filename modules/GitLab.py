import asyncio
from utils import async_requests, compile_url
import logger
log = logger.get_logger('logger')


def get_name():
    return 'GitLab'


def get_tags():
    return ['limit']


def get_description():
    return 'This module uses bruteforce URL-path over gitlab.com/<path> to find users and groups'


def wordslist_for_check_module():
    return {
        'real': ['Camila13L', 'haven', 'exploit-database'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    headers = {'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest'}
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = list(set([item.lower() for item in words]))  # lowercase and remove doubles
    patches = []
    for word in words:
        patches.append('/groups/{}/-/children.json'.format(word))
        patches.append('/users/{}/calendar.json'.format(word))

    urls = compile_url('gitlab.com', patches)
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='head', additional_headers=headers))
    founded_projects = []
    for r in responses:
        if r.status_code == 200 or r.status_code == 301:
            founded_projects.append('https://gitlab.com/{}'.format(str(r.url).split('/')[4]))
        elif r.status_code != 302:
            log.warning('Error request to {} (status code: {})'.format(r.url, r.status_code))

    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
