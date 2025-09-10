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
import math
from typing import List, Tuple, Collection

import Bio.Restriction
import cairo
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

import insillyclo.models
import insillyclo.observer
import insillyclo.additional_exception

__all_enzymes = {enzyme.__name__: enzyme for enzyme in Bio.Restriction.AllEnzymes}


def get_biopython_enzyme(name: str):
    return __all_enzymes[name]


def produce_gel_image(
    *,
    filename,
    plasmids: List[Tuple[str, List[tuple[int, bool]]]],
    thin_markers=None,
    markers_bold=None,
    text: str = None,
):
    filename = str(filename)
    height = 500
    # print(max_weight)
    if thin_markers is None:
        # DNA marker for gel simulation
        thin_markers = [
            250,
            500,
            750,
            1000,
            1500,
            2000,
            2500,
            3000,
            3500,
            4000,
            5000,
            6000,
            8000,
            10000,
        ]
    if markers_bold is None:
        markers_bold = [1000, 3000, 6000]
    markers_bold = set(markers_bold)
    thin_markers = set(thin_markers) - markers_bold
    max_weight = max(
        *[max([w for w, _ in weights]) for _, weights in plasmids if weights],
        *thin_markers,
        *markers_bold,
    )
    max_weight_log = math.log(max_weight)
    min_weight_log = math.log(min(*thin_markers, *markers_bold))
    width = 150 + len(plasmids) * 120
    with cairo.SVGSurface(filename, width, height) as surface:
        ctx = cairo.Context(surface)
        ctx.set_font_size(15)
        ctx.set_source_rgb(0, 0, 0)
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        max_legend_width = ctx.text_extents(str(max_weight))[2]

        for markers, line_width in [(thin_markers, 2), (markers_bold, 5)]:
            ctx.set_line_width(line_width)
            for marker in markers:
                s_marker = str(marker)
                y = _weight_to_y(height, marker, max_weight_log, min_weight_log)
                ctx.move_to(50, y)
                ctx.line_to(100, y)
                ctx.stroke()
                # ctx.set_line_width(0.04)
                ctx.move_to(5 + max_legend_width - ctx.text_extents(s_marker)[2], y + 6)
                ctx.show_text(s_marker)
                ctx.stroke()
        del markers, marker

        if text:
            # ctx.set_source_rgba(1, 1, 1, 1)
            # ctx.rectangle(-5, height - 70, 150, 90)
            # ctx.fill()

            ctx.set_source_rgb(0, 0, 0)
            y_text = height - 55
            text = text.strip()
            start = 0
            end = len(text)
            while start < end:
                end = text.find('\n', start, end)
                if end == -1:
                    end = len(text)
                while ctx.text_extents(text[start:end])[2] > 145:
                    end = text.rfind(' ', start, end)
                if y_text >= height - 20:
                    text = text[start:].replace('\n', '')
                    start = 0
                    end = len(text)
                # ctx.set_source_rgba(1, 1, 1, 1)
                # ctx.rectangle(
                #     3,
                #     y_text - ctx.text_extents(text[start:end])[3],
                #     ctx.text_extents(text[start:end])[2] + 4,
                #     18,
                # )
                # ctx.fill()
                # ctx.set_source_rgba(0, 0, 0)
                ctx.move_to(5, y_text)
                ctx.show_text(text[start:end].strip())
                ctx.stroke()
                start = end + 1
                end = len(text)
                y_text += 17

        for p_id, (plasmid, weights) in enumerate(plasmids):
            x = 150 + p_id * 120

            ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_source_rgb(0, 0, 0)
            text_width = ctx.text_extents(plasmid)[2]
            ctx.move_to(x + 40 - text_width / 2, height - 20)
            ctx.show_text(plasmid)
            ctx.stroke()
            for weight, expected in weights:
                if expected:
                    ctx.set_line_width(4)
                    ctx.set_source_rgb(0, 0, 0)
                else:
                    ctx.set_line_width(2)
                    ctx.set_source_rgb(0.85, 0.85, 0.85)
                y = _weight_to_y(height, weight, max_weight_log, min_weight_log)
                ctx.move_to(x, y)
                ctx.line_to(x + 80, y)
                ctx.stroke()

                if expected:
                    weight_str = str(weight)
                    ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                    text_width, text_height = ctx.text_extents(weight_str)[2:4]
                    ctx.move_to(x + 40 - text_width / 2, y - text_height / 2)
                    ctx.show_text(weight_str)
                    ctx.stroke()

        surface.write_to_png(filename[:-4] + ".png")


def _weight_to_y(height, marker, max_weight_log, min_weight_log):
    y = 1 - (math.log(marker) - min_weight_log) / (max_weight_log - min_weight_log)
    y = y * 0.9 * (height - 60) + 20
    return y


