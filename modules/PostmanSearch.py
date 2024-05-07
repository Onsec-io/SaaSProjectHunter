import asyncio
from utils import compile_url, async_requests_over_datasets
from uuid import uuid4
from json import dumps
import logger
log = logger.get_logger('logger')


def get_name():
    return 'PostmanSearch'


def get_version():
    return '1.2'


def get_description():
    return 'This module uses bruteforce of API www.postman.com to search workspaces/collections/etc'


def wordslist_for_check_module():
    return {
        'real': ['postman', 'microsoft', 'linkedin'],
        'fake': ['micrAsAft', 'uenrf348', 'doboss']
    }


def run(words):
    words = [item.lower() for item in words]  # lowercase
    # create datasets
    datasets = {}
    for word in words:
        uuid = uuid4()
        data = dumps({
            "service": "search",
            "method": "POST",
            "path": "/search-all",
            "body": {
                "queryIndices": [
                    "collaboration.workspace",
                    "runtime.collection",
                    "runtime.request",
                    "adp.api",
                    "flow.flow",
                    "apinetwork.team"
                ],
                "queryText": "{}".format(word),
                "size": 1,
                "from": 0
            }
        })
        datasets[uuid] = {
            'url': 'https://www.postman.com/_api/ws/proxy',
            'method': 'post',
            'headers': {'Content-Type': 'application/json'},
            'data': data,
            'word': word
        }
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests_over_datasets(datasets, http2=True))
    founded_projects = []
    for uuid, r in responses:
        try:
            if 'correctedQueryText' in r.json()['meta'].keys():
                if str(r.json()['meta']['correctedQueryText']).lower() == str(datasets[uuid]['word']).lower() and len(r.json()['data']) > 0:
                    founded_projects.append('https://www.postman.com/search?q={}'.format(str(datasets[uuid]['word']).lower()))
            elif len(r.json()['data']) > 0:
                founded_projects.append('https://www.postman.com/search?q={}'.format(str(datasets[uuid]['word']).lower()))
        except KeyError:
            log.warn('KeyError: {}. Response: {}'.format(datasets[uuid]['word'], r.status_code))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
