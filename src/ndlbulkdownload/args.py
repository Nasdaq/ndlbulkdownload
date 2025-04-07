import argparse
import os
from .version import version

"""
tdqm.contrib.concurrent:
https://github.com/tqdm/tqdm/blob/master/tqdm/contrib/concurrent.py#L44

tdqm max_workers keyword argument will default to this value, but we need to define it
if we want to override to a sane value so we redefine a default
here:
"""
default_worker_max = min(32, os.cpu_count())
default_worker_help = f"""
Total parallel workers (default: {default_worker_max}; min(32, os.cpu_count()))
"""


def parse_params(items):
    d = {}
    if not items:
        return None

    for v in items:
        k = v.pop(0)
        if k in d:
            if isinstance(d[k], (str, bytes)):
                d[k] = [d[k], v]
            else:
                d[k].extend(v)
        else:
            d[k] = v

    return d


def arg_parser():
    description = "Bulk Download from Data Link."
    parser = argparse.ArgumentParser(description=description)

    help_code = """
The vendor_code/table_code you are trying to download.  Example: FOO/BAR
"""
    parser.add_argument(
        "--code",
        metavar="VC/TC",
        required=True,
        default=None,
        help=help_code,
    )

    help_param = """
Add query param key/value pair
"""
    parser.add_argument(
        "--param",
        metavar=("key value", "value"),
        nargs="*",
        action="append",
        help=help_param,
    )

    help_output_directory = """
Directory to output files. Example: /tmp/ndl (default: current directory)
"""
    parser.add_argument(
        "-O",
        "--output-directory",
        metavar="O",
        type=str,
        default=os.getcwd(),
        help=help_output_directory,
    )

    help_debug = """
Increase log level to DEBUG
"""
    parser.add_argument("--debug", action="store_true", help=help_debug)

    parser.add_argument("--verbose", action="store_true", help="Show logging output")

    help_skip_proxy = """
Ignore proxy environment variables
"""
    parser.add_argument(
        "--skip-proxy",
        action="store_true",
        default=None,
        help=help_skip_proxy,
    )

    help_skip_ssl_verify = """
Do not verify SSL (not recommended in most situations)
"""
    parser.add_argument(
        "--skip-ssl-verify",
        action="store_false",
        default=None,
        help=help_skip_ssl_verify,
    )

    help_redirect = """
Request redirect to files (default: true)
"""
    parser.add_argument(
        "--redirect",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=help_redirect,
    )

    parser.add_argument(
        "--workers",
        metavar="W",
        type=int,
        default=default_worker_max,
        help=default_worker_help,
    )

    help_hostname = """
Define an alternative hostname
"""
    parser.add_argument("--host", metavar="hostname", default=None, help=help_hostname)

    parser.add_argument("--version", action="version", version=f"{version}")

    return parser
