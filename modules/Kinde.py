import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')

# Kinde businesses are served at <business>.kinde.com (the subdomain is the
# customer-chosen, name-guessable business name). The OIDC discovery document is
# the discriminator: a real business returns HTTP 200 with a JSON body containing
# an "issuer" field, while a non-existent subdomain returns HTTP 404 with an HTML
# "Domain Not Found" page. Gate on 200 + the issuer field.
WELL_KNOWN_PATH = '/.well-known/openid-configuration'


def get_name():
    return 'Kinde'


def get_tags():
    return ['subdomain', 'sso', 'identity', 'nolimit']


def get_description():
    return 'This module finds Kinde businesses by bruteforcing kinde.com subdomains and confirming a real business via the OIDC discovery endpoint'


def wordslist_for_check_module():
    return {
        'real': ['bitakora', 'musehub', 'easyweddings'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = ['{}{}'.format(u, WELL_KNOWN_PATH) for u in compile_subdomain('kinde.com', words)]
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        # Real business: 200 + OIDC JSON with issuer. Non-existent: 404 HTML.
        if r.status_code == 200 and '"issuer"' in r.text:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} businesses'.format(get_name(), len(founded_projects)))
    return founded_projects
