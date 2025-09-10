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

import pathlib
from typing import Collection, List

import xlsxwriter
import xlsxwriter.utility

import insillyclo.data_source
import insillyclo.models
import insillyclo.observer
from insillyclo import additional_exception


def make_template(
    *,
    destination_file: pathlib.Path,
    ip_names: Collection[str] = None,
    input_parts: Collection[insillyclo.models.InputPart] = None,
    observer: insillyclo.observer.InSillyCloObserver,
    data_source: insillyclo.data_source.AbstractDataSource,
    default_plasmid: List[str] = None,
    default_separator: str = "",
    enzyme: str = "",
    name: str = "",
):
    if default_separator and default_separator not in data_source.get_separators():
        raise additional_exception.InvalidePartTypesSeparator(
            f"Invalide separator {default_separator!r} only the following are allowed {data_source.get_separators()}"
        )
    if enzyme:
        data_source.get_enzyme_cut(enzyme)

    assert ip_names is None or input_parts is None, "Cannot provide both ip_names and input_parts"
    if not input_parts:
        input_parts = list()
        for id_name, ip_name in enumerate(ip_names, 2):
            input_parts.append(
                insillyclo.models.InputPart(
                    name=ip_name,
                    part_types=[str(id_name - 1)],
                    is_optional=False,
                    in_output_name=True,
                    separator=default_separator,
                )
            )
        del ip_names
    for input_part in input_parts:
        input_part.is_valid_raising()

    workbook = xlsxwriter.Workbook(destination_file)
    worksheet = workbook.add_worksheet()
    worksheet.protect()

    # Add a format for the header cells.
    editable_header_format_dict = {
        # "border": 1,
        "bg_color": "#C6EFCE",
        "bold": False,
        "text_wrap": False,
        "valign": "vcenter",
        "align": "center",
        "locked": False,
        # "indent": 1,
    }
    editable_header_format = workbook.add_format(editable_header_format_dict)
    big_header_format_dict = {
        "bg_color": "#C6EFFF",
        "bold": True,
        "text_wrap": True,
        "valign": "vcenter",
        "align": "center",
        "locked": True,
        # "indent": 1,
    }
    big_header_format = workbook.add_format(big_header_format_dict)
    readonly_header_format_dict = {
        # "border": 1,
        "bg_color": "#C6EFFF",
        "bold": True,
        "text_wrap": True,
        "valign": "vcenter",
        "locked": True,
        "indent": 1,
    }
    readonly_header_format = workbook.add_format(readonly_header_format_dict)
    readonly_header_centered_format_dict = {
        "bg_color": "#C6EFFF",
        "valign": "vcenter",
        "align": "center",
        "locked": False,
    }
    readonly_header_centered_format = workbook.add_format(readonly_header_centered_format_dict)
    border_lr = workbook.add_format({'left': 1, 'right': 1, 'locked': False})
    unlocked = workbook.add_format({'locked': False})
    worksheet.set_column('A:XDF', None, unlocked)
    worksheet.set_row(0, 32)
    worksheet.set_column("A:A", 20, unlocked)
    worksheet.set_column("B:B", 40, unlocked)
    worksheet.set_column(f"C:{xlsxwriter.utility.xl_col_to_name(len(input_parts) + 2)}", 20, unlocked)
    worksheet.write("A1", "Assembly settings", big_header_format)
    worksheet.write("A2", "Restriction enzyme", readonly_header_format)
    worksheet.write("A3", "Name", readonly_header_format)
    worksheet.write("A4", "Output separator", readonly_header_format)
    worksheet.write("B2", enzyme, editable_header_format)
    worksheet.write("B3", name, editable_header_format)
    worksheet.write("B4", default_separator, editable_header_format)

    composition_row = 9
    worksheet.write(f"A{composition_row+0}", "Assembly composition", big_header_format)
    worksheet.write(f"B{composition_row+0}", "Part name ->", readonly_header_format)
    worksheet.write(f"B{composition_row+1}", "Part types ->", readonly_header_format)
    worksheet.write(f"B{composition_row+2}", "Is optional part ->", readonly_header_format)
    worksheet.write(f"B{composition_row+3}", "Part name should be in output name ->", readonly_header_format)
    worksheet.write(f"B{composition_row+4}", "Part separator ->", readonly_header_format)
    worksheet.write(f"A{composition_row+5}", "Output plasmid id ↓", readonly_header_format)
    worksheet.write(f"B{composition_row+5}", "OutputType (optional) ↓", readonly_header_format)

    for id_name, input_part in enumerate(input_parts, 2):
        letter = xlsxwriter.utility.xl_col_to_name(id_name)
        worksheet.write(f"{letter}{composition_row+0}", input_part.name, editable_header_format)
        worksheet.write(f"{letter}{composition_row+1}", input_part.part_types_str, editable_header_format)
        worksheet.write(f"{letter}{composition_row+2}", str(input_part.is_optional), editable_header_format)
        worksheet.write(f"{letter}{composition_row+3}", str(input_part.in_output_name), editable_header_format)
        worksheet.write(f"{letter}{composition_row+4}", input_part.separator, editable_header_format)
        worksheet.write(f"{letter}{composition_row+5}", "↓", readonly_header_centered_format)
    worksheet.data_validation(
        f"C{composition_row+2}:Z{composition_row+3}",
        {
            "validate": "list",
            "source": ["True", "False"],
        },
    )
    worksheet.data_validation(
        "B2",
        {
            "validate": "list",
            "source": data_source.get_enzyme_names(),
        },
    )
    for area in [
        "B4",
        f"C{composition_row+4}:Z{composition_row+4}",
    ]:
        worksheet.data_validation(
            area,
            {
                "validate": "list",
                "source": data_source.get_separators(),
            },
        )
    worksheet.freeze_panes(composition_row + 5, 2)

    for c in range(2 + len(input_parts)):
        letter = xlsxwriter.utility.xl_col_to_name(c)
        for r in range(composition_row + 6, composition_row + 46):
            worksheet.write(f"{letter}{r}", "", border_lr)

    for j, content in enumerate(default_plasmid if default_plasmid is not None else ["pID001"]):
        letter = xlsxwriter.utility.xl_col_to_name(j)
        worksheet.write(f"{letter}{composition_row+6}", content, border_lr)

    workbook.close()
