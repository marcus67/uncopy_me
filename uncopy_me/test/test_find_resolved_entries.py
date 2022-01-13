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
from uncopy_me.test.test_tools import \
    get_resource_path, CHECK_DIRS, INDEX_DIRS, \
    EXPECTED_RESOLVED_IDENTICAL_ENTRIES, EXPECTED_RESOLVED_SIMILAR_ENTRIES, \
    EXPECTED_RESOLVED_IDENTICAL_ENTRIES_WITH_PRIORITY

def compare_resolved_entries(p_expected_resolved_entries, p_resolved_entries):

    assert p_resolved_entries is not None
    assert len(p_resolved_entries) == len(p_expected_resolved_entries)

    resolved_entries_map = { entry.keep[0].filename : entry for entry in p_resolved_entries }

    for expected_keep_pic_file, expected_delete_list in p_expected_resolved_entries.items():
        full_name = get_resource_path(p_rel_path=expected_keep_pic_file)

        assert full_name in resolved_entries_map

        resolved_entry = resolved_entries_map[full_name]

        assert len(expected_delete_list) == len(resolved_entry.discard)

        resolved_delete_list = [ pic.filename for pic in resolved_entry.discard ]

        for pic_filename in expected_delete_list:
            full_name = get_resource_path(p_rel_path=pic_filename)

            assert full_name in resolved_delete_list

def test_find_resolved_identical_entries(default_uncopy_handler:UncopyHandler):

    relocated_index_dirs = test_tools.relocate_path_list(INDEX_DIRS, test_tools.get_resource_path())
    relocated_check_dirs = test_tools.relocate_path_list(CHECK_DIRS, test_tools.get_resource_path())
    default_uncopy_handler.index_directories(relocated_index_dirs)
    resolved_entries = default_uncopy_handler.check_directories(relocated_check_dirs, p_similar=False)

    compare_resolved_entries(p_expected_resolved_entries=EXPECTED_RESOLVED_IDENTICAL_ENTRIES, p_resolved_entries=resolved_entries)

def test_find_resolved_similar_entries(default_uncopy_handler:UncopyHandler):

    relocated_index_dirs = test_tools.relocate_path_list(INDEX_DIRS, test_tools.get_resource_path())
    relocated_check_dirs = test_tools.relocate_path_list(CHECK_DIRS, test_tools.get_resource_path())
    default_uncopy_handler.index_directories(relocated_index_dirs)
    resolved_entries = default_uncopy_handler.check_directories(relocated_check_dirs, p_similar=True)

    compare_resolved_entries(p_expected_resolved_entries=EXPECTED_RESOLVED_SIMILAR_ENTRIES, p_resolved_entries=resolved_entries)

def test_find_resolved_identitical_entries_with_priorities(default_uncopy_handler:UncopyHandler):

    relocated_index_dirs = test_tools.relocate_path_list(INDEX_DIRS, test_tools.get_resource_path())
    relocated_check_dirs = test_tools.relocate_path_list(CHECK_DIRS, test_tools.get_resource_path())
    default_uncopy_handler.index_directories(relocated_index_dirs)
    resolved_entries = default_uncopy_handler.resolve_priorities_in_cache(p_similar=False)

    compare_resolved_entries(p_expected_resolved_entries=EXPECTED_RESOLVED_IDENTICAL_ENTRIES_WITH_PRIORITY,
                             p_resolved_entries=resolved_entries)

