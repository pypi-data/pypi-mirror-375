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
from dataclasses import dataclass

import math
import pathlib
from functools import reduce, cmp_to_key
from typing import List, Dict, NamedTuple, Any, Tuple

import Bio.SeqRecord
import Bio.SeqUtils

import insillyclo.additional_exception
import insillyclo.conf
import insillyclo.models
import insillyclo.observer

_DILUTION_STRATEGY_KEY_10X = '10x'

_DILUTION_STRATEGY_KEY_DIRECT = 'direct'
_POST_PROCESS_STRATEGY_KEY_MASTER_MIX = 'mastermix'


DILUTION_STRATEGIES = [
    _DILUTION_STRATEGY_KEY_DIRECT,
    f'{_DILUTION_STRATEGY_KEY_DIRECT}_{_POST_PROCESS_STRATEGY_KEY_MASTER_MIX}',
    _DILUTION_STRATEGY_KEY_10X,
    f'{_DILUTION_STRATEGY_KEY_10X}_{_POST_PROCESS_STRATEGY_KEY_MASTER_MIX}',
]


def optional_dilution(func):
    def wrapper(
        dilution_strategy_key: str = None,
        dilutions: Tuple[str, list[PlasmidDilutionSpec]] = None,
        post_process_strategy_key: str = None,
        target_dilutions=None,
        *args,
        **kwargs,
    ):
        assert len(args) == 0, "use only named arguments"
        if target_dilutions is None:
            target_dilutions = DILUTION_STRATEGIES
        if dilution_strategy_key:
            # called with a dilution algorithm
            kwargs['dilution_strategy_key'] = dilution_strategy_key
        elif dilutions and post_process_strategy_key:
            # called with a post process algorithm
            kwargs['dilutions'] = dilutions
            kwargs['post_process_strategy_key'] = post_process_strategy_key
            dilution_strategy_key = f'{dilutions[0]}_{post_process_strategy_key}'
        if dilution_strategy_key in target_dilutions and (
            post_process_strategy_key is None or dilutions is not None and dilutions[1] is not None
        ):
            ret = func(
                *args,
                **kwargs,
            )
        else:
            ret = (dilution_strategy_key, None)
        return ret

    return wrapper


class UsedPart(NamedTuple):
    part: insillyclo.models.InputPart
    sequence: Bio.SeqRecord.SeqRecord


class PlasmidDilutionInfo(NamedTuple):
    plasmid_id: str
    used_sequences: List[Bio.SeqRecord.SeqRecord]


@dataclass
class PlasmidDilutionSpec:
    plasmid_id: str
    h2o_volume: float
    ip_volumes: Dict[str, float]
    time_used: int


def prepare_mol_concentration(
    *,
    plasmids_dilution_info: List[PlasmidDilutionInfo],
    default_mass_concentration: float | None,
    observer: insillyclo.observer.InSillyCloObserver,
):

    ip_usage_count: Dict[str, Dict[str, Any]] = dict()
    for info in plasmids_dilution_info:
        # dilutions.append(plasmid_dilution := dict())
        for sequence in info.used_sequences:
            try:
                ip_usage_count[sequence.name]["count"] += 1
            except KeyError:
                try:
                    ip_mol_concentration = sequence.annotations['mol_concentration']  # femtomol/µL
                except KeyError:
                    ip_molecular_weight = Bio.SeqUtils.molecular_weight(
                        sequence,
                        seq_type="DNA",
                        double_stranded=True,
                        circular=True,
                    )  # Da == g/mol
                    ip_molecular_weight *= 10**9 / 10**15  # ng/femtomol #
                    ip_mass_concentration = sequence.annotations.get(
                        'mass_concentration', default_mass_concentration
                    )  # ng/µL
                    if ip_mass_concentration is None:
                        observer.notify_missing_mass_concentration(
                            input_plasmid_id=sequence.name, plasmid_id=info.plasmid_id
                        )
                        continue
                    ip_mol_concentration = ip_mass_concentration / ip_molecular_weight  # femtomol/µL
                ip_usage_count[sequence.name] = dict(
                    count=1,
                    ip_mol_concentration=ip_mol_concentration,
                )
    return ip_usage_count


