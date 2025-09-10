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
import csv
import logging
import pathlib
from typing import Collection, Tuple

from insillyclo import additional_exception


def is_csv_empty(input_file) -> bool:
    try:
        reader = csv.reader(input_file)
        for row in reader:
            if any(cell.strip() for cell in row):
                input_file.seek(0)
                return False
        input_file.seek(0)
        return True
    except:
        input_file.seek(0)
        raise


def get_csv_delimiter(input_file) -> str:

    if is_csv_empty(input_file):
        return ';'

    try:
        sniffer = csv.Sniffer()
        echantillon = input_file.read(2048)
        input_file.seek(0)
        dialecte = sniffer.sniff(echantillon)
        return dialecte.delimiter
    except:
        input_file.seek(0)
        raise additional_exception.InvalidDelimiterCSV(input_file)


def parse_primer_pairs(primer_pairs: pathlib.Path) -> Collection[Tuple[str, str]]:
    with open(primer_pairs, 'r') as f:
        delimiter = get_csv_delimiter(f)
        csv_reader = csv.reader(f, delimiter=delimiter)
        header = next(csv_reader)
        if len(header) != 2:
            logging.warning(f"Expecting two columns file for primers_file such as \"forward;reverse\": {header}")
            if len(header) < 2:
                raise additional_exception.InvalidePrimerFile(primer_pairs)
        for row in csv_reader:
            yield row[0], row[1]
