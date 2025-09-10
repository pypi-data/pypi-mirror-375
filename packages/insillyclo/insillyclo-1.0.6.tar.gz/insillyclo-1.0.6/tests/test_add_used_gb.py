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
from unittest import skipIf

import insillyclo.data_source
import insillyclo.models
import insillyclo.observer
import insillyclo.parser
import insillyclo.simulator
from tests.base_test_case import BaseTestCase


def actually_run_add_gb_file(
    *,
    input_template_filled,
    input_part_factory,
    assembly_factory,
    plasmid_factory,
    observer,
    input_parts_files,
    gb_plasmids,
    data_source,
):
    assembly, plasmids = insillyclo.parser.parse_assembly_and_plasmid_from_template(
        input_template_filled,
        input_part_factory=input_part_factory,
        assembly_factory=assembly_factory,
        plasmid_factory=plasmid_factory,
        observer=observer,
    )
    needed_input_parts = insillyclo.simulator.extract_needed_input_parts(plasmids)
    input_parts_gb_mapping = insillyclo.simulator.fetch_gb_for_input_parts(
        needed_input_parts=needed_input_parts,
        input_parts_files=input_parts_files,
        gb_plasmids=gb_plasmids,
        observer=observer,
    )
    for plasmid in plasmids:
        plasmid_instance = insillyclo.simulator.instantiate_plasmid_to_assemble(
            plasmid=plasmid,
            available_sequence=input_parts_gb_mapping,
            assembly=assembly,
            data_source=data_source,
            observer=observer,
        )
        for parts_n_sequence in plasmid_instance[1]:
            for s in parts_n_sequence[3]:
                import subprocess

                subprocess.run(["git", "add", f"./tests/data/plasmids_gb/{s.name}.gb"])


@skipIf(os.getenv('CI_PROJECT_ID') is not None, "Skipping auto add of gb file as in CI")
class TestAddGBFiles(BaseTestCase):

    def test_add_gb_file(self):
        input_part_factory = insillyclo.models.InputPartDataClassFactory()
        assembly_factory = insillyclo.models.AssemblyDataClassFactory()
        plasmid_factory = insillyclo.models.PlasmidDataClassFactory()
        data_source = insillyclo.data_source.DataSourceHardCodedImplementation()
        observer = insillyclo.observer.InSillyCloCliObserver(
            debug=False,
            fail_on_error=True,
        )
        input_parts_file = [
            self.test_data_dir / "DB_iP_typed.csv",
            self.test_data_dir / "DB_iP_not_typed.csv",
        ]
        for input_template_filled in [
            "template_01_mixed_ok.xlsx",
            "template_01_no_type_ok.xlsx",
            "template_01_ok.xlsx",
        ]:
            actually_run_add_gb_file(
                input_template_filled=self.test_data_dir / input_template_filled,
                input_part_factory=input_part_factory,
                assembly_factory=assembly_factory,
                plasmid_factory=plasmid_factory,
                gb_plasmids=(self.test_data_dir / "plasmids_gb").glob('*.gb'),
                observer=observer,
                input_parts_files=input_parts_file,
                data_source=data_source,
            )
