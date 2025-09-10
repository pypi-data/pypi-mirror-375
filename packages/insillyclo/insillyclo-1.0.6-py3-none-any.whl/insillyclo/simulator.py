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

import bisect
import copy
import csv
import json
import logging
import pathlib
from datetime import datetime
from operator import itemgetter
from typing import Set, Tuple, List, Iterable, Dict, Collection, NamedTuple

import Bio.SeqIO
import Bio.SeqRecord
import itertools
import sbol2
from Bio.Seq import Seq
from Bio.SeqFeature import FeatureLocation
from Bio.SeqRecord import SeqRecord

import insillyclo.conf
import insillyclo.data_source
import insillyclo.digestion
import insillyclo.dilution
import insillyclo.gel
import insillyclo.models
import insillyclo.observer
import insillyclo.parser
import insillyclo.cli_utils
from insillyclo import additional_exception


def primer_id_pairs_to_primer_with_seq(
    *,
    primer_id_pairs: Collection[Tuple[str, str]],
    primers_file: pathlib.Path | str,
    observer: insillyclo.observer.InSillyCloObserver,
) -> Collection[insillyclo.models.PCRPrimerPair]:
    if not primer_id_pairs:
        return []
    primer_ids = dict((f, None) for f, r in primer_id_pairs)
    primer_ids.update(dict((r, None) for f, r in primer_id_pairs))
    with open(primers_file, "r") as input_parts_file_stream:
        delimiter = insillyclo.cli_utils.get_csv_delimiter(input_parts_file_stream)
        csr_reader = csv.reader(input_parts_file_stream, delimiter=delimiter)
        header = next(csr_reader)
        if len(header) != 2:
            logging.warning(f"Expecting two columns file for primers_file such as \"primerId;sequence\": {header}")
        for row in csr_reader:
            try:
                if primer_ids[row[0]] is not None:
                    logging.info(f"Duplicated primer in {primers_file}: {primer_ids[row[0]]}")
                primer_ids[row[0]] = row[1].replace(' ', '').strip()
            except KeyError:
                # not needed
                pass
    err = []
    ret = []
    for f, r in primer_id_pairs:
        forward_primer = primer_ids[f]
        reverse_primer = primer_ids[r]
        if forward_primer is None:
            err.append(f"Primer sequence not found in {primers_file} for '{f}'")
        if reverse_primer is None:
            err.append(f"Primer sequence not found in {primers_file} for '{r}'")
        elif forward_primer is not None:
            ret.append(insillyclo.models.PCRPrimerPair(f, forward_primer, r, reverse_primer))
    if err:
        err = ', '.join(err)
        logging.warning(err)
        if observer.is_fail_on_error():
            raise additional_exception.PrimerNotFound(err)
    return ret


def extract_needed_input_parts(
    plasmids: List[insillyclo.models.Plasmid],
) -> Set[Tuple[str, str | None]]:
    ip_name_set = set()
    for plasmid in plasmids:
        for ip_instance, ip in plasmid.parts:
            for interpretation in ip.get_possible_interpretation(ip_instance):
                for interpreted, part_type in interpretation:
                    ip_name_set.add((interpreted, part_type))
    return ip_name_set


