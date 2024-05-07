import asyncio
from utils import async_nslookup, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return 'Azure'


def get_version():
    return '1.2'


def get_description():
    return 'This module uses bruteforce of subdomains by Azure endpoints (except storages/buckets)'


def wordslist_for_check_module():
    return {
        'real': ['coodash', 'admin', 'mhraproducts4853'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    domains = []
    for endpoint in endpoints():
        domains.extend(compile_subdomain(endpoint, words, proto=''))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_nslookup(domains))
    founded_projects = ['https://{}'.format(domain) for domain in responses if domain is not None]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects


def endpoints():
    # https://learn.microsoft.com/bs-latn-ba/azure/security/fundamentals/azure-domains
    endpoint_list = [
        'azure-api.net',
        'azure-mobile.net',
        'azurecr.io',
        'azureedge.net',
        'azurewebsites.net',
        'database.windows.net',
        'documents.azure.com',
        'redis.cache.windows.net',
        'scm.azurewebsites.net',
        'vault.azure.net',
    ]
    endpoint_list.extend(endpoints_by_regions())
    return endpoint_list


def endpoints_by_regions():
    endpoints_list = [
        'cloudapp.azure.com',
        'azurecontainer.io',
    ]
    return ['{}.{}'.format(region, endpoint) for endpoint in endpoints_list for region in regions()]


def regions():
    # https://gist.github.com/ausfestivus/04e55c7d80229069bf3bc75870630ec8
    return [
        'asia',
        'asiapacific',
        'australia',
        'australiacentral',
        'australiacentral2',
        'australiaeast',
        'australiasoutheast',
        'brazil',
        'brazilsouth',
        'brazilsoutheast',
        'brazilus',
        'canada',
        'canadacentral',
        'canadaeast',
        'centralindia',
        'centralus',
        'centraluseuap',
        'centralusstage',
        'eastasia',
        'eastasiastage',
        'eastus',
        'eastus2',
        'eastus2euap',
        'eastus2stage',
        'eastusstage',
        'eastusstg',
        'europe',
        'france',
        'francecentral',
        'francesouth',
        'germany',
        'germanynorth',
        'germanywestcentral',
        'global',
        'india',
        'japan',
        'japaneast',
        'japanwest',
        'jioindiacentral',
        'jioindiawest',
        'korea',
        'koreacentral',
        'koreasouth',
        'northcentralus',
        'northcentralusstage',
        'northeurope',
        'norway',
        'norwayeast',
        'norwaywest',
        'polandcentral',
        'qatarcentral',
        'singapore',
        'southafrica',
        'southafricanorth',
        'southafricawest',
        'southcentralus',
        'southcentralusstage',
        'southcentralusstg',
        'southeastasia',
        'southeastasiastage',
        'southindia',
        'swedencentral',
        'switzerland',
        'switzerlandnorth',
        'switzerlandwest',
        'uae',
        'uaecentral',
        'uaenorth',
        'uk',
        'uksouth',
        'ukwest',
        'unitedstates',
        'unitedstateseuap',
        'westcentralus',
        'westeurope',
        'westindia',
        'westus',
        'westus2',
        'westus2stage',
        'westus3',
        'westusstage',
    ]
