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
ResolvedEntry = collections.namedtuple("ResolvedEntry", "keep discard type")

TYPE_IDENTICAL = 1
TYPE_SIMILAR = 2

class UncopyHandler(object):

    def __init__(self, p_logger, p_config, p_args=None):

        self._logger = p_logger
        self._args = p_args
        self._config = p_config
        self._p : persistence.Persistence = None
        self._priorities = []
        self._priority_patterns = []
        self._home_directory = os.path.expanduser(HOME_DIR)

    def destroy(self):
        if self._p is not None:
            self._p.destroy()

    def replace_home_directory(self, p_filename):

        if len(p_filename) > 0 and p_filename[0] == HOME_DIR:
            return self._home_directory + p_filename[1:]

        else:
            return p_filename


    def evaluate_config(self, p_base_directory=None):
        self._priorities = self._config.get_item(p_path="priorities", p_default=[])

        if p_base_directory is not None:
            self._priorities = [ os.path.join(p_base_directory, dir) for dir in self._priorities ]

        try:
            self._priority_patterns = sorted([PriorityEntry(ind, priority,
                                                            re.compile(os.path.abspath(self.replace_home_directory(priority))))
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
        new_picture.width, new_picture.height = image.size

        new_picture.filename = p_filename
        with open(p_filename, "rb") as file_in:
            image_as_string = file_in.read()
            new_picture.md5 = hashlib.md5(image_as_string).hexdigest()
            new_picture.filesize = len(image_as_string)

        return new_picture

    def evaluate_picture_list(self, p_picture_list):

        session = self._p.get_session()
        errors = 0

        new_pictures = []
        existing_pictures = []

        for filename in p_picture_list:
            existing_picture = session.query(persistence.Picture).filter_by(filename=filename).first()

            if existing_picture is None:
                try:
                    kind = filetype.guess_mime(filename)

                    if kind in RELEVANT_MIME_TYPES:
                        new_picture = self.evaluate_new_picture(p_filename=filename)
                        new_pictures.append(new_picture)

                except Exception as e:
                    fmt = "Exception while evaluating picture '{filename}': {exception}"
                    self._logger.error(fmt.format(filename=filename, exception=str(e)))
                    errors += 1

            else:
                existing_pictures.append(existing_picture)

        session.commit()
        return (existing_pictures, new_pictures, errors)


    def index_picture_list(self, p_picture_list):

        fmt = "Merging {number} images into cache..."
        self._logger.info(fmt.format(number=len(p_picture_list)))

        existing_pictures, new_pictures, errors = self.evaluate_picture_list(p_picture_list=p_picture_list)

        session = self._p.get_session()
        images_added = 0

        for new_picture in new_pictures:
            session.add(new_picture)
            images_added = images_added + 1

            if images_added % self._args.commit_block_size == 0:
                fmt = "Images newly added: {added}..."
                self._logger.info(fmt.format(added=images_added))
                session.commit()

        fmt = "Images newly added: {added} - with errors: {errors}."
        self._logger.info(fmt.format(added=images_added, errors=errors))
        session.commit()

    def check_picture_list(self, p_picture_list, p_similar):

        fmt = "Checking {number} images against the cache..."
        self._logger.info(fmt.format(number=len(p_picture_list)))

        existing_pictures, new_pictures, errors = self.evaluate_picture_list(p_picture_list=p_picture_list)

        if len(existing_pictures) > 0:
            fmt = "Ignoring {count} images since they are also the cache!"
            self._logger.warning(fmt.format(count=len(existing_pictures)))

        all_pictures = self.get_all_pictures_in_cache()

        similar_hash_bins, identical_hash_bins = self.get_hash_bins(p_picture_list=all_pictures)

        resolved_entries = []

        for pic in new_pictures:
            if pic.md5 in identical_hash_bins:
                entry = ResolvedEntry(keep=identical_hash_bins.get(pic.md5), discard=[pic], type=TYPE_IDENTICAL)
                resolved_entries.append(entry)
            elif pic.hash in similar_hash_bins and p_similar:
                entry = ResolvedEntry(keep=similar_hash_bins.get(pic.hash), discard=[pic], type=TYPE_SIMILAR)
                resolved_entries.append(entry)


        return resolved_entries


    def scan_directories(self, p_directory_list):

        full_file_list = []

        f_tool = filetool.FileTool(p_logger=self._logger,
                                   p_exclude_patterns=self._args.exclude_patterns)

        fmt = "Scanning {number} directories..."
        self._logger.info(fmt.format(number=len(p_directory_list)))

        for directory in p_directory_list:
            effective_directory = os.path.abspath(directory)
            file_list = f_tool.scan_directory(p_directory=effective_directory, p_recursive=self._args.index_recursively)
            full_file_list.extend(file_list)

        return full_file_list

    def index_directories(self, p_directories):

        full_file_list = self.scan_directories(p_directory_list=p_directories)
        self.index_picture_list(p_picture_list=full_file_list)

    def check_directories(self, p_directories, p_similar):

        full_file_list = self.scan_directories(p_directory_list=p_directories)
        return self.check_picture_list(p_picture_list=full_file_list, p_similar=p_similar)

    def get_hash_bins(self, p_picture_list):

        similar_hash_sets = {}
        identical_hash_sets = {}

        for pic in p_picture_list:
            identical_hash_bin = identical_hash_sets.get(pic.md5)

            if identical_hash_bin is None:
                identical_hash_sets[pic.md5] = [pic]

            else:
                identical_hash_bin.append(pic)

            similar_hash_bin = similar_hash_sets.get(pic.hash)

            if similar_hash_bin is None:
                similar_hash_sets[pic.hash] = [ pic ]

            else:
                similar_hash_bin.append(pic)


        return (similar_hash_sets, identical_hash_sets)

    def get_duplicate_hash_sets(self, p_picture_list):

        similar_hash_sets, identical_hash_sets = self.get_hash_bins(p_picture_list=p_picture_list)
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


        return  ( effective_similar_hashes,
                  { identical_hash:pics for (identical_hash, pics) in identical_hash_sets.items() if len(pics) > 1 }
                )

    def resolve_priorities(self, p_hash_sets, p_type):


        resolved_entries = []

        for hash, pics in p_hash_sets.items():
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

                resolved_entry = ResolvedEntry(keep=[keep], discard=discard, type=p_type)
                resolved_entries.append(resolved_entry)

        return resolved_entries


    def get_all_pictures_in_cache(self):

        session = self._p.get_session()
        pics = list(session.query(persistence.Picture))
        session.commit()
        return pics


    def find_duplicates(self):

        all_pictures = self.get_all_pictures_in_cache()
        similar_hash_sets, identical_hash_sets = self.get_duplicate_hash_sets(p_picture_list=all_pictures)

        fmt = "\nFound {identical_number} identical image(s) and "\
              "additional {similar_number} similar image(s) in more than one location"
        self._logger.info(fmt.format(similar_number=len(similar_hash_sets),
                                     identical_number=len(identical_hash_sets)))

        for (md5, pics) in identical_hash_sets.items():

            fmt = "    Pictures with MD5 hash {hash} was found in {number} locations:"
            self._logger.info(fmt.format(hash=md5, number=len(pics)))

            for pic in pics:
                fmt = "        location:{filename}"
                self._logger.info(fmt.format(filename=pic.filename))

        if self._args.similar:
            for (hash, pics) in similar_hash_sets.items():

                fmt = "    Pictures with similarity hash {hash} was found in {number} locations:"
                self._logger.info(fmt.format(hash=hash, number=len(pics)))

                for pic in pics:
                    fmt ="        * {filename} md5={md5}"
                    self._logger.info(fmt.format(filename=pic.filename, md5=pic.md5))

    def list_resolved_entries(self, p_resolved_entries):

        fmt = "\nList of resolved {number} entries:"
        self._logger.info(fmt.format(number=len(p_resolved_entries)))

        for entry in p_resolved_entries:
            fmt = "    Picture(s) to be kept:"
            self._logger.info(fmt)

            for pic in entry.keep:
                fmt = "        * {filename}"
                self._logger.info(fmt.format(filename=pic.filename))

            fmt = "        with {type} duplicate(s) to be deleted in:"
            self._logger.info(fmt.format(type="identical" if entry.type == TYPE_IDENTICAL else "similar"))

            for pic in entry.discard:
                fmt = "        * {filename}"
                self._logger.info(fmt.format(filename=pic.filename))

    def delete_resolved_entries(self, p_resolved_entries):

        fmt = "\nDeleting {number} resolved entries..."
        self._logger.info(fmt.format(number=len(p_resolved_entries)))

        session = self._p.get_session()

        for entry in p_resolved_entries:
            for pic in entry.discard:
                fmt = "    * {filename}"
                self._logger.debug(fmt.format(filename=pic.filename))

                try:
                    session.query(persistence.Picture).filter(persistence.Picture.filename==pic.filename).delete()
                    os.unlink(pic.filename)

                except IOError as e:
                    fmt = 'IOError "{msg}" while deleting "{filename}"!'
                    self._logger.error(fmt.format(msg=str(e), filename=pic.filename))

        session.commit()

    def check_cache(self):

        session = self._p.get_session()
        count = 0

        for pic in session.query(persistence.Picture):
            if not os.path.exists(pic.filename) or not os.path.isabs(pic.filename):

                fmt = "Removing non-existing picture '{filename}' from cache..."
                self._logger.debug(fmt.format(filename=pic.filename))

                session.delete(pic)
                count = count + 1

        fmt = "Removed {count} entries from cache."
        self._logger.info(fmt.format(count=count))

        session.commit()

    def init(self, p_cache_directory, p_delete_cache=False, p_base_directory=None):

        self.evaluate_config(p_base_directory=p_base_directory)

        cache_directory = os.path.expanduser(p_cache_directory)

        if not os.path.exists(cache_directory):
            os.mkdir(cache_directory)

        db_filename = os.path.join(cache_directory, DB_FILENAME)
        url = 'sqlite:///{filename}'.format(filename=db_filename)

        if p_delete_cache and os.path.exists(db_filename):
            fmt = "Deleting cache at {filename}..."
            self._logger.info(fmt.format(filename=db_filename))
            os.unlink(db_filename)

        self._p = persistence.Persistence(p_url=url)
        self._p.create_database()


    def run(self):

        result = 0

        self.init(p_cache_directory=self._args.cache_directory)

        if len(self._args.index_directories) > 0:
            self.index_directories(p_directories=self._args.index_directories)

        if self._args.check_cache:
            self.check_cache()

        resolved_entries = []

        if len(self._args.check_directories) > 0:
            resolved_entries.extend(self.check_directories(p_directories=self._args.check_directories,
                                                           p_similar=self._args.similar))

        if self._args.find_duplicates:
            self.find_duplicates()

            if self._args.use_priorities:
                resolved_entries.extend(self.resolve_priorities_in_cache(p_similar=self._args.similar))

        if len(resolved_entries) > 0:
            self.list_resolved_entries(p_resolved_entries=resolved_entries)

            if self._args.delete:
                self.delete_resolved_entries(p_resolved_entries=resolved_entries)

            else:
                fmt = "\nResolved entries were only listed. Use option '--delete' to delete them."
                self._logger.info(fmt)



        return result

    def resolve_priorities_in_cache(self, p_similar):

        all_pictures = self.get_all_pictures_in_cache()
        similar_hash_sets, identical_hash_sets = self.get_duplicate_hash_sets(p_picture_list=all_pictures)

        if p_similar:
            return self.resolve_priorities(p_hash_sets=similar_hash_sets, p_type=TYPE_SIMILAR)

        else:
            return self.resolve_priorities(p_hash_sets=identical_hash_sets, p_type=TYPE_IDENTICAL)
