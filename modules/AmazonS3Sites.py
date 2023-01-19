import asyncio
import random
import re
from utils import async_requests, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'AmazonS3Sites'


def get_version():
    return '1.0'


def get_description():
    return 'This module uses bruteforce of <s3-website-region>.amazonaws.com subdomain-sites to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['j4s', 'digiprofiili', 'macbookrepair'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]  # lowercase
    endpoint = random_endpoint()
    urls = compile_subdomain(endpoint, words, proto='http')
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    correct_endpoints_for_bucket = []
    for r in responses:
        if r.status_code == 400 and 'Please direct requests to the specified endpoint' in r.text:
            host_regex = re.compile(r"Endpoint: ([\w\.\-]+)")
            match = host_regex.search(r.text)
            if match:
                host = match.group(1)
                log.debug('Found correct endpoint for {}: {}'.format(str(r.url), host))
                correct_endpoints_for_bucket.append('http://{}'.format(host))
        elif r.status_code != 404:
            founded_projects.append(str(r.url))

    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(correct_endpoints_for_bucket, method='get'))
    founded_projects.extend(['http://{}/'.format(r.url.host) for r in responses if
                             r.status_code != 404
                             and
                             'The specified bucket does not have a website configuration' not in r.text])
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects


def random_endpoint():
    endpoints = [  # https://docs.aws.amazon.com/general/latest/gr/s3.html#s3_website_region_endpoints
        's3-website-ap-northeast-1.amazonaws.com',
        's3-website-ap-southeast-1.amazonaws.com',
        's3-website-ap-southeast-2.amazonaws.com',
        's3-website-eu-west-1.amazonaws.com',
        's3-website-sa-east-1.amazonaws.com',
        's3-website-us-east-1.amazonaws.com',
        's3-website-us-west-1.amazonaws.com',
        's3-website-us-west-2.amazonaws.com',
        's3-website.af-south-1.amazonaws.com',
        's3-website.ap-east-1.amazonaws.com',
        's3-website.ap-northeast-2.amazonaws.com',
        's3-website.ap-northeast-3.amazonaws.com',
        's3-website.ap-south-1.amazonaws.com',
        's3-website.ap-south-2.amazonaws.com',
        's3-website.ap-southeast-3.amazonaws.com',
        's3-website.ca-central-1.amazonaws.com',
        's3-website.cn-northwest-1.amazonaws.com',
        's3-website.eu-central-1.amazonaws.com',
        's3-website.eu-central-2.amazonaws.com',
        's3-website.eu-north-1.amazonaws.com',
        's3-website.eu-south-1.amazonaws.com',
        's3-website.eu-south-2.amazonaws.com',
        's3-website.eu-west-2.amazonaws.com',
        's3-website.eu-west-3.amazonaws.com',
        's3-website.me-central-1.amazonaws.com',
        's3-website.me-south-1.amazonaws.com',
        's3-website.us-east-2.amazonaws.com',
    ]
    return random.choice(endpoints)
