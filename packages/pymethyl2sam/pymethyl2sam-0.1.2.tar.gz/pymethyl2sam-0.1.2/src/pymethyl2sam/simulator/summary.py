from collections import defaultdict
from typing import Dict, Any, Set, Tuple

from pysam import SamtoolsError
from pysam.libcalignmentfile import AlignmentFile

from pymethyl2sam.utils import setup_logging
from pymethyl2sam.utils.pysam import get_read_to_reference_mapping, ReadPosition

logger = setup_logging(__name__)


def get_simulation_summary(bam_path: str) -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        "total_reads": 0,
        "reads_with_methylation": 0,
        "chromosome_count": 0,
        "regions_per_chromosome": defaultdict(int),
        "total_methylation_sites": 0,
    }

    methylation_sites: Set[Tuple[str, int]] = set()

    logger.info(f"Opening BAM file: {bam_path}")

    try:
        with AlignmentFile(bam_path, "rb") as bamfile:
            chromosomes: Set[str] = set()
            logger.info("Processing reads...")

            for read in bamfile.fetch(until_eof=True):
                reverse_strand_offset = 1 if read.is_reverse else 0
                stats["total_reads"] += 1

                if read.is_unmapped:
                    continue

                chrom = bamfile.get_reference_name(read.reference_id)
                chromosomes.add(chrom)
                stats["regions_per_chromosome"][chrom] += 1

                if read.has_tag("MM") and read.modified_bases:
                    read2ref = get_read_to_reference_mapping(read)
                    stats["reads_with_methylation"] += 1

                    modified_read_positions: Set[ReadPosition] = {
                        pos - reverse_strand_offset
                        for mods in read.modified_bases.values()
                        for pos, _ in mods
                    }

                    for pos in modified_read_positions:
                        if pos in read2ref:
                            methylation_sites.add((chrom, read2ref[pos]))

            stats["total_methylation_sites"] = len(methylation_sites)
            stats["chromosome_count"] = len(chromosomes)
            logger.info("Finished processing BAM file.")

    except (FileNotFoundError, PermissionError) as io_err:
        logger.error(f"File error: {bam_path}", exc_info=io_err)
    except (ValueError, TypeError, KeyError, AttributeError) as data_err:
        logger.error("Data format or logic error while parsing BAM.", exc_info=data_err)
    except (SamtoolsError, EOFError) as bam_err:
        logger.error("BAM file appears corrupted or unreadable.", exc_info=bam_err)

    return stats
