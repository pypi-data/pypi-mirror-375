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
import hashlib
import os
import pathlib
from tempfile import NamedTemporaryFile, TemporaryDirectory

import Bio.SeqIO

import insillyclo.additional_exception
import insillyclo.conf
import insillyclo.data_source
import insillyclo.models
import insillyclo.observer
import insillyclo.simulator
import insillyclo.cli_utils
from tests.base_test_case import (
    BaseTestCase,
    TemporaryDirectoryPathLib as TemporaryDirectory,
    TemporaryDirectoryPathLib,
)


class TestParsing(BaseTestCase):
    maxDiff = None

    def test_extract_needed_input_parts(self):
        assembly, plasmids = self.load_filled_templates("template_02_ok.xlsx")
        needed = insillyclo.simulator.extract_needed_input_parts(plasmids)
        self.assertSetEqual(
            needed,
            {
                ('3xFLAG-6xHIS.Venus', '3'),
                ('3xFLAG-6xHIS', '3a'),
                ('AmpR', '67'),
                ('AmpR~ColE1', '678'),
                ('Cas9', '3'),
                ('ColE1', '8'),
                ('ConLS', '1'),
                ('ConR1', None),
                ('pTDH3_2', '2'),
                ('pTDH3', '2'),
                ('pTDH4', '2'),
                ('tENO1', '4'),
                ('Venus', '3'),
                ('Venus', '3b'),
                ("URA3marker.URA3~3'.AmpR~ColE1.URA3~5'", '678'),
                ('3xFLAG-6xHIS.Venus', insillyclo.models.get_direct_identifier()),
                ('AmpR~ColE1', insillyclo.models.get_direct_identifier()),
                ('Cas9', insillyclo.models.get_direct_identifier()),
                ('ConLS', insillyclo.models.get_direct_identifier()),
                ('ConR1', insillyclo.models.get_direct_identifier()),
                ('pTDH3_2', insillyclo.models.get_direct_identifier()),
                ('pTDH3', insillyclo.models.get_direct_identifier()),
                ('pTDH4', insillyclo.models.get_direct_identifier()),
                ('tENO1', insillyclo.models.get_direct_identifier()),
                ('Venus', insillyclo.models.get_direct_identifier()),
                ('Venus', insillyclo.models.get_direct_identifier()),
                ('URA3marker.URA3~3\'.AmpR~ColE1.URA3~5\'', insillyclo.models.get_direct_identifier()),
            },
        )

    def test_fetch_gb_for_input_parts(self):
        needed_input_parts = {
            ('3xFLAG-6xHIS.Venus', '3'),
            ('3xFLAG-6xHIS', '3a'),
            ('foobar', '3'),
        }
        seqs = insillyclo.simulator.fetch_gb_for_input_parts(
            needed_input_parts,
            input_parts_files=[self.test_data_dir / "DB_iP_typed.csv"],
            gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
            observer=insillyclo.observer.InSillyCloCliObserver(
                debug=False,
                fail_on_error=True,
            ),
        )
        self.assertNotIn(('ConL1', '1'), seqs, "Not needed")

        # 3xFLAG-6xHIS.Venus is not in file
        self.assertNotIn(('3xFLAG-6xHIS.Venus', '3'), seqs, "absent from file")

        # pYTK040
        self.assertIn(('3xFLAG-6xHIS', '3a'), seqs)
        self.assertNotIn(('3xFLAG-6xHIS', '3'), seqs)
        gb = seqs[('3xFLAG-6xHIS', '3a')]
        self.assertEqual(gb.id, "<unknown id>")
        self.assertEqual(
            hashlib.sha256(str(gb.seq).encode("UTF-8")).hexdigest(),
            "ca1641e8c9839a1a2cfc6df08fde5401f265df85a61c502cf039591fdfb2bc32",
        )

        # pYTK666  : ('foobar', '3'), gb file absent
        self.assertNotIn(('foobar', '3'), seqs)

    def test_fetch_gb_for_input_parts_ConL1(self):
        needed_input_parts = {
            ('ConL1', '1'),
        }
        seqs = insillyclo.simulator.fetch_gb_for_input_parts(
            needed_input_parts,
            input_parts_files=[self.test_data_dir / "DB_iP_typed.csv"],
            gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
            observer=insillyclo.observer.InSillyCloCliObserver(
                debug=False,
                fail_on_error=True,
            ),
        )
        self.assertIn(('ConL1', '1'), seqs)

    def test_fetch_gb_for_input_parts_mass_concentration(self):
        needed_input_parts = {
            ('ConLS', '1'),
        }
        seqs = insillyclo.simulator.fetch_gb_for_input_parts(
            needed_input_parts,
            input_parts_files=[self.test_data_dir / "DB_iP_typed_with_mass_concentration.csv"],
            gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
            observer=insillyclo.observer.InSillyCloCliObserver(
                debug=False,
                fail_on_error=True,
            ),
        )
        self.assertIn(('ConLS', '1'), seqs)
        seq = seqs[('ConLS', '1')]
        self.assertIn('mass_concentration', seq.annotations)
        self.assertNotIn('mol_concentration', seq.annotations)
        self.assertEqual(55.547, seq.annotations['mass_concentration'])

    def test_fetch_gb_for_input_parts_mol_concentration(self):
        needed_input_parts = {
            ('ConLS', '1'),
        }
        seqs = insillyclo.simulator.fetch_gb_for_input_parts(
            needed_input_parts,
            input_parts_files=[self.test_data_dir / "DB_iP_typed_with_mol_concentration.csv"],
            gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
            observer=insillyclo.observer.InSillyCloCliObserver(
                debug=False,
                fail_on_error=True,
            ),
        )
        self.assertIn(('ConLS', '1'), seqs)
        seq = seqs[('ConLS', '1')]
        self.assertNotIn('mass_concentration', seq.annotations)
        self.assertIn('mol_concentration', seq.annotations)
        self.assertEqual(75.233, seq.annotations['mol_concentration'])

    def test_fetch_gb_for_typed_input_parts_space_issues(self):
        needed_input_parts = {
            ('with-a-space-at-the-end', '3'),
            ('with-a-space-at-the-beginning', '3'),
        }
        seqs = insillyclo.simulator.fetch_gb_for_input_parts(
            needed_input_parts,
            input_parts_files=[self.test_data_dir / "DB_iP_typed.csv"],
            gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
            observer=insillyclo.observer.InSillyCloCliObserver(
                debug=False,
                fail_on_error=True,
            ),
        )
        self.assertEqual(len(seqs), 2)

    def test_fetch_gb_for_not_typed_input_parts_space_issues(self):
        needed_input_parts = {
            ('with-a-space-at-the-end_3', None),
            ('with-a-space-at-the-beginning_3', None),
        }
        seqs = insillyclo.simulator.fetch_gb_for_input_parts(
            needed_input_parts,
            input_parts_files=[self.test_data_dir / "DB_iP_not_typed.csv"],
            gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
            observer=insillyclo.observer.InSillyCloCliObserver(
                debug=False,
                fail_on_error=True,
            ),
        )
        self.assertEqual(len(seqs), 2)

    def test_fetch_gb_for_input_parts_invalide_input_parts_files(self):
        with NamedTemporaryFile(suffix='.csv', delete=True) as f:
            with open(f.name, 'w') as fw:
                fw.write("foo;bar;zoo\n")
                fw.write("0;1;2\n")
            needed_input_parts = {
                ('foobar', '3'),
            }
            with self.assertRaises(insillyclo.additional_exception.InvalidePartFileHeader) as cm:
                insillyclo.simulator.fetch_gb_for_input_parts(
                    needed_input_parts,
                    input_parts_files=[f.name],
                    gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                    observer=insillyclo.observer.InSillyCloCliObserver(
                        debug=False,
                        fail_on_error=True,
                    ),
                )

    def test_ip_files_typed_extended(self):
        with NamedTemporaryFile(suffix='.csv', delete=True) as f:
            with open(f.name, 'w') as fw:
                fw.write('pID;Name;Type;foo;bar\n')
                fw.write("pYTK033;Venus;3;0;0\n")
            needed_input_parts = {
                ('Venus', '3'),
            }
            insillyclo.simulator.fetch_gb_for_input_parts(
                needed_input_parts,
                input_parts_files=[f.name],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
            )

    def test_ip_files_no_type_extended(self):
        with NamedTemporaryFile(suffix='.csv', delete=True) as f:
            with open(f.name, 'w') as fw:
                fw.write('pID;Name;foo;bar\n')
                fw.write("pYTK033;Venus;0;0\n")
            needed_input_parts = {
                ('Venus', None),
            }
            insillyclo.simulator.fetch_gb_for_input_parts(
                needed_input_parts,
                input_parts_files=[f.name],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
            )

    def test_empty_ip_files(self):
        with NamedTemporaryFile(suffix='.csv', delete=True) as f:
            with open(f.name, 'w') as fw:
                fw.write('pID;Name\n')
            needed_input_parts = {
                ('Venus', None),
            }
            insillyclo.simulator.fetch_gb_for_input_parts(
                needed_input_parts,
                input_parts_files=[f.name],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
            )

    def test_fetch_gb_for_input_parts__invalid_gb(self):
        invalid_gb_files = [f.name.split('.')[0] for f in (self.test_data_dir / "invalid_plasmids_gb").glob('*.gb')]

        with NamedTemporaryFile(suffix='.csv', delete=True) as f:
            # create a valide not typed input-parts file
            with open(f.name, 'w') as fw:
                fw.write('pID;Name\n')
                for n in invalid_gb_files:
                    fw.write(f"{n};{n}\n")
            # for each plasmid, need it in fetch_gb_for_input_parts and check that it transmit the issue higher
            for n in invalid_gb_files:
                with self.subTest(f"Opening invalid gb file {n}"):
                    needed_input_parts = {
                        (n, None),
                    }
                    with self.assertRaises(ValueError, msg=f"With file {f}"):
                        insillyclo.simulator.fetch_gb_for_input_parts(
                            needed_input_parts,
                            input_parts_files=[f.name],
                            gb_plasmids=(self.test_data_dir / "invalid_plasmids_gb").glob('*.gb'),
                            observer=insillyclo.observer.InSillyCloCliObserver(
                                debug=False,
                                fail_on_error=True,
                            ),
                        )

    def test_primer_id_pairs_to_primer_with_seq(self):
        with self.assertRaises(insillyclo.additional_exception.PrimerNotFound):
            insillyclo.simulator.primer_id_pairs_to_primer_with_seq(
                primer_id_pairs=[
                    ("foo", "P84"),
                ],
                primers_file=self.test_data_dir / "primers.csv",
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
            )
        with self.assertRaises(insillyclo.additional_exception.PrimerNotFound):
            insillyclo.simulator.primer_id_pairs_to_primer_with_seq(
                primer_id_pairs=[
                    ("P134", "bar"),
                ],
                primers_file=self.test_data_dir / "primers.csv",
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
            )
        with self.assertRaises(insillyclo.additional_exception.PrimerNotFound):
            insillyclo.simulator.primer_id_pairs_to_primer_with_seq(
                primer_id_pairs=[
                    ("foo", "bar"),
                ],
                primers_file=self.test_data_dir / "primers.csv",
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
            )
        ret = insillyclo.simulator.primer_id_pairs_to_primer_with_seq(
            primer_id_pairs=[
                ("P134", "P84"),
            ],
            primers_file=self.test_data_dir / "primers.csv",
            observer=insillyclo.observer.InSillyCloCliObserver(
                debug=False,
                fail_on_error=True,
            ),
        )
        self.assertEqual("GAGATAGGTGCCTCACTGATTAAG", list(ret)[0].forward_seq)
        self.assertEqual("TTACGGTTCCTGGCCTTTTG", list(ret)[0].reverse_seq)

        with NamedTemporaryFile(suffix='.csv', delete=True) as f:
            # test that with more column it works and log  a warning
            with open(f.name, 'w') as fw:
                fw.write("primerId;sequence;foo\n")
                fw.write("P134;AAA;bar\n")
                fw.write("P84;GGG;bar\n")
                fw.write("P01;TTT;bar\n")
                fw.write("P666;CCCC;bar\n")
            insillyclo.simulator.primer_id_pairs_to_primer_with_seq(
                primer_id_pairs=[
                    ("P134", "P84"),
                ],
                primers_file=f.name,
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
            )
            ret = insillyclo.simulator.primer_id_pairs_to_primer_with_seq(
                primer_id_pairs=[
                    ("P134", "P84"),
                    ("P666", "P01"),
                ],
                primers_file=f.name,
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
            )
            self.assertEqual("AAA", list(ret)[0].forward_seq)
            self.assertEqual("GGG", list(ret)[0].reverse_seq)
            self.assertEqual("CCCC", list(ret)[1].forward_seq)
            self.assertEqual("TTT", list(ret)[1].reverse_seq)

    def test_primer_id_pairs_to_primer_with_seq_empty(self):
        insillyclo.simulator.primer_id_pairs_to_primer_with_seq(
            primer_id_pairs=[],
            primers_file="",
            observer=insillyclo.observer.InSillyCloCliObserver(
                debug=False,
                fail_on_error=True,
            ),
        )