def fetch_gb_for_input_parts(
    needed_input_parts: Set[Tuple[str, str | None]],
    input_parts_files: Collection[str | pathlib.Path],
    gb_plasmids: Iterable[pathlib.Path],
    observer: insillyclo.observer.InSillyCloObserver,
) -> Dict[Tuple[str, str | None], Bio.SeqRecord.SeqRecord]:
    """

    :param needed_input_parts: a set of tuple (part_name, part_type) that are needed by plasmids
    :param input_parts_files: a csv file containing translation between part id and tuple (part_name, part_type)
    :param gb_plasmids: a list of all available part in GeneBank file
    :param observer:
    :return:
    """
    # translate needed_input_parts into a set of pId needed
    needed_gb = dict()
    for input_parts_file in input_parts_files:
        with open(input_parts_file, "r") as input_parts_file_stream:
            delimiter = insillyclo.cli_utils.get_csv_delimiter(input_parts_file_stream)
            csr_reader = csv.reader(input_parts_file_stream, delimiter=delimiter)
            concentration_key = None
            header = next(csr_reader)
            if header[:3] == ['pID', 'Name', 'Type']:
                typed = True
                concentration_col = 3
            elif header[:2] == ['pID', 'Name']:
                typed = False
                concentration_col = 2
            else:
                observer.notify_invalide_parts_file(
                    row_id=0,
                    filepath=str(input_parts_file),
                    content=json.dumps(header),
                )
                raise additional_exception.InvalidePartFileHeader()
            if len(header) > concentration_col:
                if header[concentration_col] == "Mass Concentration":
                    concentration_key = 'mass_concentration'
                if header[concentration_col] == "Mol Concentration":
                    concentration_key = 'mol_concentration'
            for row in csr_reader:
                additional_info = list()
                concentration_value = None
                if concentration_key:
                    concentration_value = row[concentration_col].strip()
                    if concentration_value == '':
                        concentration_value = None
                    else:
                        concentration_value = float(concentration_value)
                if concentration_value:
                    additional_info.append((concentration_key, concentration_value))
                if typed:
                    part_n_type = (row[1].strip(), row[2].strip())
                else:
                    part_n_type = (row[1].strip(), None)
                if part_n_type in needed_input_parts:
                    filename = row[0]
                    if not filename.endswith('.gb'):
                        filename += '.gb'
                    needed_gb.setdefault(filename, list()).append((part_n_type, additional_info))

    # Build result dict to get sequence from a tuple (part_name, part_type)
    sequences = dict()
    for gb_plasmid in gb_plasmids:
        part_n_type = (gb_plasmid.stem, insillyclo.models.get_direct_identifier())
        if part_n_type in needed_input_parts:
            needed_gb.setdefault(gb_plasmid.name, list()).append((part_n_type, list()))
        try:
            part_n_types_needing_it = needed_gb[gb_plasmid.name]
            seq = Bio.SeqIO.read(gb_plasmid, 'genbank')
            for part_n_type_n_info, additional_info in part_n_types_needing_it:
                part_n_type = (part_n_type_n_info[0], part_n_type_n_info[1])
                if seq.name in insillyclo.data_source.INVALIDE_SEQUENCE_NAMES:
                    seq.name = gb_plasmid.stem
                sequences[part_n_type] = seq
                for k, v in additional_info:
                    seq.annotations[k] = v
        except KeyError:
            # gb file not needed
            pass
        except ValueError as e:
            raise ValueError(f'{e.args[0]} on {gb_plasmid.absolute()}', e)

    return sequences


def override_from_concentration_file_and_update(
    sequences: Dict[Tuple[str, str | None], Bio.SeqRecord.SeqRecord],
    concentration_file: str | pathlib.Path | None,
    observer: insillyclo.observer.InSillyCloObserver,
):
    if concentration_file is None:
        return
    concentrations = []
    use_plasmid_id = itemgetter(0)
    delimiter = ';'
    try:
        with open(concentration_file, "r") as stream:
            delimiter = insillyclo.cli_utils.get_csv_delimiter(stream)
            csr_reader = csv.reader(stream, delimiter=delimiter)
            header = next(csr_reader)
            if header != ['pID', 'Mass Concentration']:
                observer.notify_invalide_parts_file(
                    row_id=0,
                    filepath=str(concentration_file),
                    content=json.dumps(header),
                )
                raise additional_exception.InvalidePartFileHeader()
            for row in csr_reader:
                concentrations.append(row)
    except (FileNotFoundError, StopIteration):
        pass
    for seq in sequences.values():
        pos = bisect.bisect_left(concentrations, seq.name, key=use_plasmid_id)
        if pos == len(concentrations) or use_plasmid_id(concentrations[pos]) != seq.name:
            concentrations.insert(pos, (seq.name, ''))
        elif pos < len(concentrations) and concentrations[pos][1] != '' and concentrations[pos][0] == seq.name:
            seq.annotations['mass_concentration'] = float(concentrations[pos][1])
    for seq in sequences.values():
        pos = bisect.bisect_left(concentrations, seq.name, key=use_plasmid_id)
        if pos < len(concentrations) and 'mass_concentration' in seq.annotations and concentrations[pos][0] == seq.name:
            concentrations[pos] = (seq.name, str(float(seq.annotations['mass_concentration'])))

    with open(concentration_file, mode='w', newline='') as stream:
        csvwriter = csv.writer(stream, delimiter=delimiter)
        csvwriter.writerow(['pID', 'Mass Concentration'])
        for concentration in concentrations:
            csvwriter.writerow(concentration)


class PlasmidInstancePart(NamedTuple):
    part_instance: str
    input_part: insillyclo.models.InputPart
    chosen_interpretation: List[Tuple[str, str | None]]
    sequences: List[Bio.SeqRecord.SeqRecord]
    fragments: List[insillyclo.digestion.FragmentsInOutSensAntiSens]