@optional_dilution
def compute_minimalist_equimolar_dilutions(
    *,
    plasmids_dilution_info: List[PlasmidDilutionInfo],
    ip_usage_count: Dict[str, Dict[str, Any]],
    observer: insillyclo.observer.InSillyCloObserver,
    output_plasmid_expected_volume: float,  # = 10,  # microL
    enzyme_and_buffer_volume: float,  # = 1,  # microL
    input_plasmid_minimal_puncture_volume: float,  # = 1,
    expected_concentration_in_output: float,  # = 10,  # femtomol/µL
    dilution_strategy_key: str,
) -> Tuple[str, list[PlasmidDilutionSpec]]:
    direct_dilutions = list()
    for info in plasmids_dilution_info:
        try:
            max_ip_mol_concentration = max(
                ip_usage_count[sequence.name]["ip_mol_concentration"] for sequence in info.used_sequences
            )
        except (KeyError, ValueError):
            observer.notify_skipped_dilution(plasmid_id=info.plasmid_id, dilution_strategy=dilution_strategy_key)
            continue

        # Get how much plasmid we will have in fmol ...
        plasmid_expected_fmol = max_ip_mol_concentration * input_plasmid_minimal_puncture_volume
        # ... while it must be at least minimum_fmol_in_dilution
        plasmid_expected_fmol = max(
            plasmid_expected_fmol,
            expected_concentration_in_output * output_plasmid_expected_volume,
        )

        if plasmid_expected_fmol > (expected_concentration_in_output * output_plasmid_expected_volume):
            observer.notify_concentration_issue_for_dilution(
                plasmid_id=info.plasmid_id,
                reason=f"Final plasmid concentration raised to satisfy minimal puncture volume requirement"
                f"(from {expected_concentration_in_output * output_plasmid_expected_volume} "
                f"to {plasmid_expected_fmol:0.2f}). ",
            )

        oP_volume = enzyme_and_buffer_volume
        ip_volumes = dict(
            buffer=enzyme_and_buffer_volume,
        )
        for sequence in info.used_sequences:
            direct_ip_volume = plasmid_expected_fmol / ip_usage_count[sequence.name]['ip_mol_concentration']
            oP_volume += direct_ip_volume
            ip_volumes[sequence.name] = direct_ip_volume

        h2o_volume = output_plasmid_expected_volume - oP_volume
        if h2o_volume < 0:
            observer.notify_exceeded_produced_volume_with_dilution(
                plasmid_id=info.plasmid_id,
                produced_volume=oP_volume,
                expected_volume=output_plasmid_expected_volume,
                dilution_strategy=dilution_strategy_key,
            )
        plasmid_dilution = PlasmidDilutionSpec(
            plasmid_id=info.plasmid_id,
            h2o_volume=h2o_volume,
            ip_volumes=ip_volumes,
            time_used=1,
        )
        direct_dilutions.append(plasmid_dilution)

        del plasmid_expected_fmol
    return dilution_strategy_key, direct_dilutions


