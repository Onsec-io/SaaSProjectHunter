import time
import asyncio
import random
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
global proxies
global tlds
global auto_resend
global auto_resend_counter


def init(args_verbose, args_threads, args_user_agent, args_limit_requests, args_proxies=None, args_tld=None, args_auto_resend=None):
    global verbose
    verbose = args_verbose

    global limit
    limit = asyncio.Semaphore(value=int(args_threads))

    global header_useragent
    header_useragent = {'user-agent': args_user_agent}

    global limit_requests
    limit_requests = args_limit_requests

    global proxies
    if args_proxies:
        log.info('Loading proxies...')
        for p in args_proxies:
            if p.startswith('#'):
                continue
            if not p.startswith('http://') and not p.startswith('https://') and not p.startswith('socks://'):
                log.error('Invalid proxy: {}'.format(p))
        log.info('Number of proxies loaded: {}'.format(len(args_proxies)))
    proxies = args_proxies

    global tlds
    tlds = ['com', 'net', 'org', 'io', 'dev', 'tech', 'xyz', 'top', 'app', 'online']
    if args_tld:
        for tld in args_tld.split(','):
            if tld not in tlds:
                tlds.append(tld)
        print('Added new TLDs. Result: {}'.format(', '.join(tlds)))

    global auto_resend
    auto_resend = args_auto_resend


def get_proxy(num=None):
    if not proxies:
        return None
    if num is not None:
        proxy_str = proxies[num]
    else:
        proxy_str = random.choice(proxies)

    if proxy_str.startswith('http://') or proxy_str.startswith('https://') or proxy_str.startswith('socks://'):
        log.debug('Used proxy: {}'.format(proxy_str))
        return proxy_str
    else:
        return None


async def check_proxy_ip(proxy):
    log.debug(f"Starting check for proxy: {proxy}")
    url = 'https://api.ipify.org/?format=text'
    try:
        async with httpx.AsyncClient(proxy=proxy, verify=False) as client:
            r = await client.get(url)
            if r.status_code == 200:
                log.info(f"Proxy {proxy} is working, IP: {r.text}")
                return r.text
            else:
                log.error(f"Proxy {proxy} failed with status code {r.status_code}")
    except Exception as e:
        log.error(f"Failed to check proxy {proxy}: {e}")
        exit()
    return None


async def check_all_proxies():
    if not proxies:
        log.warning('No proxies found')
        return
    tasks = []
    for i in range(len(proxies)):
        task = asyncio.create_task(check_proxy_ip(get_proxy(num=i)))
        tasks.append(task)
    if verbose > 0:
        responses = await asyncio.gather(*tasks)  # return None and response
    else:
        responses = await tqdm_asyncio.gather(*tasks, leave=False)  # return None and response
    for proxy, ip in zip(proxies, responses):
        if ip:
            log.info(f'Proxy {proxy} is working, IP: {ip}')
        else:
            log.error(f'Proxy {proxy} failed.')


def check_all_proxies_sync():
    print('Checking proxies...')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_all_proxies())
    print('Checking proxies complete')


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
    unique_words = set(word.lower().strip() for word in words if len(word) > 3)
    result = set()
    for word in unique_words:
        parts = re.split(r'[ .]', word)
        result.update({
            ''.join(parts),
            '_'.join(parts),
            '-'.join(parts)
        })
        if len(parts[-1]) < 5:
            result.add(parts[0])
    blacklist = {'http', 'https', 'www', 'com', 'net', 'org', 'edu', 'gov', 'mil', 'int', 'arpa', 'co.uk'}
    return [word for word in result if word not in blacklist]


async def make_nslookup(resolver, domain):
    try:
        async with limit:
            if limit.locked():
                await asyncio.sleep(0.1)
            log.debug('Run lookup: {}'.format(domain))
            log.debug('Run resolve domain: {}'.format(domain))
            result = await resolver.query(domain, 'A')
            return domain if result else None
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
        if auto_resend:
            exit(0)
        else:
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
            
            proxy = get_proxy()
            if proxy:
                log.debug('Run request over proxy: {}'.format(proxy))
                async with httpx.AsyncClient(http2=True, proxy=proxy, verify=False) as client:
                    r = await perform_request(client, url, method, data, headers, cookies)
            else:
                r = await perform_request(client, url, method, data, headers, cookies)

            log.debug('Response status: {} ({})'.format(r.status_code, url))
            if r.status_code == 429:
                log.warning('Too many requests (code: 429): {}. Please wait 5-15 seconds'.format(url))
                return [uuid, url]
            elif r.status_code == 503:
                log.warning('Service unavailable (code: 503): {}. Please wait 5-15 seconds'.format(url))
                return [uuid, url]
            return [uuid, r]
    except asyncio.CancelledError:
        log.debug('Cancelled request to: {}'.format(url))
        return [uuid, url]
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ReadError, httpx.LocalProtocolError, httpx.RemoteProtocolError):
        log.warning('Error connect to {}...'.format(url))
        return [uuid, url]


