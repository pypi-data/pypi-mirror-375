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

import itertools
import logging
from typing import List

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

import insillyclo.data_source
import insillyclo.digestion
from tests.base_test_case import BaseTestCase


class TestDigestion(BaseTestCase):
    maxDiff = None
    data_source = insillyclo.data_source.DataSourceHardCodedImplementation()

    def actual_test(
        self,
        enzyme_name: str,
        shift: int = 0,
        len_out_1: int = 4,
        len_in: int = 12,
        len_out_2: int = 20,
    ):
        # Test built by reverse engineering function, must be re-evaluated (probable inversion between site_for and Y
        enzyme = [e for e in self.data_source.get_enzymes() if e.name == enzyme_name][0]
        seq1 = self.seq_record(
            [
                "Y" * len_out_1,
                enzyme.site_for,
                "X" * len_in,
                enzyme.site_rev,
                "Z" * len_out_2,
            ],
            shift=shift,
        )
        fragments = insillyclo.digestion.get_fragments(
            [seq1],
            enzyme=enzyme.name,
            data_source=self.data_source,
        )
        expected = [
            insillyclo.digestion.FragmentsInOutSensAntiSens(
                out_sens=''.join(
                    [
                        "X" * (4 + enzyme.inter_s),
                        enzyme.site_rev,
                        "Z" * len_out_2,
                        "Y" * len_out_1,
                        enzyme.site_for,
                        "X" * (4 + enzyme.inter_s),
                    ]
                ),
                in_sens="X" * (len_in - enzyme.inter_s * 2),
                out_antisens=''.join(
                    [
                        "X" * (4 + enzyme.inter_s),
                        enzyme.site_rev,
                        "R" * len_out_1,
                        "Z" * len_out_2,
                        enzyme.site_for,
                        "X" * (4 + enzyme.inter_s),
                    ]
                ),
                in_antisens="X" * (len_in - 2 * enzyme.inter_s),
            ),
        ]
        logging.debug(seq1.seq)
        logging.debug(expected)
        logging.debug(fragments)
        self.assertEqual(expected, fragments, seq1.seq)

    def test_simple(self):
        for enzyme in self.data_source.get_enzymes():
            with self.subTest(enzyme.name):
                self.actual_test(enzyme_name=enzyme.name)

    def test_site_for_split(self):
        shift = -6
        for enzyme in self.data_source.get_enzymes():
            with self.subTest(msg=f'{enzyme.name} with a shift {shift}'):
                # using a len_out_1 smaller than the shift so site_for in cut between and need permutation
                self.actual_test(enzyme_name=enzyme.name, len_out_1=-shift - 2, shift=shift)

    def test_site_rev_split(self):
        shift = 22
        for enzyme in self.data_source.get_enzymes():
            with self.subTest(msg=f'{enzyme.name} with a shift {shift}'):
                # using a len_out_1 smaller than the shift so site_for in cut between and need permutation
                self.actual_test(enzyme_name=enzyme.name, len_out_2=-shift - 2, shift=shift)
