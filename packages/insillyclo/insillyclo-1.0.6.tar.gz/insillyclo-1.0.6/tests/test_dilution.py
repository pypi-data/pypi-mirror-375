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
import json
from tempfile import NamedTemporaryFile
from typing import List

import Bio.SeqIO
import Bio.SeqRecord

import insillyclo.conf
import insillyclo.data_source
import insillyclo.dilution
import insillyclo.observer
import insillyclo.simulator
import insillyclo.template_generator
import insillyclo.cli_utils
from tests.base_test_case import BaseTestCase, TemporaryDirectoryPathLib as TemporaryDirectory


class TestWriter(BaseTestCase):
    maxDiff = None
    specs = [
        insillyclo.dilution.PlasmidDilutionSpec(
            time_used=11,
            h2o_volume=22,
            ip_volumes=dict(
                riri=111,
                fifi=222,
            ),
            plasmid_id="foo",
        ),
        insillyclo.dilution.PlasmidDilutionSpec(
            time_used=33,
            h2o_volume=44,
            ip_volumes=dict(
                riri=333,
                loulou=444,
            ),
            plasmid_id="bar",
        ),
        insillyclo.dilution.PlasmidDilutionSpec(
            time_used=55,
            h2o_volume=66,
            ip_volumes=dict(
                fifi=555,
                loulou=666,
            ),
            plasmid_id="zoo",
        ),
    ]

    def test_json(self):
        with NamedTemporaryFile() as f:
            insillyclo.dilution.write_dilution_spec(
                filename=f.name,
                specs=self.specs,
                output_format='json',
            )
            with open(f.name) as fp:
                d = json.load(fp)
            self.assertEqual(
                d,
                [
                    dict(
                        plasmid_id=self.specs[i].plasmid_id,
                        h2o_volume=self.specs[i].h2o_volume,
                        **self.specs[i].ip_volumes,
                    )
                    for i in [1, 0, 2]
                ],
            )

    def test_csv(self):
        with NamedTemporaryFile() as f:
            insillyclo.dilution.write_dilution_spec(
                filename=f.name,
                specs=self.specs,
                output_format='csv',
            )
            with open(f.name) as csvfile:
                delimiter = insillyclo.cli_utils.get_csv_delimiter(csvfile)
                csv_reader = csv.reader(csvfile, delimiter=delimiter)
                header = next(csv_reader)
                self.assertEqual(
                    header,
                    [
                        'plasmid_id',
                        'h2o_volume',
                        'fifi',
                        'loulou',
                        'riri',
                    ],
                )
                # plasmid name are sorted, thus fifi loulou riri, event if presented in a different ordre
                for row in csv_reader:
                    plasmid: insillyclo.dilution.PlasmidDilutionSpec = next(
                        filter(lambda x: x.plasmid_id == row[0], self.specs)
                    )
                    self.assertEqual(row[1], str(plasmid.h2o_volume))
                    self.assertEqual(row[2], str(plasmid.ip_volumes.get("fifi", '')))
                    self.assertEqual(row[3], str(plasmid.ip_volumes.get("loulou", '')))
                    self.assertEqual(row[4], str(plasmid.ip_volumes.get("riri", '')))

    def test_exceeded_warning(self):
        template_name = "template_01_mixed_ok.xlsx"

        with TemporaryDirectory() as out_dir, self.assertLogs('root', level='WARNING') as cm:
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
                minimal_puncture_volume=1,
                observer=insillyclo.observer.InSillyCloCliObserver(
                    debug=False,
                    fail_on_error=True,
                ),
            )
        self.assertTrue(
            any('pID003' in m and 'Expected output' in m for m in cm.output),
            "a warning should be raised for pID003",
        )

    def test_no_specs(self):
        with NamedTemporaryFile() as f:
            insillyclo.dilution.write_dilution_spec(
                filename=f.name,
                specs=[],
                output_format='json',
            )
            with open(f.name) as fp:
                d = json.load(fp)
            self.assertEqual(d, [])


