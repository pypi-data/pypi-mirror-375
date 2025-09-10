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

from typing import List, NamedTuple

from Bio import SeqRecord
from Bio.Seq import Seq

import insillyclo.data_source


def get_nb_cut(
    seq,
    site_for,
    site_rev,
):
    return len(seq.split(site_for)) + len(seq.split(site_rev)) - 2


class FragmentsInOutSensAntiSens(NamedTuple):
    out_sens: str
    in_sens: str
    out_antisens: str
    in_antisens: str


def get_sens_antisens(
    inpart: str,
    outpart: str,
    inter_s: int,
) -> FragmentsInOutSensAntiSens:
    out_sens = str(inpart[-(4 + inter_s) :] + outpart + inpart[: 4 + inter_s])
    in_sens = str(inpart[inter_s:-inter_s])
    out_antisens = str(Seq(out_sens).reverse_complement())
    in_antisens = str(Seq(in_sens).reverse_complement())
    return FragmentsInOutSensAntiSens(
        out_sens=out_sens,
        in_sens=in_sens,
        out_antisens=out_antisens,
        in_antisens=in_antisens,
    )


def reorder_seq(
    seq: SeqRecord,
    site_for: str,
) -> str:
    splt_seq = seq.split(site_for)
    return splt_seq[1] + splt_seq[0] + site_for


def get_in_out_part(
    seq: SeqRecord,
    site_rev: str,
) -> (str, str):
    splt_seq = seq.split(site_rev)
    return site_rev + splt_seq[1], splt_seq[0]


def get_fragments(
    seqs: list[SeqRecord],
    enzyme: str,
    data_source: insillyclo.data_source.AbstractDataSource,
) -> List[FragmentsInOutSensAntiSens]:
    site_for, site_rev, inter_s = data_source.get_enzyme_cut(enzyme)
    fragments = list()
    for seq_part in seqs:
        seq = str(seq_part.seq)

        i = 0
        notfound = False
        while (site_for not in seq) or (site_rev not in seq):
            shift = len(site_for) + len(site_rev) + inter_s - 2
            seq = seq[shift:] + seq[:shift]
            i += 1

            if i >= 100:
                notfound = True
                break
                # raise ValueError(f'Restriction site not found in {seq_part.id}')

        if notfound:
            continue

        # if get_nb_cut(seq, site_for, site_rev) != 2:
        # raise ValueError(f'Number of restriction sites in {seq_part.id} is not 2')

        (out_part, in_part) = get_in_out_part(reorder_seq(seq, site_for), site_rev)
        fragments.append(get_sens_antisens(in_part, out_part, inter_s))

    return fragments