class TestComputeAll(BaseTestCase):
    observer = insillyclo.observer.InSillyCloCliObserver(
        debug=False,
        fail_on_error=True,
    )

    # def test_debug_issue(self):
    #     issue_dir = self.test_data_dir / "issue_cli_45"
    #     out_dir = issue_dir / 'out_dir'
    #     out_dir.mkdir(exist_ok=True)
    #     input_template_filled = list(issue_dir.glob('*.xlsx'))[0]
    #     # input_template_filled = self.test_data_dir / "template_03_ok_single.xlsx"
    #     gb_plasmids = (self.test_data_dir / 'plasmids_gb').glob('**/*.gb')
    #     gb_plasmids = issue_dir.glob('**/*.gb')
    #     insillyclo.simulator.compute_all(
    #         input_template_filled=input_template_filled,
    #         settings=insillyclo.conf.InSillyCloConfig(None),
    #         input_parts_files=[
    #             # issue_dir / "iP_foo_bar.csv",
    #             self.test_data_dir / "DB_iP_typed.csv",
    #             self.test_data_dir / "DB_iP_not_typed.csv",
    #         ],
    #         gb_plasmids=gb_plasmids,
    #         default_mass_concentration=None,
    #         output_dir=out_dir,
    #         data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
    #         # primers_file=self.test_data_dir / "primers.csv",
    #         observer=self.observer,
    #     )

    def test_mixed_ok_primer_enzyme(self):
        with TemporaryDirectoryPathLib() as out_dir:
            output = insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / "template_01_mixed_ok.xlsx",
                settings=insillyclo.conf.InSillyCloConfig(None),
                input_parts_files=[
                    self.test_data_dir / "DB_iP_typed.csv",
                    self.test_data_dir / "DB_iP_not_typed.csv",
                ],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=None,
                output_dir=out_dir,
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                enzyme_names=[
                    "NotI",
                ],
                primer_id_pairs=[
                    ("P84", "P134"),
                ],
                primers_file=self.test_data_dir / "primers.csv",
                observer=self.observer,
            )
            filenames = set(file.name for file in out_dir.glob('*'))
            expected = {
                'DB_produced_plasmid.csv',
                'auto-gg-combination-to-make.csv',
                f'pcr.png',
                f'pcr.svg',
                f'digestion.png',
                f'digestion.svg',
            }
            plasmid_ids = [
                'pID001',
                'pID002',
                'pID003',
                'pID004',
            ]
            for p in plasmid_ids:
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
            self.assertEqual(
                output,
                insillyclo.simulator.SimulationOutput(
                    plasmid_ids=[out_dir / f'{p}.gb' for p in plasmid_ids],
                    dilutions=dict(),
                ),
            )

    def test_unknown_enzymes(self):
        with self.assertRaises(insillyclo.additional_exception.EnzymeNotFound):
            with TemporaryDirectoryPathLib() as out_dir:
                enzyme_names = [
                    "NotIZZZ",
                    "BstAPIFooBar",
                ]
                insillyclo.simulator.compute_all(
                    input_template_filled=self.test_data_dir / "template_01_mixed_ok.xlsx",
                    settings=insillyclo.conf.InSillyCloConfig(None),
                    input_parts_files=[
                        self.test_data_dir / "DB_iP_typed.csv",
                        self.test_data_dir / "DB_iP_not_typed.csv",
                    ],
                    gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                    default_mass_concentration=None,
                    output_dir=out_dir,
                    data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                    enzyme_names=enzyme_names,
                    observer=self.observer,
                )

    def test_mixed_ok_two_enzymes(self):
        with TemporaryDirectoryPathLib() as out_dir:
            enzyme_names = [
                "NotI",
                "BstAPI",
            ]
            output = insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / "template_01_mixed_ok.xlsx",
                settings=insillyclo.conf.InSillyCloConfig(None),
                input_parts_files=[
                    self.test_data_dir / "DB_iP_typed.csv",
                    self.test_data_dir / "DB_iP_not_typed.csv",
                ],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=None,
                output_dir=out_dir,
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                enzyme_names=enzyme_names,
                observer=self.observer,
            )
            filenames = set(file.name for file in out_dir.glob('*'))
            expected = {
                'DB_produced_plasmid.csv',
                'auto-gg-combination-to-make.csv',
                f'digestion.png',
                f'digestion.svg',
                f'digestion.svg',
                f'digestion.png',
                f'digestion.svg',
            }
            for e in enzyme_names:
                expected.update(
                    {
                        f'digestion-{e}.png',
                        f'digestion-{e}.svg',
                    }
                )
            plasmid_ids = [
                'pID001',
                'pID002',
                'pID003',
                'pID004',
            ]
            for p in plasmid_ids:
                expected.update(
                    {
                        f'{p}.gb',
                        f'{p}-digestion.png',
                        f'{p}-digestion.svg',
                    }
                )
                for e in enzyme_names:
                    expected.update(
                        {
                            f'{p}-digestion-{e}.png',
                            f'{p}-digestion-{e}.svg',
                        }
                    )

            self.assertEqual(expected, filenames)
            self.assertEqual(
                output,
                insillyclo.simulator.SimulationOutput(
                    plasmid_ids=[out_dir / f'{p}.gb' for p in plasmid_ids],
                    dilutions=dict(),
                ),
            )

    def test_mixed_ok(self):
        with TemporaryDirectory() as out_dir:
            insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / "template_01_mixed_ok.xlsx",
                settings=insillyclo.conf.InSillyCloConfig(None),
                input_parts_files=[
                    self.test_data_dir / "DB_iP_typed.csv",
                    self.test_data_dir / "DB_iP_not_typed.csv",
                ],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=None,
                output_dir=out_dir,
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                primers_file=self.test_data_dir / "primers.csv",
                observer=self.observer,
            )
            filenames = set(file.name for file in out_dir.glob('*'))
            expected = {
                'DB_produced_plasmid.csv',
                'auto-gg-combination-to-make.csv',
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

    def test_with_dilution(self):
        template_name = "template_01_ok.xlsx"
        assembly, plasmids, plasmids_instantiated = self.load_and_instantiate_filled_templates(
            template_name,
        )

        with TemporaryDirectory() as out_dir:
            insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / template_name,
                settings=insillyclo.conf.InSillyCloConfig(None),
                input_parts_files=[
                    self.test_data_dir / "DB_iP_typed.csv",
                    self.test_data_dir / "DB_iP_not_typed.csv",
                ],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=100,
                output_dir=out_dir,
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                primers_file=self.test_data_dir / "primers.csv",
                observer=self.observer,
            )
            filenames = set(file.name for file in out_dir.glob('*'))
            expected = {
                'DB_produced_plasmid.csv',
                'auto-gg-combination-to-make.csv',
                'dilution-10x.csv',
                'dilution-direct.json',
                'dilution-direct.csv',
                'dilution-10x.json',
                'dilution-direct_mastermix.csv',
                'dilution-direct_mastermix.json',
                'dilution-10x_mastermix.csv',
                'dilution-10x_mastermix.json',
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

            ##################################################
            # check all plasmid used are found in the CSV
            ##################################################
            ip_used = set()
            for _, parts in plasmids_instantiated:
                for part in parts:
                    for s in part.sequences:
                        ip_used.add(s.name)

            ip_used = sorted(list(ip_used))
            with open(out_dir / 'dilution-direct.csv') as csvfile:
                delimiter = insillyclo.cli_utils.get_csv_delimiter(csvfile)
                csv_reader = csv.reader(csvfile, delimiter=delimiter)
                header = next(csv_reader)
                self.assertEqual(
                    header,
                    [
                        'plasmid_id',
                        'h2o_volume',
                        'buffer',
                    ]
                    + ip_used,
                )
            ##################################################

    def test_id_only(self):
        with TemporaryDirectory() as out_dir:
            insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / "template_05_only_id.xlsx",
                settings=insillyclo.conf.InSillyCloConfig(None),
                input_parts_files=[],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=None,
                output_dir=out_dir,
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                primers_file=self.test_data_dir / "primers.csv",
                observer=self.observer,
            )
            filenames = set(file.name for file in out_dir.glob('*'))
            expected = {
                'DB_produced_plasmid.csv',
                'auto-gg-combination-to-make.csv',
            }
            for p in [
                'pID001',
            ]:
                expected.add(
                    f'{p}.gb',
                )

            self.assertEqual(expected, filenames)

    def test_ko_missing_input_part_translation(self):
        with (
            self.assertRaises(insillyclo.additional_exception.MissingSequenceForInputPart),
            TemporaryDirectory() as out_dir,
        ):
            insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / "template_ko_03.xlsx",
                settings=insillyclo.conf.InSillyCloConfig(None),
                input_parts_files=[],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=None,
                output_dir=pathlib.Path(out_dir),
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                primers_file=self.test_data_dir / "primers.csv",
                observer=self.observer,
            )

    def test_with_mass_concentration_both_in_db_ip_and_file(self):
        with TemporaryDirectoryPathLib() as out_dir, NamedTemporaryFile(suffix='.csv') as cf:
            with open(cf.name, 'w') as csvfile:
                csvfile.write(
                    '\n'.join(
                        [
                            "pID;Mass Concentration",
                            "pYTK001;15",
                            "pYTK005;1599",
                        ]
                    )
                )
            insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / "template_01_ok.xlsx",
                settings=insillyclo.conf.InSillyCloConfig(None),
                input_parts_files=[
                    self.test_data_dir / "DB_iP_typed_with_mass_concentration.csv",
                    self.test_data_dir / "DB_iP_typed.csv",
                ],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=200,
                output_dir=out_dir,
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                enzyme_names=[
                    "NotI",
                ],
                primer_id_pairs=[
                    ("P84", "P134"),
                ],
                primers_file=self.test_data_dir / "primers.csv",
                observer=self.observer,
                concentration_file=pathlib.Path(cf.name),
            )

    def test_inverted(self):
        with TemporaryDirectory() as out_dir, NamedTemporaryFile(suffix='.csv') as cf:
            insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / "template_03_ok_single_inverted.xlsx",
                settings=insillyclo.conf.InSillyCloConfig(None),
                input_parts_files=[
                    self.test_data_dir / "DB_iP_typed.csv",
                    self.test_data_dir / "DB_iP_not_typed.csv",
                ],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                concentration_file=pathlib.Path(cf.name),
                default_mass_concentration=None,
                output_dir=out_dir,
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                primers_file=self.test_data_dir / "primers.csv",
                observer=self.observer,
            )
            filenames = set(file.name for file in out_dir.glob('*'))
            expected = {
                'DB_produced_plasmid.csv',
                'auto-gg-combination-to-make.csv',
            }
            for p in [
                'pID001',
            ]:
                expected.add(
                    f'{p}.gb',
                )

            self.assertEqual(expected, filenames)
            with open(cf.name, 'r') as csvfile:
                self.assertEqual(
                    list(csv.reader(csvfile, delimiter=';')),
                    [
                        ['pID', 'Mass Concentration'],
                        ['pYTK002', ''],
                        ['pYTK009', ''],
                        ['pYTK033i', ''],
                        ['pYTK051', ''],
                        ['pYTK067', ''],
                        ['pYTK095', ''],
                    ],
                )


