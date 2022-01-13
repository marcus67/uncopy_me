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

INDEX_DIRS = [
  "pictures/high_priority",
  "pictures/medium_priority",
  "pictures/low_priority",
  "pictures/transitory"
]

CHECK_DIRS = [
    "pictures/to_be_checked",
]

EXPECTED_RESOLVED_IDENTICAL_ENTRIES = {
    "pictures/high_priority/subdir_1/bm01.small.jpeg" : [
        "pictures/to_be_checked/bm01.small.jpeg"
    ],
    "pictures/medium_priority/subdir_1/subsubdir_1/bm13.small.jpeg" : [
        "pictures/to_be_checked/bm13.small.jpeg"
    ]
}

EXPECTED_RESOLVED_SIMILAR_ENTRIES = {
    "pictures/high_priority/subdir_1/bm01.small.jpeg" : [
        "pictures/to_be_checked/bm01.small.jpeg"
    ],
    "pictures/medium_priority/subdir_1/subsubdir_1/bm13.small.jpeg" : [
        "pictures/to_be_checked/bm13.small.jpeg"
    ],
    "pictures/medium_priority/bm14.small.jpeg" : [
        "pictures/to_be_checked/bm14.small.similar.jpeg"
    ]
}

EXPECTED_RESOLVED_IDENTICAL_ENTRIES_WITH_PRIORITY = {
    "pictures/high_priority/subdir_1/bm06.small.jpeg" : [
        "pictures/low_priority/bm06.small.jpeg"
    ],
}

def relocate_path_list(p_list, p_prefix):
    return [ os.path.join(p_prefix, dir) for dir in p_list]

def relocate_path_dict(p_dict, p_prefix):
    return { os.path.join(p_prefix, dir):relocate_path_list(value, p_prefix) for dir, value in p_dict }

def get_resource_path(p_rel_path: str=None) -> str:
    if p_rel_path is None:
        return os.path.join(os.path.dirname(__file__), "resources")

    else:
        return os.path.join(os.path.dirname(__file__), "resources", p_rel_path)

def gather_deleted_files(p_dict):
    deleted_files = []
    for value in p_dict.values():
        deleted_files.extend(value)

    return deleted_files
