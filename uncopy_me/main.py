# -*- coding: utf-8 -*-

# Copyright (C) 2020  Marcus Rickert
#
# See https://github.com/marcus67/uncopy_me
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import argparse
import logging

from uncopy_me import uncopy_handler
from uncopy_me import yaml_config

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_USER_CONFIG_FILENAME = ".config/uncopy_me/uncopy_me.yaml"
LOGGING_NAME = "uncopy_me"

logger = None

DEFAULT_COMMIT_BLOCK_SIZE = 1000

def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scan-directories', nargs='*', dest='scan_directories', default=[],
                        help='directories to be parsed')
    parser.add_argument('--cache-directory', dest='cache_directory', default="~/.cache/uncopy_me",
                        help='directory to be used for cache files')
    parser.add_argument('--config-file', dest='config_file',
                        help='configuration file')
    parser.add_argument('--commit-block-size', dest='commit_block_size', default=DEFAULT_COMMIT_BLOCK_SIZE,
                        help='number of cache operations between commits')
    parser.add_argument('--scan-recursively', dest='scan_recursively', default=True,
                        help='scan recursively into directories')
    parser.add_argument('--find-duplicates', dest='find_duplicates', action="store_true",
                        help='find duplicates in cache')
    parser.add_argument('--exclude-patterns', nargs='*', dest='exclude_patterns', default = [],
                        help='set exclude pattern for scanned picture names')
    parser.add_argument('--loglevel', dest='log_level', default=DEFAULT_LOG_LEVEL,
                        help='logging level', choices=['WARN', 'INFO', 'DEBUG'])
    parser.add_argument('--delete', dest='delete', action="store_true",
                        help='actually delete pictures regarded as duplicates (otherwise duplicates are only listed)')
    parser.add_argument('--check-cache', dest='check_cache', action="store_true",
                        help='removes cache entries referring to non-existing pictures')
    parser.add_argument('--similar', dest='similar', action="store_true",
                        help='use similarity hash for find duplicates '
                             '(otherwise only identical pictures are regarded as duplicates)')
    parser.add_argument('--use-priorities', dest='use_priorities', action="store_true",
                        help='use priority declarations to determine which duplicates are deleted')
    return parser

def start_loggging(p_loglevel):

    global logger

    root_logger = logging.getLogger()
    root_logger.handlers = []

    handler = logging.StreamHandler()
    handler.setLevel(DEFAULT_LOG_LEVEL)
    root_logger.addHandler(handler)

    logger = logging.getLogger(LOGGING_NAME)
    logger.setLevel(DEFAULT_LOG_LEVEL)

    if p_loglevel is not None:
        logging_level = logging.getLevelName(p_loglevel)

        if p_loglevel != DEFAULT_LOG_LEVEL:

            fmt = "Changing logging level to {level}"
            logger.info(fmt.format(level=p_loglevel))

            handler.setLevel(logging_level)
            root_logger.setLevel(logging_level)
            logger.setLevel(logging_level)


def main():

    global logger

    result = 0

    parser = get_argument_parser()
    arguments = parser.parse_args()

    start_loggging(p_loglevel=arguments.log_level)

    try:
        config = yaml_config.YamlConfig(p_logger=logger)

        yaml_config.read_user_config_file(p_config=config,
                                          p_user_filename=DEFAULT_USER_CONFIG_FILENAME,
                                          p_filename=arguments.config_file)

        handler = uncopy_handler.UncopyHandler(p_logger=logger, p_args=arguments, p_config=config)
        result = handler.run()

    except yaml_config.ConfigurationException as e:
        fmt = "Error in configuration: {msg}"
        logger.error(fmt.format(msg=str(e)))
        result = 2

    except (NameError, IndexError, TypeError) as e:
        fmt = "Exception: {msg}"
        logger.exception(fmt.format(msg=str(e)))
        result = 3


    except Exception as e:
        fmt = "General exception of type {type}: {msg}"
        logger.error(fmt.format(type=type(e), msg=str(e)))
        result = 3

    return result


if __name__ == '__main__':
    exit(main())
