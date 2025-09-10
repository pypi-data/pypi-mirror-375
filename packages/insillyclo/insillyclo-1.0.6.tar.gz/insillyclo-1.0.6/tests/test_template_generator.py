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

import pathlib
from tempfile import NamedTemporaryFile

import insillyclo.additional_exception
import insillyclo.data_source
import insillyclo.models
import insillyclo.observer
import insillyclo.parser
import insillyclo.simulator
import insillyclo.template_generator
from tests.base_test_case import BaseTestCase


class TestTemplate(BaseTestCase):
    maxDiff = None

    def test_it(self):
        ip_names = ['ConL', 'Promoter', 'CDS', 'Terminator', 'ConR', 'Backbone', 'Tralala']
        data_source = insillyclo.data_source.DataSourceHardCodedImplementation()
        plasmid = [
            # "pID001", "TU1", "ConLS", "pTDH3", "Venus", "tENO1", "ConR1", "AmpR~ColE1", "TralalaIP"
        ]
        enzyme = data_source.get_enzyme_names()[0]
        name = "TestTemplate.test_it foo bar"
        separator = data_source.get_separators()[0]
        with NamedTemporaryFile(suffix=".xlsx") as template:
            insillyclo.template_generator.make_template(
                destination_file=pathlib.Path(template.name),
                # destination_file="local.xlsx",
                ip_names=ip_names,
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
                data_source=data_source,
                default_plasmid=plasmid,
                enzyme=enzyme,
                name=name,
                default_separator=separator,
            )
            assembly, plasmids = insillyclo.parser.parse_assembly_and_plasmid_from_template(
                template.name,
                input_part_factory=insillyclo.models.InputPartDataClassFactory(),
                assembly_factory=insillyclo.models.AssemblyDataClassFactory(),
                plasmid_factory=insillyclo.models.PlasmidDataClassFactory(),
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=False,
                ),
            )
            self.assertEqual(name, assembly.name)
            self.assertEqual(enzyme, assembly.enzyme)
            self.assertEqual(separator, assembly.separator)
            self.assertEqual(ip_names, [ip.name for ip in assembly.input_parts])

    def test_check_enzyme(self):
        ip_names = ['ConL', 'Promoter', 'CDS', 'Terminator', 'ConR', 'Backbone', 'Tralala']
        data_source = insillyclo.data_source.DataSourceHardCodedImplementation()
        defaults = dict(
            plasmid=[
                # "pID001", "TU1", "ConLS", "pTDH3", "Venus", "tENO1", "ConR1", "AmpR~ColE1", "TralalaIP"
            ],
            enzyme=data_source.get_enzyme_names()[0],
            name="TestTemplate.test_it foo bar",
            separator=data_source.get_separators()[0],
        )
        with NamedTemporaryFile(suffix=".xlsx") as template:
            self.assertRaises(
                insillyclo.additional_exception.EnzymeNotFound,
                insillyclo.template_generator.make_template,
                destination_file=pathlib.Path(template.name),
                # destination_file="local.xlsx",
                ip_names=ip_names,
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
                data_source=data_source,
                enzyme="blabla",
            )

    def test_advanced_param(self):
        ips = [
            insillyclo.models.InputPart(
                name='P1',
                part_types=["1", "A"],
                is_optional=False,
                in_output_name=True,
                separator="~",
            ),
            insillyclo.models.InputPart(
                name='P2',
                part_types=["2", ["2a", "2b", "2c"]],
                is_optional=False,
                in_output_name=True,
                separator="-",
            ),
            insillyclo.models.InputPart(
                name='P3',
                part_types=["3"],
                is_optional=True,
                in_output_name=False,
                separator=None,
            ),
        ]
        data_source = insillyclo.data_source.DataSourceHardCodedImplementation()
        enzyme = data_source.get_enzyme_names()[0]
        name = "TestTemplate.test_it foo bar"
        separator = data_source.get_separators()[0]
        with NamedTemporaryFile(suffix=".xlsx") as template:
            insillyclo.template_generator.make_template(
                destination_file=pathlib.Path(template.name),
                # destination_file="local.xlsx",
                input_parts=ips,
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
                data_source=data_source,
                default_plasmid=[],
                enzyme=enzyme,
                name=name,
                default_separator=separator,
            )
            assembly, plasmids = insillyclo.parser.parse_assembly_and_plasmid_from_template(
                template.name,
                input_part_factory=insillyclo.models.InputPartDataClassFactory(),
                assembly_factory=insillyclo.models.AssemblyDataClassFactory(),
                plasmid_factory=insillyclo.models.PlasmidDataClassFactory(),
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=False,
                ),
            )
            self.assertEqual(name, assembly.name)
            self.assertEqual(enzyme, assembly.enzyme)
            self.assertEqual(separator, assembly.separator)
            self.assertEqual(ips, assembly.input_parts)

    def test_check_ips(self):
        ips = [
            insillyclo.models.InputPart(
                name='P1',
                part_types=["1", "A"],
                is_optional=False,
                in_output_name=True,
                separator="~",
            ),
            insillyclo.models.InputPart(
                name='P2',
                part_types=["2", ["2a", "2b", "2c"]],
                is_optional=False,
                in_output_name=True,
                separator=None,
            ),
            insillyclo.models.InputPart(
                name='P3',
                part_types=["3"],
                is_optional=True,
                in_output_name=False,
                separator=None,
            ),
        ]
        data_source = insillyclo.data_source.DataSourceHardCodedImplementation()
        enzyme = data_source.get_enzyme_names()[0]
        name = "TestTemplate.test_it foo bar"
        separator = data_source.get_separators()[0]
        with NamedTemporaryFile(suffix=".xlsx") as template:
            self.assertRaises(
                insillyclo.additional_exception.MissingSeparatorInPartTypesDeclaration,
                insillyclo.template_generator.make_template,
                destination_file=pathlib.Path(template.name),
                # destination_file="local.xlsx",
                input_parts=ips,
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
                data_source=data_source,
                default_plasmid=[],
                enzyme=enzyme,
                name=name,
                default_separator=separator,
            )

    def test_check_ips_or_names(self):
        data_source = insillyclo.data_source.DataSourceHardCodedImplementation()
        enzyme = data_source.get_enzyme_names()[0]
        name = "TestTemplate.test_it foo bar"
        separator = data_source.get_separators()[0]
        with NamedTemporaryFile(suffix=".xlsx") as template:
            self.assertRaises(
                AssertionError,
                insillyclo.template_generator.make_template,
                destination_file=pathlib.Path(template.name),
                # destination_file="local.xlsx",
                input_parts=[],
                ip_names=[],
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
                data_source=data_source,
                default_plasmid=[],
                enzyme=enzyme,
                name=name,
                default_separator=separator,
            )
