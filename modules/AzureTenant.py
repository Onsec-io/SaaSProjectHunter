import asyncio
from utils import compile_url, async_requests
import logger
from utils import verbose, tlds
import xml.etree.ElementTree as ET
log = logger.get_logger('logger')


def get_name():
    return 'AzureTenant'


def get_version():
    return '1.1'


def get_tags():
    return ['azure', 'tenant', 'openid', 'nolimit']


def get_description():
    return 'This module for search subdomains of Azure tenant'


def wordslist_for_check_module():
    return {
        'real': ['wallarm.com', 'microsoft', 'azure'],
        'fake': ['micraaaaaarverv34', 'uenrf348', 'sde2d23A']
    }


def post_exploitation(domain):
    import httpx
    body = f'''<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:a="http://www.w3.org/2005/08/addressing">
            <soap:Header>
                <a:Action soap:mustUnderstand="1">http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation</a:Action>
                <a:To soap:mustUnderstand="1">https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc</a:To>
            </soap:Header>
            <soap:Body>
                <GetFederationInformationRequestMessage xmlns="http://schemas.microsoft.com/exchange/2010/Autodiscover">
                    <Request>
                        <Domain>{domain}</Domain>
                    </Request>
                </GetFederationInformationRequestMessage>
            </soap:Body>
        </soap:Envelope>
    '''
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': '"http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation"',
        'User-Agent': 'AutodiscoverClient'
    }
    r = httpx.post('https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc', data=body, headers=headers)
    root = ET.fromstring(r.text)
    namespaces = {
        's': 'http://schemas.xmlsoap.org/soap/envelope/',
        'autodiscover': 'http://schemas.microsoft.com/exchange/2010/Autodiscover'
    }
    domains = root.findall('.//s:Body//autodiscover:Domains/autodiscover:Domain', namespaces)
    return [domain.text for domain in domains]


def run(words):
    founded_projects = []
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]  # lowercase
    domains = []
    for item in words:
        if '_' in item:
            item.replace('_', '.')
        if '.' not in item or not any(item.endswith(f'.{tld}') for tld in tlds):
            domains.extend(f"{item}.{domain}" for domain in tlds)
        else:
            domains.append(item)
    domains = list(set(domains))  # remove duplicates

    # urls = "https://login.microsoftonline.com/{domain}/v2.0/.well-known/openid-configuration"
    urls = compile_url('login.microsoftonline.com/getuserrealm.srf?json=1&login=', domains)
    log.debug('Compiled {} urls for request ({})'.format(len(urls), get_name()))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = [str(r.url) for r in responses if r.status_code != 404 and '"NameSpaceType":"Unknown"' not in r.text]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))

    if verbose > 0:
        for project in founded_projects:
            log.debug(f"Found tenant by url: {project}")
            domain = project.split('login=')[-1]
            log.debug(f"Domain: {domain}")
            subdomains = post_exploitation(domain)
            log.info(f"Extracted {len(subdomains)} related domains and subdomains for {domain}")
            for sub in subdomains:
                print(sub)

    return founded_projects
