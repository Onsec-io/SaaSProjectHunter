import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')

# Frontegg tenants are served at <tenant>.frontegg.com. The OIDC discovery
# document is the discriminator: a real tenant returns HTTP 200 with a JSON body
# containing an "issuer" field, while a non-existent subdomain returns HTTP 404
# with a JSON error body ({"errors":["Failed to find vendor for host: ..."]}).
# Because both real and fake bodies are JSON, gate on status 200 AND the issuer
# field (a JSON-body check alone would not discriminate here).
WELL_KNOWN_PATH = '/.well-known/openid-configuration'


def get_name():
    return 'Frontegg'


def get_tags():
    return ['subdomain', 'sso', 'identity', 'nolimit']


def get_description():
    return 'This module finds Frontegg tenants by bruteforcing frontegg.com subdomains and confirming a real tenant via the OIDC discovery endpoint'


def wordslist_for_check_module():
    return {
        'real': ['superwise', 'okera', 'materialize'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = ['{}{}'.format(u, WELL_KNOWN_PATH) for u in compile_subdomain('frontegg.com', words)]
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        # Real tenant: 200 + OIDC JSON with issuer. Non-existent: 404 JSON error.
        if r.status_code == 200 and '"issuer"' in r.text:
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} tenants'.format(get_name(), len(founded_projects)))
    return founded_projects
