import asyncio
import random
import re
from utils import async_requests, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'AlibabaCloudS3'


def get_version():
    return '1.0'


def get_tags():
    return ['s3', 'backet', 'subdomain', 'nolimit']


def get_description():
    return 'This module uses bruteforce of <region>.aliyuncs.com subdomain-sites to find interesting buckets'


def wordslist_for_check_module():
    return {
        'real': ['tripkeda', 'pasion-tropicalcom', 'shopping41'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.lower() for item in words]  # lowercase
    endpoint = random_endpoint()
    urls = compile_subdomain(endpoint, words, proto='http://')
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_requests(urls, method='get'))
    founded_projects = []
    correct_endpoints_for_bucket = []
    for r in responses:
        if r.status_code == 403 and 'Please send all future requests to this endpoint' in r.text:
            host_regex = re.compile(r"<Endpoint>(.*?)</Endpoint>")
            host_match = host_regex.search(r.text)
            if host_match:
                host = host_match.group(1)
                log.debug('Found correct endpoint for {}: {}'.format(str(r.url), host))
                log.debug('Extract bucket name from {}'.format(r.url))
                bucket_regex = re.compile(r"<Bucket>(.*?)</Bucket>")
                bucket_match = bucket_regex.search(r.text)
                bucket = bucket_match.group(1)
                log.debug('Found correct subdomain for {}: {}.{}'.format(str(r.url), bucket,host))
                correct_endpoints_for_bucket.append('http://{}.{}'.format(bucket, host))
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
    # https://www.alibabacloud.com/help/en/object-storage-service/latest/regions-and-endpoints
    endpoints = [
        'oss-cn-hangzhou.aliyuncs.com',
        'oss-cn-shanghai.aliyuncs.com',
        'oss-cn-nanjing.aliyuncs.com',
        'oss-cn-qingdao.aliyuncs.com',
        'oss-cn-beijing.aliyuncs.com',
        'oss-cn-zhangjiakou.aliyuncs.com',
        'oss-cn-huhehaote.aliyuncs.com',
        'oss-cn-wulanchabu.aliyuncs.com',
        'oss-cn-shenzhen.aliyuncs.com',
        'oss-cn-heyuan.aliyuncs.com',
        'oss-cn-guangzhou.aliyuncs.com',
        'oss-cn-chengdu.aliyuncs.com',
        'oss-cn-hongkong.aliyuncs.com',
        'oss-us-west-1.aliyuncs.com',
        'oss-us-east-1.aliyuncs.com',
        'oss-ap-northeast-1.aliyuncs.com',
        'oss-ap-northeast-2.aliyuncs.com',
        'oss-ap-southeast-1.aliyuncs.com',
        'oss-ap-southeast-2.aliyuncs.com',
        'oss-ap-southeast-3.aliyuncs.com',
        'oss-ap-southeast-5.aliyuncs.com',
        'oss-ap-southeast-6.aliyuncs.com',
        'oss-ap-southeast-7.aliyuncs.com',
        'oss-ap-south-1.aliyuncs.com',
        'oss-eu-central-1.aliyuncs.com',
        'oss-eu-west-1.aliyuncs.com',
        'oss-me-east-1.aliyuncs.com',
    ]
    return random.choice(endpoints)
