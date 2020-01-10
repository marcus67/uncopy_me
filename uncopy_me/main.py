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
import os.path

from uncopy_me import persistence
from uncopy_me import filetool

DEFAULT_LOG_LEVEL = "INFO"
LOGGING_NAME = "uncopy_me"

DB_FILENAME = "uncopy-sqlite3.db"

logger = None


class UncopyMe(object):

    def __init__(self, p_logger, p_args):

        self._logger = p_logger
        self._args = p_args
        self._p = None

        
    def scan_directories(self):

        full_file_list = []

        f_tool = filetool.FileTool(p_logger=logger)

        for directory in self._args.scan_directories:
            file_list = f_tool.scan_directory(p_directory=directory, p_recursive=self._args.scan_recursively)
            full_file_list.extend(file_list)

        session = self._p.get_session()

        for filename in full_file_list:
            result = session.query(persistence.Picture).filter_by(filename=filename).first()

            if result is None:

                fmt = "Adding new picture {filename} to cache..."
                self._logger.debug(fmt.format(filename=filename))

                new_picture = persistence.Picture()
                new_picture.filename = filename
                session.add(new_picture)

        session.commit()


    def run(self):

        result = 0

        cache_directory = os.path.expanduser(self._args.cache_directory)

        if not os.path.exists(cache_directory):
            os.mkdir(cache_directory)

        db_filename = os.path.join(cache_directory, DB_FILENAME)
        url = 'sqlite:///{filename}'.format(filename=db_filename)

        self._p = persistence.Persistence(p_url=url)
        self._p.create_database()
        
        if len(self._args.scan_directories) > 0:
            self.scan_directories()

        return result

def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scan-directories', nargs='*', dest='scan_directories', default=[],
                        help='directories to be parsed')
    parser.add_argument('--cache-directory', dest='cache_directory', default="~/.cache/uncopy_me",
                        help='directory to be used for cache files')
    parser.add_argument('--scan-recursively', dest='scan_recursively', default=True,
                        help='scan recursively into directories')
    parser.add_argument('--loglevel', dest='log_level', default=DEFAULT_LOG_LEVEL,
                        help='logging level', choices=['WARN', 'INFO', 'DEBUG'])

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

    uncopy_me = UncopyMe(p_logger=logger, p_args=arguments)

    result = uncopy_me.run()

    return result


if __name__ == '__main__':
    exit(main())