@optional_dilution
def compute_10x_dilutions(
    *,
    plasmids_dilution_info: List[PlasmidDilutionInfo],
    ip_usage_count: Dict[str, Dict[str, Any]],
    observer: insillyclo.observer.InSillyCloObserver,
    output_plasmid_expected_volume: float,  # = 10,  # microL
    enzyme_and_buffer_volume: float,  # = 1,  # microL
    puncture_volume_10x: float,  # = 1,
    minimal_puncture_volume: float,  # = 0.2,
    minimum_remaining_volume_for_10x_intermediate_dilution: float,  # = 1,  # microL
    expected_concentration_in_output: float,  # = 10,  # femtomol/µL
    dilution_strategy_key: str,
    nb_reaction_more: int = 0,
) -> Tuple[str, list[PlasmidDilutionSpec]]:
    if minimal_puncture_volume > puncture_volume_10x:
        raise insillyclo.additional_exception.InvalideParameterValue(
            "Minimal tip volume can be greater than tip from intermediate dilution"
        )
    d10x_dilutions = list()

    # Compute the theoretical intermediate concentration of input plasmid so that addition of puncture_volume_10x
    # in output_plasmid_expected_volume results in minimal_concentration_in_dilution_and_output
    theory_10x_ip_mol_concentration = (
        expected_concentration_in_output * output_plasmid_expected_volume / puncture_volume_10x
    )

    # Check that we have enough plasmid concentration to perform the intermediate (10x) dilution
    for plasmid_id, ip_usage in ip_usage_count.items():
        if ip_usage['ip_mol_concentration'] < theory_10x_ip_mol_concentration:
            observer.notify_concentration_issue_for_dilution(
                plasmid_id=plasmid_id,
                reason="Input plasmid mol concentration is lower than requested to perform 10x dilution. "
                "h2o dilution set to 0 µL, mix using this plasmid will be not equimolar.",
            )

    for ip_name, usage in ip_usage_count.items():
        # mass conservation: same mol ion punctured ip, and 10x diluted
        # usage['ip_mol_concentration'] * puncture_volume_10x
        # == min_10x_ip_mol_concentration * (puncture_volume_10x+ d10x_h2o_volume)
        d10x_h2o_volume = (
            usage['ip_mol_concentration'] * puncture_volume_10x / theory_10x_ip_mol_concentration - puncture_volume_10x
        )
        if d10x_h2o_volume < 0:
            # concentration was not enough, so h2o become negative, we set it to 0. We do not warn as there already
            # has been a warning on the concentration issue.
            d10x_h2o_volume = 0

        # min_10x_ip_mol_concentration can have been raised due to low amount of plasmid in a 10x dilution.
        # We thus might not have enough dilution, we do a ratio, round it to higher µL
        time_used = usage['count']
        if nb_reaction_more > 0 and usage['count'] == len(plasmids_dilution_info):
            time_used += nb_reaction_more

        factor = math.ceil(
            (time_used * puncture_volume_10x + minimum_remaining_volume_for_10x_intermediate_dilution)
            / (d10x_h2o_volume + puncture_volume_10x)
        )
        # if the minimal tip volume for water is higher than what we need, we increase make more 10x dilution
        # should we notify that concentration of ip is close to min concentration, and thus cause issue with min tip ?
        if d10x_h2o_volume == 0:
            factor_min_tip = 1
        else:
            factor_min_tip = math.ceil(minimal_puncture_volume / round(d10x_h2o_volume, 8))

        if factor_min_tip > 4:
            observer.notify_concentration_issue_for_dilution(
                plasmid_id=ip_name,
                reason="Concentration is too close to intermediate expected concentration "
                "which lead to picking less water than the minimal tip volume",
            )
        else:
            factor = max(factor, factor_min_tip)
        plasmid_dilution = PlasmidDilutionSpec(
            plasmid_id=f'{ip_name}__10x__',
            h2o_volume=d10x_h2o_volume * factor,
            ip_volumes={ip_name: puncture_volume_10x * factor},
            time_used=usage['count'],
        )
        d10x_dilutions.append(plasmid_dilution)
    for info in plasmids_dilution_info:
        try:
            for sequence in info.used_sequences:
                assert ip_usage_count[sequence.name]
        except KeyError:
            observer.notify_skipped_dilution(plasmid_id=info.plasmid_id, dilution_strategy=dilution_strategy_key)
            continue
        # dilutions.append(plasmid_dilution := dict())
        ip_volumes = dict(
            buffer=enzyme_and_buffer_volume,
        )
        for sequence in info.used_sequences:
            ip_volumes[f'{sequence.name}__10x__'] = puncture_volume_10x
        h2o_volume = (
            output_plasmid_expected_volume - enzyme_and_buffer_volume - puncture_volume_10x * len(info.used_sequences)
        )
        if h2o_volume < 0:
            observer.notify_exceeded_produced_volume_with_dilution(
                plasmid_id=info.plasmid_id,
                produced_volume=puncture_volume_10x * len(info.used_sequences) + enzyme_and_buffer_volume,
                expected_volume=output_plasmid_expected_volume,
                dilution_strategy=dilution_strategy_key,
            )
        plasmid_dilution = PlasmidDilutionSpec(
            plasmid_id=info.plasmid_id,
            h2o_volume=h2o_volume,
            ip_volumes=ip_volumes,
            time_used=1,
        )
        d10x_dilutions.append(plasmid_dilution)
    return dilution_strategy_key, d10x_dilutions


