import asyncio
import httpx
import aiodns
from tqdm.asyncio import tqdm_asyncio
import re
import logger
import signal
log = logger.get_logger('logger')
global limit
global header_useragent
global verbose
global limit_requests


def init(args_verbose, args_threads, args_user_agent, args_limit_requests):
    global verbose
    verbose = args_verbose

    global limit
    limit = asyncio.Semaphore(value=int(args_threads))

    global header_useragent
    header_useragent = {'user-agent': args_user_agent}

    global limit_requests
    limit_requests = args_limit_requests


def wait_user_input():
    while True:
        answer = input("\nPress 'r' to repeat requests, 'p' to pass current module or 'q' to quit: ")
        if answer == 'r':
            break
        elif answer == 'q':
            exit()
        elif answer == 'p':
            return 'pass'


def generator(words):
    words = list(
        set([x.lower().strip() for x in words if len(x) > 3]))  # locawecase, remove doubles and spaces
    result = []
    for w in words:
        if ' ' in w:
            if '.' in w:
                w = w.replace('.', '')
            result.append(w.replace(' ', ''))
            result.append(w.replace(' ', '_'))
            result.append(w.replace(' ', '-'))
            if len(w.split(' ')[-1]) < 5:  # remove `LTD/corp/etc` from 'Blablabla LTD'
                result.append(w.split(' ')[0])

        elif '.' in w:
            result.append(w)  # add original
            result.append(w.split('.')[0])
            result.append(w.replace('.', '_'))
            result.append(w.replace('.', ''))
            result.append(w.replace('.', '-'))
            result.append(w.replace('.', ''))
        else:
            result.append(w)
    result = list(set(result))
    blacklist = ['http', 'https', 'www', 'com', 'net', 'org', 'edu', 'gov', 'mil', 'int', 'arpa', 'co.uk']
    result = [x for x in result if x not in blacklist]
    return result


async def make_nslookup(resolver, domain):
    try:
        async with limit:
            if limit.locked():
                await asyncio.sleep(0.1)
            log.debug('Run lookup: {}'.format(domain))
            log.debug('Run resolve domain: {}'.format(domain))
            result = await resolver.query(domain, 'A')
            if result:
                return domain
            else:
                return None
    except asyncio.CancelledError:
        log.debug('Cancelled lookup: {}'.format(domain))
        return None
    except Exception as e:
        log.debug('Error lookup {}: {}'.format(domain, e))
        return None


async def async_nslookup(domains):
    resolver = aiodns.DNSResolver()
    tasks = []
    if len(domains) > limit_requests:
        log.warning('Count tasks more than limit. Run only first {} requests'.format(limit_requests))
    for domain in domains[:limit_requests]:
        task = asyncio.create_task(make_nslookup(resolver, domain))
        tasks.append(task)

    def signal_handler(sig, frame):
        log.warning('Current running module has been cancelled')
        for current_task in tasks:
            current_task.cancel()

    signal.signal(signal.SIGINT, signal_handler)

    if verbose > 0:
        responses = await asyncio.gather(*tasks)  # return None and response
    else:
        responses = await tqdm_asyncio.gather(*tasks, leave=False)  # return None and response
    return responses


async def make_request(client, url, method, uuid=None, data=None, headers=None, cookies=None):
    try:
        async with limit:
            response = []
            response.insert(0, uuid)
            if limit.locked():
                await asyncio.sleep(0.1)
            if data:
                log.debug('Run request to: {} ({})'.format(url, data))
            else:
                log.debug('Run request to: {}'.format(url))
            method = method.lower()
            if method == 'head':
                r = await client.head(url, headers=headers, cookies=cookies)
            elif method == 'post':
                r = await client.post(url, data=data, headers=headers, cookies=cookies)
            else:
                r = await client.get(url, headers=headers, cookies=cookies)

            log.debug('Response status: {} ({})'.format(r.status_code, url))
            return [uuid, r]
    except asyncio.CancelledError:
        log.debug('Cancelled request to: {}'.format(url))
        return [uuid, url]
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ReadError, httpx.LocalProtocolError, httpx.RemoteProtocolError):
        log.error('Error connect to {}...'.format(url))
        return [uuid, url]


async def async_requests(urls, method='head', http2=True, additional_headers=None):
    if additional_headers:
        headers = {**header_useragent, **additional_headers}  # merge two dict: useragent and additional headers
    else:
        headers = header_useragent
    client = httpx.AsyncClient(http2=http2, headers=headers)
    tasks = []
    if len(urls) > limit_requests:
        log.warning('Count tasks more than limit. Run only first {} requests'.format(limit_requests))
    for url in urls[:limit_requests]:
        task = asyncio.create_task(make_request(client, url, method))
        tasks.append(task)

    def signal_handler(sig, frame):
        log.warning('Current running module has been cancelled')
        for current_task in tasks:
            current_task.cancel()

    signal.signal(signal.SIGINT, signal_handler)

    if verbose > 0:
        responses = await asyncio.gather(*tasks)  # return None and response
    else:
        responses = await tqdm_asyncio.gather(*tasks, leave=False)  # return None and response

    completed_responses = []  # list of successful responses
    recheck = []  # list of url if error (return from `make_request` string)
    recheck_responses = []
    for _, r in responses:
        if type(r) == str:
            log.debug('Found url for recheck: {}'.format(r))
            recheck.append(r)
        else:
            completed_responses.append(r)

    if len(recheck) > 0:
        if wait_user_input() != 'pass':
            recheck_responses = await async_requests(recheck, method=method, http2=http2, additional_headers=additional_headers)

    completed_responses.extend(recheck_responses)
    return completed_responses


