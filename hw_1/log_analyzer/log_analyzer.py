#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
import re
import os
import time
import argparse
import shutil
from statistics import median
import operator
from datetime import datetime
import configparser
import json
from template import REPORT_TEMPLATE
import logging



arg_parser = argparse.ArgumentParser(description='Set way to specific config file')
arg_parser.add_argument('--config',
                        type=str,
                        help='Way to specific config file')

args = arg_parser.parse_args()

config = configparser.RawConfigParser()

if args.config:
    config.read(args.config)
else:
    cur_dir = os.getcwd()
    full_path = f'{cur_dir}\\hw_1\\config.ini'
    config.read(full_path)

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%y.%m.%d %h:%m:%s")

logging.basicConfig(format=formatter,
                    filename=config.get("DEFAULT", "LOG_FILE"),
                    level=logging.INFO)

def logger(level, event):
    if level == 'error':
        logging.error(event)

    elif level == 'warning':
        logging.warning(event)

    elif level == 'info':
        logging.info(event)


def log_finder(configurations):
    """  Required log signatures - nginx-access-ui.log """

    current_date = datetime.today().strftime('%Y%m%d')
    file_signature = 'nginx-access-ui.log-' + current_date

    register_date = register_reader()

    if register_date == current_date:
        logger('error', f"The log for {current_date} already performed")
        return None, None

    else:

        try:
            file_path = configurations.get("DEFAULT", "LOG_DIR")
            files = os.listdir(file_path)

            try:
                pattern = re.compile(r'%s[.gz]{,3}$' % file_signature)
                logs = [re.match(pattern, x).string for x in files if re.match(pattern, x) is not None][0]
                logger('info', f"Log file is {logs}")

                return logs, current_date

            except IndexError:
                #  No log files
                logger('error', "No log files for %s" % current_date)
                return None, None

        except FileNotFoundError:
            #  No log folder
            logger('error', "Log folder not found")


def tmp_cleaner(configurations):
    tmp_file = os.listdir(configurations.get("DEFAULT", 'TMP_DIR'))
    if len(tmp_file) > 0:
        for file in tmp_file:
            full_path = f'{configurations.get("DEFAULT", "TMP_DIR")}/{file}'
            os.remove(full_path)
            logger('info', f'File {file} deleted from TMP folder')


def log_parser(data):
    URLS = []
    rows = iter(data)
    count_all = 0
    count_err = 0

    for row in rows:
        split_row = row.split(' ')
        count_all += 1
        try:
            url, request_time = split_row[7], split_row[-1]
            URLS.append([url, float(request_time)])

        except IndexError:
            count_err += 1
            logger('error', f"Unexpected row`s format {r if len(r) > 0 else 'EMPTY ROW'}")

    logger('info', f"Parsing result: ordinary rows - {count_all},"
                   f" unexpected format - {count_err},"
                   f" percentage {round((count_err / count_all) * 100, 3)}")

    return URLS


def log_performer(source):
    RESULT = []

    LEN_SOURCE_URL = len(source)

    URLS_SET = set()

    for url in source:
        URLS_SET.add(url[0])

    URLS = {x: [] for x in list(URLS_SET)}

    for parsed_log_string in source:
        url, request_time = parsed_log_string
        data_set = URLS[url]
        data_set.append(request_time)
        URLS[url] = data_set

    ALL_TIME_URL = sum([sum([float(y) for y in x[1]]) for x in URLS.items()])

    for url in URLS.items():
        url, time_data = url
        res = {'url': url,
               'count': len(time_data),
               'count_perc': round((len(time_data) / LEN_SOURCE_URL) * 100, 4),
               'time_sum': round(sum(time_data), 4),
               'time_perc': round((round(sum(time_data), 4) / ALL_TIME_URL) * 100, 4),
               'time_avg': round(round(sum(time_data), 4) / LEN_SOURCE_URL, 4),
               'max_time': max(time_data, key=lambda i: float(i)) if len(time_data) > 0 else 0,
               'time_med': round(median(time_data) if len(time_data) > 0 else 0, 4),
               }
        RESULT.append(res)

    return RESULT


def file_writer(report_result, configurations, file_name_data):
    report_array = json.dumps(report_result)

    html_template = re.sub('{%table%}', report_array, REPORT_TEMPLATE)
    file_name = f'./{configurations.get("DEFAULT", "REPORT_DIR")}/report-{file_name_data}.html'

    with open(file_name, 'w') as html_file:
        html_file.write(html_template)


def main():
    file, file_name_data = log_finder(config)

    try:
        if file is not None:
            # Copy file to TMP dir
            shutil.copyfile(f'{config.get("DEFAULT", "LOG_DIR")}/{file}',
                            f'{config.get("DEFAULT", "TMP_DIR")}/{file}')

            # Unpacking the log file
            data = gzip_unpacker(config.get("DEFAULT", "TMP_DIR"), file)

            # Parsing rows
            parsed_rows = log_parser(data)
            REPORT_RESULT = log_performer(parsed_rows)

            logger('info', 'Sorting result')
            REPORT_RESULT.sort(key=operator.itemgetter('time_sum'))

            rep_size = config.get("DEFAULT", "REPORT_SIZE")
            res = REPORT_RESULT[(-1 * int(rep_size)):]
            logger('info', f'Write to the html file result {len(REPORT_RESULT)}')

            file_writer(res[::-1], config, file_name_data)

            register_writer(file_name_data if not config.get("DEFAULT", "DEBUG") else False)

            tmp_cleaner(config)
        else:
            logger('error', "File parser error")

    except BaseException as err:
        logger('error', f'Unexpected error -> {err}')


if __name__ == "__main__":
    logger('info', f"Start process {time.ctime()}")
    main()
    logger('info', f"End process {time.ctime()}\n\n")