@optional_dilution
def master_mix(
    dilutions: Tuple[str, list[PlasmidDilutionSpec]],
    post_process_strategy_key: str,
) -> Tuple[str, list[PlasmidDilutionSpec]]:
    dilution_strategy_key, dilutions = dilutions
    inputs = set()
    final_dilution_count = 0
    # get all plasmid and buffer used as input
    for dilution in dilutions:
        inputs.update(list(dilution.ip_volumes.items()))
    for dilution in dilutions:
        if 'buffer' in dilution.ip_volumes.keys():
            # keep only one used in final dilution (keep as is intermediate 10x dilution for example)
            # as using items we also look at the volume used : we must use the same amount of each
            inputs = inputs.intersection(list(dilution.ip_volumes.items()))
            final_dilution_count += 1

    # the master mix is the sum of all the input used in all final dilution
    mm_dilution = PlasmidDilutionSpec(
        plasmid_id=_POST_PROCESS_STRATEGY_KEY_MASTER_MIX,
        h2o_volume=0,
        ip_volumes=dict([(k, v * final_dilution_count) for k, v in inputs]),
        time_used=final_dilution_count,
    )
    master_mix_volume_to_use = sum([v for _, v in inputs])
    # prepare the new dilutions
    new_dilutions: list[PlasmidDilutionSpec] = [
        mm_dilution,
    ]
    for dilution in dilutions:
        if 'buffer' in dilution.ip_volumes.keys():
            # if a final mix, replace input used by the mastermix
            ip_volumes = dict([(k, v) for k, v in dilution.ip_volumes.items() if k not in mm_dilution.ip_volumes])
            ip_volumes[_POST_PROCESS_STRATEGY_KEY_MASTER_MIX] = master_mix_volume_to_use
        else:
            # just copy intermediate dilutions
            ip_volumes = dict([(k, v) for k, v in dilution.ip_volumes.items()])

        new_dilutions.append(
            PlasmidDilutionSpec(
                plasmid_id=dilution.plasmid_id,
                h2o_volume=dilution.h2o_volume,
                ip_volumes=ip_volumes,
                time_used=dilution.time_used,
            )
        )
    return f'{dilution_strategy_key}_{post_process_strategy_key}', new_dilutions


def _write_dilution_spec_json(
    filename: str | pathlib.Path,
    fieldnames: List[str],
    specs: List[Dict[str, float | str]],
):
    with open(filename, 'w') as f:
        json.dump(
            specs,
            fp=f,
            indent=4,
        )


def _write_dilution_spec_csv(
    filename: str | pathlib.Path,
    fieldnames: List[str],
    specs: List[Dict[str, float | str]],
):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()  # Write header row
        writer.writerows(specs)  # Write data rows


__firsts = ['buffer', 'mastermix']


def alpha_10x_after(a: str, b: str) -> int:
    if a == b:
        return 0
    if a in __firsts:
        try:
            if __firsts.index(a) < __firsts.index(b):
                return -1
            return 1
        except ValueError:
            pass
        return -1
    if b in __firsts:
        return 1
    if a.endswith('__10x__') and not b.endswith('__10x__'):
        return -1
    if not a.endswith('__10x__') and b.endswith('__10x__'):
        return 1
    if a < b:
        return -1
    return 1


def alpha_10x_after_get(a: Dict, b: Dict) -> int:
    return alpha_10x_after(a['plasmid_id'], b['plasmid_id'])


def write_dilution_spec(
    filename: str | pathlib.Path,
    specs: List[PlasmidDilutionSpec],
    output_format: str = "json",
):
    fieldnames = [
        'plasmid_id',
        'h2o_volume',
    ] + sorted(
        reduce(lambda x, y: x.union(y), [set(spec.ip_volumes.keys()) for spec in specs], set()),
        key=cmp_to_key(alpha_10x_after),
    )
    dict_specs = [
        dict(
            plasmid_id=spec.plasmid_id,
            h2o_volume=spec.h2o_volume,
            **spec.ip_volumes,
        )
        for spec in specs
    ]
    dict_specs = sorted(dict_specs, key=cmp_to_key(alpha_10x_after_get))
    if output_format == "json":
        return _write_dilution_spec_json(filename, fieldnames, dict_specs)
    if output_format == "csv":
        return _write_dilution_spec_csv(filename, fieldnames, dict_specs)
    raise NotImplementedError(output_format)


def round_dilution_spec(
    specs: list[PlasmidDilutionSpec],
    ndigits: int | None,
):
    if ndigits is None:
        return specs
    for spec in specs:
        spec.h2o_volume = round(spec.h2o_volume, ndigits=ndigits)
        for k, v in spec.ip_volumes.items():
            if isinstance(v, float):
                spec.ip_volumes[k] = round(v, ndigits=ndigits)
    return specs


