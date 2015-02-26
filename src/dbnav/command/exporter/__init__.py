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

import sys
import re
import logging

from collections import OrderedDict

from dbnav import Wrapper
from dbnav.logger import LogWith
from dbnav.config import Config
from dbnav.sources import Source
from dbnav.utils import prefix, prefixes, remove_prefix, replace_wildcards
from dbnav.queryfilter import QueryFilter
from dbnav.writer import Writer
from dbnav.jsonable import Jsonable, from_json
from dbnav.dto.mapper import to_dto
from dbnav.exception import UnknownColumnException, UnknownTableException

from .args import parser, SqlInsertWriter

logger = logging.getLogger(__name__)


class RowItem(Jsonable):
    def __init__(self, row, include, exclude):
        self.row = row
        self.include = include
        self.exclude = exclude

    def __hash__(self):
        return hash(self.row.row)

    def __eq__(self, o):
        return hash(self) == hash(o)

    @staticmethod
    def from_json(d):
        return RowItem(
            from_json(d['row']),
            from_json(d['include']),
            from_json(d['exclude'])
        )


def fk_by_a_table_name(fks):
    return dict(map(lambda (k, v): (v.a.table.name, v), fks.iteritems()))


@LogWith(logger)
def create_items(connection, items, include, exclude):
    results_pre = []
    results_post = []
    includes = {}
    for item in items:
        for i in include:
            p = re.compile(replace_wildcards(prefix(i)))
            col, fk = None, None
            for key, val in item.table.foreign_keys().iteritems():
                if p.match(val.a.table.name):
                    fk = val
                    break
            for c in item.table.columns():
                if p.match(c.name):
                    col = c
                    break
            if not col and not fk:
                raise UnknownColumnException(item.table, i)
            if '.' not in i:
                # Only include column, don't include referencing rows
                #
                # Examples:
                # 1) user_id - include column user_id, but no referenced rows
                # 2) user_id. - include column user_id with referencing user
                #    row
                # 3) user_id.article - include column user_id with referenced
                #    articles
                continue
            if fk:
                if fk not in includes:
                    includes[fk] = []
                includes[fk].append(item[fk.b.name])
            if col and col.name in item.table.foreign_keys():
                fk = item.table.foreign_key(col.name)
                if fk not in includes:
                    includes[fk] = []
                includes[fk].append(item[fk.a.name])
    if exclude:
        for item in items:
            for x in exclude:
                p = re.compile(replace_wildcards(prefix(x)))
                fks = fk_by_a_table_name(item.table.foreign_keys())
                col, fk = None, None
                for k in fks.keys():
                    if p.match(k):
                        fk = fks[k]
                        break
                for c in item.table.columns():
                    if p.match(c.name):
                        col = c
                        break
                if not col and not fk:
                    raise UnknownColumnException(
                        item.table, x,
                        fks.keys() + map(
                            lambda c: c.name, item.table.columns()))
            # only check first item, as we expect all items are from the same
            # table
            break
    for fk in includes.keys():
        if fk.a.table.name == item.table.name:
            # forward references, must be in pre
            results_pre += create_items(
                connection,
                connection.rows(
                    fk.b.table,
                    QueryFilter(fk.b.name, 'in', includes[fk]),
                    limit=-1,
                    simplify=False),
                remove_prefix(fk.a.name, include),
                remove_prefix(fk.a.name, exclude))
        else:
            # backward reference, must be in post
            results_post += create_items(
                connection,
                connection.rows(
                    fk.a.table,
                    QueryFilter(fk.a.name, 'in', includes[fk]),
                    limit=-1,
                    simplify=False),
                remove_prefix(fk.a.table.name, include),
                remove_prefix(fk.a.table.name, exclude))

    return results_pre + map(
        lambda i: RowItem(to_dto(i), prefixes(include), prefixes(exclude)),
        items) + results_post


class DatabaseExporter(Wrapper):
    """The main class"""
    def __init__(self, options):
        Wrapper.__init__(self, options)

        if options.formatter:
            Writer.set(options.formatter(options))
        else:
            Writer.set(SqlInsertWriter(options))

    def execute(self):
        """The main method that splits the arguments and starts the magic"""
        options = self.options

        cons = Source.connections()

        # search exact match of connection
        for connection in cons:
            opts = options.get(connection.dbms)
            if ((opts.show == 'values'
                    or opts.show == 'columns' and opts.filter is not None)
                    and connection.matches(opts)):
                try:
                    connection.connect(opts.database)
                    tables = connection.tables()
                    if opts.table not in tables:
                        raise UnknownTableException(opts.table, tables.keys())
                    table = tables[opts.table]
                    items = create_items(
                        connection,
                        connection.rows(
                            table,
                            opts.filter,
                            opts.limit,
                            simplify=False),
                        opts.include,
                        opts.exclude)
                    # remove duplicates
                    return list(OrderedDict.fromkeys(items))
                finally:
                    connection.close()

        raise Exception('Specify the complete URI to a table')


def execute(args):
    """
    Directly calls the execute method and avoids using the wrapper
    """
    return DatabaseExporter(Config.init(args, parser)).execute()


def run(args):
    return DatabaseExporter(Config.init(args, parser)).run()


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    return DatabaseExporter(Config.init(args, parser)).write()