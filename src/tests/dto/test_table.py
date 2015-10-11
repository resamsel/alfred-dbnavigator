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

from tests.testcase import ParentTestCase
from dbmanagr.dto import table


class TableTestCase(ParentTestCase):
    def test_str(self):
        """Tests the Table.__str__ method"""

        t = table.Table(name='a')

        self.assertEqual('a', str(t))

    def test_from_json(self):
        """Tests the Table.from_json static method"""

        t = table.Table(name='a')

        self.assertEqual(
            t,
            table.Table.from_json({
                'name': 'a'
            })
        )
