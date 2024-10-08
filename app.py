import argparse
import os
import importlib
import logger
from tabulate import tabulate
import utils


def load_wordlist(path_to_file):
    if not path_to_file:
        return None
    words = []
    if path_to_file:
        log.debug('Reading {}...'.format(path_to_file))
        if not os.path.exists(path_to_file) or not os.path.isfile(path_to_file):
            log.error('File {} not found'.format(path_to_file))
            exit()
        with open(path_to_file, 'r') as f:
            words = f.read().splitlines()
    if not words:
        log.error('File is empty. Please, check your input')
        exit()
    return words


def load_modules(name=False, tag=None):
    folder = 'modules'
    if not os.path.exists(folder) or not os.path.isdir(folder):
        log.error('Folder of modules not found!')
        exit()

    modules = []
    if name:
        log.debug('Loading module {}...'.format(name))
        try:
            module = importlib.import_module(f'{folder}.{name}')
        except ModuleNotFoundError:
            log.error('Module {} not found!'.format(name))
            exit()
        modules.append(module)
    else:
        for file in os.listdir(folder):
            if file == '__init__.py' or file[-3:] != '.py':
                continue
            module_name = file[:-3]
            log.debug('Import {}...'.format(module_name))
            module = importlib.import_module(f'{folder}.{module_name}')
            if not tag or tag in module.get_tags():
                modules.append(module)
    return sorted(modules, key=lambda x: x.get_name())


def main():
    words = []

    if args.list:
        log.debug('Loading modules...')
        modules = load_modules()
        print('List of available modules ({}):'.format(len(modules)))
        for m in modules:
            print(' - {} {} (tags: {}): {}'.format(m.get_name(), m.get_version(), ', '.join(m.get_tags()), m.get_description()))
        exit()

    if args.check:
        if args.proxies:
            utils.check_all_proxies_sync()
        log.info('Check modules...')
        utils.check_modules(load_modules(args.module, args.tag))
        print('Check completed')
        exit()

    if args.strings:
        log.debug('Using strings provided by user...')
        words = args.strings
    elif args.wordlist:
        log.debug('Loading wordlist...')
        words = load_wordlist(args.wordlist)
    if words:
        log.info('Number of lines: {}'.format(len(words)))

    if args.generator is not None:
        if words:
            log.debug('Applying generator on provided words...')
            words = utils.generator(words)
            log.info('Number of lines after applying generator: {}'.format(len(words)))
        else:
            log.debug('Applying generator with your input...')
            result = utils.generator(args.generator)
            print(' '.join(result))
            exit()

    if not words:
        log.error('No words provided and no generator input specified!')
        exit()

    if args.postfix:
        log.info('Loading postfix...')
        postfixlist = load_wordlist(args.postfix)
        combined_words = []
        for w in words:
            combined_words.append(w)
            for p in postfixlist:
                combined_words.append(w + p)
        words = combined_words
        log.info('Number of lines after applying postfix: {}'.format(len(words)))

    log.debug('Loading modules...')
    modules = load_modules(args.module, args.tag)
    log.info('Number of loaded modules: {}'.format(len(modules)))

    output = []
    for module in modules:
        print('Run {}'.format(module.get_name()))
        for url in module.run(words):
            output.append([module.get_name(), url])
    print(tabulate(output))


print("SaaSProjectHunter (developed by ONSEC.io)\n")
parser = argparse.ArgumentParser(description='Example usage: python3 app.py -s google logstash octocat -v')

parser.add_argument('-g', '--generator', nargs='*', help='Apply a generator to the wordlist.')
parser.add_argument('-m', '--module', action='store', type=str, default=False, help='Specify the module name to run or check.')
parser.add_argument('-t', '--threads', default=int(os.cpu_count()) * 2, type=int, help='Set the number of concurrent threads. Defaults to twice the number of CPU cores.')
parser.add_argument('-u', '--user-agent', default='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0', help='Set the User-Agent string for HTTP requests.')
parser.add_argument('-v', '--verbose', default=0, action='count', help='Increase output verbosity (e.g., -v for verbose, -vv for more verbose).')
parser.add_argument('-nc', '--no-color', action='store_true', default=False, help='Disable colored output.')
parser.add_argument('-p', '--postfix', help='Specify the file path for postfixes.')
parser.add_argument('--limit', default=10000, type=int, help='Set the maximum number of requests per module.')
parser.add_argument('--proxies', default=None, help='Specify the file path for HTTP/SOCKS proxies.')
parser.add_argument('--tag', default=None, help='Specify the tag for run only specific modules.')

group = parser.add_mutually_exclusive_group()
group.add_argument('-l', '--list', action='store_true', default=False, help='Display a list of available modules and exit.')
group.add_argument('-c', '--check', action='store_true', default=False, help='Execute module checks and exit.')

input_group = parser.add_mutually_exclusive_group()
input_group.add_argument('-w', '--wordlist', help='Specify the file path to the wordlist.')
input_group.add_argument('-s', '--strings', nargs='+', help='Provide a list of strings separated by spaces.')

args = parser.parse_args()
if not (args.wordlist or args.strings or args.generator or args.list or args.check):
    parser.error('You must specify one of the following arguments: -w/--wordlist, -s/--strings, -g/--generator, -l/--list, or -c/--check.')


log = logger.init_logger(args.verbose, args.no_color)
utils.init(args.verbose, args.threads, args.user_agent, args.limit, load_wordlist(args.proxies))

if __name__ == "__main__":
    main()
