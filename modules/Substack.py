import ssl
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import utils
from utils import compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Substack'


def get_tags():
    return ['subdomain', 'nolimit', 'newsletter']


def get_description():
    return 'This module uses bruteforce of substack.com subdomain to find company newsletters'


def wordslist_for_check_module():
    return {
        'real': ['platformer', 'simonowens', 'davidlebovitz'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def _check_archive(url):
    headers = utils.header_useragent or {'user-agent': 'Mozilla/5.0'}
    request = urllib.request.Request(url, headers=headers)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(request, context=context, timeout=15) as response:
            if response.status == 200 and response.headers.get_content_type() == 'application/json':
                return 'https://{}/'.format(urllib.parse.urlparse(url).hostname)
    except urllib.error.HTTPError as e:
        if e.code not in (403, 404):
            log.warning('Error {} for url {}'.format(e.code, url))
    except Exception:
        log.warning('Error connect to {}...'.format(url))
    return None


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    urls = compile_subdomain('substack.com/api/v1/archive', words)
    founded_projects = []
    with ThreadPoolExecutor(max_workers=min(10, len(urls) or 1)) as executor:
        futures = [executor.submit(_check_archive, url) for url in urls]
        for future in as_completed(futures):
            result = future.result()
            if result:
                founded_projects.append(result)
    log.info('{}: founded {} newsletters'.format(get_name(), len(founded_projects)))
    return founded_projects
