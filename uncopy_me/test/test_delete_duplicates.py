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

import os

import uncopy_me.test_setup
from uncopy_me.test.test_tools import EXPECTED_RESOLVED_IDENTICAL_ENTRIES
from uncopy_me.test_setup import \
    relocate_path_list, gather_deleted_files, CHECK_DIRS, INDEX_DIRS
from uncopy_me.uncopy_handler import UncopyHandler

from uncopy_me.test.fixtures import *

def check_files_exists(p_deleted_files, p_root_dir):
    resource_root_dir = uncopy_me.test_setup.get_resource_path("pictures")
    for root, dirs, files in os.walk(resource_root_dir):
        rel_path = root[len(resource_root_dir) + 1:]

        for file in files:
            path = os.path.join(p_root_dir, rel_path, file)

            if path in p_deleted_files:
                assert not os.path.exists(path)

            else:
                assert os.path.exists(path)


def test_delete_resoved_identical_entries(default_uncopy_handler: UncopyHandler, local_picture_tree_copy):
    target_dir = os.path.join(local_picture_tree_copy, "pictures")
    check_files_exists(p_deleted_files=[], p_root_dir=target_dir)

    relocated_index_dirs = relocate_path_list(INDEX_DIRS, local_picture_tree_copy)
    default_uncopy_handler.index_directories(relocated_index_dirs)

    relocated_check_dirs = relocate_path_list(CHECK_DIRS, local_picture_tree_copy)
    resolved_entries = default_uncopy_handler.check_directories(relocated_check_dirs, p_similar=False)
    default_uncopy_handler.delete_resolved_entries(p_resolved_entries=resolved_entries)

    deleted_files = relocate_path_list(gather_deleted_files(p_dict=EXPECTED_RESOLVED_IDENTICAL_ENTRIES),
                                       local_picture_tree_copy)

    check_files_exists(p_deleted_files=deleted_files, p_root_dir=target_dir)