class AbstractTestDirectDilution(BaseTestCase):
    maxDiff = None
    observer = insillyclo.observer.InSillyCloCliObserver(
        debug=False,
        fail_on_error=True,
    )
    input_parts_file_names = [
        "DB_iP_typed.csv",
        "DB_iP_not_typed.csv",
    ]
    settings = insillyclo.conf.InSillyCloConfig(None)

    def setUp(self):
        super().setUp()
        self.settings.update_settings("nb_digits_rounding", None)

    def actual_test_direct(
        self,
        default_output_plasmid_volume=settings.output_plasmid_expected_volume,
        minimal_remaining_well_volume=settings.minimum_remaining_volume_in_dilution,
        puncture_volume=settings.puncture_volume_10x,
        minimal_puncture_volume=settings.minimal_puncture_volume,
        expected_concentration_in_output=settings.expected_concentration_in_output,
        enzyme_and_buffer_volume=settings.enzyme_and_buffer_volume,
        concentration_file=None,
        check_positive_volume: bool = True,
        assume_same_concentration: bool = True,
        target_dilutions: List[str] | None = None,
    ):
        template_name = "template_03_ok_single.xlsx"

        with TemporaryDirectory() as out_dir:
            insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / template_name,
                settings=self.settings,
                input_parts_files=[self.test_data_dir / f for f in self.input_parts_file_names],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=100,
                concentration_file=concentration_file,
                output_dir=out_dir,
                primers_file=self.test_data_dir / "primers.csv",
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                observer=self.observer,
                default_output_plasmid_volume=default_output_plasmid_volume,
                target_dilutions=target_dilutions,
                minimal_remaining_well_volume=minimal_remaining_well_volume,
                minimal_puncture_volume=minimal_puncture_volume,
                expected_concentration_in_output=expected_concentration_in_output,
                enzyme_and_buffer_volume=enzyme_and_buffer_volume,
            )
            with open(out_dir / 'dilution-direct.json', 'r') as fp:
                dilution = json.load(fp)
            with self.subTest("Output volume respect settings"):
                self.assertGreaterEqual(
                    default_output_plasmid_volume,
                    round(sum(v for v in dilution[0].values() if isinstance(v, float)), 8),
                )
            if check_positive_volume:
                with self.subTest("input volume is possible"):
                    for v in dilution[0].values():
                        if isinstance(v, float):
                            self.assertGreaterEqual(v, 0.0)
            with self.subTest("input volume respect minimal_puncture_volume"):
                for k, v in dilution[0].items():
                    if k in ['plasmid_id', 'h2o_volume', 'buffer']:
                        continue
                    self.assertGreaterEqual(v, minimal_puncture_volume)
            if assume_same_concentration:
                with self.subTest("same ordre in puncture and mol weight"):
                    vols_mass = dict()
                    for k, v in dilution[0].items():
                        if k in ['plasmid_id', 'h2o_volume', 'buffer']:
                            continue
                        ip_molecular_weight = Bio.SeqUtils.molecular_weight(
                            Bio.SeqIO.read(self.test_data_dir / "plasmids_gb" / f'{k}.gb', 'genbank'),
                            seq_type="DNA",
                            double_stranded=True,
                            circular=True,
                        )  # Da == g/mol
                        vols_mass[k] = dict(
                            vol=v,
                            mass=ip_molecular_weight,
                        )
                    self.assertEqual(
                        sorted(list(vols_mass.items()), key=lambda x: x[1]['vol']),
                        sorted(list(vols_mass.items()), key=lambda x: x[1]['mass']),
                    )
            return dilution


class TestDirectDilutionWithRounding(AbstractTestDirectDilution):
    settings = insillyclo.conf.InSillyCloConfig(None)

    def test_simple(self):
        self.settings.update_settings("nb_digits_rounding", 4)
        dilution = self.actual_test_direct(
            minimal_puncture_volume=0.5,
            default_output_plasmid_volume=10,
            expected_concentration_in_output=1.0,
            enzyme_and_buffer_volume=1.0,
        )
        self.assertDictEqual(
            self.round_dilution(dilution[0]),
            self.round_dilution(
                {
                    "buffer": 1.0,
                    "plasmid_id": "pID001",
                    "h2o_volume": 5.3960311996241055,
                    "pYTK002": 0.5057210838181545,
                    "pYTK009": 0.6405557827377443,
                    "pYTK033": 0.6481849111223225,
                    "pYTK051": 0.5176912281226581,
                    "pYTK067": 0.5,
                    "pYTK095": 0.7918157945750149,
                },
                self.settings.nb_digits_rounding,
            ),
        )


