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
import pathlib
from tempfile import NamedTemporaryFile

import Bio.SeqIO
from Bio.Seq import Seq

import insillyclo.gel
import insillyclo.models
import insillyclo.cli_utils
from tests.base_test_case import BaseTestCase


class TestImageExport(BaseTestCase):
    maxDiff = None

    def test_it(self):
        with NamedTemporaryFile(suffix='.svg', delete=True) as image:
            # image = "gel.svg"
            image = pathlib.Path(image.name)
            insillyclo.gel.produce_gel_image(
                filename=image,
                plasmids=[
                    ('pID0006', [(1763, True), (11757, True), (11757, True)]),
                    ('pID0007', [(1763, True), (11856, True)]),
                ],
                text="Enzyme digestion by InSillyClo.\nUsing " + ("NotI, BsmbI, " * 6),
            )
            # print(image.name)
            # os.system(f'eog {image}')

    def test_empty(self):
        with NamedTemporaryFile(suffix='.svg', delete=True) as image:
            # image = "gel.svg"
            image = pathlib.Path(image.name)
            insillyclo.gel.produce_gel_image(
                filename=image,
                plasmids=[
                    ('pID0006', [(1763, True), (11757, True), (11757, True)]),
                    ('pID0007', []),
                ],
            )
        with NamedTemporaryFile(suffix='.svg', delete=True) as image:
            # image = "gel.svg"
            image = pathlib.Path(image.name)
            insillyclo.gel.produce_gel_image(
                filename=image,
                plasmids=[
                    ('pID0007', []),
                ],
            )


class TestPCRAmplification(BaseTestCase):
    maxDiff = None

    def actual_test(
        self,
        shift: int,
        linear=False,
        check=True,
        rc_forward_in_well=False,
        rc_reverse_in_well=False,
    ):
        primer_for = "TTAC"
        primer_rev = "GAGA"
        seq = ''.join(
            [
                'Y' * 4,
                primer_for,
                'X' * 10,
                str(Seq(primer_rev).reverse_complement()),
                'Z' * 20,
            ]
        )
        seq_ko = ''.join(
            [
                'Y' * 4,
                primer_for[1:] + 'GG',
                'X' * 10,
                str(Seq(primer_rev[1:] + 'GG').reverse_complement()),
                'Z' * 20,
            ]
        )
        seq = seq[shift:] + seq[:shift]
        seq_ko = seq_ko[shift:] + seq_ko[:shift]
        if rc_forward_in_well:
            primer_for_in_well = str(Seq(primer_for).reverse_complement())
        else:
            primer_for_in_well = primer_for
        if rc_reverse_in_well:
            primer_rev_in_well = str(Seq(primer_rev).reverse_complement())
        else:
            primer_rev_in_well = primer_rev
        well = insillyclo.models.PCRWell(
            name="TOTO",
            sequences=[
                (self.seq_record(seq, linear=linear), True),
                (self.seq_record(seq_ko, linear=linear), False),
            ],
            primers=[
                ok_pair := insillyclo.models.PCRPrimerPair(
                    forward_id=primer_for,
                    forward_seq=primer_for_in_well,
                    reverse_id=primer_rev,
                    reverse_seq=primer_rev_in_well,
                ),
                insillyclo.models.PCRPrimerPair(
                    forward_id=primer_for + "TT",
                    forward_seq=primer_for_in_well + "TT",
                    reverse_id=primer_rev + "TT",
                    reverse_seq=primer_rev_in_well + "TT",
                ),
            ],
        )
        l, p = insillyclo.gel.get_amplified_sequences_lengths(well=well)
        if check:
            self.assertEqual([(10 + len(primer_for) + len(primer_rev), True)], l)
            self.assertEqual(p, [ok_pair])
        return l, p

    def test_simple(self):
        self.actual_test(shift=0)

    def test_simple_linear(self):
        self.actual_test(shift=0, linear=True)

    def test_for_split(self):
        self.actual_test(shift=6)

    def test_for_split_linear(self):
        l, p = self.actual_test(shift=6, linear=True, check=False)
        self.assertEqual([], l)
        self.assertEqual(p, [])

    def test_rev_split(self):
        self.actual_test(shift=-22)

    def test_rev_split_linear(self):
        l, p = self.actual_test(shift=-22, linear=True, check=False)
        self.assertEqual([], l)
        self.assertEqual([], p)

    def test_amplified_split(self):
        self.actual_test(shift=10)

    def test_amplified_split_linear(self, linear=True, check=False):
        l, p = self.actual_test(shift=10, linear=True, check=False)
        self.assertEqual([], l)
        self.assertEqual([], p)

    def test_amplified_split_manual(self):
        primer_for = "TTAC"
        primer_rev = "GAGA"
        seq = [
            'Y' * 4,
            str(Seq(primer_rev).reverse_complement()),
            'X' * 10,
            primer_for,
            'Z' * 20,
        ]
        sequence = self.seq_record(seq, linear=False)
        well = insillyclo.models.PCRWell(
            name="TOTO",
            sequences=[(sequence, True), (seq, True)],  # test both with a linear SeqRecord, and a simple Seq
            primers=[
                insillyclo.models.PCRPrimerPair(
                    forward_id=primer_for,
                    forward_seq=primer_for,
                    reverse_id=primer_rev,
                    reverse_seq=primer_rev,
                ),
            ],
        )
        l, _ = insillyclo.gel.get_amplified_sequences_lengths(well=well)
        self.assertEqual([(20 + 4 + len(primer_for) + len(primer_rev), True)], l)

    def test_simple_with_forward_rc(self):
        self.actual_test(shift=0, rc_forward_in_well=True)

    def test_simple_with_reverse_rc(self):
        self.actual_test(shift=0, rc_reverse_in_well=True)

    def test_simple_with_both_rc(self):
        self.actual_test(shift=0, rc_reverse_in_well=True, rc_forward_in_well=True)


class TestPCRAmplificationWithRealData(BaseTestCase):
    def test_real_data(self):
        seq = Bio.SeqIO.read(self.test_data_dir / 'plasmids_gb' / f'pID001.gb', 'genbank')
        with open(self.test_data_dir / 'primers.csv') as f:
            delimiter = insillyclo.cli_utils.get_csv_delimiter(f)
            csr_reader = csv.reader(f, delimiter=delimiter)
            next(csr_reader)
            for row in csr_reader:
                if row[0] == "P84":
                    forward = row
                elif row[0] == "P134":
                    reverse = row
            assert forward is not None
            assert reverse is not None

        well = insillyclo.models.PCRWell(
            name=seq.name,
            sequences=[(seq, False)],
            primers=[
                insillyclo.models.PCRPrimerPair(
                    forward_id=forward[0],
                    forward_seq=forward[1].replace(' ', ''),
                    reverse_id=reverse[0],
                    reverse_seq=reverse[1].replace(' ', ''),
                ),
            ],
        )
        l, _ = insillyclo.gel.get_amplified_sequences_lengths(well=well)
        self.assertEqual(l, [(2236, False)])
