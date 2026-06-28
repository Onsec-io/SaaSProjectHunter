import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')

# Okta serves a catch-all "parked" organization for any non-existent
# subdomain. Every parked subdomain returns this shared placeholder org id
# (pipeline "v1"), while a real provisioned tenant returns a unique id.
# Discriminating on this id is reliable where status code is not (Okta
# answers 200 for both real and non-existent subdomains).
PLACEHOLDER_ORG_ID = '00oplaODtXoEq1eQo0g3'
WELL_KNOWN_PATH = '/.well-known/okta-organization'


def get_name():
    return 'Okta'


def get_tags():
    return ['subdomain', 'sso', 'identity', 'nolimit']


def get_description():
    return 'This module finds Okta SSO tenants by bruteforcing okta.com subdomains and confirming a real org via the okta-organization metadata endpoint'


def wordslist_for_check_module():
    return {
        'real': ['dropbox', 'snowflake', 'databricks'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = ['{}{}'.format(u, WELL_KNOWN_PATH) for u in compile_subdomain('okta.com', words)]
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        # A real tenant: 200 + valid okta-organization JSON (id starts with
        # "00o") whose id is not the shared parked-subdomain placeholder.
        if r.status_code == 200 and '"id":"00o' in r.text and PLACEHOLDER_ORG_ID not in r.text:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} tenants'.format(get_name(), len(founded_projects)))
    return founded_projects