class TestDirectDilution(AbstractTestDirectDilution):
    def test_simple(self):
        dilution = self.actual_test_direct(
            minimal_puncture_volume=0.5,
            default_output_plasmid_volume=10,
            expected_concentration_in_output=1.0,
            enzyme_and_buffer_volume=1.0,
        )
        self.assertDictEqual(
            self.round_dilution(dilution[0]),
            self.round_dilution(
                {
                    "buffer": 1.0,
                    "plasmid_id": "pID001",
                    "h2o_volume": 5.3960311996241055,
                    "pYTK002": 0.5057210838181545,
                    "pYTK009": 0.6405557827377443,
                    "pYTK033": 0.6481849111223225,
                    "pYTK051": 0.5176912281226581,
                    "pYTK067": 0.5,
                    "pYTK095": 0.7918157945750149,
                }
            ),
        )

    def test_direct_2(self):
        with self.assertLogs('root', level='WARNING') as cm:
            self.actual_test_direct(
                minimal_puncture_volume=2,
                check_positive_volume=False,
                target_dilutions=['direct'],
            )

    def test_direct_2_20(self):
        self.actual_test_direct(
            minimal_puncture_volume=2,
            default_output_plasmid_volume=20,
            target_dilutions=['direct'],
        )


class TestDirectDilutionWithMass(AbstractTestDirectDilution):
    input_parts_file_names = [
        "DB_iP_typed.csv",
        "DB_iP_not_typed.csv",
        "DB_iP_typed_with_mass_concentration.csv",
    ]

    def test_simple(self):
        dilution = self.actual_test_direct(
            minimal_puncture_volume=0.5,
            default_output_plasmid_volume=10,
            assume_same_concentration=False,
            enzyme_and_buffer_volume=1.0,
        )
        # compared to TestDirectDilution only pYTK002 should be raised as
        # it mass concentration is lower than default, and thus h2o_volume reduced
        self.assertDictEqual(
            self.round_dilution(dilution[0]),
            self.round_dilution(
                {
                    "buffer": 1.0,
                    "plasmid_id": "pID001",
                    "h2o_volume": 4.991314125093196,
                    "pYTK002": 0.9104381583490639,
                    "pYTK009": 0.6405557827377443,
                    "pYTK033": 0.6481849111223225,
                    "pYTK051": 0.5176912281226581,
                    "pYTK067": 0.5,
                    "pYTK095": 0.7918157945750149,
                }
            ),
        )


class TestDirectDilutionWithMassInConcentrationFile(AbstractTestDirectDilution):
    input_parts_file_names = [
        "DB_iP_typed.csv",
        "DB_iP_not_typed.csv",
    ]

    def test_simple(self):
        with NamedTemporaryFile() as cf:
            with open(cf.name, 'w') as f:
                csv_writer = csv.writer(f, delimiter=';')
                csv_writer.writerows(
                    [
                        ['pID', 'Mass Concentration'],
                        ['pYTK002', '55.547'],
                        ['pYTK010', '150.54'],
                    ],
                )
            dilution = self.actual_test_direct(
                minimal_puncture_volume=0.5,
                default_output_plasmid_volume=10,
                assume_same_concentration=False,
                concentration_file=cf.name,
                expected_concentration_in_output=1.0,
                enzyme_and_buffer_volume=1.0,
            )
            with open(cf.name) as f:
                delimiter = insillyclo.cli_utils.get_csv_delimiter(f)
                csv_reader = csv.reader(f, delimiter=delimiter)
                self.assertEqual(
                    list(csv_reader),
                    [
                        ['pID', 'Mass Concentration'],
                        ['pYTK002', '55.547'],
                        ['pYTK009', ''],
                        ['pYTK010', '150.54'],
                        ['pYTK033', ''],
                        ['pYTK051', ''],
                        ['pYTK067', ''],
                        ['pYTK095', ''],
                    ],
                )

            # compared to TestDirectDilution only pYTK002 should be raised as
            # it mass concentration is lower than default, and thus h2o_volume reduced
            self.assertDictEqual(
                self.round_dilution(dilution[0]),
                self.round_dilution(
                    {
                        "buffer": 1.0,
                        "plasmid_id": "pID001",
                        "h2o_volume": 4.991314125093196,
                        "pYTK002": 0.9104381583490639,
                        "pYTK009": 0.6405557827377443,
                        "pYTK033": 0.6481849111223225,
                        "pYTK051": 0.5176912281226581,
                        "pYTK067": 0.5,
                        "pYTK095": 0.7918157945750149,
                    }
                ),
            )


