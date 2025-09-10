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

import insillyclo.models
from insillyclo.additional_exception import MissingSeparatorInPartTypesDeclaration, InvalidePartTypesExpression
from tests.base_test_case import BaseTestCase


class TestModels(BaseTestCase):
    maxDiff = None

    def test_get_possible_interpretation(self):
        assembly, plasmids = self.load_filled_templates()
        self.assertEqual(
            assembly.input_parts[3].get_possible_interpretation("foo"),
            [
                [("foo", "4")],
                [("foo", insillyclo.models.get_direct_identifier())],
            ],
        )
        self.assertEqual(assembly.input_parts[2].separator, '.')
        self.assertEqual(
            assembly.input_parts[2].get_possible_interpretation("foo.bar"),
            [
                [('foo.bar', '3')],
                [('foo', '3a'), ('bar', '3b')],
                [("foo.bar", insillyclo.models.get_direct_identifier())],
            ],
        )
        self.assertEqual(
            assembly.input_parts[2].get_possible_interpretation("foo~bar"),
            [
                [('foo~bar', '3')],
                [("foo~bar", insillyclo.models.get_direct_identifier())],
            ],
        )

    def test_get_possible_interpretation_not_typed(self):
        assembly, plasmids = self.load_filled_templates("template_01_no_type_ok.xlsx")
        self.assertEqual(assembly.input_parts[3].part_types, None)
        self.assertEqual(
            assembly.input_parts[3].get_possible_interpretation("foo.bar"),
            [
                [("foo.bar", None)],
                [("foo.bar", insillyclo.models.get_direct_identifier())],
            ],
        )
        self.assertEqual(assembly.input_parts[2].separator, '.')
        self.assertEqual(
            [
                [('foo.bar', None)],
                [('foo', None), ('bar', None)],
                [("foo.bar", insillyclo.models.get_direct_identifier())],
            ],
            assembly.input_parts[2].get_possible_interpretation("foo.bar"),
        )

    def test_separator_missing_not_allowed(self):
        self.assertRaises(
            MissingSeparatorInPartTypesDeclaration,
            insillyclo.models.InputPart(
                name='P1',
                part_types=["1", "A"],
                is_optional=False,
                in_output_name=True,
                separator=None,
            ).is_valid_raising,
        )
        insillyclo.models.InputPart(
            name='P1',
            part_types=["1", "A"],
            is_optional=False,
            in_output_name=True,
            separator="~",
        ).is_valid_raising()

        self.assertRaises(
            MissingSeparatorInPartTypesDeclaration,
            insillyclo.models.InputPart(
                name='P1',
                part_types=[["3a", "3b"]],
                is_optional=False,
                in_output_name=True,
                separator=None,
            ).is_valid_raising,
        )
        insillyclo.models.InputPart(
            name='P1',
            part_types=[["3a", "3b"]],
            is_optional=False,
            in_output_name=True,
            separator="~",
        ).is_valid_raising()

    def test_invalide_no_type_declaration(self):
        self.assertRaises(
            InvalidePartTypesExpression,
            insillyclo.models.InputPart(
                name='P1',
                part_types=[None],
                is_optional=False,
                in_output_name=True,
                separator="~",
            ).is_valid_raising,
        )

    def test_separator_allowed_when_not_typed(self):
        ip = insillyclo.models.InputPart(
            name='P1',
            part_types=None,
            is_optional=False,
            in_output_name=True,
            separator="~",
        )
        ip.is_valid_raising()
        self.assertEqual(ip.part_types_str, '')

    def test_misc_input_part(self):
        ip = insillyclo.models.InputPart(
            name='P1',
            part_types=None,
            is_optional=False,
            in_output_name=True,
            separator=None,
        )
        ip.is_valid_raising()
        self.assertEqual(ip.part_types_str, '')