def compute_all_dilutions(
    plasmids_dilution_info: List[PlasmidDilutionInfo],
    settings: insillyclo.conf.InSillyCloConfig,
    default_mass_concentration: float | None,
    enzyme_and_buffer_volume: float | None,
    observer: insillyclo.observer.InSillyCloObserver,
    output_plasmid_expected_volume: float,  # = 10,  # microL
    minimal_puncture_volume: float,  # = 1,
    puncture_volume_10x: float,  # = 1,
    minimum_remaining_volume_for_10x_intermediate_dilution: float,  # = 1,  # microL
    expected_concentration_in_output: float,  # = 10,  # femtomol/µL
    target_dilutions: List[str] | None,
) -> Dict[str, list[PlasmidDilutionSpec]]:
    if default_mass_concentration is None:
        default_mass_concentration = settings.default_mass_concentration
    if output_plasmid_expected_volume is None:
        output_plasmid_expected_volume = settings.output_plasmid_expected_volume
    if enzyme_and_buffer_volume is None:
        enzyme_and_buffer_volume = settings.enzyme_and_buffer_volume
    if minimal_puncture_volume is None:
        minimal_puncture_volume = settings.minimal_puncture_volume
    if puncture_volume_10x is None:
        puncture_volume_10x = settings.puncture_volume_10x
    if minimum_remaining_volume_for_10x_intermediate_dilution is None:
        minimum_remaining_volume_for_10x_intermediate_dilution = settings.minimum_remaining_volume_in_dilution
    if expected_concentration_in_output is None:
        expected_concentration_in_output = settings.expected_concentration_in_output

    ip_usage_count = prepare_mol_concentration(
        plasmids_dilution_info=plasmids_dilution_info,
        default_mass_concentration=default_mass_concentration,
        observer=observer,
    )
    for plasmid_id, ip_usage in ip_usage_count.items():
        if ip_usage['ip_mol_concentration'] < expected_concentration_in_output:
            observer.notify_concentration_issue_for_dilution(
                plasmid_id,
                reason="Input plasmid mol concentration is lower than requested minimal mol concentration",
            )

    nb_reaction_more = 0
    if not target_dilutions:
        augmented_target_dilutions = None
        nb_reaction_more = 1
    else:
        # if we ask only for a post-processed dilution we still have to do it, so augmented to do list with this algo
        augmented_target_dilutions = set(target_dilutions)
        for target_dilution in target_dilutions:
            split = list(target_dilution.split(_POST_PROCESS_STRATEGY_KEY_MASTER_MIX))
            if len(split) == 2 and split[1] == '':
                augmented_target_dilutions.add(split[0][:-1])
                # master mix is used, will need nb_reaction+1 on intermediate dilution
                nb_reaction_more = 1
        augmented_target_dilutions = list(augmented_target_dilutions)

    direct_dilution = compute_minimalist_equimolar_dilutions(
        plasmids_dilution_info=plasmids_dilution_info,
        ip_usage_count=ip_usage_count,
        observer=observer,
        output_plasmid_expected_volume=output_plasmid_expected_volume,
        enzyme_and_buffer_volume=enzyme_and_buffer_volume,
        input_plasmid_minimal_puncture_volume=minimal_puncture_volume,
        expected_concentration_in_output=expected_concentration_in_output,
        dilution_strategy_key=_DILUTION_STRATEGY_KEY_DIRECT,
        target_dilutions=augmented_target_dilutions,
    )

    dilution_10x = compute_10x_dilutions(
        plasmids_dilution_info=plasmids_dilution_info,
        ip_usage_count=ip_usage_count,
        observer=observer,
        output_plasmid_expected_volume=output_plasmid_expected_volume,
        enzyme_and_buffer_volume=enzyme_and_buffer_volume,
        puncture_volume_10x=puncture_volume_10x,
        minimal_puncture_volume=minimal_puncture_volume,
        minimum_remaining_volume_for_10x_intermediate_dilution=minimum_remaining_volume_for_10x_intermediate_dilution,
        expected_concentration_in_output=expected_concentration_in_output,
        dilution_strategy_key=_DILUTION_STRATEGY_KEY_10X,
        target_dilutions=augmented_target_dilutions,
        nb_reaction_more=nb_reaction_more,
    )

    direct_dilution_mm = master_mix(
        dilutions=direct_dilution,
        post_process_strategy_key=_POST_PROCESS_STRATEGY_KEY_MASTER_MIX,
        target_dilutions=augmented_target_dilutions,
    )

    dilution_10x_mm = master_mix(
        dilutions=dilution_10x,
        post_process_strategy_key=_POST_PROCESS_STRATEGY_KEY_MASTER_MIX,
        target_dilutions=augmented_target_dilutions,
    )

    return dict(
        (k, v)
        for k, v in [
            direct_dilution,
            direct_dilution_mm,
            dilution_10x,
            dilution_10x_mm,
        ]
        if v is not None and (target_dilutions is None or k in target_dilutions)
    )
