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

import os
from pathlib import Path

from click.testing import CliRunner

import insillyclo.conf
import insillyclo.data_source
import insillyclo.main
import insillyclo.models
import insillyclo.observer
import insillyclo.parser
import insillyclo.simulator
from tests.base_test_case import BaseTestCase, LazyTracebackPrint


class TestLazyTracebackPrint(BaseTestCase):

    def test_it(self):
        result = CliRunner().invoke(insillyclo.main.cli, ['--help'])
        self.assertIsNotNone(str(LazyTracebackPrint(result)))


class TestSetUpClassWhenNotGlobalConfig(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        os.close(os.open(Path.home() / f".{insillyclo.conf.INSILLYCLO_INI}", os.O_CREAT))
        super().setUpClass()
        cls.initial_content = cls.initial_content or ""

    def test_it(self):
        pass
