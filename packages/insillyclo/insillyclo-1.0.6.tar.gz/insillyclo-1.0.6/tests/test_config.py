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
import configparser
import os.path
import pathlib
import traceback
from io import StringIO
from pathlib import Path

from click.testing import CliRunner

import insillyclo.main
from insillyclo.conf import InSillyCloConfigIO, InSillyCloConfig
from tests.base_test_case import BaseTestCase, TemporaryDirectoryPathLib as TemporaryDirectory


class TestConfig(BaseTestCase):
    maxDiff = None

    def test_first(self):
        with TemporaryDirectory() as temp_dir:

            local_ini = temp_dir / "insillyclo.ini"
            with open(local_ini, "w") as f:
                f.write("[DILUTION]\npuncture_volume_10x = 666\n\n[FOO]\nbar=42\n")
            # check old settings kept
            test_settings = InSillyCloConfig(local_ini)
            settings = InSillyCloConfig("toto.ini")
            self.assertEqual(test_settings.puncture_volume_10x, 666)
            self.assertEqual(test_settings.minimal_puncture_volume, settings.minimal_puncture_volume)

            # can update settings
            self.assertEqual(test_settings.output_plasmid_expected_volume, settings.output_plasmid_expected_volume)
            test_settings.update_settings('output_plasmid_expected_volume', 32)
            self.assertNotEqual(test_settings.output_plasmid_expected_volume, settings.output_plasmid_expected_volume)

            # check export add default settings
            test_settings.save()
            with open(local_ini, "r") as f:
                file_content = ''.join(f.readlines())
            self.assertIn("minimal_puncture_volume", file_content)
            self.assertIn("FOO", file_content)
            self.assertIn("bar", file_content)

            del test_settings

            # check re-load has both settings
            test_settings_reloaded = InSillyCloConfig(local_ini)
            self.assertEqual(test_settings_reloaded.puncture_volume_10x, 666)
            self.assertEqual(test_settings_reloaded.output_plasmid_expected_volume, 32)
            self.assertEqual(test_settings_reloaded.minimal_puncture_volume, settings.minimal_puncture_volume)

            # check other prop are kept
            config_override = configparser.ConfigParser()
            config_override.read(local_ini)
            self.assertEqual(config_override["FOO"]['bar'], "42")

            # test can reload settings during execution
            test_settings_reloaded.update_settings('output_plasmid_expected_volume', 33)
            self.assertEqual(test_settings_reloaded.output_plasmid_expected_volume, 33)
            test_settings_reloaded = InSillyCloConfig(local_ini)
            self.assertEqual(test_settings_reloaded.output_plasmid_expected_volume, 32)

    def test_loading_old_setting_loading(self):
        with TemporaryDirectory() as temp_dir:

            local_ini = temp_dir / "insillyclo.ini"
            with open(local_ini, "w") as f:
                f.write("[DILUTION]\npuncture_volume_10x = 666\nblabla=55\n\n[FOO]\nbar=42\n")
            # load settings with a parameter unknown, and survive
            InSillyCloConfig(local_ini)


class TestCli(BaseTestCase):
    maxDiff = None

    def test_run(self):
        with TemporaryDirectory() as temp_dir:
            runner = CliRunner()
            mass = '2467618'
            result = runner.invoke(insillyclo.main.config, ['--default-mass-concentration', mass, '--config', temp_dir])
            self.assertInvokeWorks(result)
            with open(temp_dir / 'insillyclo.ini', "r") as f:
                file_content = ''.join(f.readlines())
            self.assertIn(f'default_mass_concentration = {mass}', file_content)

            result = runner.invoke(insillyclo.main.config, ['--no-default-mass-concentration', '--config', temp_dir])
            self.assertInvokeWorks(result)
            with open(temp_dir / 'insillyclo.ini', "r") as f:
                file_content = ''.join(f.readlines())
            self.assertIn(f'default_mass_concentration = None', file_content)

    def test_rounding(self):
        with TemporaryDirectory() as temp_dir:
            runner = CliRunner()
            mass = '878946'
            result = runner.invoke(insillyclo.main.config, ['--nb-digits-rounding', mass, '--config', temp_dir])
            self.assertInvokeWorks(result)
            with open(temp_dir / 'insillyclo.ini', "r") as f:
                file_content = ''.join(f.readlines())
            self.assertIn(f'nb_digits_rounding = {mass}', file_content)

            result = runner.invoke(insillyclo.main.config, ['--no-nb-digits-rounding', '--config', temp_dir])
            self.assertInvokeWorks(result)
            with open(temp_dir / 'insillyclo.ini', "r") as f:
                file_content = ''.join(f.readlines())
            self.assertIn(f'nb_digits_rounding = None', file_content)

    def test_run_enzyme_and_buffer_volume(self):
        with TemporaryDirectory() as temp_dir:
            runner = CliRunner()
            mass = '2467618'
            result = runner.invoke(insillyclo.main.config, ['--enzyme-and-buffer-volume', mass, '--config', temp_dir])
            self.assertInvokeWorks(result)
            with open(temp_dir / 'insillyclo.ini', "r") as f:
                file_content = ''.join(f.readlines())
            self.assertIn(f'enzyme_and_buffer_volume = {mass}', file_content)

    def test_list(self):
        with TemporaryDirectory() as temp_dir:
            runner = CliRunner()
            mass = '49841681'
            result = runner.invoke(insillyclo.main.config, ['--list', '--config', temp_dir])
            self.assertInvokeWorks(result)
            self.assertIn(f"default_mass_concentration=None", result.output)
            result = runner.invoke(insillyclo.main.config, ['--default-mass-concentration', mass, '--config', temp_dir])
            self.assertInvokeWorks(result)
            result = runner.invoke(insillyclo.main.config, ['--list', '--config', temp_dir])
            self.assertInvokeWorks(result)
            self.assertIn(f"default_mass_concentration={mass}", result.output)

            result = runner.invoke(insillyclo.main.config, ['--list', '--global'])
            self.assertInvokeWorks(result)
            self.assertNotIn(f"default_mass_concentration={mass}", result.output)
