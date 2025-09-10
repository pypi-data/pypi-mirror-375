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

from tempfile import TemporaryDirectory, NamedTemporaryFile
from click.testing import CliRunner

import insillyclo.main
from tests.base_test_case import BaseTestCase
import insillyclo.models
import insillyclo.observer
import insillyclo.parser


class TestTemplate(BaseTestCase):
    maxDiff = None

    def test_count(self):
        with NamedTemporaryFile() as file:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'template',
                    file.name,
                    '--nb-input-parts',
                    4,
                    '--separator',
                    '-',
                    '-e',
                    'BbsI',
                    '--name',
                    'foobar',
                ],
            )
            self.assertInvokeWorks(result)

            assembly, plasmids = self.load_filled_templates(file.name, load_only_assembly=True)
            self.assertEqual(0, len(plasmids))
            self.assertEqual(
                ["InputPart1", "InputPart2", "InputPart3", "InputPart4"],
                [ip.name for ip in assembly.input_parts],
            )
            self.assertEqual("BbsI", assembly.enzyme)
            self.assertEqual("foobar", assembly.name)

    def test_name(self):
        with NamedTemporaryFile() as file:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'template',
                    file.name,
                    '--input-part',
                    'riri',
                    '--input-part',
                    'fifi',
                    '-p',
                    'loulou',
                    '--separator',
                    '-',
                    '--restriction-enzyme-goldengate',
                    'BsaI',
                ],
            )
            self.assertInvokeWorks(result)

            assembly, plasmids = self.load_filled_templates(file.name, load_only_assembly=True)
            self.assertEqual(0, len(plasmids))
            self.assertEqual(
                ["riri", "fifi", "loulou"],
                [ip.name for ip in assembly.input_parts],
            )

    def test_short(self):
        with NamedTemporaryFile() as file:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'template',
                    file.name,
                    '-p',
                    'riri',
                    '--input-part',
                    'fifi',
                    '-p',
                    'loulou',
                    '-s',
                    '-',
                    '--restriction-enzyme-goldengate',
                    'BsaI',
                    '-n',
                    'My Assembly',
                ],
            )
            self.assertInvokeWorks(result)

            assembly, plasmids = self.load_filled_templates(file.name, load_only_assembly=True)
            self.assertEqual(0, len(plasmids))
            self.assertEqual(
                ["riri", "fifi", "loulou"],
                [ip.name for ip in assembly.input_parts],
            )
            self.assertEqual('My Assembly', assembly.name)
            self.assertEqual('-', assembly.separator)
            self.assertEqual('BsaI', assembly.enzyme)
