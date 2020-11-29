#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
import re
import os
import logging
import time
import argparse
import shutil
from threading import Thread
from math import ceil
from statistics import median
import operator
from datetime import datetime
import configparser
import json
from template import REPORT_TEMPLATE

arg_parser = argparse.ArgumentParser(description='Set way to specific config file')
arg_parser.add_argument('--config',
                        type=str,
                        help='Way to specific config file')

args = arg_parser.parse_args()

REPORT_RESULT = []

config = configparser.RawConfigParser()

if args.config:
    config.read(args.config)
else:
    cur_dir = os.getcwd()
    config.read(f'{cur_dir}/config.ini')

logging.basicConfig(format='%(levelname)-8s[%(asctime)s] %(message)s',
                    filename=config.get("DEFAULT", "LOG_FILE"),
                    level=logging.INFO)


class LogPerformerThread(Thread):

    def __init__(self, arr, source):
        Thread.__init__(self)
        self.arr = arr
        self.source = source

    def run(self):
        url_performer(self.arr, self.source)

    # def join(self):
    #     Thread.join(self)
    #     return self._return


def logger(level, event):
    if level == 'error':
        logging.error(event)

    elif level == 'warning':
        logging.warning(event)

    elif level == 'info':
        logging.info(event)


def gzip_unpacker(directory, file):
    full_file_path = (f'{directory}/{file}' if directory is not None else file)

    try:
        with gzip.open(full_file_path, 'rb') as file:
            result = file.read()
            logger('info', f"ZIP Log file contains data => {len(result)}")
            return result.decode('utf-8').split('\n')

    except gzip.BadGzipFile:
        with open(full_file_path, 'rb') as file:
            result = file.read()
            logger('info', f"Plain Log file contains data => {len(result)}")
            return result.decode('utf-8').split('\n')


def log_finder(configurations):
    # LOG_SIGNATURE = "nginx-access-ui.log",

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
                ''' No log files '''
                logger('error', "No log files for %s" % current_date)
                return None, None

        except FileNotFoundError:
            ''' No log folder '''
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

    for r in rows:
        split_row = r.split(' ')
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


def log_performer(source, threads):
    URLS_SET = set()

    for url in source:
        URLS_SET.add(url[0])

    # STOLEN
    def parting(xs, parts):
        part_len = ceil(len(xs) / parts)
        return [xs[part_len * k:part_len * (k + 1)] for k in range(parts)]

    URLS_PART = parting(list(URLS_SET), threads)
    logger('info', f'Threads - {len(URLS_PART)} are running')

    for arr in URLS_PART:
        my_thread = LogPerformerThread(arr, source)
        my_thread.start()


def url_performer(arr, source):
    LEN_SOURCE_URL = len(source)
    ALL_TIME_URL = sum([x[1] for x in source])

    iterator = iter(arr)

    while True:
        try:
            url = next(iterator)
            time_data = []

            for el in source:
                if el[0] == url:
                    time_data.append(el[1])

            res = {'url': url,
                   'count': len(time_data),
                   'count_perc': round((len(time_data) / LEN_SOURCE_URL) * 100, 4),
                   'time_sum': round(sum(time_data), 4),
                   'time_perc': round((round(sum(time_data), 4) / ALL_TIME_URL) * 100, 4),
                   'time_avg': round(round(sum(time_data), 4) / LEN_SOURCE_URL, 4),
                   'max_time': max(time_data, key=lambda i: float(i)) if len(time_data) > 0 else 0,
                   'time_med': round(median(time_data) if len(time_data) > 0 else 0, 4)
                   }

            REPORT_RESULT.append(res)

        except StopIteration:
            break


def file_writer(report_result, configurations, file_name_data):
    report_array = json.dumps(report_result)

    html_template = re.sub('{%table%}', report_array, REPORT_TEMPLATE)
    file_name = f'./{configurations.get("DEFAULT", "REPORT_DIR")}/report-{file_name_data}.html'

    with open(file_name, 'w') as html_file:
        html_file.write(html_template)


def register_writer(result_status):
    try:
        with open('./register', 'w') as f:
            f.writelines(result_status)

    except FileNotFoundError:
        logger('error', f'NOT FOUND REGISTER FILE FOR WRITING')


def register_reader():
    try:
        with open('./register', 'r') as file:
            res = file.readlines()
            return res[0]

    except FileNotFoundError:
        logger('error', f'NOT FOUND REGISTER FILE FOR READING')

    except IndexError:
        ''' Register file is empty '''
        return ''


def main():
    file, file_name_data = log_finder(config)

    try:
        if file is not None:

            # Copy file to TMP dir
            shutil.copyfile(f'{config.get("DEFAULT", "LOG_DIR")}/{file}', f'{config.get("DEFAULT", "TMP_DIR")}/{file}')

            # Unpacking the log file
            data = gzip_unpacker(config.get("DEFAULT", "TMP_DIR"), file)

            # Parsing rows
            parsed_rows = log_parser(data)
            log_performer(parsed_rows, os.cpu_count())

            logger('info', 'Sorting result')
            REPORT_RESULT.sort(key=operator.itemgetter('time_sum'))

            rep_size = config.get("DEFAULT", "REPORT_SIZE")
            res = REPORT_RESULT[(-1 * int(rep_size)):]
            logger('info', f'Write to the html file result {len(REPORT_RESULT)}')

            file_writer(res[::-1], config, file_name_data)

            # COMMENT THIS WHEN TESTING
            # register_writer(FILE_NAME_DATA)

            tmp_cleaner(config)

        else:
            logger('error', "File parser error")

    except BaseException as err:
        logger('error', f'Unexpected error -> {err}')


if __name__ == "__main__":
    logger('info', f"Start process {time.ctime()}")
    main()
    logger('info', f"End process {time.ctime()}\n\n")