class TestDirectDilutionWithMol(AbstractTestDirectDilution):
    input_parts_file_names = [
        "DB_iP_typed.csv",
        "DB_iP_not_typed.csv",
        "DB_iP_typed_with_mol_concentration.csv",
    ]

    def test_simple_low_out_concentration(self):
        dilution = self.actual_test_direct(
            minimal_puncture_volume=0.5,
            default_output_plasmid_volume=10,
            assume_same_concentration=False,
            expected_concentration_in_output=1.0,
            enzyme_and_buffer_volume=1.0,
        )
        # compared to TestDirectDilution only pYTK002 should be raised as
        # it mol concentration is lower than default, and thus h2o_volume reduced
        self.assertDictEqual(
            self.round_dilution(dilution[0]),
            self.round_dilution(
                {
                    "buffer": 1.0,
                    "plasmid_id": "pID001",
                    "h2o_volume": 5.315587737877966,
                    "pYTK002": 0.5861645455642945,
                    "pYTK009": 0.6405557827377443,
                    "pYTK033": 0.6481849111223225,
                    "pYTK051": 0.5176912281226581,
                    "pYTK067": 0.5,
                    "pYTK095": 0.7918157945750149,
                }
            ),
        )

    def test_simple(self):
        dilution = self.actual_test_direct(
            minimal_puncture_volume=0.5,
            expected_concentration_in_output=10,
            default_output_plasmid_volume=10,
            assume_same_concentration=False,
            enzyme_and_buffer_volume=1.0,
        )
        # compared to TestDirectDilution only pYTK002 should be raised as
        # it mol concentration is lower than default, and thus h2o_volume reduced
        self.assertDictEqual(
            self.round_dilution(dilution[0]),
            self.round_dilution(
                {
                    "buffer": 1.0,
                    "plasmid_id": "pID001",
                    "h2o_volume": 0.64511854,
                    "pYTK002": 1.32920394,
                    "pYTK009": 1.45254311,
                    "pYTK033": 1.46984314,
                    "pYTK051": 1.17393183,
                    "pYTK067": 1.13381469,
                    "pYTK095": 1.79554475,
                }
            ),
        )


