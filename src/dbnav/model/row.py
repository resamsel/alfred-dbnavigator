# -*- coding: utf-8 -*-
#
# Copyright © 2014 René Samselnig
#
# This file is part of Database Navigator.
#
# Database Navigator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Database Navigator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Database Navigator.  If not, see <http://www.gnu.org/licenses/>.
#

import logging

from dbnav.model.baseitem import BaseItem
from dbnav.formatter import Formatter
from dbnav.jsonable import as_json, from_json

logger = logging.getLogger(__name__)


def val(row, column):
    # colname = '%s_title' % column
    # if colname in row.row:
    #     return '%s (%s)' % (row.row[colname], row.row[column])
    return row[column]


def primary_key_or_first_column(table):
    column = table.primary_key
    if not column:
        column = table.column(0).name
    return column


class Row(BaseItem):
    """A table row from the database"""

    def __init__(self, table, row):
        self.table = table
        self.row = row

    def __getitem__(self, i):
        if i is None:
            return None
        if type(i) == unicode:
            i = i.encode('ascii')
        if type(i) is str:
            try:
                return self.row.__dict__[i]
            except:
                return None
        return self.row[i]

    def __repr__(self):
        return str(self.row)

    def title(self):
        if 'title' in self.row.__dict__:
            return val(self, 'title')
        return val(self, primary_key_or_first_column(self.table))

    def subtitle(self):
        return val(self, 'subtitle')

    def autocomplete(self):
        column = primary_key_or_first_column(self.table)
        return self.table.autocomplete(column, self[column])

    def icon(self):
        return 'images/row.png'

    def format(self):
        return Formatter.format_row(self)

    def as_json(self):
        return {
            '__cls__': str(self.__class__),
            'table': self.table.as_json(),
            'row': as_json(self.row)
        }

    @staticmethod
    def from_json(d):
        return Row(from_json(d['table']), from_json(d['row']))
