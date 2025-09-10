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

import logging


class InSillyCloObserver(ABC):
    def __init__(
        self,
        *,
        debug: bool = False,
        fail_on_error: bool | None = None,
    ):
        super().__init__()
        self._debug = debug
        self._fail_on_error = fail_on_error if fail_on_error is not None else debug

    def is_debug(self) -> bool:
        return self._debug

    def is_fail_on_error(self) -> bool:
        return self._fail_on_error

    @abstractmethod
    def notify_missing_input_part(self, *, plasmid_id, row_id, content):
        pass

    @abstractmethod
    def notify_invalide_part_types(self, *, part_name, col_id, content):
        pass

    @abstractmethod
    def notify_invalide_parts_file(self, row_id: int, filepath: str, content: str):
        pass

    @abstractmethod
    def notify_missing_sequence_for_input_part(self, plasmid_id, input_part_name):
        pass

    @abstractmethod
    def notify_missing_mass_concentration(self, *, plasmid_id: str, input_plasmid_id: str):
        pass

    @abstractmethod
    def notify_skipped_dilution(self, plasmid_id, dilution_strategy: str, reason: str = None):
        pass

    @abstractmethod
    def notify_concentration_issue_for_dilution(self, plasmid_id, reason: str = None):
        pass

    @abstractmethod
    def notify_exceeded_produced_volume_with_dilution(
        self, *, plasmid_id: str, produced_volume: float, expected_volume: float, dilution_strategy: str
    ):
        pass

    @abstractmethod
    def notify_unknown_digestion_enzyme(self, *, enzyme_name: str):
        pass

    @abstractmethod
    def notify_input_part_name_used_as_identifier(self, plasmid_id: str, input_part: str, part_name: str):
        pass

    @abstractmethod
    def notify_csv_delimiter_not_found(self, input_files: str):
        pass


class InSillyCloCliObserver(InSillyCloObserver):
    def notify_concentration_issue_for_dilution(self, plasmid_id, reason: str = None):
        logging.error(f"[{plasmid_id}] Concentration issue: {reason}")

    def notify_exceeded_produced_volume_with_dilution(
        self,
        plasmid_id: str,
        produced_volume: float,
        expected_volume: float,
        dilution_strategy: str,
    ):
        logging.warning(
            f"[{plasmid_id}] Expected output volume cannot be respected with "
            f"dilution \"{dilution_strategy}\": {produced_volume:,.2f}>{expected_volume:,.2f}"
        )

    def notify_missing_sequence_for_input_part(self, plasmid_id, input_part_name):
        logging.error(
            f"[{plasmid_id}, {input_part_name}] "
            f"Cannot find sequence for any interpretation of part '{input_part_name}' for \"{plasmid_id}\""
        )

    def notify_invalide_parts_file(self, row_id: int, filepath: str, content: str):
        logging.error(f"[{row_id}] Invalid part file at row '{row_id}': \"{content}\" at {filepath}")

    def notify_invalide_part_types(self, *, part_name, col_id, content):
        logging.error(
            f"[{col_id},{part_name}] Could not parse part types '{content}' in part '{part_name}' at col {col_id}"
        )

    def notify_missing_input_part(self, *, plasmid_id, row_id, content):
        logging.error(
            f"[{row_id},{plasmid_id}] Missing input part for '{content}' in plasmid '{plasmid_id}' at row {row_id}"
        )

    def notify_missing_mass_concentration(self, *, plasmid_id: str, input_plasmid_id: str):
        logging.error(
            f"[{plasmid_id},{input_plasmid_id}] Missing mass concentration for plasmid '{input_plasmid_id}' while producing {plasmid_id}"
        )

    def notify_skipped_dilution(self, plasmid_id, dilution_strategy, reason="missing input plasmid concentration"):
        logging.error(f"[{plasmid_id}] Dilution \"{dilution_strategy}\" not computed for {plasmid_id} due to: {reason}")

    def notify_unknown_digestion_enzyme(self, *, enzyme_name: str):
        logging.error(f"Unknown digestion enzyme: \"{enzyme_name}\"")

    def notify_input_part_name_used_as_identifier(self, plasmid_id: str, input_part: str, part_name: str):
        logging.info(f"[{plasmid_id}] Part name {part_name!r} for {input_part!r} is used as an input plasmid filename")

    def notify_csv_delimiter_not_found(self, input_files: str):
        logging.info(f"Could not find csv delimiter for file {input_files}")