class Test10XDilution(BaseTestCase):
    maxDiff = None
    observer = insillyclo.observer.InSillyCloCliObserver(
        debug=False,
        fail_on_error=True,
    )
    settings: insillyclo.conf.InSillyCloConfig = insillyclo.conf.InSillyCloConfig(None)

    def setUp(self):
        super().setUp()
        self.settings.update_settings("nb_digits_rounding", None)

    def actual_test_10x(
        self,
        default_output_plasmid_volume=settings.output_plasmid_expected_volume,
        enzyme_and_buffer_volume=settings.enzyme_and_buffer_volume,
        minimal_remaining_well_volume=settings.minimum_remaining_volume_in_dilution,
        puncture_volume=settings.puncture_volume_10x,
        minimal_puncture_volume=settings.minimal_puncture_volume,
        expected_concentration_in_output=settings.expected_concentration_in_output,
        check_positive_volume: bool = True,
        default_mass_concentration: float = 100,
        target_dilutions=None,
        concentration_file=None,
    ):
        template_name = "template_03_ok_single.xlsx"

        with TemporaryDirectory() as out_dir:
            insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / template_name,
                settings=self.settings,
                input_parts_files=[
                    self.test_data_dir / "DB_iP_typed.csv",
                    self.test_data_dir / "DB_iP_not_typed.csv",
                ],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=default_mass_concentration,
                output_dir=out_dir,
                primers_file=self.test_data_dir / "primers.csv",
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                observer=self.observer,
                default_output_plasmid_volume=default_output_plasmid_volume,
                enzyme_and_buffer_volume=enzyme_and_buffer_volume,
                minimal_remaining_well_volume=minimal_remaining_well_volume,
                minimal_puncture_volume=minimal_puncture_volume,
                puncture_volume_10x=puncture_volume,
                expected_concentration_in_output=expected_concentration_in_output,
                target_dilutions=(
                    target_dilutions
                    if target_dilutions
                    else [
                        '10x',
                    ]
                ),
                concentration_file=concentration_file,
            )
            with open(out_dir / 'dilution-10x.json', 'r') as fp:
                dilution = json.load(fp)
            with self.subTest("Output volume respect settings"):
                self.assertGreaterEqual(
                    default_output_plasmid_volume, sum(v for v in dilution[-1].values() if isinstance(v, float))
                )
            if check_positive_volume:
                with self.subTest("input volume is possible"):
                    for d in dilution:
                        self.assertGreaterEqual(d['h2o_volume'], 0.0)
            with self.subTest("input volume respect puncture_volume"):
                for k, v in dilution[0].items():
                    if k in ['plasmid_id', 'h2o_volume', 'buffer']:
                        continue
                    self.assertEqual(v / puncture_volume, int(v / puncture_volume))
                    self.assertGreaterEqual(v, puncture_volume)
            with self.subTest("reverse ordre between water amendment and mol weight"):
                vols_mass = dict()
                amount_is_always_1 = True
                for d in dilution:
                    if '_' not in d['plasmid_id']:
                        continue
                    # we cannot compare the order if we took more than 1µL of one plasmid
                    amount_is_always_1 &= d[d['plasmid_id'][:-7]] == 1
                    k = d['plasmid_id'].split('_')[0]
                    ip_molecular_weight = Bio.SeqUtils.molecular_weight(
                        Bio.SeqIO.read(self.test_data_dir / "plasmids_gb" / f'{k}.gb', 'genbank'),
                        seq_type="DNA",
                        double_stranded=True,
                        circular=True,
                    )  # Da == g/mol
                    vols_mass[k] = dict(
                        vol=d['h2o_volume'],
                        mass=ip_molecular_weight,
                    )
                if amount_is_always_1:
                    self.assertEqual(
                        sorted(list(vols_mass.items()), key=lambda x: x[1]['vol']),
                        list(reversed(sorted(list(vols_mass.items()), key=lambda x: x[1]['mass']))),
                    )
            return dilution

    def test_simple(self):
        default_output_plasmid_volume = 10
        enzyme_and_buffer_volume = 1
        puncture_volume = 1
        minimal_remaining_well_volume = 0
        minimal_puncture_volume = 0.2
        default_mass_concentration = 200
        expected_concentration_in_output = 2
        dilution = self.actual_test_10x(
            default_output_plasmid_volume=default_output_plasmid_volume,
            enzyme_and_buffer_volume=enzyme_and_buffer_volume,
            minimal_remaining_well_volume=minimal_remaining_well_volume,
            puncture_volume=puncture_volume,
            expected_concentration_in_output=expected_concentration_in_output,
            minimal_puncture_volume=minimal_puncture_volume,
            check_positive_volume=True,
            default_mass_concentration=default_mass_concentration,
        )
        dilution = self.round_dilutions(dilution, 8)
        parts = []
        for pID in [
            'pYTK002',
            'pYTK009',
            'pYTK033',
            'pYTK051',
            'pYTK067',
            'pYTK095',
        ]:
            seq = Bio.SeqIO.read(self.test_data_dir / 'plasmids_gb' / f'{pID}.gb', 'genbank')
            ip_molecular_weight = Bio.SeqUtils.molecular_weight(
                seq,
                seq_type="DNA",
                double_stranded=True,
                circular=True,
            )  # Da == g/mol
            ip_molecular_weight *= 10**9 / 10**15  # ng/femtomol #
            ip_mol_concentration = default_mass_concentration / ip_molecular_weight  # femtomol/µL
            parts.append(
                (
                    pID,
                    ip_mol_concentration
                    / (expected_concentration_in_output * default_output_plasmid_volume / puncture_volume)
                    - puncture_volume,
                )
            )

        expected_dilution = [
            {
                "plasmid_id": f"{p}__10x__",
                "h2o_volume": v,
                p: 1,
            }
            for p, v in parts
        ] + [
            dict(
                plasmid_id="pID001",
                h2o_volume=default_output_plasmid_volume - len(parts) * puncture_volume - enzyme_and_buffer_volume,
                buffer=1.0,
                **dict([(f"{p}__10x__", 1) for p, _ in parts]),
            )
        ]

        self.assertDictEqual(
            dict(d=dilution),
            dict(d=self.round_dilutions(expected_dilution, 8)),
        )

    def test_simple_with_factor(self):
        default_output_plasmid_volume = 10
        enzyme_and_buffer_volume = 1
        puncture_volume = 1
        minimal_remaining_well_volume = 0.5
        minimal_puncture_volume = 0.2
        default_mass_concentration = 200
        expected_concentration_in_output = 2
        # a low concentration on pYTK095 trigger to use 2 µL of it
        with NamedTemporaryFile(suffix='.csv') as cf:
            with open(cf.name, 'w') as csvfile:
                csvfile.write(
                    '\n'.join(
                        [
                            "pID;Mass Concentration",
                            "pYTK095;40",
                        ]
                    )
                )
            dilution = self.actual_test_10x(
                default_output_plasmid_volume=default_output_plasmid_volume,
                enzyme_and_buffer_volume=enzyme_and_buffer_volume,
                minimal_remaining_well_volume=minimal_remaining_well_volume,
                puncture_volume=puncture_volume,
                expected_concentration_in_output=expected_concentration_in_output,
                minimal_puncture_volume=minimal_puncture_volume,
                check_positive_volume=True,
                default_mass_concentration=default_mass_concentration,
                concentration_file=cf.name,
            )
            target = [d for d in dilution if d['plasmid_id'] == 'pYTK095__10x__'][0]
            self.assertEqual(target['pYTK095'], 2)

    def test_warning_to_much_produced(self):
        with self.assertLogs('root', level='WARNING') as cm:
            self.actual_test_10x(
                default_output_plasmid_volume=1,
                check_positive_volume=False,
            )

    def test_too_high_concentration(self):
        with self.assertLogs('root', level='ERROR') as cm:
            self.actual_test_10x(
                expected_concentration_in_output=200,
                default_output_plasmid_volume=10,
                check_positive_volume=False,
            )
            # 6 plasmid * 2 warning
            self.assertEqual(len(cm.records), 6 * 2, "All plasmid or to low")

    def test_high_concentration(self):
        d = self.actual_test_10x(
            expected_concentration_in_output=100,
            default_output_plasmid_volume=10,
        )
        pytk095_10x = [x for x in d if x['plasmid_id'] == 'pYTK095__10x__'][0]
        self.assertGreater(
            pytk095_10x['pYTK095'], 1, 'Concentration is very high, needing 2µL plus the min remaining volume'
        )

    def test_high_concentration_2(self):
        minimal_puncture_volume = 0.2
        d = self.actual_test_10x(
            expected_concentration_in_output=5,
            default_output_plasmid_volume=10,
            minimal_puncture_volume=minimal_puncture_volume,
        )
        pytk095_10x = [x for x in d if x['plasmid_id'] == 'pYTK095__10x__'][0]
        self.assertGreater(
            pytk095_10x['h2o_volume'],
            minimal_puncture_volume,
            'h2o volume should still be higher than the min tip volume',
        )

    def test_simple_20(self):
        default_output_plasmid_volume = 20
        puncture_volume = 1
        minimal_remaining_well_volume = 1
        self.actual_test_10x(
            default_output_plasmid_volume=default_output_plasmid_volume,
            minimal_remaining_well_volume=minimal_remaining_well_volume,
            puncture_volume=puncture_volume,
            expected_concentration_in_output=10,
            check_positive_volume=True,
        )


