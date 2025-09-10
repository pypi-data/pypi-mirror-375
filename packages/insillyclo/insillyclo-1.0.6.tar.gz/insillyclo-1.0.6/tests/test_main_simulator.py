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
import csv

from click.testing import CliRunner

import insillyclo.main
import insillyclo.models
import insillyclo.observer
import insillyclo.cli_utils
from tests.base_test_case import BaseTestCase, TemporaryDirectoryPathLib as TemporaryDirectory


class TestParsing(BaseTestCase):
    maxDiff = None

    def test_typed(self):
        with TemporaryDirectory() as out_dir:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'simulate',
                    '--input-template-filled',
                    self.test_data_dir / "template_01_ok.xlsx",
                    '--input-parts-file',
                    self.test_data_dir / "DB_iP_typed.csv",
                    '--plasmid-repository',
                    self.test_data_dir / "plasmids_gb",
                    '--recursive-plasmid-repository',
                    '--output-dir',
                    out_dir,
                ],
            )
            self.assertInvokeWorks(result)

    def test_not_typed(self):
        with TemporaryDirectory() as out_dir:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'simulate',
                    '--input-template-filled',
                    self.test_data_dir / "template_01_no_type_ok.xlsx",
                    '--input-parts-file',
                    self.test_data_dir / "DB_iP_not_typed.csv",
                    '--plasmid-repository',
                    self.test_data_dir / "plasmids_gb",
                    '--recursive-plasmid-repository',
                    '--output-dir',
                    out_dir,
                    '--primer-pair',
                    'P84,P134',
                    '--primers-file',
                    self.test_data_dir / "primers.csv",
                    '--restriction-enzyme-gel',
                    'NotI',
                    '--no-default-mass-concentration',
                ],
            )
            self.assertInvokeWorks(result)
            filenames = set(file.name for file in out_dir.glob('*'))
            expected = {
                'DB_produced_plasmid.csv',
                'auto-gg-combination-to-make.csv',
                f'pcr.png',
                f'pcr.svg',
                f'digestion.png',
                f'digestion.svg',
                insillyclo.main.DEFAULT_CONCENTRATIONS_FILENAME,
            }
            for p in [
                'pID001',
                'pID002',
                'pID004',
            ]:
                expected.update(
                    {
                        f'{p}.gb',
                        f'{p}-pcr.png',
                        f'{p}-pcr.svg',
                        f'{p}-digestion.png',
                        f'{p}-digestion.svg',
                    }
                )

            self.assertEqual(expected, filenames)

    def test_mixed(self):
        with TemporaryDirectory() as out_dir:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'simulate',
                    '--input-template-filled',
                    self.test_data_dir / "template_01_mixed_ok.xlsx",
                    '--input-parts-file',
                    self.test_data_dir / "DB_iP_typed.csv",
                    '--input-parts-file',
                    self.test_data_dir / "DB_iP_not_typed.csv",
                    '--plasmid-repository',
                    self.test_data_dir / "plasmids_gb",
                    '--recursive-plasmid-repository',
                    '--default-mass-concentration',
                    200,
                    '--output-dir',
                    out_dir,
                ],
            )
            self.assertInvokeWorks(result)
            filenames = set(file.name for file in out_dir.glob('*'))
            expected = {
                'DB_produced_plasmid.csv',
                'auto-gg-combination-to-make.csv',
                'dilution-10x.csv',
                'dilution-10x.json',
                'dilution-direct.csv',
                'dilution-direct.json',
                'dilution-direct_mastermix.csv',
                'dilution-direct_mastermix.json',
                'dilution-10x_mastermix.csv',
                'dilution-10x_mastermix.json',
                insillyclo.main.DEFAULT_CONCENTRATIONS_FILENAME,
            }
            for p in [
                'pID001',
                'pID002',
                'pID003',
                'pID004',
            ]:
                expected.add(
                    f'{p}.gb',
                )

            self.assertEqual(expected, filenames)

            with open(out_dir / 'DB_produced_plasmid.csv') as csvfile:
                delimiter = insillyclo.cli_utils.get_csv_delimiter(csvfile)
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                self.assertEqual(
                    list(reader),
                    [
                        {'Name': 'ConLS-pTDH3_2-Venus_3-tENO1-ConR1', 'Type': 'TU1', 'pID': 'pID001'},
                        {'Name': 'ConLS-pTDH3_2-3xFLAG-6xHIS_3a-Venus_3b-tENO1-ConR1', 'Type': 'TU1', 'pID': 'pID002'},
                        {'Name': 'ConLS-pTDH3_2-Cas9_3-tENO1-ConR1', 'Type': 'TU33', 'pID': 'pID003'},
                        {'Name': 'ConLS-pTDH3_2-Cas9_3-tENO1-ConR1', 'Type': 'TU1', 'pID': 'pID004'},
                    ],
                )

            with open(out_dir / 'auto-gg-combination-to-make.csv') as csvfile:
                reader = csv.reader(csvfile, delimiter=",")
                self.assertEqual(
                    list(reader),
                    [
                        [
                            'pID001',
                            'ConLS-pTDH3_2-Venus_3-tENO1-ConR1',
                            'pYTK002',
                            'pYTK009',
                            'pYTK033',
                            'pYTK051',
                            'pYTK067',
                            'pYTK095',
                        ],
                        [
                            'pID002',
                            'ConLS-pTDH3_2-3xFLAG-6xHIS_3a-Venus_3b-tENO1-ConR1',
                            'pYTK002',
                            'pYTK009',
                            'pYTK040',
                            'pYTK045',
                            'pYTK051',
                            'pYTK067',
                            'pYTK095',
                        ],
                        [
                            'pID003',
                            'ConLS-pTDH3_2-Cas9_3-tENO1-ConR1',
                            'pYTK002',
                            'pYTK009',
                            'pYTK036',
                            'pYTK051',
                            'pYTK067',
                            'pYTK074',
                            'pYTK086',
                            'pYTK089',
                            'pYTK092',
                        ],
                        [
                            'pID004',
                            'ConLS-pTDH3_2-Cas9_3-tENO1-ConR1',
                            'pYTK002',
                            'pYTK009',
                            'pYTK036',
                            'pYTK051',
                            'pYTK067',
                            'pYTK095',
                        ],
                    ],
                )

    def test_mixed_type_mixed_name_identifier(self):
        with TemporaryDirectory() as out_dir:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'simulate',
                    '--input-template-filled',
                    self.test_data_dir / "template_04_mixed_type_mixed_name_id.xlsx",
                    '--input-parts-file',
                    self.test_data_dir / "DB_iP_typed.csv",
                    '--input-parts-file',
                    self.test_data_dir / "DB_iP_not_typed.csv",
                    '--plasmid-repository',
                    self.test_data_dir / "plasmids_gb",
                    '--recursive-plasmid-repository',
                    '--output-dir',
                    out_dir,
                ],
            )
            self.assertInvokeWorks(result)

    def test_only_identifier(self):
        with TemporaryDirectory() as out_dir:
            runner = CliRunner()
            result = runner.invoke(
                insillyclo.main.cli,
                [
                    '--debug',
                    '--fail-on-error',
                    'simulate',
                    '--input-template-filled',
                    self.test_data_dir / "template_05_only_id.xlsx",
                    '--plasmid-repository',
                    self.test_data_dir / "plasmids_gb",
                    '--recursive-plasmid-repository',
                    '--output-dir',
                    out_dir,
                ],
            )
            self.assertInvokeWorks(result)
