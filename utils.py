from progressbar import progressbar
import asyncio
import httpx
import aiodns
import re
import logger
log = logger.get_logger('logger')
global limit
global header_useragent


def set_threads_limit(count_threads):
    log.info('Set limit of threads: {}'.format(count_threads))
    global limit
    limit = asyncio.Semaphore(value=count_threads)


def set_useragent(useragent):
    log.debug('Set user-agent: {}'.format(useragent))
    global header_useragent
    header_useragent = {'user-agent': useragent}


def wait_user_input():
    while True:
        answer = input("\nPress 'y' to repeat requests, or 'n' to exit: ")
        if answer == 'y':
            break
        elif answer == 'n':
            exit()


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
    async with limit:
        if limit.locked():
            await asyncio.sleep(0.1)
        log.debug('Run lookup: {}'.format(domain))
        try:
            log.debug('Run resolve domain: {}'.format(domain))
            result = await resolver.query(domain, 'A')
            if result:
                return domain
            else:
                return None
        except Exception as e:
            log.debug('Error lookup {}: {}'.format(domain, e))
            return None


async def async_nslookup(domains):
    resolver = aiodns.DNSResolver()
    tasks = []
    for domain in domains:
        task = asyncio.create_task(make_nslookup(resolver, domain))
        tasks.append(task)
    responses = await asyncio.gather(*tasks)
    return responses


async def make_request(client, url, method, uuid=None, data=None, headers=None, cookies=None):
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
        try:
            if method == 'head':
                r = await client.head(url, headers=headers, cookies=cookies)
            elif method == 'post':
                r = await client.post(url, data=data, headers=headers, cookies=cookies)
            else:
                r = await client.get(url, headers=headers, cookies=cookies)
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout):
            log.error('Error connect to {}...'.format(url))
            return [uuid, url]
        log.debug('Response status: {} ({})'.format(r.status_code, url))
        return [uuid, r]


async def async_requests(urls, method='head', http2=True, additional_headers=None):
    if additional_headers:
        headers = {**header_useragent, **additional_headers}  # merge two dict: useragent and additional headers
    else:
        headers = header_useragent
    client = httpx.AsyncClient(http2=http2, headers=headers)
    tasks = []
    for url in urls:
        task = asyncio.create_task(make_request(client, url, method))
        tasks.append(task)
    responses = await asyncio.gather(*tasks)  # return None and response

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
        wait_user_input()
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
    responses = await asyncio.gather(*tasks)
    for uuid, r in responses:
        if type(r) == str:
            log.debug('Found url for recheck: {}'.format(r))
            recheck[uuid] = datasets[uuid]
        else:
            completed_responses.append([uuid, r])

    if len(recheck) > 0:
        wait_user_input()
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


def run_check_module(m):
    print('Check module {} v{}: '.format(m.get_name(), m.get_version()), end='')
    d = m.wordslist_for_check_module()
    n = 0
    log.debug('>> Test set: {}'.format(d))

    # Check fake/pseudo projects
    fake = d['fake']
    log.info('>> Check fake project name: {}'.format(fake))
    r = m.run(fake)
    if len(r) == 0:
        log.info('>> Pseudo projects not found')
        n += 1
    else:
        log.warning('Test {} fail. Found pseudo projects: {}'.format(m.get_name(), [x for x in r]))

    # Check real projects
    real = d['real']
    log.info('>> Check real project name ({}): {}'.format(len(real), real))
    r = m.run(real)
    if len(r) >= len(real):
        log.info('>> All real projects found')
        n += 1
    else:
        log.warning('Test {} fail. Found only {} out of {} projects: {}'.format(m.get_name(), len(r), len(real), [x for x in r]))

    if n == 2:
        print('complete, problem not found, all ok!'.format(m.get_name(), m.get_version()))
    else:
        log.error('Failed check module {} v{}!'.format(m.get_name(), m.get_version()))


def check_modules(modules, module_name, verbose):
    if module_name.lower() == 'all':
        if verbose == 0:
            for m in progressbar(modules, redirect_stdout=True):
                run_check_module(m)
        else:
            for m in modules:
                run_check_module(m)
    else:
        for m in modules:
            if m.get_name().lower() == module_name.lower():
                run_check_module(m)
                exit()
        # after iterating modules and not finding name in modules:
        print('Please, input module name or `all`')
