#!/usr/bin/env python
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

import logging
import pathlib
from typing import Collection

import click

from insillyclo import (
    _version,
    conf,
    simulator,
    observer,
    template_generator,
    data_source,
    cli_utils,
)

settings = conf.InSillyCloConfig()
DEFAULT_PCR_FILENAME = 'primer-sequences.csv'
DEFAULT_CONCENTRATIONS_FILENAME = "input-plasmid-concentrations.csv"


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option(
    '--fail-on-error/--no-fail-on-error',
    is_flag=True,
    default=False,
    help='Stop execution with exit code 2 when error is detected.',
)
@click.version_option(_version.__version__)
@click.pass_context
def cli(
    ctx,
    debug: bool,
    fail_on_error: bool,
):
    ctx.obj = observer.InSillyCloCliObserver(
        debug=debug,
        fail_on_error=fail_on_error,
    )


@cli.command(
    help="Simulate golden gate assembly",
    context_settings={'show_default': True},
)
@click.option(
    '--input-template-filled',
    type=click.Path(),
    required=True,
    help='Where to find the template filled with plasmid you want to produce.',
)
@click.option(
    '--config',
    'config_file',
    type=click.Path(),
    default=conf.INSILLYCLO_INI,
    help='Override configuration options with the configuration file.',
)
@click.option(
    '--input-parts-file',
    type=click.Path(),
    required=False,
    multiple=True,
    help='File containing partID, name of each input part you have available. '
    'Can have a third column indicating its type.',
)
@click.option(
    '--plasmid-repository',
    type=click.Path(),
    required=True,
    help='Directory where the GenBank of your plasmid  can be found.',
)
@click.option(
    '-r',
    '--recursive-plasmid-repository',
    is_flag=True,
    default=False,
    help='Dig recursively in the gene bank directory.',
)
@click.option(
    '--default-mass-concentration',
    type=click.FLOAT,
    required=False,
    default=settings.default_mass_concentration,
    help='Default concentration to consider (ng/µL).',
)
@click.option(
    '--no-default-mass-concentration',
    is_flag=True,
    required=False,
    default=False,
    help='Default concentration should be set to None, i.e there is no default concentration.',
)
@click.option(
    '--plasmid-concentration-file',
    'concentration_file',
    type=click.Path(),
    required=False,
    default=None,
    help='A CSV file containing plasmid_id and the associated mass concentration. '
    'This file will be created/updated to contain at least all the plasmid that are used in the simulation.'
    f'Default to {DEFAULT_CONCENTRATIONS_FILENAME} in the output directory',
)
@click.option(
    '--output-plasmid-expected-volume',
    'output_plasmid_expected_volume',
    type=click.FLOAT,
    required=False,
    default=settings.output_plasmid_expected_volume,
    help='Default volume (µL) of the output plasmid to produce.',
)
@click.option(
    '--enzyme-and-buffer-volume',
    '--veb',
    type=click.FLOAT,
    required=False,
    default=settings.enzyme_and_buffer_volume,
    help='Volume (µL) of enzyme and buffer that have to be in each output plasmid well as recommended by the kit',
)
@click.option(
    '--minimal-tip-volume',
    'minimal_puncture_volume',
    type=click.FLOAT,
    required=False,
    default=settings.minimal_puncture_volume,
    help='Minimal volume (µL) allowed to be taken from any source (input plasmid, dilution, ...).',
)
@click.option(
    '--10x-minimal-remaining-well-volume',
    'minimal_remaining_well_volume',
    type=click.FLOAT,
    required=False,
    default=settings.minimum_remaining_volume_in_dilution,
    help='Minimal volume (µL) left in a well for 10x intermediate dilution, useful if use with robot.',
)
@click.option(
    '--10x-tip-volume',
    'puncture_volume_10x',
    type=click.FLOAT,
    required=False,
    default=settings.puncture_volume_10x,
    help='Volume (µL) taken from input plasmid, and expected to be taken from intermediate 10x dilution. '
    'Can be more, but always a multiple of the tip volume.',
)
@click.option(
    '--concentration-of-input-plasmid-in-output',
    'expected_concentration_in_output',
    type=click.FLOAT,
    required=False,
    default=settings.expected_concentration_in_output,
    help='Concentration (fmol/µL) of input plasmid in final dilutions.',
)
@click.option(
    '-o',
    '--output-dir',
    type=click.Path(),
    default='output/',
    help='Output directory to write all produce files.',
)
@click.option(
    '--restriction-enzyme-gel',
    '-e',
    type=click.STRING,
    required=False,
    multiple=True,
    default=[],
    help='Restriction enzyme used when producing digestion gel',
)
@click.option(
    '--primer-pair',
    type=click.STRING,
    required=False,
    multiple=True,
    default=[],
    help='A pair of PCR primer id used in gel validation. '
    'Multiple pairs may be provided. '
    'Primer id are translated to sequence thanks to --primers-file. '
    'Example: insillyclo simulate (...) --primer-pair P84,P190 --primer-pair P68,P_80 --primers-file my-primers.csv',
)
@click.option(
    '--primer-pairs',
    type=click.Path(),
    required=False,
    help='A csv file containing a pairs of pcr primers id that can be used in gel validation. '
    'Primer id are translated to sequence thanks to --primers-file.',
)
@click.option(
    '--primers-file',
    type=click.Path(),
    required=False,
    default=DEFAULT_PCR_FILENAME,
    help='A csv file containing for each row primerId, and its sequence.',
)
@click.option(
    '--sbol/--no-sbol',
    'sbol_export',
    help='Export plasmids in an SBOL file',
    default=False,
)
@click.pass_obj
def simulate(
    obs: observer.InSillyCloCliObserver,
    input_template_filled: str | pathlib.Path,
    config_file: str | pathlib.Path,
    input_parts_file: Collection[str | pathlib.Path],
    plasmid_repository: str | pathlib.Path,
    recursive_plasmid_repository: bool,
    sbol_export: bool,
    output_plasmid_expected_volume: float | None = None,
    enzyme_and_buffer_volume: float | None = None,
    minimal_remaining_well_volume: float | None = None,
    puncture_volume_10x: float | None = None,
    minimal_puncture_volume: float | None = None,
    concentration_file: str | pathlib.Path | None = None,
    default_mass_concentration: float | None = None,
    no_default_mass_concentration: bool = False,
    expected_concentration_in_output: float | None = None,
    output_dir: str | pathlib.Path = './output/',
    restriction_enzyme_gel: Collection[str] | None = None,
    primer_pair: Collection[str | pathlib.Path] | None = None,
    primer_pairs: str | pathlib.Path = None,
    primers_file: str | pathlib.Path = None,
):
    input_template_filled = pathlib.Path(input_template_filled)
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if obs.is_debug():
        logging.getLogger().setLevel(logging.DEBUG)
    logging.info(f"Debug mode is {'on' if obs.is_debug() else 'off'}")
    input_parts_files = [pathlib.Path(f) for f in input_parts_file]
    if not input_parts_file:
        logging.info(
            f"No input part file provided, all part in template must specify a plasmid identifier (filename) "
            f"that can be found in the plasmid_repository"
        )
    plasmid_repository = pathlib.Path(plasmid_repository)
    if recursive_plasmid_repository:
        gb_plasmids = plasmid_repository.glob('**/*.gb')
    else:
        gb_plasmids = plasmid_repository.glob('*.gb')

    primer_id_pairs = set()
    if primer_pair is not None:
        for pair in primer_pair:
            f, r = pair.split(',')
            primer_id_pairs.add((f, r))
    if primer_pairs:
        primer_id_pairs |= cli_utils.parse_primer_pairs(primer_pairs)

    if concentration_file is None:
        concentration_file = output_dir / DEFAULT_CONCENTRATIONS_FILENAME

    settings_overridden = conf.InSillyCloConfig(config_file)
    if no_default_mass_concentration:
        default_mass_concentration = None
        settings_overridden.update_settings("default_mass_concentration", None)

    simulator.compute_all(
        input_template_filled=input_template_filled,
        settings=settings_overridden,
        input_parts_files=input_parts_files,
        gb_plasmids=gb_plasmids,
        default_mass_concentration=default_mass_concentration,
        concentration_file=concentration_file,
        output_dir=output_dir,
        data_source=data_source.DataSourceHardCodedImplementation(),
        enzyme_names=restriction_enzyme_gel,
        primer_id_pairs=primer_id_pairs,
        primers_file=primers_file,
        default_output_plasmid_volume=output_plasmid_expected_volume,
        enzyme_and_buffer_volume=enzyme_and_buffer_volume,
        minimal_remaining_well_volume=minimal_remaining_well_volume,
        puncture_volume_10x=puncture_volume_10x,
        minimal_puncture_volume=minimal_puncture_volume,
        expected_concentration_in_output=expected_concentration_in_output,
        sbol_export=sbol_export,
        observer=obs,
    )


