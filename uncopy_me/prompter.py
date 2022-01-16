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

ANSWER_YES = 0
ANSWER_NO = 1
ANSWER_NONE = 2
ANSWER_ALL = 3
ANSWER_BREAK = 4

ANSWERS = "ynolb"

from uncopy_me import logging_tools

class BasePrompter:

    def __init__(self, p_logger):
        self._logger = p_logger
        self._count = None

    def prompt_start(self, p_count):
        self._count = p_count

        msg = "Prompting for the deletion of {count} files..."
        self._logger.info(msg.format(count=self._count))

    def prompt_end(self):
        pass

    def prompt_file(self, p_index, p_filename):

        msg = "{index} of {count}: Delete file {filename}?\n(y)es,(n)o[default],n(o)ne,a(l)l a(b)ort:"

        while True:
            #logging_tools.flush()
            self._logger.info(msg.format(index=p_index, count=self._count, filename=p_filename))
            answer = input()

            if len(answer) != 1:
                self._logger.warning("Only respond by typing single letter.\n")

            elif answer.lower() not in ANSWERS:
                fmt = "Use one of the letters '{letters}'.\n"
                self._logger.warning(fmt.format(letters=ANSWERS))

            else:
                break

        return ANSWERS.index(answer.lower())
