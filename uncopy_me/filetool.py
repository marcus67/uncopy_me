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

import os
import os.path

import filetype

RELEVANT_MIME_TYPES = [
    'image/jpeg',
    'image/png'
]

# See https://pypi.org/project/filetype/

class FileTool(object):

    def __init__(self, p_logger):

        self._logger = p_logger

    def scan_directory(self, p_directory, p_recursive=True):

        file_list = []

        for (dirpath, _dirnames, filenames) in os.walk(p_directory):

            for filename in filenames:
                full_path = os.path.join(dirpath, filename)

                kind = filetype.guess_mime(full_path)

                if kind in RELEVANT_MIME_TYPES:

                    fmt = "Found image {full_path}"
                    self._logger.debug(fmt.format(full_path=full_path))

                    file_list.append(full_path)

            if not p_directory:
                break

        fmt = "Found {number} images{mode} in {directory}"
        self._logger.info(fmt.format(number=len(file_list),
                                     directory=p_directory,
                                     mode=" recursively" if p_recursive else ""))

        return file_list