@click.argument(
    'destination_template_path',
    type=click.Path(),
    required=False,
    default="template.xlsx",
)
@click.option(
    '--input-part',
    '-p',
    type=click.STRING,
    required=False,
    multiple=True,
    help='Name of the input parts you want in your template. Incompatible with --nb-input-parts.',
)
@click.option(
    '--nb-input-parts',
    '-b',
    type=click.INT,
    required=False,
    help='Number of input parts you want in your template. Incompatible with --input-parts.',
)
@click.option(
    '--separator',
    '-s',
    type=click.STRING,
    required=False,
    help='Default separator to set in the generated template.',
)
@click.option(
    '--restriction-enzyme-goldengate',
    '--enzyme',
    '-e',
    type=click.STRING,
    required=False,
    help='Enzyme to use in the generated template.',
)
@click.option(
    '--name',
    '-n',
    type=click.STRING,
    required=False,
    help='Assembly name used in the generated template.',
)
@cli.command(
    help="Generate an xlsx template to DESTINATION_TEMPLATE_PATH",
)
@click.pass_context
def template(
    obs: observer.InSillyCloCliObserver,
    destination_template_path: str | pathlib.Path,
    input_part: Collection[str],
    nb_input_parts: int,
    restriction_enzyme_goldengate: str,
    separator: str,
    name: str,
):
    assert nb_input_parts is None or len(input_part) == 0, "Cannot use both --nb-input-parts and --input-part"
    if not (input_part or nb_input_parts or restriction_enzyme_goldengate or separator or name):
        logging.warning("No option provided, generating default template. Use insillyclo template --help for more info")
        nb_input_parts = 6
    if nb_input_parts is not None:
        input_part = [f'InputPart{i}' for i in range(1, 1 + nb_input_parts)]
    template_generator.make_template(
        observer=obs,
        destination_file=destination_template_path,
        ip_names=input_part,
        data_source=data_source.DataSourceHardCodedImplementation(),
        default_separator=separator,
        enzyme=restriction_enzyme_goldengate,
        name=name,
    )


