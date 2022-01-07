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

import sqlalchemy.ext.declarative
import sqlalchemy.orm

from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Boolean
from sqlalchemy.exc import ProgrammingError

Base = sqlalchemy.ext.declarative.declarative_base()


class Picture(Base):
    __tablename__ = 'picture'

    id = Column(Integer, primary_key=True)
    filename = Column(String(1024))
    filesize = Column(Integer())
    width =  Column(Integer())
    height = Column(Integer())
    hash = Column(String(256))
    md5 = Column(String(256))



class Persistence(object):

    def __init__(self, p_url):
        self._engine = sqlalchemy.create_engine(p_url, pool_recycle=True)

        self._session = None

    def create_database(self):

        Base.metadata.create_all(self._engine)

        # See https://stackoverflow.com/questions/55921584/create-an-ordered-index-in-sqlite-db-using-sqlalchemy
        try:
            sqlalchemy.Index('picture_index_filename', Picture.filename.asc()).create(self._engine)

        except sqlalchemy.exc.OperationalError:
            pass

        try:
            sqlalchemy.Index('picture_index_hash', Picture.hash.asc()).create(self._engine)

        except sqlalchemy.exc.OperationalError:
            pass

    def get_session(self):

        if self._session is None:
            self._session = sqlalchemy.orm.sessionmaker(bind=self._engine)()

        return self._session

    def find_picture_by_filename(self, p_filename):

        session = self.get_session()
        result = session.query(Picture).filter_by(filename == p_filename)

        if not exists:
            pinfo = create_class_instance(ProcessInfo, p_initial_values=p_process_info)
            pinfo.key = p_process_info.get_key()
            session.add(pinfo)

        session.commit()
