import asyncio
from utils import compile_url, async_requests_over_datasets
from uuid import uuid4
from json import dumps
import logger
log = logger.get_logger('logger')


def get_name():
    return 'PostmanUsers'


def get_version():
    return '1.0'


def get_description():
    return 'This module uses bruteforce of API www.postman.com (/api/profiles/<name>) to find users/orgs'


def wordslist_for_check_module():
    return {
        'real': ['linkedin-developer-apis', 'notionhq', 'doboss'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    # create datasets
    datasets = {}
    for word in words:
        word = word.lower().strip()
        uuid = uuid4()
        data = dumps({'path': '/api/profiles/{}'.format(word), 'service': 'ums', 'method': 'get'})
        datasets[uuid] = {
            'url': 'https://www.postman.com/_api/ws/proxy',
            'method': 'post',
            'headers': {'Content-Type': 'application/json'},
            'data': data,
        }
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests_over_datasets(datasets, http2=True))
    founded_projects = ['https://www.postman.com/{}'.format(str(r.json()['info']['slug'])) for _, r in responses if r.status_code != 404]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
