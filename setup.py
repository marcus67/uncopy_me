# -*- coding: utf-8 -*-

#    Copyright (C) 202ß-2022  Marcus Rickert
#
#    See https://github.com/marcus67/uncopy_me
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os.path

from setuptools import setup

import uncopy_me.settings

# See https://stackoverflow.com/questions/26900328/install-dependencies-from-setup-py

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'requirements.txt')) as f:
    install_requires = f.read().splitlines()

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup_params = {
    # standard setup configuration

    "install_requires": install_requires,

    "packages": ['uncopy_me', 'uncopy_me.test'],

    "include_package_data": True,

    "scripts": [
        "uncopy-me",
        "run-uncopy-me-tests",
    ],

    "long_description_content_type" : 'text/markdown',
    "long_description": long_description,
}

extended_setup_params = {
    # additional setup configuration used by CI stages

    "ci_pip_dependencies": [ "python_base_app" ],

    # technical name used for e.g. directories, PIP-package, and users
    "build_debian_package" : False,
    "build_pypi_package": True,
#    "publish_pypi_package": {'release': ('https://upload.pypi.org/legacy/', 'PYPI_API_TOKEN'),
#                             'master': ('https://test.pypi.org/legacy/', 'TEST_PYPI_API_TOKEN')},
    "analyze": True,

    "run_test_suite": "run-uncopy-me-tests",
    "run_test_suite_no_venv": "run-uncopy-me-tests",
}

setup_params.update(uncopy_me.settings.settings)
extended_setup_params.update(uncopy_me.settings.extended_settings)
extended_setup_params.update(setup_params)

if __name__ == '__main__':
    setup(**setup_params)