@cli.command(
    help="Utility to set inSillyClo options, locally or globally",
    context_settings={'show_default': True},
)
@click.option(
    '--global',
    'global_config',
    is_flag=True,
    required=False,
    default=False,
    help='Save settings globally, not only for the current directory',
)
@click.option(
    '--config',
    'local_config_dir_or_file',
    type=click.Path(),
    default=None,
    required=False,
    help='Directory containing the local config file, or the file itself.',
)
@click.option(
    '-l',
    '--list',
    'list_values',
    is_flag=True,
    default=False,
    help='List all variables set in config file(s), along with their values, and exit.',
)
@click.option(
    '--default-mass-concentration',
    type=click.FLOAT,
    required=False,
    default=settings.default_mass_concentration,
    help='Default concentration to consider (ng/µL).',
)
@click.option(
    '--no-default-mass-concentration',
    is_flag=True,
    required=False,
    default=False,
    help='Default concentration should be set to None, i.e there is no default concentration.',
)
@click.option(
    '--output-plasmid-expected-volume',
    type=click.FLOAT,
    required=False,
    default=settings.output_plasmid_expected_volume,
    help='Default volume (µL) of the output plasmid to produce.',
)
@click.option(
    '--enzyme-and-buffer-volume',
    '--veb',
    type=click.FLOAT,
    required=False,
    default=settings.enzyme_and_buffer_volume,
    help='Volume (µL) of enzyme and buffer that have to be in each output plasmid well as recommended by the kit',
)
@click.option(
    '--minimal-tip-volume',
    'minimal_puncture_volume',
    type=click.FLOAT,
    required=False,
    default=settings.minimal_puncture_volume,
    help='Minimal volume (µL) allowed to be taken from any source (input plasmid, dilution, ...).',
)
@click.option(
    '--10x-minimal-remaining-well-volume',
    'minimum_remaining_volume_in_dilution',
    type=click.FLOAT,
    required=False,
    default=settings.minimum_remaining_volume_in_dilution,
    help='Minimal volume (µL) left in a well for 10x intermediate dilution, useful if use with robot.',
)
@click.option(
    '--10x-tip-volume',
    'puncture_volume_10x',
    type=click.FLOAT,
    required=False,
    default=settings.puncture_volume_10x,
    help='Volume (µL) taken from input plasmid, and expected to be taken from intermediate 10x dilution. '
    'Can be more, but always a multiple of the tip volume.',
)
@click.option(
    '--concentration-of-input-plasmid-in-output',
    'expected_concentration_in_output',
    type=click.FLOAT,
    required=False,
    default=settings.expected_concentration_in_output,
    help='Concentration (fmol/µL) of input plasmid in final dilutions.',
)
@click.option(
    '--nb-digits-rounding',
    'nb_digits_rounding',
    type=click.FLOAT,
    required=False,
    default=settings.nb_digits_rounding,
    help='The default number of digit to keep after comma. Set to None to prevent rounding.',
)
@click.option(
    '--no-nb-digits-rounding',
    is_flag=True,
    required=False,
    default=False,
    help='Set nb-digits-rounding to None, so no rounding is done.',
)
def config(
    global_config: bool = False,
    local_config_dir_or_file: str | pathlib.Path = '.',
    list_values: bool = False,
    output_plasmid_expected_volume: float | None = None,
    no_default_mass_concentration: bool = False,
    enzyme_and_buffer_volume: float | None = None,
    minimum_remaining_volume_in_dilution: float | None = None,
    puncture_volume_10x: float | None = None,
    minimal_puncture_volume: float | None = None,
    default_mass_concentration: float | None = None,
    expected_concentration_in_output: float | None = None,
    nb_digits_rounding: int | None = None,
    no_nb_digits_rounding: bool = False,
):
    if global_config:
        assert local_config_dir_or_file is None, "Cannot use both --nb-input-parts and --input-part"
        current_config_file = None
    else:
        local_config_dir_or_file = pathlib.Path(local_config_dir_or_file or '.')
        if local_config_dir_or_file.is_dir():
            current_config_file = local_config_dir_or_file / conf.INSILLYCLO_INI
        else:
            current_config_file = local_config_dir_or_file
    current_settings = conf.InSillyCloConfig(current_config_file)
    if list_values:
        for k, v in current_settings.read_config():
            print(k, v, sep='=')
        return

    if output_plasmid_expected_volume:
        current_settings.update_settings("output_plasmid_expected_volume", output_plasmid_expected_volume)
    if enzyme_and_buffer_volume:
        current_settings.update_settings("enzyme_and_buffer_volume", enzyme_and_buffer_volume)
    if minimum_remaining_volume_in_dilution:
        current_settings.update_settings("minimum_remaining_volume_in_dilution", minimum_remaining_volume_in_dilution)
    if puncture_volume_10x:
        current_settings.update_settings("puncture_volume_10x", puncture_volume_10x)
    if minimal_puncture_volume:
        current_settings.update_settings("minimal_puncture_volume", minimal_puncture_volume)
    if no_default_mass_concentration:
        current_settings.update_settings("default_mass_concentration", None)
    elif default_mass_concentration:
        current_settings.update_settings("default_mass_concentration", default_mass_concentration)
    if expected_concentration_in_output:
        current_settings.update_settings("expected_concentration_in_output", expected_concentration_in_output)
    if no_nb_digits_rounding:
        current_settings.update_settings("nb_digits_rounding", None)
    elif nb_digits_rounding:
        current_settings.update_settings("nb_digits_rounding", nb_digits_rounding)

    current_settings.save(global_config=global_config)


if __name__ == '__main__':
    cli()