class TestOptionalDilution(AbstractTestDirectDilution):
    def my_compute_all(self, target_dilutions: List[str]):
        template_name = "template_01_ok.xlsx"
        with TemporaryDirectory() as out_dir:
            output = insillyclo.simulator.compute_all(
                input_template_filled=self.test_data_dir / template_name,
                settings=self.settings,
                input_parts_files=[self.test_data_dir / f for f in self.input_parts_file_names],
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                default_mass_concentration=100,
                # concentration_file=concentration_file,
                output_dir=out_dir,
                primers_file=self.test_data_dir / "primers.csv",
                data_source=insillyclo.data_source.DataSourceHardCodedImplementation(),
                observer=self.observer,
                target_dilutions=target_dilutions,
            )
        return output

    def test_none(self):
        output = self.my_compute_all(
            target_dilutions=[],
        )
        self.assertEqual(output.dilutions.keys(), set())

    def test_only_direct(self):
        output = self.my_compute_all(
            target_dilutions=[
                insillyclo.dilution._DILUTION_STRATEGY_KEY_DIRECT,
            ],
        )
        self.assertEqual(
            output.dilutions.keys(),
            {
                insillyclo.dilution._DILUTION_STRATEGY_KEY_DIRECT,
            },
        )

    def test_only_10x(self):
        output = self.my_compute_all(
            target_dilutions=[
                insillyclo.dilution._DILUTION_STRATEGY_KEY_10X,
            ],
        )
        self.assertEqual(
            output.dilutions.keys(),
            {
                insillyclo.dilution._DILUTION_STRATEGY_KEY_10X,
            },
        )

    def test_only_10x_direct(self):
        output = self.my_compute_all(
            target_dilutions=[
                insillyclo.dilution._DILUTION_STRATEGY_KEY_DIRECT,
                insillyclo.dilution._DILUTION_STRATEGY_KEY_10X,
            ],
        )
        self.assertEqual(
            output.dilutions.keys(),
            {
                insillyclo.dilution._DILUTION_STRATEGY_KEY_10X,
                insillyclo.dilution._DILUTION_STRATEGY_KEY_DIRECT,
            },
        )
