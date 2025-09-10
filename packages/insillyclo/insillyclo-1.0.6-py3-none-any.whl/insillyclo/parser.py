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

import json
import pathlib
import re
from json import JSONDecodeError
from typing import Tuple, List

import pandas as pd

import insillyclo.models
import insillyclo.observer
from insillyclo import additional_exception


def __na_nan_to_none(x):
    if x == "na":
        return None
    if x == "n.a.":
        return None
    if str(x) == "nan":
        return None
    # if x is None:
    #     return None
    return x


def __to_bool(x):
    return str(x).lower() in ["true", "t", "yes", "y"]


__part_types_re = re.compile(r"([a-zA-Z0-9]+)")


def parse_assembly_and_plasmid_from_template(
    input_template_filled: pathlib.Path | str,
    input_part_factory: insillyclo.models.InputPartFactory,
    assembly_factory: insillyclo.models.AssemblyFactory,
    plasmid_factory: insillyclo.models.PlasmidFactory,
    observer: insillyclo.observer.InSillyCloObserver,
    load_only_assembly: bool = False,
) -> Tuple[insillyclo.models.Assembly, List[insillyclo.models.Plasmid]]:
    df = pd.read_excel(input_template_filled, sheet_name=0, header=None)
    row_count, col_count = df.shape
    row_settings_header_row_id = df.index[df[0] == "Assembly settings"][0]
    row_composition_header_row_id = df.index[df[0] == "Assembly composition"][0]
    output_plasmid_header_row_id = df.index[df[0] == "Output plasmid id ↓"][0]

    assembly_name = None
    assembly_separator = None
    enzyme = None
    for i in range(row_settings_header_row_id + 1, min(row_count, row_composition_header_row_id)):
        if df.iloc[i, 0] == "Restriction enzyme":
            enzyme = __na_nan_to_none(df.iloc[i, 1])
        elif df.iloc[i, 0] == "Name":
            assembly_name = df.iloc[i, 1]
        elif df.iloc[i, 0] == "Output separator":
            assembly_separator = df.iloc[i, 1]
        elif df.iloc[i, 0] == "" or str(df.iloc[i, 0]) == "nan":
            break
        else:
            raise additional_exception.TemplateParsingFailure(f"Unknown settings '{df.iloc[i,0]}'")

    if enzyme is None:
        raise additional_exception.EnzymeNotFound("No enzyme found in Assembly settings")

    part_name_row_id = None
    part_types_row_id = None
    part_optional_row_id = None
    part_in_output_row_id = None
    part_separator_row_id = None
    for i in range(row_composition_header_row_id, row_count):
        key = str(df.iloc[i, 1])
        if not key.endswith(" ->"):
            break
        if key == "Part name ->":
            part_name_row_id = i
        elif key == "Part types ->":
            part_types_row_id = i
        elif key == "Is optional part ->":
            part_optional_row_id = i
        elif key == "Part name should be in output name ->":
            part_in_output_row_id = i
        # elif key == "Allowed number of subparts ->":
        #     allowed_subparts_row_id = i
        elif key == "Part separator ->":
            part_separator_row_id = i
    assert part_name_row_id is not None
    assert part_types_row_id is not None
    assert part_optional_row_id is not None
    assert part_in_output_row_id is not None
    assert part_separator_row_id is not None
    del i

    ips: list[insillyclo.models.InputPart] = list()
    for j in range(2, col_count):
        part_name = df.iloc[part_name_row_id, j]
        part_types_str = df.iloc[part_types_row_id, j]
        if __na_nan_to_none(part_types_str) is None:
            part_types = None
        else:
            try:
                part_types_str = str(part_types_str)
                part_types_str = __part_types_re.sub(r'"\1"', part_types_str)
                part_types_str = part_types_str.replace('"nan"', "null")
                part_types = json.loads('[' + part_types_str + ']')
            except JSONDecodeError as e:
                observer.notify_invalide_part_types(
                    part_name=part_name,
                    col_id=j,
                    content=part_types_str,
                )
                raise additional_exception.InvalidePartTypesExpression(e)

        # allowed_subpart_scheme = df.iloc[allowed_subparts_row_id, j]
        # if allowed_subpart_scheme == 'na':
        #     allowed_subpart_scheme = None
        # else:
        #     if type(allowed_subpart_scheme) == float:
        #         allowed_subpart_scheme = str(allowed_subpart_scheme).replace('.', ',')
        #     allowed_subpart_scheme = [int(s) for s in allowed_subpart_scheme.split(',')]
        ips.append(
            input_part_factory.create_input_part(
                name=part_name,
                part_types=part_types,
                is_optional=__to_bool(df.iloc[part_optional_row_id, j]),
                in_output_name=__to_bool(df.iloc[part_in_output_row_id, j]),
                # allowed_subpart_scheme=allowed_subpart_scheme,
                separator=__na_nan_to_none(df.iloc[part_separator_row_id, j]),
            )
        )
    del j

    assembly = assembly_factory.create_assembly(
        name=assembly_name,
        separator=assembly_separator,
        enzyme=enzyme,
        input_parts=ips,
    )

    if load_only_assembly:
        return assembly, []

    plasmids = list()
    for i in range(output_plasmid_header_row_id + 1, row_count):
        plasmid_id = df.iloc[i, 0]
        plasmid_type = df.iloc[i, 1]
        if str(plasmid_type) == "nan":
            plasmid_type = None
        parts = list()
        for j, ip in enumerate(ips, start=2):
            if str(df.iloc[i, j]) == "nan":
                if not ip.is_optional:
                    observer.notify_missing_input_part(
                        plasmid_id=plasmid_id,
                        row_id=i,
                        content=ip.name,
                    )
                    if observer.is_fail_on_error:
                        raise additional_exception.MissingInputPart()
            input_part = df.iloc[i, j]
            if str(input_part) == "nan":
                continue
            # as the getter raise an exception if incompatible, we test by calling it
            ip.get_possible_interpretation(input_part)
            parts.append((input_part, ip))
        plasmid = plasmid_factory.create_plasmid(
            plasmid_id=plasmid_id,
            output_type=plasmid_type,
            parts=parts,
        )
        plasmids.append(plasmid)

    return assembly, plasmids
