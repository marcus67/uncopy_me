# -*- coding: utf-8 -*-

# Copyright (C) 2020-2022  Marcus Rickert
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

import re
import os
import os.path

RELEVANT_FILE_EXTENSIONS = re.compile('^.+\.(jpeg|jpg|png|JPEG|JPG|PNG)$')

class FileTool(object):

    def __init__(self, p_logger, p_exclude_patterns):

        self._logger = p_logger
        self._compiled_patterns = [ re.compile(pattern) for pattern in p_exclude_patterns ]


    def is_excluded(self, p_filename):

        for compiled_pattern in self._compiled_patterns:
            if compiled_pattern.match(p_filename):
                return True

        return False

    def scan_directory(self, p_directory, p_recursive=True):

        file_list = []

        images_in_dir = 0

        for (dirpath, _dirnames, filenames) in os.walk(p_directory):
            images_in_dir = 0

            for filename in filenames:
                if RELEVANT_FILE_EXTENSIONS.match(filename):
                    try:
                        if not self.is_excluded(p_filename=filename):
                            full_path = os.path.join(dirpath, filename)

                            fmt = "Found image {full_path}"
                            self._logger.debug(fmt.format(full_path=full_path))

                            file_list.append(full_path)
                            images_in_dir += 1

                    except IOError as e:
                        fmt = "Exception while scanning file '{filename}' in directory '{dir}': {exception}"
                        self._logger.error(fmt.format(filename=filename, dir=dirpath, exception=str(e)))

            fmt = "Found {number} images in {dir}"
            self._logger.info(fmt.format(number=images_in_dir, dir=dirpath))

            if not p_recursive:
                break

        if images_in_dir != len(file_list):
            fmt = "Found {number} images{mode} in {directory}"
            self._logger.info(fmt.format(number=len(file_list),
                                         directory=p_directory,
                                         mode=" recursively" if p_recursive else ""))

        return file_list



