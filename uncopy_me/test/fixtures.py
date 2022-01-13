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

import os.path
import shutil
import tempfile

import pytest

from uncopy_me import uncopy_handler
from uncopy_me import argument_parser
from uncopy_me import yaml_config
from uncopy_me import logging_tools
from uncopy_me.test import test_tools

@pytest.fixture
def logger():
    return logging_tools.start_loggging(p_loglevel="DEBUG")

@pytest.fixture
def default_config(logger) -> yaml_config.YamlConfig:
    config = yaml_config.YamlConfig(p_logger=logger)
    filename = test_tools.get_resource_path("configs/default.yaml")
    config.read_config(p_filename=filename)
    return config

@pytest.fixture
def default_uncopy_handler(logger, default_config) -> uncopy_handler.UncopyHandler:

    #parser = argument_parser.get_argument_parser()
    defaults = argument_parser.default_args()
    with tempfile.TemporaryDirectory() as temporary_directory:

        defaults.cache_directory = temporary_directory
        handler = uncopy_handler.UncopyHandler(p_logger=logger, p_config=default_config,
                                               p_args=defaults)
        handler.init(p_delete_cache=True, p_cache_directory=defaults.cache_directory,
                     p_base_directory=test_tools.get_resource_path())
        yield handler

        handler.destroy()

@pytest.fixture
def local_picture_tree_copy(logger):

    with tempfile.TemporaryDirectory() as t:

        target_dir = os.path.join(t, "pictures")
        shutil.copytree(test_tools.get_resource_path("pictures"), target_dir)
        yield t
