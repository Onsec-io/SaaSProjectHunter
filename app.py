import argparse
import os
import importlib
import logger
from tabulate import tabulate
import utils


def load_wordlist(path_to_file):
    words = []
    if path_to_file:
        log.debug('Reading {}...'.format(path_to_file))
        if not os.path.exists(path_to_file) or not os.path.isfile(path_to_file):
            log.error('Please, check your input file!')
            exit()
        with open(path_to_file, 'r') as f:
            words = f.read().splitlines()
    elif args.strings:
        log.debug('Read list of strings from user input: {}'.format(args.strings))
        words = args.strings
    if len(words) < 1:
        log.error('Number of lines < 1. Please, check your input')
        exit()
    return words


def load_modules(name=False):
    modules = []
    folder = 'modules'
    if not os.path.exists(folder) or not os.path.isdir(folder):
        log.error('Folder of modules not found!')
        exit()

    if name:
        log.debug('Loading module {}...'.format(name))
        try:
            module = importlib.import_module(f'{folder}.{name}')
        except ModuleNotFoundError:
            log.error('Module {} not found!'.format(name))
            exit()
        modules.append(module)
        return modules

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
        result = utils.generator(args.generator)
        print(' '.join(result))
        exit()

    if args.check:
        log.info('Check modules...')
        utils.check_modules(load_modules(args.module))
        exit()

    log.debug('Loading wordlist...')
    words = load_wordlist(args.wordlist)
    log.info('Number of lines: {}'.format(len(words)))

    if args.postfix:
        log.info('Loading postfix...')
        postfixlist = load_wordlist(args.postfix)
        result = []
        for w in words:
            result.append(w)
            for p in postfixlist:
                result.append(w + p)
        words = result
        log.info('Number of lines in postfix file and new size of wordlist: {} - {}'.format(len(postfixlist), len(words)))

    log.debug('Loading modules...')
    modules = load_modules(args.module)
    log.info('Number of loaded modules: {}'.format(len(modules)))

    output = []
    for module in modules:
        print('Run {}'.format(module.get_name()))
        for url in module.run(words):
            output.append([module.get_name(), url])
    print(tabulate(output))


parser = argparse.ArgumentParser(description='Example: python3 app.py -s google logstash octocat -v')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--list', action='store_true', default=False, help='print a list of available modules and exit')
group.add_argument('-c', '--check', action='store_true', default=False, help='Run check modules and exit')
group.add_argument('-w', '--wordlist', help='wordlist file path')
group.add_argument('-s', '--strings', help='or list of string over space', nargs='+')
group.add_argument('-g', '--generator', help='run a generator for a list of input strings and exit', nargs='+')
parser.add_argument('-m', '--module', action='store', type=str, default=False, help='Specify the name of the module to run/check')
parser.add_argument('-t', '--threads', default=int(os.cpu_count())*2, type=int, help='number of concurrent threads. If not specified, the number of threads will be equal to the number of CPUs*2')
parser.add_argument('-u', '--user-agent', default='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0', help='set User-Agent to use for requests')
parser.add_argument('-v', '--verbose', default=0, action='count', help='increase output verbosity (-v, -vv)')
parser.add_argument('-nc', '--no-color', action='store_true', default=False, help='disable color output')
parser.add_argument('-p', '--postfix', help='Path to file with postfixes')
parser.add_argument('--limit', default=2500, type=int, help='limit the number of requests per modules')

args = parser.parse_args()
log = logger.init_logger(args.verbose, args.no_color)
utils.init(args.verbose, args.threads, args.user_agent, args.limit)

if __name__ == "__main__":
    main()
