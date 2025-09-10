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

from abc import ABC, abstractmethod
from typing import List, NamedTuple, Tuple

from insillyclo import additional_exception
from insillyclo import models


class Enzyme(NamedTuple):
    name: str
    site_for: str
    site_rev: str
    inter_s: int


class AbstractDataSource(ABC):
    @abstractmethod
    def get_enzymes(self) -> List[Enzyme]:
        pass

    @abstractmethod
    def get_enzyme_names(self) -> List[str]:
        pass

    @abstractmethod
    def get_enzyme_cut(self, name) -> Tuple[str, str, int]:
        """

        :param name:
        :return: A tuple site_for, site_rev and inter_s
        :exception raise additional_exception.EnzymeNotFound when enzyme is not found
        """
        pass

    @abstractmethod
    def get_separators(self) -> List[str]:
        pass


class DataSourceHardCodedImplementation(AbstractDataSource):

    def __init__(self):
        self._enzymes = [
            Enzyme(
                name='BsaI',
                site_for='GGTCTC',
                site_rev='GAGACC',
                inter_s=1,
            ),
            Enzyme(
                name='BsmBI',
                site_for='CGTCTC',
                site_rev='GAGACG',
                inter_s=1,
            ),
            Enzyme(
                name='BbsI',
                site_for='GAAGAC',
                site_rev='GTCTTC',
                inter_s=2,
            ),
            Enzyme(
                name='SapI',
                site_for='GCTCTTC',
                site_rev='GAAGAGC',
                inter_s=1,
            ),
        ]
        self._separators = models.ALLOWED_INPUT_PART_SEPARATOR

    def get_enzymes(self) -> List[Enzyme]:
        return self._enzymes.copy()

    def get_enzyme_cut(self, name) -> Tuple[str, str, int]:
        for e in self._enzymes:
            if e.name == name:
                return e.site_for, e.site_rev, e.inter_s
        raise additional_exception.EnzymeNotFound(f"Unknown enzyme {name}")

    def get_enzyme_names(self) -> List[str]:
        return [e.name for e in self._enzymes]

    def get_separators(self) -> List[str]:
        return self._separators.copy()


INVALIDE_SEQUENCE_NAMES = [
    '',
    'Exported',
]