def instantiate_plasmid_to_assemble(
    plasmid: insillyclo.models.Plasmid,
    available_sequence: Dict[Tuple[str, str | None], Bio.SeqRecord.SeqRecord],
    assembly: insillyclo.models.Assembly,
    data_source: insillyclo.data_source.AbstractDataSource,
    observer: insillyclo.observer.InSillyCloObserver,
) -> (str, List[PlasmidInstancePart]):
    """
    From a given plasmid, the available sequences and the assembly aimed, the fonction produce the plasmid name
    and the list of sequence needed to produce it.
    :param plasmid:
    :param available_sequence:
    :param assembly:
    :param data_source:
    :param observer:
    :return:
    """
    full_name_part = []
    parts_n_sequence = list()
    for part_instance, input_part in plasmid.parts:
        seqs = None
        chosen_interpretation = None
        fragments = None
        for interpretation in input_part.get_possible_interpretation(part_instance):
            try:
                seqs = list()
                for part_n_type in interpretation:
                    seqs.append(available_sequence[part_n_type])
                if len(interpretation) == 1 and interpretation[0][1] == insillyclo.models.get_direct_identifier():
                    observer.notify_input_part_name_used_as_identifier(
                        plasmid.plasmid_id, input_part.name, interpretation[0][0]
                    )

                fragments = insillyclo.digestion.get_fragments(seqs, assembly.enzyme, data_source)
                chosen_interpretation = interpretation
                break
            except KeyError:
                # a part_n_type does not have an associated gb file, this interpretation cannot be used
                pass
        if chosen_interpretation is None:
            observer.notify_missing_sequence_for_input_part(plasmid.plasmid_id, part_instance)
            raise additional_exception.MissingSequenceForInputPart()
        assert len(chosen_interpretation) == len(fragments), "fragment set should be found for each interpretation"
        parts_n_sequence.append(PlasmidInstancePart(part_instance, input_part, chosen_interpretation, seqs, fragments))

        if input_part.in_output_name:
            full_name_part.extend([n for n, t in chosen_interpretation])
    return assembly.separator.join(full_name_part), parts_n_sequence


def assemble(
    plasmid_parts: List[PlasmidInstancePart],
    hint: str = "in_sens",
) -> str:
    """
    assemble the part, assuming that the first part have to be interpreted as inside and read in sens
    :param hint: which fragment should be used for the first part
    :param plasmid_parts:
    :return:
    """
    # TODO test with all hint
    output_sequence = ""
    for part in plasmid_parts:
        for interpretation, part_fragments in itertools.zip_longest(part.chosen_interpretation, part.fragments):
            overhang = output_sequence[-4:]
            if output_sequence == "" and hint == "in_sens" or overhang == part_fragments.in_sens[0:4]:
                output_sequence = output_sequence + part_fragments.in_sens[4:]
            elif output_sequence == "" and hint == "in_antisens" or overhang == part_fragments.in_antisens[0:4]:
                output_sequence = output_sequence + part_fragments.in_antisens[4:]
            elif output_sequence == "" and hint == "out_sens" or overhang == part_fragments.out_sens[0:4]:
                output_sequence = output_sequence + part_fragments.out_sens[4:]
            elif output_sequence == "" and hint == "out_antisens" or overhang == part_fragments.out_antisens[0:4]:
                output_sequence = output_sequence + part_fragments.out_antisens[4:]
            else:
                # TODO test with part that cannot be assembled
                raise additional_exception.PlasmidAssemblingFailure(
                    f"Cannot assemble part  {interpretation[0]}, no matching fragment overhang {overhang}"
                )

    if (
        hint == "in_sens"
        and output_sequence[-4:] != plasmid_parts[0].fragments[0].in_sens[0:4]
        or hint == "in_antisens"
        and output_sequence[-4:] != plasmid_parts[0].fragments[0].in_antisens[0:4]
        or hint == "out_sens"
        and output_sequence[-4:] != plasmid_parts[0].fragments[0].out_sens[0:4]
        or hint == "out_antisens"
        and output_sequence[-4:] != plasmid_parts[0].fragments[0].out_antisens[0:4]
    ):
        # TODO test it
        raise additional_exception.PlasmidAssemblingFailure(f"Cannot assemble last part with first one")
    return output_sequence


