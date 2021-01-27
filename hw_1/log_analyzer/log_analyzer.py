#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
import re
import os
import time

import argparse
import configparser

import shutil
from statistics import median
import operator
from functools import partial
from datetime import datetime

import json

import logging
import traceback
import sys

from template import REPORT_TEMPLATE


def parse_args(args):
    """Parsing input argumnts

    :param args: arguments
    :type args: list
    :return: args
    :rtype: obj
    """

    arg_parser = argparse.ArgumentParser(description="Set way to specific config file")
    arg_parser.add_argument("--config", type=str, help="Way to specific config file")

    return arg_parser.parse_args(args)


def parse_config(args):
    """Parsing config file

    :return: config obj
    :rtype: object
    """

    extra_config = {
        "debug": "False",
        "log_dir": "./log",
        "log_file": "./performer.log",
        "report_dir": "./reports",
        "report_size": "1000",
        "tmp_dir": "./tmp",
    }

    config = configparser.RawConfigParser()

    if args.config:
        config.read(args.config)

    else:
        cur_dir = os.getcwd()
        full_path = f"{cur_dir}/log_analyzer/config.ini"
        config.read(full_path)

        if not config._defaults:
            config._defaults = extra_config

    return config


def gzip_unpacker(directory, source_file):
    """Unpack log file

    :param source_file: sorce file name
    :param directory: log directory
    :type directory: str
    :type file: str
    :return: parsed file
    :rtype: list
    """

    full_file_path = f"{directory}/{source_file}" if directory is not None else source_file

    if len(re.findall(".gz$", full_file_path)) == 1:
        file_opener = partial(gzip.open, mode="rb")
    else:
        file_opener = partial(open, mode="rb")

    with file_opener(full_file_path) as log_file:
        result = log_file.read()
        return result.decode("utf-8").split("\n")


def log_finder(configurations, logger=None):
    """Findlog file with appropriate signature

    Required log signatures - nginx-access-ui.log

    :param configurations: config obj
    :type configurations: obj
    :param logger: logging obj, defaults to None
    :type logger: object, optional
    """

    current_date = datetime.today().strftime("%Y%m%d")
    file_signature = "nginx-access-ui.log-" + current_date

    register_date = register_reader(logger=None)

    if register_date == current_date:
        logger.error(
            "The log for %s already performed" % current_date
        ) if logger is not None else None
        return None, None

    else:

        try:
            file_path = configurations.get("DEFAULT", "LOG_DIR")
            files = os.listdir(file_path)

            try:
                pattern = re.compile(r"%s[.gz]{,3}$" % file_signature)
                logs = [
                    re.match(pattern, file).string
                    for file in files
                    if re.match(pattern, file) is not None
                ][0]

                logger.info("Log file is %s" % logs) if logger is not None else None

                return logs, current_date

            except IndexError:
                #  No log files
                logger.error(
                    "No log files for %s" % current_date
                ) if logger is not None else None
                return None, None

        except FileNotFoundError:
            #  No log folder
            logger.error("Log folder not found") if logger is not None else None
            return None, None


def tmp_cleaner(configurations, logger=None):
    """Clean tmp file

    :param configurations: config obj
    :type configurations: object
    :param logger: logger obj, defaults to None
    :type logger: object, optional
    """

    tmp_file = os.listdir(configurations.get("DEFAULT", "TMP_DIR"))

    if len(tmp_file) > 0:
        for file in tmp_file:
            full_path = f'{configurations.get("DEFAULT", "TMP_DIR")}/{file}'
            os.remove(full_path)
            logger.info(
                "File %s deleted from TMP folder" % file
            ) if logger is not None else None


def log_parser(data, logger=None):
    """Parsing log list

    :param data: data list
    :type data: list
    :param logger: logger obj, defaults to None
    :type logger:  object, optional
    :return: URLS list - url, time
    :rtype: list
    """

    URLS = []
    rows = iter(data)
    count_all = 0
    count_err = 0

    for row in rows:
        split_row = row.split(" ")
        count_all += 1
        try:
            url, request_time = split_row[7], split_row[-1]
            try:
                URLS.append([url, float(request_time)])
            except ValueError:
                logger.error(
                    "Unexpected row`s format %s" % row
                ) if logger is not None else None

        except IndexError:
            count_err += 1
            logger.error(
                "Unexpected row`s format %s" % row if len(row) > 0 else "EMPTY ROW"
            ) if logger is not None else None

    logger.info(
        "Parsing result: ordinary rows - %s" % count_all
    ) if logger is not None else None
    logger.info("Unexpected format - %s" % count_err) if logger is not None else None
    logger.info(
        "Errors percentage %d" % round((count_err / count_all) * 100, 3)
    ) if logger is not None else None

    return URLS


