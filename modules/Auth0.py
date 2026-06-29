import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')

# Auth0 tenants are served at <tenant>.auth0.com. The OIDC discovery document is
# the discriminator: a real tenant returns HTTP 200 with a JSON body containing
# an "issuer" field, while a non-existent tenant still resolves (Cloudflare
# wildcard DNS) but returns HTTP 404. Gate on 200 + the issuer field so the
# wildcard parked hosts are rejected. Regional hosts (<tenant>.us|eu|au.auth0.com)
# follow the same signature and can be added as extra base domains if needed.
WELL_KNOWN_PATH = '/.well-known/openid-configuration'


def get_name():
    return 'Auth0'


def get_tags():
    return ['subdomain', 'sso', 'identity', 'nolimit']


def get_description():
    return 'This module finds Auth0 tenants by bruteforcing auth0.com subdomains and confirming a real tenant via the OIDC discovery endpoint'


def wordslist_for_check_module():
    return {
        'real': ['coursera', 'nvidia', 'siemens'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = ['{}{}'.format(u, WELL_KNOWN_PATH) for u in compile_subdomain('auth0.com', words)]
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        # Real tenant: 200 + OIDC JSON with issuer. Parked/non-existent: 404.
        if r.status_code == 200 and '"issuer"' in r.text:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} tenants'.format(get_name(), len(founded_projects)))
    return founded_projects
