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

from uncopy_me import yaml_config
from uncopy_me.test.fixtures import default_config, logger

def test_read_default_config_file(default_config: yaml_config.YamlConfig):

    priorities = default_config.get_item(p_path="priorities")
    assert priorities is not None
    assert priorities[0] == "pictures/high_priority"
    assert priorities[1] == "pictures/medium_priority"
    assert priorities[2] == "pictures/low_priority"
    assert priorities[3] == "pictures/transitory"