def assemble_to_seq_record(
    plasmid: insillyclo.models.Plasmid,
    part_to_assemble: List[PlasmidInstancePart],
    plasmid_name: str,
) -> SeqRecord:
    sequence = Seq(assemble(part_to_assemble))
    record = SeqRecord(
        sequence,
        id=plasmid.plasmid_id,
        name=plasmid.plasmid_id,
        description=plasmid_name,
        annotations={
            "molecule_type": "dna",
            "topology": "circular",
            "date": datetime.now(),
            "comment": f"Generated using InSillyClo {insillyclo.__version__}",
        },
    )
    features_dict = dict()
    for part in part_to_assemble:
        for seq_part in part.sequences:
            for feature in seq_part.features:
                seq_feature = seq_part.seq[feature.location.start : feature.location.end]
                position = sequence.find(seq_feature)
                if position != -1:
                    new_feature = copy.copy(feature)
                    new_feature.location = FeatureLocation(
                        start=position,
                        end=position + len(seq_feature),
                        strand=feature.location.strand,
                    )
                    features_dict[str(new_feature)] = new_feature
    for new_feature in features_dict.values():
        record.features.append(new_feature)
    return record


class SimulationOutput(NamedTuple):
    plasmid_ids: List[pathlib.Path]
    dilutions: Dict[str, List[pathlib.Path]]


