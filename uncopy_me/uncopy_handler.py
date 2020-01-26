# -*- coding: utf-8 -*-

# Copyright (C) 2020  Marcus Rickert
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
import hashlib
import re
import collections

import PIL
import imagehash

# See https://pypi.org/project/filetype/
import filetype

from uncopy_me import persistence
from uncopy_me import filetool
from uncopy_me import yaml_config

DB_FILENAME = "uncopy-sqlite3.db"

HOME_DIR = "~"

RELEVANT_MIME_TYPES = [
    'image/jpeg',
    'image/png'
]

PriorityEntry = collections.namedtuple("PriorityEntry", "priority pattern compiled_pattern")

ResolvedEntry = collections.namedtuple("ResolvedEntry", "keep discard")

class UncopyHandler(object):

    def __init__(self, p_logger, p_args, p_config):

        self._logger = p_logger
        self._args = p_args
        self._config = p_config
        self._p = None
        self._priorities = []
        self._priority_patterns = []
        self._home_directory = os.path.expanduser(HOME_DIR)

    def replace_home_directory(self, p_filename):

        if len(p_filename) > 0 and p_filename[0] == HOME_DIR:
            return self._home_directory + p_filename[1:]

        else:
            return p_filename


    def evaluate_config(self):
        self._priorities = self._config.get_item(p_path="priorities", p_default=[])

        try:
            self._priority_patterns = sorted([PriorityEntry(ind, priority,
                                                            re.compile(self.replace_home_directory(priority)))
                                              for ind, priority in enumerate(self._priorities)],
                                             key=lambda entry:-len(entry.pattern))

        except re.error as e:
            fmt = "Error {msg} while evaluating priority directories"
            raise yaml_config.ConfigurationException(fmt.format(msg=str(e)))

    def evaluate_new_picture(self, p_filename):

        # See https://realpython.com/fingerprinting-images-for-near-duplicate-detection/

        fmt = "Adding new picture {filename} to cache..."
        self._logger.debug(fmt.format(filename=p_filename))

        new_picture = persistence.Picture()

        image = PIL.Image.open(p_filename)
        new_picture.hash = str(imagehash.dhash(image))

        new_picture.filename = p_filename
        with open(p_filename, "rb") as file_in:
            new_picture.md5 = hashlib.md5(file_in.read()).hexdigest()

        return new_picture

    def scan_directories(self):

        full_file_list = []

        f_tool = filetool.FileTool(p_logger=self._logger,
                                   p_exclude_patterns=self._args.exclude_patterns)

        fmt = "Scanning {number} directories..."
        self._logger.info(fmt.format(number=len(self._args.scan_directories)))

        for directory in self._args.scan_directories:
            file_list = f_tool.scan_directory(p_directory=directory, p_recursive=self._args.scan_recursively)
            full_file_list.extend(file_list)

        session = self._p.get_session()

        fmt = "Merging {number} images into cache..."
        self._logger.info(fmt.format(number=len(full_file_list)))

        images_merged = 0
        new_images = 0
        errors = 0

        for filename in full_file_list:
            result = session.query(persistence.Picture).filter_by(filename=filename).first()
            images_merged += 1

            if result is None:
                try:
                    kind = filetype.guess_mime(filename)

                    if kind in RELEVANT_MIME_TYPES:
                        new_picture = self.evaluate_new_picture(p_filename=filename)
                        session.add(new_picture)
                        new_images += 1

                except Exception as e:
                    fmt = "Exception while evaluating new image '{filename}': {exception}"
                    self._logger.error(fmt.format(filename=filename, exception=str(e)))
                    errors += 1

            if images_merged % self._args.commit_block_size == 0:
                fmt = "Images merged/newly added/with errors: {merged}/{added}/{errors}..."
                self._logger.info(fmt.format(merged=images_merged, added=new_images, errors=errors))
                session.commit()


        fmt = "Images merged/newly added/with errors: {merged}/{added}/{errors}."
        self._logger.info(fmt.format(merged=images_merged, added=new_images, errors=errors))
        session.commit()


    def get_duplicate_hash_sets(self):

        session = self._p.get_session()
        similar_hash_sets = {}
        identical_hash_sets = {}

        for pic in session.query(persistence.Picture):
            similar_hash_bin = similar_hash_sets.get(pic.hash)

            if similar_hash_bin is None:
                similar_hash_sets[pic.hash] = [ pic ]

            else:
                similar_hash_bin.append(pic)

            identical_hash_bin = identical_hash_sets.get(pic.md5)

            if identical_hash_bin is None:
                identical_hash_sets[pic.md5] = [pic]

            else:
                identical_hash_bin.append(pic)

        effective_similar_hashes = {}

        for (similar_hash, pics) in similar_hash_sets.items():
            if len(pics) > 1:
                md5 = None
                mismatch_found = False

                for pic in pics:
                    if md5 is None:
                        md5 = pic.md5

                    else:
                        if pic.md5 != md5:
                            mismatch_found = True
                            break

                if mismatch_found:
                    effective_similar_hashes[similar_hash] = pics

        session.commit()

        return  ( effective_similar_hashes,
                  { identical_hash:pics for (identical_hash, pics) in identical_hash_sets.items() if len(pics) > 1 }
                )

    def resolve_priorities(self):
        similar_hash_sets, identical_hash_sets = self.get_duplicate_hash_sets()

        hash_sets = similar_hash_sets if self._args.similar else identical_hash_sets

        resolved_entries = []

        for hash, pics in hash_sets.items():
            priority_values = []

            for index in range(0, len(self._priority_patterns)):
                priority_values.append([])

            for pic in pics:
                for priority_entry in self._priority_patterns:
                    if priority_entry.compiled_pattern.match(pic.filename):
                        priority_values[priority_entry.priority].append(pic)
                        break

            priority_to_be_kept = None

            for index, pics in enumerate(priority_values):
                if len(pics) == 0:
                    continue

                elif len(pics) == 1:
                    if priority_to_be_kept is None:
                        priority_to_be_kept = index
                        break

            if priority_to_be_kept is not None:

                keep = priority_values[priority_to_be_kept][0]
                discard = []

                for index in range(priority_to_be_kept+1, len(priority_values)):
                    discard.extend(priority_values[index])

                resolved_entry = ResolvedEntry(keep=keep, discard=discard)
                resolved_entries.append(resolved_entry)

        return resolved_entries




    def find_duplicates(self):

        similar_hash_sets, identical_hash_sets = self.get_duplicate_hash_sets()

        fmt = "Found {identical_number} identical image(s) and "\
              "additional {similar_number} similar image(s) in more than one location"
        self._logger.info(fmt.format(similar_number=len(similar_hash_sets),
                                     identical_number=len(identical_hash_sets)))

        for (md5, pics) in identical_hash_sets.items():

            fmt = "Pictures with MD5 hash {hash} was found in {number} locations:"
            self._logger.info(fmt.format(hash=md5, number=len(pics)))

            for pic in pics:
                fmt = "   location:{filename}"
                self._logger.info(fmt.format(filename=pic.filename))

        if self._args.similar:
            for (hash, pics) in similar_hash_sets.items():

                fmt = "Additional pictures with similarity hash {hash} was found in {number} locations:"
                self._logger.info(fmt.format(hash=hash, number=len(pics)))

                for pic in pics:
                    fmt ="   location:{filename} md5={md5}"
                    self._logger.info(fmt.format(filename=pic.filename, md5=pic.md5))

    def list_resolved_entries(self, p_resolved_entries):

        for entry in p_resolved_entries:
            fmt = "Picture {filename} will be kept with duplicates to be deleted in:"
            self._logger.info(fmt.format(filename=entry.keep.filename))

            for pic in entry.discard:
                fmt = "* {filename}"
                self._logger.info(fmt.format(filename=pic.filename))


    def run(self):

        result = 0

        self.evaluate_config()

        cache_directory = os.path.expanduser(self._args.cache_directory)

        if not os.path.exists(cache_directory):
            os.mkdir(cache_directory)

        db_filename = os.path.join(cache_directory, DB_FILENAME)
        url = 'sqlite:///{filename}'.format(filename=db_filename)


        self._p = persistence.Persistence(p_url=url)
        self._p.create_database()
        
        if len(self._args.scan_directories) > 0:
            self.scan_directories()

        if self._args.find_duplicates:
            self.find_duplicates()

            if self._args.use_priorities:
                resolved_entries = self.resolve_priorities()

                self.list_resolved_entries(p_resolved_entries=resolved_entries)

        return result