class TestSimulationSBOL(BaseTestCase):

    observer = insillyclo.observer.InSillyCloCliObserver(
        debug=False,
        fail_on_error=True,
    )

    def test_with_sbol(self):
        template_name = "template_01_ok.xlsx"
        assembly, plasmids, plasmids_instantiated = self.load_and_instantiate_filled_templates(
            template_name,
        )

        with TemporaryDirectory() as out_dir:
            insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / template_name,
                settings=insillyclo.conf.InSillyCloConfig(None),
                input_parts_files=[
                    self.test_data_dir / "DB_iP_typed.csv",
                    self.test_data_dir / "DB_iP_not_typed.csv",
                ],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=100,
                output_dir=out_dir,
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                primers_file=self.test_data_dir / "primers.csv",
                observer=self.observer,
                sbol_export=True,
            )
            filenames = set(file.name for file in out_dir.glob('*'))
            self.assertIn('plasmids.xml', filenames)
            with open(out_dir / 'plasmids.xml', 'r') as f:
                content = '\n'.join(f.readlines())
            for p in [
                'pID001',
                'pID002',
                'pID003',
                'pID004',
            ]:
                seq = Bio.SeqIO.read(out_dir / f'{p}.gb', 'genbank').seq
                self.assertIn(str(seq), content)


