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

import semantic_version
import validators

from uncopy_me import git
from uncopy_me import settings

GIT_KEYS = [
    "commit_id",
    "branch",
    "author_name",
    "author_email"
]

SETTINGS_KEYS = {
    "name": "STRING",
    "url": "URL",
    "version": "VERSION",
    "description": "STRING",
    "author": "AUTHOR",
    "author_email": "EMAIL",
}


def test_git():
    for key in GIT_KEYS:
        assert key in git.git_metadata


def test_settings():
    all_keys = {}
    all_keys.update(settings.settings)
    all_keys.update(settings.extended_settings)

    for key, type in SETTINGS_KEYS.items():
        if type == "STRING":
            assert key in all_keys

        elif type == "URL":
            assert validators.url(all_keys[key])

        elif type == "EMAIL":
            assert validators.email(all_keys[key])

        elif type == "VERSION":
            _v = semantic_version.Version(all_keys[key])

        elif type == "AUTHOR":
            assert "Marcus Rickert" == all_keys[key]