async def async_requests_over_datasets(datasets, http2=True):
    tasks = []
    # example `dataset`: {'UNIQUE-UUID': {'url': 'https://<company>.example.com/<project>', 'method': 'post', 'cookies': "{'key': 'value'}"}}
    method = 'head'
    headers = header_useragent  # example: {'X-Auth': 'from-client'}
    cookies = None  # example: {'key': 'value'}
    data = None  # example: {'key': 'value'}
    client = httpx.AsyncClient(http2=True)  # usage one async client for reuse sockets

    if len(datasets) > limit_requests:
        log.warning('Count tasks more than limit. Run only first {} requests'.format(limit_requests))
        keys_to_keep = list(datasets.keys())[:limit_requests]
        new_datasets = {key: datasets[key] for key in keys_to_keep}
        datasets = new_datasets

    for uuid in datasets.keys():
        url = datasets[uuid]['url']
        if 'method' in datasets[uuid].keys():
            method = datasets[uuid]['method']
        if 'data' in datasets[uuid].keys():
            data = datasets[uuid]['data']
        if 'headers' in datasets[uuid].keys():
            headers.update(datasets[uuid]['headers'])
        if 'cookies' in datasets[uuid].keys():
            cookies = datasets[uuid]['cookies']

        task = asyncio.create_task(make_request(client, url, method, uuid=uuid, data=data, headers=headers, cookies=cookies))
        tasks.append(task)

    completed_responses = []  # list of successful responses
    recheck = {}  # datasets for recheck (added if return from `make_request` [uuid, url])
    recheck_responses = []

    def signal_handler(sig, frame):
        log.warning('Current running module has been cancelled')
        for current_task in tasks:
            current_task.cancel()

    signal.signal(signal.SIGINT, signal_handler)

    if verbose > 0:
        responses = await asyncio.gather(*tasks)  # return None and response
    else:
        responses = await tqdm_asyncio.gather(*tasks, leave=False)  # return None and response
    for uuid, r in responses:
        if type(r) == str:
            log.debug('Found url for recheck: {}'.format(r))
            recheck[uuid] = datasets[uuid]
        else:
            completed_responses.append([uuid, r])

    if len(recheck) > 0:
        if wait_user_input() != 'pass':
            recheck_responses = await async_requests_over_datasets(recheck, http2=http2)

    completed_responses.extend(recheck_responses)
    return completed_responses


def compile_subdomain(url, words, proto='https://'):
    words = [item.lower() for item in words]  # lowercase
    words = [item.strip() for item in words]  # delete spaces\newline
    words = list(set(words))  # remove doubles
    temp = []
    for s in words:
        if re.match(r'^[a-z0-9-]+$', s):  # only alphabet, digits and hyphen
            temp.append(s)
        else:
            log.debug('Deleted {}'.format(s))
    words = temp
    log.debug('Size of wordlist: {}'.format(len(words)))
    urls = ['{}{}.{}'.format(proto, w, url) for w in words]
    return urls


def compile_url(url, paths, proto='https://'):
    paths = [item.strip() for item in paths]  # delete spaces\newline
    paths = list(set(paths))  # remove doubles
    log.debug('Size of wordlist: {}'.format(len(paths)))
    urls = ['{}{}{}'.format(proto, url, p) for p in paths]
    return urls


def run_check_module(module):
    print('Check {} v{}'.format(module.get_name(), module.get_version()))
    data = module.wordslist_for_check_module()
    count = 0
    log.debug('>> Test set: {}'.format(data))

    # Check fake/pseudo projects
    fake_projects = data['fake']
    log.info('>> Check fake project name: {}'.format(fake_projects))
    result = module.run(fake_projects)
    if len(result) == 0:
        log.info('>> Pseudo projects not found')
        count += 1
    else:
        log.warning('Test {} failed. Found pseudo projects: {}'.format(module.get_name(), [x for x in result]))

    # Check real projects
    real_projects = data['real']
    log.info('>> Check real project name ({}): {}'.format(len(real_projects), real_projects))
    result = module.run(real_projects)
    if len(result) >= len(real_projects):
        found_projects = set()
        for source_str in result:
            for check_str in real_projects:
                if check_str.lower() in source_str.lower():
                    found_projects.add(check_str)
        if len(found_projects) == len(real_projects):
            log.info('>> All real projects found')
            count += 1
        else:
            log.warning('Test {} failed. Found only: {}'.format(module.get_name(), [x for x in real_projects]))
            log.debug('List of responses URL: {}'.format(result))
    else:
        log.warning('Test {} failed. Found only {} out of {} projects: {}'.format(module.get_name(), len(result), len(real_projects), [x for x in result]))

    if count == 2:
        pass
        # print('Check {} v{} complete, problem not found'.format(module.get_name(), module.get_version()))
    else:
        log.error('Failed check module {} v{}!'.format(module.get_name(), module.get_version()))


def check_modules(modules):
    for m in modules:
        run_check_module(m)
