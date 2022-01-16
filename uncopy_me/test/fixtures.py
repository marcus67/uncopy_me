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
import tempfile

import pytest

from uncopy_me import uncopy_handler
from uncopy_me import yaml_config
from uncopy_me import logging_tools
from uncopy_me import test_setup

@pytest.fixture
def logger():
    return logging_tools.start_loggging(p_loglevel="DEBUG")

@pytest.fixture
def default_config(logger) -> yaml_config.YamlConfig:
    return test_setup.default_config(logger)

@pytest.fixture
def default_uncopy_handler(logger, default_config) -> uncopy_handler.UncopyHandler:
    with tempfile.TemporaryDirectory() as cache_directory:
        yield test_setup.default_uncopy_handler(logger, default_config, p_cache_directory=cache_directory)

@pytest.fixture
def local_picture_tree_copy(logger):
    with tempfile.TemporaryDirectory() as target_directory:
        test_setup.local_picture_tree_copy(logger, p_target_dir=target_directory)
        yield target_directory