def log_performer(source, logger=None):
    """Performing log list

    :param source: urls list - [url, time]
    :type source: list
    :param logger: loggong obj, defaults to None
    :type logger:  object, optional
    :return: result
    :rtype: list
    """

    RESULT = []

    LEN_SOURCE_URL = len(source)

    URLS_SET = set()

    for url in source:
        URLS_SET.add(url[0])

    URLS = {url: [] for url in list(URLS_SET)}

    for parsed_log_string in source:
        try:
            url, request_time = parsed_log_string
            data_set = URLS[url]

            if isinstance(request_time, float):
                data_set.append(request_time)

            URLS[url] = data_set
        except ValueError:
            logger.error(
                "Unexpected row`s data %s" % parsed_log_string
            ) if logger is not None else None

    ALL_TIME_URL = sum(
        (sum([float(url_time) for url_time in url[1]]) for url in URLS.items())
    )

    for url in URLS.items():
        url, time_data = url
        res = {
            "url": url,
            "count": len(time_data),
            "count_perc": round((len(time_data) / LEN_SOURCE_URL) * 100, 4),
            "time_sum": round(sum(time_data), 4),
            "time_perc": round((round(sum(time_data), 4) / ALL_TIME_URL) * 100, 4),
            "time_avg": round(round(sum(time_data), 4) / LEN_SOURCE_URL, 4),
            "max_time": max(time_data, key=lambda i: float(i))
            if len(time_data) > 0
            else 0,
            "time_med": round(median(time_data) if len(time_data) > 0 else 0, 4),
        }
        RESULT.append(res)

    return RESULT


def file_writer(report_result, configurations, file_name_data):
    """Write result file

    :param report_result: result list
    :type report_result: list
    :param configurations: config obj
    :type configurations: object
    :param file_name_data: file name
    :type file_name_data: str
    """

    report_array = json.dumps(report_result)

    html_template = re.sub("{%table%}", report_array, REPORT_TEMPLATE)
    file_name = (
        f'./{configurations.get("DEFAULT", "REPORT_DIR")}/report-{file_name_data}.html'
    )

    with open(file_name, "w") as html_file:
        html_file.write(html_template)


def register_writer(result_status, logger=None):
    """Write register file

    :param result_status: result string (data or False)
    :type result_status: str or bool
    :param logger: logging obj, defaults to None
    :type logger: object, optional
    """

    if result_status is not False:
        try:
            with open("./register", "w") as register_file:
                register_file.writelines(result_status)

        except FileNotFoundError:
            logger.error(
                "NOT FOUND REGISTER FILE FOR WRITING"
            ) if logger is not None else None


def register_reader(logger=None):
    """Read register file

    :param logger: logging obj, defaults to None
    :type logger: object, optional
    :return: last performing data
    :rtype: str
    """

    try:
        with open("./log_analyzer/register", "r") as register_file:
            res = register_file.readlines()
            return res[0]

    except FileNotFoundError:
        logger.error(
            "NOT FOUND REGISTER FILE FOR READING"
        ) if logger is not None else None

    except IndexError:
        """ Register file is empty """
        return ""


def main():
    # SET ARGS
    args_parser = parse_args(sys.argv[1:])

    # SET CONFIG
    config = parse_config(args_parser)

    # SET LOGGER
    logging.basicConfig(
        format="%(asctime)s %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
        filename=config.get("DEFAULT", "LOG_FILE"),
        level=logging.INFO,
    )

    logger = logging.getLogger("log_analyzer")

    logger.info("Start process %s" % time.ctime())

    log_file, file_name_data = log_finder(config, logger=logger)

    try:
        if log_file is not None:
            # Copy file to TMP dir
            shutil.copyfile(
                f'{config.get("DEFAULT", "LOG_DIR")}/{log_file}',
                f'{config.get("DEFAULT", "TMP_DIR")}/{log_file}',
            )

            # Unpacking the log file
            data = gzip_unpacker(config.get("DEFAULT", "TMP_DIR"), log_file)

            # Parsing rows
            parsed_rows = log_parser(data, logger=logger)
            REPORT_RESULT = log_performer(parsed_rows, logger=logger)

            logger.info("Sorting result")
            REPORT_RESULT.sort(key=operator.itemgetter("time_sum"))

            rep_size = config.get("DEFAULT", "REPORT_SIZE")
            res = REPORT_RESULT[(-1 * int(rep_size)):]
            logger.info("Write to the html file result %s" % len(REPORT_RESULT))

            file_writer(res[::-1], config, file_name_data)

            register_writer(
                (
                    file_name_data
                    if not bool(config.getboolean("DEFAULT", "DEBUG"))
                    else False
                ),
                logger,
            )

            tmp_cleaner(config, logger=logger)
        else:
            logger.error("File parser error")

    except BaseException as e:
        logger.error("Unexpected error -> %s" % traceback.format_exc())

    logger.info("End process %s \n\n" % time.ctime())


if __name__ == "__main__":
    main()
