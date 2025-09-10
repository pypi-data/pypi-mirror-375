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
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, NamedTuple

from Bio.SeqRecord import SeqRecord

from insillyclo import additional_exception

ALLOWED_INPUT_PART_SEPARATOR = [
    ',',
    '-',
    '_',
    '.',
    '~',
    ':',
    ';',
    '/',
    '\\',
    '\'',
    '+',
    '=',
]

_DIRECT_IDENTIFIER = "__DIRECT_IDENTIFIER__"


def get_direct_identifier() -> str:
    return _DIRECT_IDENTIFIER


@dataclass
class InputPart:
    name: str
    part_types: None | List[str | List[str]]
    is_optional: bool
    in_output_name: bool
    separator: str | None

    @property
    def part_types_str(self):
        if self.part_types is None:
            return ''
        return ','.join(json.dumps(t).replace('"', '') for t in self.part_types)

    def is_valid(self) -> bool:
        try:
            self.is_valid_raising()
        except additional_exception.InvalidePartTypesException:
            return False
        return True

    def is_valid_raising(self):
        if self.separator is None and self.part_types is None:
            return
        if self.separator is None and (len(self.part_types) > 1 or not isinstance(self.part_types[0], str)):
            raise additional_exception.MissingSeparatorInPartTypesDeclaration(f"Missing types in part {self.name}")
        if self.part_types is None:
            return
        for part in self.part_types:
            if type(part) == str:
                continue
            elif type(part) == list:
                for e in part:
                    if type(e) != str:
                        raise additional_exception.InvalidePartTypesExpression()
            else:
                raise additional_exception.InvalidePartTypesExpression()

    def get_possible_interpretation(self, ip_instance: str) -> List[List[Tuple[str, str | None]]]:
        if self.separator is None:
            return [
                [(ip_instance, self.part_types[0] if self.part_types else None)],
                [(ip_instance, _DIRECT_IDENTIFIER)],
            ]
        interpreted = ip_instance.split(self.separator)
        if self.part_types is None:
            return [
                [(ip_instance, None)],
                [(sub, None) for sub in interpreted],
                [(ip_instance, _DIRECT_IDENTIFIER)],
            ]
        possible_interpretation = list()
        for part_type in self.part_types:
            if type(part_type) == str:
                possible_interpretation.append([(ip_instance, part_type)])
            elif type(part_type) == list:
                if len(part_type) == len(interpreted):
                    possible_interpretation.append(list(itertools.zip_longest(interpreted, part_type)))
        possible_interpretation.append(
            [(ip_instance, _DIRECT_IDENTIFIER)],
        )
        return possible_interpretation


class InputPartFactory(ABC):
    @staticmethod
    @abstractmethod
    def create_input_part(
        name: str,
        part_types: List[List[str]],
        is_optional: bool,
        in_output_name: bool,
        separator: str | None,
    ) -> InputPart:
        pass


class InputPartDataClassFactory(InputPartFactory):
    @staticmethod
    def create_input_part(
        name: str,
        part_types: List[List[str]],
        is_optional: bool,
        in_output_name: bool,
        separator: str | None,
    ):
        # print(
        #     name,
        #     part_types,
        #     is_optional,
        #     in_output_name,
        #     separator,
        # )
        if separator is not None and separator not in ALLOWED_INPUT_PART_SEPARATOR:
            raise additional_exception.InvalidePartTypesSeparator()

        ip = InputPart(
            name,
            part_types,
            is_optional,
            in_output_name,
            separator,
        )
        ip.is_valid_raising()
        return ip


@dataclass
class Assembly:
    name: str
    enzyme: str
    separator: str
    input_parts: list


class AssemblyFactory(ABC):
    @staticmethod
    @abstractmethod
    def create_assembly(
        name: str,
        enzyme: str,
        separator: str,
        input_parts: list,
    ):
        pass


class AssemblyDataClassFactory(AssemblyFactory):
    @staticmethod
    def create_assembly(
        name: str,
        enzyme: str,
        separator: str,
        input_parts: list,
    ):
        # print(
        #     name,
        #     enzyme,
        #     separator,
        #     input_parts,
        # )
        return Assembly(
            name,
            enzyme,
            separator,
            input_parts,
        )


@dataclass
class Plasmid:
    plasmid_id: str
    output_type: str | None
    parts: List[Tuple[str, InputPart]]


class PlasmidFactory(ABC):
    @staticmethod
    @abstractmethod
    def create_plasmid(
        plasmid_id: str,
        output_type: str | None,
        parts: list,
    ):
        pass


class PlasmidDataClassFactory(PlasmidFactory):
    @staticmethod
    def create_plasmid(
        plasmid_id: str,
        output_type: str | None,
        parts: list,
    ):
        # print(
        #     plasmid_id,
        #     output_type,
        #     parts,
        # )
        return Plasmid(
            plasmid_id,
            output_type,
            parts,
        )


class PCRPrimerPair(NamedTuple):
    forward_id: str
    forward_seq: str
    reverse_id: str
    reverse_seq: str

    def __repr__(self):
        return f'({self.forward_id},{self.reverse_id})'


class PCRWell(NamedTuple):
    """
    A representation of a PCR well that contains primers, target sequences, and a descriptive name.

    Attributes:
        primers (List[PCRPrimerPair]): A list of primer pairs used in the PCR well.
        sequences (List[tuple[SeqRecord | str, bool]]): A list of tuples containing target sequences,
        and if they are expected (True) ou only possible (False) such as remaining fragments
        name (str): A descriptive name for the well
    """

    primers: List[PCRPrimerPair]
    sequences: List[tuple[SeqRecord | str, bool]]
    name: str
