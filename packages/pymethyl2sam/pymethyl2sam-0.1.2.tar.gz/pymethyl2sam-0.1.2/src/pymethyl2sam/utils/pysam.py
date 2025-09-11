from random import randint
from typing import List, Dict
from typing import Tuple, Set

from pysam.libcalignedsegment import AlignedSegment
from pysam.libcutils import qualities_to_qualitystring

from . import COMPLEMENT_TABLE, RUN_NUMBER, INSTRUMENT, FLOWCELL_ID
from ..core.genomics import MethylationSite
from ..core.sequencing import ReadQuality

ReadPosition = ReferencePosition = int
AlignedPairs = List[Tuple[ReadPosition, ReferencePosition]]


def get_read_to_reference_mapping(read: AlignedSegment):
    pairs: AlignedPairs = read.get_aligned_pairs(matches_only=False)
    return {read_pos: ref if ref else None for read_pos, ref in pairs}


def make_sam_dict(
    chrome: str,
    sequence: str,
    start: int,
    is_reverse: bool,
    quality: ReadQuality,
) -> Dict[str, str]:
    read_name = _generate_read_name()
    read_length = len(sequence)
    flag = 16 if is_reverse else 0
    ref_pos = start + 1
    qual = qualities_to_qualitystring([quality.sequencing_score] * read_length)
    return {
        "name": read_name,
        "flag": str(flag),
        "ref_name": chrome,
        "ref_pos": str(ref_pos),
        "next_ref_name": "*",
        "next_ref_pos": "0",
        "map_quality": str(quality.mapping_score),
        "length": "0",
        "cigar": f"{read_length}M",
        "seq": sequence,
        "qual": qual,
    }


def _generate_read_name() -> str:
    lane = randint(1, 4)
    tile = randint(1101, 1200)
    x_pos = randint(0, 3000)
    y_pos = randint(0, 3000)

    return (
        f"{INSTRUMENT}:"
        f"{RUN_NUMBER:03d}:"  # 3-digit zero padded
        f"{FLOWCELL_ID}:"
        f"{lane}:"
        f"{tile:04d}:"  # 4-digit zero padded
        f"{x_pos:04d}:"
        f"{y_pos:04d}"
    )


def generate_mm_tag(
    fw_sequence: str, methylated_sites: Set[MethylationSite], is_reverse_strand: bool
) -> str:
    """
    Generates a SAM MM tag for methylation.
    """
    target_base = "C"
    strand_tag = "+" if not is_reverse_strand else "-"
    sequence = (
        fw_sequence.translate(COMPLEMENT_TABLE)[::-1]
        if is_reverse_strand
        else fw_sequence
    )
    transform_pos = (
        (lambda x: len(sequence) - 1 - x) if is_reverse_strand else lambda x: x
    )
    methylated_positions = set(
        transform_pos(site.get_cytosine_position(is_reverse_strand))
        for site in methylated_sites
    )

    candidate_positions = (i for i, char in enumerate(sequence) if char == target_base)

    offsets = []
    last_methyl_idx = -1
    for candidate_idx, pos in enumerate(candidate_positions):
        if pos in methylated_positions:
            offsets.append(candidate_idx - last_methyl_idx - 1)
            last_methyl_idx = candidate_idx
            methylated_positions.remove(pos)

    return f"{target_base}{strand_tag}m,{','.join(map(str, offsets))};"
