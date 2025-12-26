import asyncio
from utils import async_nslookup, compile_subdomain
import logger
log = logger.get_logger('logger')


def get_name():
    return '3CX'


def get_tags():
    return ['dns', 'nolimit', 'voip']


def get_description():
    return 'This module uses bruteforce subdomains using the 3XC service domain list to find interesting projects'


def wordslist_for_check_module():
    return {
        'real': ['intersoft', 'roemercapital', '3cxcastillo'],
        'fake': ['8457fj20d', 'uenrf348', '8rurur8ud']
    }


def run(words):
    log.debug('Checking the wordlist for requirements of {} module...'.format(get_name()))
    words = [item.replace('.', '-').replace('_', '-') for item in words]
    subdomains = []
    for domain in list_domains():
        subdomains.extend(compile_subdomain(domain, words, proto=''))
    log.debug('Run requests...')
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(async_nslookup(subdomains))
    founded_projects = ['https://{}/'.format(domain) for domain in responses if domain is not None]
    log.info('{}: founded {} sites'.format(get_name(), len(founded_projects)))
    return founded_projects


def list_domains():  # https://activate.3cx.com/apiv2/domains
    return [
        "3cx.at",
        "my3cx.com.au",
        "3cx.com.au",
        "3cx.agency",
        "3cx.asia",
        "3cx.be",
        "3cx.hamburg",
        "3cx.berlin",
        "3cx.paris",
        "3cx.barcelona",
        "3cx.madrid",
        "3cx.bayern",
        "3cx.ca",
        "3cx.cn",
        "3cx.cz",
        "3cx.dk",
        "elastix.com",
        "3cx.fr",
        "3cx.gr",
        "3cx.hu",
        "3cx.de",
        "3cx.it",
        "3cx.ie",
        "3cx.in",
        "3cx.jp",
        "3cx.miami",
        "3cx.nl",
        "3cx.co.nz",
        "3cx.gl",
        "3cx.nu",
        "3cx.pl",
        "3cx.ru",
        "3cx.ro",
        "3cx.es",
        "3cx.ch",
        "3cx.se",
        "3cx.sg",
        "3cx.co.za",
        "3cx.com.tr",
        "3cx.com.mx",
        "3cx.co.uk",
        "north.3cx.us",
        "east.3cx.us",
        "south.3cx.us",
        "west.3cx.us",
        "3cx.wales",
        "3cx.eu",
        "3cx.us",
        "3cx.cloud",
        "3cx.ae",
        "3cx.com.my",
        "3cx.kr",
        "3cx.az",
        "3cx.com.tw",
        "3cx.hk",
        "3cx.vn",
        "3cx.amsterdam",
        "3cx.wien",
        "3cx.com.cy",
        "3cx.pt",
        "3cx.fi",
        "3cx.no",
        "3cx.com.br",
        "3cx.co",
        "al.3cx.us",
        "ak.3cx.us",
        "az.3cx.us",
        "ar.3cx.us",
        "ca.3cx.us",
        "co.3cx.us",
        "ct.3cx.us",
        "de.3cx.us",
        "fl.3cx.us",
        "ga.3cx.us",
        "hi.3cx.us",
        "id.3cx.us",
        "il.3cx.us",
        "in.3cx.us",
        "ia.3cx.us",
        "ks.3cx.us",
        "ky.3cx.us",
        "la.3cx.us",
        "me.3cx.us",
        "md.3cx.us",
        "ma.3cx.us",
        "mi.3cx.us",
        "mn.3cx.us",
        "ms.3cx.us",
        "mo.3cx.us",
        "mt.3cx.us",
        "ne.3cx.us",
        "nv.3cx.us",
        "nh.3cx.us",
        "nj.3cx.us",
        "nm.3cx.us",
        "ny.3cx.us",
        "nc.3cx.us",
        "nd.3cx.us",
        "oh.3cx.us",
        "ok.3cx.us",
        "or.3cx.us",
        "pa.3cx.us",
        "ri.3cx.us",
        "sc.3cx.us",
        "sd.3cx.us",
        "tn.3cx.us",
        "tx.3cx.us",
        "ut.3cx.us",
        "vt.3cx.us",
        "va.3cx.us",
        "wa.3cx.us",
        "wv.3cx.us",
        "wi.3cx.us",
        "wy.3cx.us",
        "my3cx.uk",
        "my3cx.at",
        "my3cx.be",
        "my3cx.ca",
        "my3cx.co.uk",
        "my3cx.mx",
        "my3cx.com.br",
        "my3cx.de",
        "my3cx.es",
        "my3cx.eu",
        "my3cx.fr",
        "my3cx.it",
        "my3cx.nl",
        "my3cx.nz",
        "my3cx.ru",
        "my3cx.sg",
        "my3cx.us",
        "3cx.as",
        "3cx.ag",
        "3cx.vg",
        "3cx.cl",
        "3cx.hr",
        "3cx.ec",
        "3cx.co.ee",
        "3cx.fo",
        "3cx.ht",
        "3cx.hn",
        "3cx.lt",
        "3cx.com.mt",
        "3cx.fm",
        "3cx.me",
        "3cx.ma",
        "3cx.ng",
        "3cx.pe",
        "3cx.re",
        "3cx.sc",
        "3cx.ruhr",
        "3cx.koeln",
        "3cx.ph",
        "3cx.dentist",
        "3cx.eco",
        "3cx.fit",
        "3cx.red",
        "3cx.run",
        "3cx.school",
        "3cx.lat",
        "3cx.uk",
        "on3cx.de",
        "on3cx.fr",
        "3cx.blue",
    ]