async def perform_request(client, url, method, data, headers, cookies):
    if method == 'head':
        return await client.head(url, headers=headers, cookies=cookies)
    elif method == 'post':
        return await client.post(url, data=data, headers=headers, cookies=cookies)
    else:
        return await client.get(url, headers=headers, cookies=cookies)


async def async_requests(urls, method='head', http2=True, additional_headers=None):
    global auto_resend_counter
    if additional_headers:
        headers = {**header_useragent, **additional_headers}  # merge two dict: useragent and additional headers
    else:
        headers = header_useragent
    client = httpx.AsyncClient(http2=http2, headers=headers, verify=False)
    tasks = []
    if len(urls) > limit_requests:
        log.warning('Count tasks more than limit. Run only first {} requests'.format(limit_requests))
    for url in urls[:limit_requests]:
        task = asyncio.create_task(make_request(client, url, method, headers=headers))
        tasks.append(task)

    def signal_handler(sig, frame):
        log.warning('Current running module has been cancelled')
        if auto_resend:
            exit(0)
        else:
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
        if auto_resend:
            auto_resend_counter += 1
            if auto_resend_counter > 5:
                log.error('Too many auto-resend attempts. Exit...')
                return completed_responses
            print(f"Auto-resend enabled. Resending requests after {auto_resend}s...")
            time.sleep(auto_resend)
            recheck_responses = await async_requests(recheck, method=method, http2=http2, additional_headers=additional_headers)
        elif wait_user_input() != 'pass':
            recheck_responses = await async_requests(recheck, method=method, http2=http2, additional_headers=additional_headers)

    completed_responses.extend(recheck_responses)
    return completed_responses


async def async_requests_over_datasets(datasets, http2=True):
    global auto_resend_counter
    tasks = []
    # example `dataset`: {'UNIQUE-UUID': {'url': 'https://<company>.example.com/<project>', 'method': 'post', 'cookies': "{'key': 'value'}"}}
    method = 'head'
    headers = header_useragent  # example: {'X-Auth': 'from-client'}
    cookies = None  # example: {'key': 'value'}
    data = None  # example: {'key': 'value'}
    client = httpx.AsyncClient(http2=True, verify=False)  # usage one async client for reuse sockets

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
        if auto_resend:
            exit(0)
        else:
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
        if auto_resend:
            auto_resend_counter += 1
            if auto_resend_counter > 5:
                log.error('Too many auto-resend attempts. Exit...')
                return completed_responses
            print(f"Auto-resend enabled. Resending requests after {auto_resend}s...")
            time.sleep(auto_resend)
            recheck_responses = await async_requests_over_datasets(recheck, http2=http2)
        elif wait_user_input() != 'pass':
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
    # paths = [item.lower() for item in paths]  # lowercase
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
                if check_str.lower() in str(source_str).lower().replace('%20', ' '):
                    found_projects.add(check_str)
        if len(found_projects) == len(real_projects):
            log.info('>> All real projects found')
            count += 1
        else:
            log.warning('Test {} failed. Found only: {}'.format(module.get_name(), [x for x in found_projects]))
            log.debug('List of responses URL: {}'.format(result))
    else:
        log.warning('Test {} failed. Found only {} out of {} projects: {}'.format(module.get_name(), len(result), len(real_projects), [x for x in result]))

    if count == 2:
        pass
        # print('Check {} v{} complete, problem not found'.format(module.get_name(), module.get_version()))
    else:
        log.error('Failed check module {} v{}!'.format(module.get_name(), module.get_version()))


async def async_websocket(url, messages=[]):
    import httpx
    from httpx_ws import aconnect_ws
    responses = []
    log.info('Connect to websocket: {}'.format(url))
    async with httpx.AsyncClient(timeout=5.0) as client:
        async with aconnect_ws(url, client) as ws:
            status = await ws.receive_text()
            log.debug(status)
            if len(messages) == 0:
                return status
            for m in messages:
                await ws.send_text(m)
                responses.append(await ws.receive_text())
    log.debug(responses)
    log.debug('Websocket closed')
    return responses


def check_modules(modules):
    for m in modules:
        global auto_resend_counter
        auto_resend_counter = 0
        run_check_module(m)
