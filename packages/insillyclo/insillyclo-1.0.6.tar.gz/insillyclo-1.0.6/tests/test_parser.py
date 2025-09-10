#
#  InSillyClo
#  Copyright (C) 2025  The InSillyClo Authors
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from insillyclo import additional_exception
import insillyclo.additional_exception
import insillyclo.models
from tests.base_test_case import BaseTestCase


class TestParsing(BaseTestCase):
    maxDiff = None

    def test_parser_01(self):
        assembly, plasmids = self.load_filled_templates("template_01_ok.xlsx")
        self.assertEqual(assembly.separator, '-')
        self.assertEqual(assembly.input_parts[2].separator, '.')
        self.assertIsNone(assembly.input_parts[3].separator)
        self.assertEqual(
            assembly.input_parts[4].get_possible_interpretation("foo"),
            [
                [("foo", "5")],
                [("foo", insillyclo.models.get_direct_identifier())],
            ],
        )
        self.assertEqual(assembly.input_parts[4].part_types, ['5'])

    def test_parser_02(self):
        # check not enzyme does not crash the parser
        assembly, plasmids = self.load_filled_templates("template_02_ok.xlsx")
        self.assertEqual(
            assembly.input_parts[3].get_possible_interpretation("foo"),
            [
                [("foo", "4")],
                [("foo", insillyclo.models.get_direct_identifier())],
            ],
        )
        self.assertEqual(
            assembly.input_parts[4].get_possible_interpretation("foo"),
            [
                [("foo", None)],
                [("foo", insillyclo.models.get_direct_identifier())],
            ],
        )
        self.assertEqual(assembly.input_parts[4].part_types, None)
        self.assertEqual(
            plasmids[1].parts[0][0],
            "pTDH3_2",
        )
        self.assertIsNotNone(assembly.enzyme)
        self.assertEqual('BsaI', assembly.enzyme)

    def test_ko_01(self):
        # check unknown option make parser crash
        with self.assertRaises(insillyclo.additional_exception.TemplateParsingFailure):
            self.load_filled_templates("template_ko_01.xlsx")

    def test_ko_02(self):
        # check missing enzyme
        with self.assertRaises(insillyclo.additional_exception.EnzymeNotFound):
            self.load_filled_templates("template_ko_02.xlsx")
