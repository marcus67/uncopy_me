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

import sys
import tempfile

from uncopy_me import argument_parser
from uncopy_me import uncopy_handler
from uncopy_me import yaml_config
from uncopy_me import logging_tools
from uncopy_me import test_setup

DEFAULT_USER_CONFIG_FILENAME = ".config/uncopy_me/uncopy_me.yaml"


def main(p_args=None):

    parser = argument_parser.get_argument_parser()
    arguments = parser.parse_args(args=p_args)

    logger = logging_tools.start_loggging(p_loglevel=arguments.log_level)

    try:
        if arguments.use_test_setup:
            logger.info("Using test setup...")
            config = test_setup.default_config(logger=logger)

            with tempfile.TemporaryDirectory() as target_dir:
                test_setup.local_picture_tree_copy(p_logger=logger, p_target_dir=target_dir)

                with tempfile.TemporaryDirectory() as cache_directory:
                    handler = test_setup.default_uncopy_handler(logger=logger, default_config=config,
                                                                p_args=arguments, p_base_directory=target_dir,
                                                                p_cache_directory=cache_directory)
                    result = handler.run()

        else:
            config = yaml_config.YamlConfig(p_logger=logger)

            yaml_config.read_user_config_file(p_config=config,
                                              p_user_filename=DEFAULT_USER_CONFIG_FILENAME,
                                              p_filename=arguments.config_file)

            handler = uncopy_handler.UncopyHandler(p_logger=logger, p_args=arguments, p_config=config)
            result = handler.run()

    except yaml_config.ConfigurationException as e:
        fmt = "Error in configuration: {msg}"
        logger.error(fmt.format(msg=str(e)))
        result = 2

    except (NameError, IndexError, TypeError, KeyError, AttributeError) as e:
        fmt = "Exception: {msg}"
        logger.exception(fmt.format(msg=str(e)))
        result = 3

    except Exception as e:
        fmt = "General exception of type {type}: {msg}"
        logger.error(fmt.format(type=type(e), msg=str(e)))
        result = 4

    return result


if __name__ == '__main__':
    sys.exit(main())
