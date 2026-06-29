import asyncio
from utils import compile_subdomain, async_requests
import logger
log = logger.get_logger('logger')

# Cloudflare Access (Zero Trust) serves a generic "App Launcher" HTML page at the
# root of every <team>.cloudflareaccess.com host, real or not, so the status code
# and body of "/" do not discriminate. The Access identity API does: a real,
# provisioned team answers /cdn-cgi/access/get-identity with HTTP 400 and a JSON
# body ({"err":"no app token set"}) because the endpoint is live but the request
# carries no Access app token, while a non-existent team returns HTTP 404 and an
# HTML error page. Discriminating on 400 + JSON is reliable where status alone
# is not (the same pattern Okta.py uses with its org-metadata endpoint).
IDENTITY_PATH = '/cdn-cgi/access/get-identity'


def get_name():
    return 'CloudflareAccess'


def get_tags():
    return ['subdomain', 'sso', 'identity', 'nolimit']


def get_description():
    return 'This module finds Cloudflare Access (Zero Trust) team domains by bruteforcing cloudflareaccess.com subdomains and confirming a real team via the Access identity endpoint'


def wordslist_for_check_module():
    return {
        'real': ['gitlab', 'shopify', 'discord'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = ['{}{}'.format(u, IDENTITY_PATH) for u in compile_subdomain('cloudflareaccess.com', words)]
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    for r in responses:
        # Real team: identity API is live -> 400 + JSON error body.
        # Non-existent team: 404 + HTML error page.
        if r.status_code == 400 and r.text.lstrip().startswith('{'):
            founded_projects.append('https://{}/'.format(r.url.host))
    log.info('{}: founded {} teams'.format(get_name(), len(founded_projects)))
    return founded_projects
