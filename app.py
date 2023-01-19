import argparse
import os
import importlib
import logger
from tabulate import tabulate
from utils import check_modules, set_threads_limit, set_useragent, generator
from progressbar import progressbar


def load_wordlist():
    words = []
    if args.wordlist:
        log.debug('Reading {}...'.format(args.wordlist))
        if not os.path.exists(args.wordlist) or not os.path.isfile(args.wordlist):
            log.error('Please, check your input file!')
            exit()
        with open(args.wordlist, 'r') as f:
            words = f.read().splitlines()
    elif args.strings:
        log.debug('Read list of strings from user input: {}'.format(args.strings))
        words = args.strings
    if len(words) < 1:
        log.error('Number of lines < 1. Please, check your input')
        exit()
    return words


def load_modules():
    modules = []
    folder = 'modules'
    if not os.path.exists(folder) or not os.path.isdir(folder):
        log.error('Folder of modules not found!')
        exit()
    for file in os.listdir(folder):
        if file == '__init__.py' or file[-3:] != '.py':
            continue
        module_name = file[:-3]
        log.debug('Import {}...'.format(module_name))
        module = importlib.import_module(f'{folder}.{module_name}')
        modules.append(module)
    if len(modules) < 1:
        log.error('Not found and/or loaded modules!')
        exit()
    # sort modules by name
    modules = sorted(modules, key=lambda x: x.get_name())
    return modules


def main():
    if args.list:
        log.debug('Loading modules...')
        modules = load_modules()
        log.debug('OK')
        print('List of available modules ({}):'.format(len(modules)))
        for m in modules:
            print(' - {} {}: {}'.format(m.get_name(), m.get_version(), m.get_description()))
        exit()

    if args.generator:
        result = generator(args.generator)
        print(' '.join(result))
        exit()

    if args.check_modules:
        log.info('Check modules...')
        check_modules(load_modules(), args.check_modules, args.verbose)
        exit()

    log.debug('Loading wordlist...')
    words = load_wordlist()
    log.info('Number of lines: {}'.format(len(words)))

    log.debug('Loading modules...')
    modules = load_modules()
    log.info('Number of loaded modules: {}'.format(len(modules)))

    output = []
    if args.verbose == 0:
        for module in progressbar(modules, redirect_stdout=True):
            for url in module.run(words):
                output.append([module.get_name(), url])
    else:
        for module in modules:
            for url in module.run(words):
                output.append([module.get_name(), url])
    print(tabulate(output))


parser = argparse.ArgumentParser(description='Example: python3 app.py -s google logstash octocat -v')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--list', action='store_true', default=False, help='print a list of available modules and exit')
group.add_argument('-c', '--check-modules', action='store', type=str, default=False, help='specify the name of the module to check. Set to "all" for check all modules')
group.add_argument('-w', '--wordlist', help='wordlist file path')
group.add_argument('-s', '--strings', help='or list of string over space', nargs='+')
group.add_argument('-g', '--generator', help='run a generator for a list of input strings and exit', nargs='+')
parser.add_argument('-t', '--threads', default=int(os.cpu_count())*2, help='number of concurrent threads. If not specified, the number of threads will be equal to the number of CPUs*2')
parser.add_argument('-u', '--user-agent', default='Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0', help='set User-Agent to use for requests')
parser.add_argument('-v', '--verbose', action='count', default=0, help='increase output verbosity (-v, -vv)')
parser.add_argument('-nc', '--no-color', action='store_true', default=False, help='disable color output')

args = parser.parse_args()
log = logger.init_logger(args.verbose, args.no_color)
set_threads_limit(int(args.threads))
set_useragent(str(args.user_agent))

if __name__ == "__main__":
    main()
