import asyncio
import json
from utils import async_websocket, compile_url, async_requests
import logger
log = logger.get_logger('logger')


def get_name():
    return 'RunKit'


def get_version():
    return '1.0'


def get_tags():
    return ['limit']


def get_description():
    return 'Search projects on npm.runkit.com and notebooks on runkit.com'


def wordslist_for_check_module():
    return {
        'real': ['nodejs', 'runkit', 'notebook'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]

    # Search by websocket
    url = "https://runkit.com"
    messages = []
    for word in words:
        messages.append('{"name":"href-registration","hrefs":[{"href":"/users/runkit/repositories?page=1&per_page=1000&listScope=everything&q=' + word + '&searchScope=all","preloaded":false}]}')
        messages.append('{"name":"href-registration","hrefs":[{"href":"/search/modules/' + word + '?page=1","preloaded":false}]}')
    loop = asyncio.get_event_loop()
    log.debug('Send messages over WS...')
    responses = loop.run_until_complete(async_websocket(url, messages=messages))
    founded_projects = []
    for r in responses:
        j = json.loads(r)
        for item in j['contents']['items']:
            try:
                founded_projects.append('{}{}'.format(url, item['url']))
            except KeyError:
                founded_projects.append('{}/{}'.format(url, item['_source']['name']))

    # Search by HTTP
    urls = compile_url('runkit.com/', words)
    responses = loop.run_until_complete(async_requests(urls))
    founded_projects.extend([str(r.url) for r in responses if r.status_code == 200])

    # Deduplicate and sort
    founded_projects = sorted(list(set(founded_projects)))
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects
