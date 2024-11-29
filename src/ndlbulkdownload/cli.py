#!/usr/bin/env python

import requests
import urllib.request
import http.client
import logging
import sys
import os
import time

import urllib.parse as urlparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from multiprocessing import freeze_support
from tqdm.auto import tqdm
from tqdm.contrib.concurrent import thread_map
from functools import partial

from .args import (
  parse_params,
  arg_parser,
)


default_hostname = 'data.nasdaq.com'
apikey_envname = "NDL_APIKEY"

halt_processing_status = [
    'CANCELLED',
    'CLOSED',
    'COLUMN_FILTER_FAILURE',
    'FAILED',
]

retry_strategy = Retry(
    total=3,
    backoff_factor=3,
    status_forcelist=[202, 429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
proxies = urllib.request.getproxies()

failed_urls = []


def api_key():
    return os.getenv(apikey_envname)


def get_headers():
    headers = {
        'X-Api-Token': api_key(),
    }

    return headers


def get_hostname(hostname=None):
    if hostname is not None:
        return hostname
    return os.getenv('NDL_HOSTNAME', default_hostname)


def bulk_download_url(args):
    host = get_hostname(args.host)
    code = args.code
    return f"https://{host}/api/v1/bulkdownloads/{code}"


def dest_file_from_url(url):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    file = os.path.basename(path)
    logging.debug(f"writing to: {file}")
    return file


def write_with_progress_uncaught(url, session, headers={}, params={},
                                 chunk_size=4096):
    file = dest_file_from_url(url)
    response = session.get(url, headers=headers, stream=True, params=params)
    total = int(response.headers.get('content-length', 0))
    with open(file, "wb") as handle:
        with tqdm(
            desc=file,
            total=total,
            unit='B',
            miniters=1,
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=chunk_size):
                size = handle.write(data)
                bar.update(size)


def write_with_progress(url, session, headers={}, params={}, chunk_size=4096):
    try:
        write_with_progress_uncaught(url, session, headers=headers,
                                     params=params, chunk_size=chunk_size)
    except Exception as e:
        logging.debug(e)
        msg = "Problem occurred while downloading, " \
            f"will retry later: {url}"
        logging.info(msg)
        global failed_urls
        failed_urls.append(url)


def halt_processing_if_necessary(status, result):
    if status in halt_processing_status:
        errors = result.get('errors')
        message = f'Something went wrong: {status}'
        if errors is not None and len(errors) > 0:
            message += f'; errors: {errors}'
        logging.warn(message)
        raise ValueError(message)


def get_files(session, url, headers, params):
    status = None
    files = []
    result = {}

    while True:
        if status == 'SUCCEEDED' and len(files) >= 0:
            break

        halt_processing_if_necessary(status, result)

        logging.info('Waiting for files to be ready...')
        time.sleep(2)

        response = session.get(url, headers=headers, params=params)
        response.raise_for_status()

        result = response.json()
        logging.debug(result)

        result = result.get('bulk_download')
        status = result.get('status')
        files = result.get('files', None)

    return files


def urls_from_files(files):
    urls = []
    for path in files:
        s3_url = path.get('url')
        urls.append(s3_url)
        logging.debug(s3_url)

    return urls


def setup_logging(args):
    level = logging.INFO
    if args.verbose:
        logging.basicConfig(format='%(levelname)-8s %(name)-20s %(message)s')

        if args.debug:
            http.client.HTTPConnection.debuglevel = 5
            level = logging.DEBUG

        logging.getLogger().setLevel(level)


def create_session(args):
    session = requests.Session()
    if not args.skip_proxy:
        logging.debug(proxies)
        session.proxies.update(proxies)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    if args.skip_ssl_verify is not None:
        requests.packages.urllib3.disable_warnings()
        session.verify = args.skip_ssl_verify
        session.trust_env = args.skip_ssl_verify

    return session


def raise_if_missing_env(env_var):
    if os.getenv(env_var, None) is None:
        raise ValueError(f'Missing required environment variable [{env_var}]')


def raise_if_missing_required():
    raise_if_missing_env(apikey_envname)


def check_code(parser, code):
    d = code.split('/')
    if len(d) != 2:
        message = f"""
Invalid CODE format. Expected vendor_code/table_code got:
{code}

"""
        sys.stderr.write(message)
        parser.print_help()
        parser.exit(1)


def retry_failed_if_necessary(session, headers, params, max_workers):
    global failed_urls

    while len(failed_urls) > 0:
        retry_urls = failed_urls.copy()
        failed_urls = []
        logging.info("Retrying failed files...")
        logging.debug(retry_urls)

        thread_map(partial(write_with_progress,
                           session=session,
                           headers=headers,
                           params=params),
                   retry_urls,
                   max_workers=max_workers)


def main():
    parser = arg_parser()
    args = parser.parse_args()

    try:
        raise_if_missing_required()
    except ValueError as ve:
        sys.stderr.write(f'{ve}\n---\n\n')
        parser.print_help()
        sys.exit(0)

    check_code(parser, args.code)

    params = parse_params(args.param)
    max_workers = args.workers
    headers = get_headers()
    setup_logging(args)

    url = bulk_download_url(args)
    logging.debug(url)
    logging.info("Fetching files...")

    session = create_session(args)
    files = get_files(session, url, headers, params)
    urls = urls_from_files(files)
    logging.debug(urls)

    params = {}
    if args.redirect:
        params['qopts.redirect'] = 'true'

    thread_map(partial(write_with_progress,
                       session=session,
                       headers=headers,
                       params=params),
               urls,
               max_workers=max_workers)

    sys.stderr.flush()
    logging.info("\n\n")

    retry_failed_if_necessary(session, headers, params, max_workers)

    sys.stderr.flush()
    logging.info("\n\ndone!")


if __name__ == '__main__':
    freeze_support()  # for Windows support
    main()
