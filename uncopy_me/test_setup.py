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

from uncopy_me import yaml_config
from uncopy_me import argument_parser
from uncopy_me import uncopy_handler
from uncopy_me import argument_parser

INDEX_DIRS = [
  "pictures/high_priority",
  "pictures/medium_priority",
  "pictures/low_priority",
  "pictures/transitory"
]

CHECK_DIRS = [
    "pictures/to_be_checked",
]


def default_config(logger) -> yaml_config.YamlConfig:
    config = yaml_config.YamlConfig(p_logger=logger)
    filename = get_resource_path("configs/default.yaml")
    config.read_config(p_filename=filename)
    return config

def default_uncopy_handler(logger, default_config, p_cache_directory, p_args=None, p_base_directory=None) -> uncopy_handler.UncopyHandler:

    if p_args is None:
        p_args = argument_parser.default_args()

    if p_base_directory is None:
        p_base_directory = get_resource_path()

    fmt = "Using cache directory {dir}..."
    logger.info(fmt.format(dir=p_cache_directory))

    if p_base_directory is not None:
        p_args.index_directories = relocate_path_list(p_list=INDEX_DIRS, p_prefix=p_base_directory)
        p_args.check_directories = relocate_path_list(p_list=CHECK_DIRS, p_prefix=p_base_directory)

    handler = uncopy_handler.UncopyHandler(p_logger=logger, p_config=default_config, p_args=p_args)
    handler.init(p_delete_cache=True, p_cache_directory=p_cache_directory,
                 p_base_directory=p_base_directory)

    return handler


def local_picture_tree_copy(p_logger, p_target_dir):
        target_dir = os.path.join(p_target_dir, "pictures")
        shutil.copytree(get_resource_path("pictures"), target_dir)

def get_resource_path(p_rel_path: str=None) -> str:
    if p_rel_path is None:
        return os.path.join(os.path.dirname(__file__), "test/resources")

    else:
        return os.path.join(os.path.dirname(__file__), "test/resources", p_rel_path)

def relocate_path_list(p_list, p_prefix):
    return [ os.path.join(p_prefix, dir) for dir in p_list]

def relocate_path_dict(p_dict, p_prefix):
    return { os.path.join(p_prefix, dir):relocate_path_list(value, p_prefix) for dir, value in p_dict }


def gather_deleted_files(p_dict):
    deleted_files = []
    for value in p_dict.values():
        deleted_files.extend(value)

    return deleted_files
