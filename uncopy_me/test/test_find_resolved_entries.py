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

from uncopy_me.test.fixtures import *
from uncopy_me.uncopy_handler import UncopyHandler
from uncopy_me.test.test_tools import get_resource_path, CHECK_DIRS, INDEX_DIRS, EXPECTED_RESOLVED_ENTRIES

def test_find_resolved_entries(default_uncopy_handler:UncopyHandler):

    default_uncopy_handler.index_directories(INDEX_DIRS)
    resolved_entries = default_uncopy_handler.check_directories(CHECK_DIRS)

    assert resolved_entries is not None
    assert len(resolved_entries) == 2

    resolved_entries_map = { entry.keep[0].filename : entry for entry in resolved_entries }

    for expected_keep_pic_file, expected_delete_list in EXPECTED_RESOLVED_ENTRIES.items():
        full_name = get_resource_path(p_rel_path=expected_keep_pic_file)

        assert full_name in resolved_entries_map

        resolved_entry = resolved_entries_map[full_name]

        assert len(expected_delete_list) == len(resolved_entry.discard)

        resolved_delete_list = [ pic.filename for pic in resolved_entry.discard ]

        for pic_filename in expected_delete_list:
            full_name = get_resource_path(p_rel_path=pic_filename)

            assert full_name in resolved_delete_list