class TestOverrideConcentration(BaseTestCase):
    observer = insillyclo.observer.InSillyCloCliObserver(
        debug=False,
        fail_on_error=True,
    )

    def actual_test_override_from_concentration_file_and_update(
        self,
        *,
        cf,
        plasmid_ids: list[str],
        plasmid_names_and_type: list[tuple[str, str]] = None,
        newly_added: int = 0,
    ):
        if plasmid_names_and_type is None:
            plasmid_names_and_type = []
        seqs = insillyclo.simulator.fetch_gb_for_input_parts(
            needed_input_parts=set(
                (plasmid_id, insillyclo.models.get_direct_identifier()) for plasmid_id in plasmid_ids
            ).union(set(plasmid_names_and_type)),
            input_parts_files=[
                self.test_data_dir / "DB_iP_typed.csv",
                self.test_data_dir / "DB_iP_typed_with_mass_concentration.csv",
            ],
            gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
            observer=insillyclo.observer.InSillyCloCliObserver(
                debug=False,
                fail_on_error=True,
            ),
        )
        insillyclo.simulator.override_from_concentration_file_and_update(
            concentration_file=cf.name,
            sequences=seqs,
            observer=self.observer,
        )
        concentrations = dict()
        with open(cf.name) as csvfile:
            delimiter = insillyclo.cli_utils.get_csv_delimiter(csvfile)
            csv_reader = csv.reader(csvfile, delimiter=delimiter)
            next(csv_reader)
            prev_row = None
            for row in csv_reader:
                if prev_row is not None:
                    self.assertGreaterEqual(row[0], prev_row[0], 'order must be alphabetical')
                prev_row = row
                concentrations[row[0]] = row[1]
        self.assertEqual(
            len(concentrations),
            len(plasmid_ids) + len(plasmid_names_and_type) + newly_added,
            'expected number of items',
        )
        return concentrations

    def test_override_from_concentration_file_and_update(self):
        with NamedTemporaryFile(suffix='.csv') as cf:
            os.unlink(cf.name)
            concentrations = self.actual_test_override_from_concentration_file_and_update(
                cf=cf,
                plasmid_ids=['pYTK002', 'pYTK003'],
                newly_added=0,
            )
            self.assertDictEqual(
                concentrations,
                {
                    "pYTK002": "",
                    "pYTK003": "",
                },
            )

    def test_override_from_concentration_file_and_update_empty(self):
        with NamedTemporaryFile(suffix='.csv') as cf:
            concentrations = self.actual_test_override_from_concentration_file_and_update(
                cf=cf,
                plasmid_ids=['pYTK002', 'pYTK003'],
                newly_added=0,
            )
            self.assertDictEqual(
                concentrations,
                {
                    "pYTK002": "",
                    "pYTK003": "",
                },
            )

    def test_override_from_concentration_file_and_update_append(self):
        with NamedTemporaryFile(suffix='.csv') as cf:
            with open(cf.name, 'w') as csvfile:
                csvfile.write(
                    '\n'.join(
                        [
                            "pID;Mass Concentration",
                            "pYTK001;15",
                            "pYTK005;1599",
                        ]
                    )
                )
            concentrations = self.actual_test_override_from_concentration_file_and_update(
                cf=cf,
                plasmid_ids=['pYTK002', 'pYTK003'],
                newly_added=2,
            )
            self.assertDictEqual(
                concentrations,
                {
                    "pYTK001": "15",
                    "pYTK005": "1599",
                    "pYTK002": "",
                    "pYTK003": "",
                },
            )

    def test_override_from_concentration_file_and_update_append_keep(self):
        with NamedTemporaryFile(suffix='.csv') as cf:
            with open(cf.name, 'w') as csvfile:
                csvfile.write(
                    '\n'.join(
                        [
                            "pID;Mass Concentration",
                            "pYTK002;",
                            "pYTK005;1599",
                            "pYTK009;35",
                        ]
                    )
                )
            concentrations = self.actual_test_override_from_concentration_file_and_update(
                cf=cf,
                plasmid_ids=['pYTK003', 'pYTK009'],
                plasmid_names_and_type=[("ConLS", "1")],
                newly_added=1,
            )
            self.assertDictEqual(
                concentrations,
                {
                    "pYTK002": "55.547",
                    "pYTK003": "",
                    "pYTK005": "1599",
                    "pYTK009": "35.0",  # as used, and so re-defined in file
                },
            )