def compute_all(
    *,
    input_template_filled: pathlib.Path,
    settings: insillyclo.conf.InSillyCloConfig | None,
    input_parts_files: Collection[str | pathlib.Path],
    gb_plasmids: Iterable[pathlib.Path],
    enzyme_names: Collection[str] | None = None,
    default_mass_concentration: float | None = None,
    concentration_file: pathlib.Path = None,
    output_dir: pathlib.Path,
    primer_id_pairs: Collection[Tuple[str, str]] = None,
    primers_file: pathlib.Path = None,
    data_source,
    observer: insillyclo.observer.InSillyCloObserver,
    default_output_plasmid_volume: float | None = None,
    enzyme_and_buffer_volume: float | None = None,
    minimal_remaining_well_volume: float | None = None,
    puncture_volume_10x: float | None = None,
    minimal_puncture_volume: float | None = None,
    expected_concentration_in_output: float | None = None,
    sbol_export: bool = False,
    target_dilutions: List[str] | None = None,
) -> SimulationOutput:
    output = SimulationOutput([], dict())
    if settings is None:
        settings = insillyclo.conf.InSillyCloConfig()
    assembly, plasmids = insillyclo.parser.parse_assembly_and_plasmid_from_template(
        input_template_filled,
        input_part_factory=insillyclo.models.InputPartDataClassFactory(),
        assembly_factory=insillyclo.models.AssemblyDataClassFactory(),
        plasmid_factory=insillyclo.models.PlasmidDataClassFactory(),
        observer=observer,
    )
    if primer_id_pairs:
        primer_pairs = primer_id_pairs_to_primer_with_seq(
            primer_id_pairs=primer_id_pairs,
            primers_file=primers_file,
            observer=observer,
        )
    else:
        primer_pairs = []

    if sbol_export:
        sbol2.Config.setOption('validate', False)
        sbol_doc = sbol2.Document()
    else:
        sbol_doc = None

    needed_input_parts = extract_needed_input_parts(plasmids)
    input_parts_gb_mapping = fetch_gb_for_input_parts(
        needed_input_parts=needed_input_parts,
        input_parts_files=input_parts_files,
        gb_plasmids=gb_plasmids,
        observer=observer,
    )
    override_from_concentration_file_and_update(
        sequences=input_parts_gb_mapping,
        concentration_file=concentration_file,
        observer=observer,
    )
    produced_plasmids = []
    wells = []
    plasmids_dilution_info = list()
    for plasmid in plasmids:
        plasmid_name, part_to_assemble = instantiate_plasmid_to_assemble(
            plasmid=plasmid,
            available_sequence=input_parts_gb_mapping,
            assembly=assembly,
            data_source=data_source,
            observer=observer,
        )
        record = assemble_to_seq_record(plasmid, part_to_assemble, plasmid_name)
        output_plasmid_path = output_dir / f'{plasmid.plasmid_id}.gb'
        output.plasmid_ids.append(output_plasmid_path)
        with open(output_plasmid_path, 'w') as gb_file:
            Bio.SeqIO.write(record, gb_file, "genbank")

        if sbol_doc:
            cd = sbol2.ComponentDefinition(record.id)
            cd.sequence = sbol2.Sequence(record.id, str(record.seq))
            cd.description = record.description
            sbol_doc.addComponentDefinition(cd)

        insillyclo.gel.enzyme_digestion_to_gel(
            filename=output_dir / f'{plasmid.plasmid_id}-digestion.svg',
            plasmids=[
                (plasmid.plasmid_id, record),
            ],
            enzyme_names=enzyme_names,
            observer=observer,
        )
        well_sequences = [
            (record, True),
        ]
        for p in part_to_assemble:
            for f in p.fragments:
                well_sequences.extend(
                    [
                        (f.out_sens, False),
                        (f.in_sens, False),
                        (f.out_antisens, False),
                        (f.in_antisens, False),
                    ]
                )
        wells.append(
            well := insillyclo.models.PCRWell(
                name=plasmid.plasmid_id,
                sequences=well_sequences,
                primers=primer_pairs,
            )
        )
        insillyclo.gel.pcr_amplification_to_gel(
            filename=output_dir / f'{plasmid.plasmid_id}-pcr.svg',
            wells=[well],
            observer=observer,
        )

        produced_plasmids.append((plasmid, part_to_assemble, record))

        used_sequences = []
        for p in part_to_assemble:
            used_sequences.extend(p.sequences)
        plasmids_dilution_info.append(
            insillyclo.dilution.PlasmidDilutionInfo(
                plasmid_id=plasmid.plasmid_id,
                used_sequences=used_sequences,
            )
        )

    with open(output_dir / f'DB_produced_plasmid.csv', mode='w', newline='') as csv_file:
        produced_plasmids_csv = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        produced_plasmids_csv.writerow(['pID', 'Name', 'Type'])
        for plasmid, _, sequence in produced_plasmids:
            produced_plasmids_csv.writerow([plasmid.plasmid_id, sequence.description, plasmid.output_type])
        del produced_plasmids_csv

    with open(output_dir / f'auto-gg-combination-to-make.csv', mode='w', newline='') as csv_file:
        combination_to_make_csv = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for plasmid, part_to_assemble, sequence in produced_plasmids:
            combination_to_make = [sequence.name, sequence.description]
            for part in part_to_assemble:
                for seq in part.sequences:
                    combination_to_make.append(seq.name)
            combination_to_make_csv.writerow(combination_to_make)
        del combination_to_make_csv

    insillyclo.gel.enzyme_digestion_to_gel(
        filename=output_dir / f'digestion.svg',
        plasmids=[(plasmid.plasmid_id, record) for plasmid, _, record in produced_plasmids],
        enzyme_names=enzyme_names,
        observer=observer,
    )
    insillyclo.gel.pcr_amplification_to_gel(
        filename=output_dir / f'pcr.svg',
        # plasmids=produced_plasmids,
        # primer_pairs=primer_pairs,
        wells=wells,
        observer=observer,
    )

    has_mass_concentration = default_mass_concentration is not None
    if not has_mass_concentration:
        for ip in input_parts_gb_mapping.values():
            if ip.annotations.get('mass_concentration', None):
                has_mass_concentration = True
                break

    if has_mass_concentration:
        dilutions = insillyclo.dilution.compute_all_dilutions(
            plasmids_dilution_info,
            settings=settings,
            puncture_volume_10x=puncture_volume_10x,
            output_plasmid_expected_volume=default_output_plasmid_volume,
            enzyme_and_buffer_volume=enzyme_and_buffer_volume,
            minimum_remaining_volume_for_10x_intermediate_dilution=minimal_remaining_well_volume,
            minimal_puncture_volume=minimal_puncture_volume,
            default_mass_concentration=default_mass_concentration,
            expected_concentration_in_output=expected_concentration_in_output,
            target_dilutions=target_dilutions,
            observer=observer,
        )
        for dilution_strategy, dilution in dilutions.items():
            for expected_format in [
                'json',
                'csv',
            ]:
                dilution_file = output_dir / f'dilution-{dilution_strategy}.{expected_format}'
                dilution = insillyclo.dilution.round_dilution_spec(
                    specs=dilution,
                    ndigits=settings.nb_digits_rounding,
                )
                insillyclo.dilution.write_dilution_spec(
                    filename=dilution_file,
                    specs=dilution,
                    output_format=expected_format,
                )
                output.dilutions.setdefault(dilution_strategy, []).append(dilution_file)

    if sbol_doc:
        sbol_doc.write(output_dir / f'plasmids.xml')
    return output