def enzyme_digestion_to_gel(
    *,
    filename,
    plasmids: List[Tuple[str, SeqRecord]],
    enzyme_names: Collection[str],
    observer: insillyclo.observer.InSillyCloObserver,
):
    filename = str(filename)
    enzymes = []
    for enzyme_name in enzyme_names or []:
        try:
            enzymes.append(__all_enzymes[enzyme_name])
        except KeyError:
            observer.notify_unknown_digestion_enzyme(enzyme_name=enzyme_name)
            if observer.is_fail_on_error:
                raise insillyclo.additional_exception.EnzymeNotFound(enzyme_name)
    if not enzymes:
        return
    if len(enzyme_names) > 1:
        for enzyme in enzymes:
            enzyme_digestion_to_gel(
                filename=f'{filename[:-4]}-{enzyme.__name__}{filename[-4:]}',
                plasmids=plasmids,
                enzyme_names=[enzyme.__name__],
                observer=observer,
            )
    digested_plasmids = list()
    for plasmid_name, sequence in plasmids:
        cut_sites = []
        for enzyme in enzymes:
            cut_sites.extend(enzyme.search(sequence.seq, linear=False))
        cut_sites = list(sorted(cut_sites))
        if len(cut_sites) == 0:
            lengths = [len(sequence.seq)]
        else:
            lengths = []
            for i in range(1, len(cut_sites)):
                lengths.append(cut_sites[i] - cut_sites[i - 1])
            lengths.append(cut_sites[0] - cut_sites[-1] + len(sequence.seq))
        digested_plasmids.append(
            (
                plasmid_name,
                [(l, True) for l in lengths],
            )
        )
    return produce_gel_image(
        filename=filename,
        plasmids=digested_plasmids,
        text=f"Enzyme digestion by InSillyClo using {','.join(enzyme_names)}.",
    )


def get_amplified_sequences_lengths(
    *,
    well: insillyclo.models.PCRWell,
) -> (list[(int, bool)], list[insillyclo.models.PCRPrimerPair]):
    # get max length of primers in case some sequence are circular so we search in a circular approach
    max_for = max([len(p.forward_seq) for p in well.primers])
    max_rev = max([len(p.reverse_seq) for p in well.primers])
    amplified_lengths = list()
    amplifying_primers = list()
    for ids, (sequence, expected) in enumerate(well.sequences):
        if isinstance(sequence, SeqRecord):
            is_circular = sequence.annotations.get('topology', '') == 'circular'
            seq = sequence.seq
        elif isinstance(sequence, Seq):
            is_circular = False
            seq = sequence
        else:
            is_circular = False
            seq = Seq(str(sequence))
        if is_circular:
            # if circular we add the end of the sequence at its beginning (and reciprocally) so
            # the search will find primers even if one it split between end and beginning
            extended_seq = seq[-max_for - 1 :] + seq + seq[: max_rev - 1]
        else:
            extended_seq = seq

        for primer in well.primers:
            start_at = extended_seq.find(primer.forward_seq)
            if start_at == -1:
                start_at = extended_seq.find(Seq(primer.forward_seq).reverse_complement())
            ends_at = extended_seq.find(primer.reverse_seq)
            if ends_at == -1:
                ends_at = extended_seq.find(Seq(primer.reverse_seq).reverse_complement())
            # both primers found AND either in the right order ot circular
            if start_at != -1 and ends_at != -1 and (is_circular or ends_at > start_at):
                # Compute the length, with circular sequence the start can be after the end,
                # to cover this case we add the sequence length,
                # and do a modulo to not affect when start is before end
                fragment_length = (ends_at - start_at + len(primer.reverse_seq) + len(seq)) % len(seq)
                logging.debug(
                    f"PCR amplification with {primer} for #{ids} sequence starting "
                    f"with {seq[:15]} : {start_at} to {ends_at}: {fragment_length}"
                )
                amplifying_primers.append(primer)

                amplified_lengths.append((fragment_length, expected))
    return amplified_lengths, amplifying_primers


def pcr_amplification_to_gel(
    *,
    filename,
    wells: List[insillyclo.models.PCRWell],
    observer: insillyclo.observer.InSillyCloObserver,
):
    str_pairs = set()
    digested_plasmids = list()
    for well in wells:
        if not well.primers:
            continue
        amplified_lengths, primers = get_amplified_sequences_lengths(well=well)
        if amplified_lengths:
            for p in primers:
                str_pairs.add(f'({p.forward_id}, {p.reverse_id})')
        digested_plasmids.append(
            (
                well.name,
                amplified_lengths,
            )
        )
    if not digested_plasmids:
        return
    produce_gel_image(
        filename=filename,
        plasmids=digested_plasmids,
        text=f"PCR amplification by InSillyClo with {', '.join(str_pairs)}.",
    )
