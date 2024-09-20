import argparse
import os

"""
tdqm.contrib.concurrent:
https://github.com/tqdm/tqdm/blob/master/tqdm/contrib/concurrent.py#L44

tdqm max_workers keyword argument will default to this value, but we need to
define it if we want to override to a sane value so we redefine a default
here:
"""
default_worker_max = min(32, os.cpu_count())
default_worker_help = f"""
Total parallel workers (default: {default_worker_max};
min(32, os.cpu_count()))
"""


class ParseEnvBool(argparse.Action):
    def __init__(self, env_var, required=False, default=False, **kwargs):
        value = (os.getenv(env_var, default) is True)

        if required and value:
            required = False

        super(ParseEnvBool, self).__init__(
            default=value,
            nargs=0,
            required=required,
            **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def parse_params(items):
    d = {}
    if not items:
        return None

    for k, v in items:
        if k in d:
            if isinstance(d[k], (str, bytes)):
                d[k] = [d[k], v]
            else:
                d[k].append(v)
        else:
            d[k] = v

    return d


def arg_parser():
    description = 'Bulk Download from Data Link.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--code',
                        metavar='VC/TC',
                        required=True,
                        default=None,
                        help='The vendor_code/table_code you are trying to '
                             'download.  Example: FOO/BAR')

    parser.add_argument('--param',
                        metavar=('key', 'value'),
                        nargs=2,
                        action='append',
                        help='Add query param key/value pair')

    parser.add_argument('--debug',
                        action='store_true',
                        help='Increase log level to DEBUG')

    parser.add_argument('--verbose',
                        action='store_true',
                        help='Show logging output')

    parser.add_argument('--skip-proxy',
                        action=ParseEnvBool,
                        env_var='NDL_SKIP_PROXY',
                        help='Ignore proxy environment variables')

    parser.add_argument('--skip-ssl-verify',
                        action=ParseEnvBool,
                        env_var='NDL_SKIP_SSL_VERIFY',
                        help='Do not verify SSL (not recommended in most '
                             'situations)')

    parser.add_argument('--workers',
                        metavar='W',
                        type=int,
                        default=default_worker_max,
                        help=default_worker_help)

    parser.add_argument('--host',
                        metavar='hostname',
                        default=None,
                        help='Define an alternative hostname')
    return parser
