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

import os.path

import yaml

class ConfigurationException(Exception):
    pass


def read_user_config_file(p_config, p_user_filename, p_filename=None, p_must_exists=False):

    if p_filename is not None and os.path.exists(p_filename):
        p_config.read_config(p_filename=p_filename)

    else:
        home = os.path.expanduser("~")
        filename = os.path.join(home, p_user_filename)

        if os.path.exists(filename):
            p_config.read_config(p_filename=filename)

        elif p_must_exists:
            fmt = "Cannot find user configuration file '{filename}'"
            raise ConfigurationException(fmt.format(filename=filename))



class YamlConfig(object):


    def __init__(self, p_logger):

        self._logger = p_logger
        self._config = {}

    def read_config(self, p_filename):

        with open(p_filename, 'r') as stream:
            try:
                self._logger.info("Reading configuration file {filename}...".format(filename=p_filename))
                self._config = yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                self._logger.exception("Error while loading config: {exception}".format(exception=str(exc)))

    def get_item(self, p_path, p_type=None, p_default=None, p_raise_error=True, p_context="ROOT"):
        subtree = self._config

        for element in p_path.split("."):
            if element not in subtree:
                if p_default is None:
                    if p_raise_error:
                        fmt = "Cannot find configuration element '{element}' of path '{path}' in context '{context}'"
                        raise ConfigurationException(fmt.format(element = element, context = p_context, path = p_path))

                    else:
                        return None

                else:
                    return p_default

            subtree = subtree[element]

            if p_type == int:
                try:
                    int_value = int(subtree)

                except Exception:
                    fmt = "invalid '{value}' cannot be converted to integer for configuration path {path}"
                    raise ConfigurationException(fmt.format(value=subtree, path=p_path))

                return int_value

            return subtree

