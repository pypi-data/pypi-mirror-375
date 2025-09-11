"""Simulator class for generating aligned reads from simulated CpG methylation data."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from importlib.metadata import version, PackageNotFoundError
from random import seed as random_seed, random
from typing import Generator, List, Optional, Set

import pysam
from pysam.libcalignedsegment import AlignedSegment
from pysam.libcalignmentfile import AlignmentFile, AlignmentHeader

from pymethyl2sam.core.genomics import GenomicInterval, Chromosome, MethylationSite
from pymethyl2sam.core.reference_genome import ReferenceGenomeProvider
from pymethyl2sam.core.sequencing import ReadTemplate, ReadGenerator, ReadQuality
from pymethyl2sam.utils.pysam import make_sam_dict, generate_mm_tag

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass(frozen=True, init=False)
class SequencedRegion:
    """Represents a genomic region with associated read generation strategy."""

    interval: GenomicInterval
    read_generator: ReadGenerator

    def __init__(self, start: int, end: int, read_generator: ReadGenerator):
        object.__setattr__(self, "interval", GenomicInterval(start, end, False))
        object.__setattr__(self, "read_generator", read_generator)


@dataclass(frozen=True)
class SequencedChromosome(Chromosome):
    regions: List[SequencedRegion]
    cpg_sites: List[MethylationSite] = field(default_factory=list)

    def __post_init__(self):
        """Validate that methylation sites do not overlap."""
        sorted_sites = sorted(self.cpg_sites, key=lambda s: s.position)
        for prev, curr in zip(sorted_sites, sorted_sites[1:]):
            prev_end = prev.position + len(prev.context)
            curr_start = curr.position
            if curr_start < prev_end:
                raise ValueError(
                    f"Overlapping methylation sites detected:\n"
                    f"  Site 1: pos={prev.position}, context='{prev.context}'\n"
                    f"  Site 2: pos={curr.position}, context='{curr.context}'"
                )

    def generate_reads(self) -> Generator[ReadTemplate, None, None]:
        """Yield reads for each defined region in the chromosome."""
        for region in self.regions:
            logger.debug(f"Generating reads for region: {region}")
            yield from region.read_generator.generate_reads(
                region.interval, self.cpg_sites
            )


@dataclass(frozen=True)
class SimulatedRead(GenomicInterval):
    """Represents a simulated read with sequence, methylation sites, and quality."""

    chrom: str
    sequence: str
    methylated_sites: Set[MethylationSite]
    quality: ReadQuality

    @staticmethod
    def from_template(
        template: ReadTemplate, chrom: str, reference_genome: ReferenceGenomeProvider
    ) -> SimulatedRead:
        """Construct a simulated read from a template and reference sequence."""
        sequence = bytearray(
            reference_genome.get_sequence(chrom, template).upper(), "ascii"
        )
        sampled_sites: Set[MethylationSite] = set()

        for site in template.local_methylated_sites:
            SimulatedRead._apply_site(sequence, site)
            if site.methylation_prob >= 1.0 or random() < site.methylation_prob:
                sampled_sites.add(site)

        return SimulatedRead(
            chrom=chrom,
            start=template.start,
            end=template.end,
            is_reverse=template.is_reverse,
            sequence=sequence.decode("ascii"),
            quality=template.quality,
            methylated_sites=sampled_sites,
        )

    @staticmethod
    def _apply_site(sequence: bytearray, site: MethylationSite) -> None:
        """Apply a methylation site's context to the sequence in-place."""
        start = max(0, site.position)
        end = min(start + len(site.context), len(sequence))
        sequence[start:end] = site.context[: end - start].encode("ascii")

    def to_aligned_segment(self, header: AlignmentHeader) -> AlignedSegment:
        """Convert this simulated read into a pysam AlignedSegment."""
        segment = AlignedSegment.from_dict(
            make_sam_dict(
                chrome=self.chrom,
                start=self.start,
                sequence=self.sequence,
                quality=self.quality,
                is_reverse=self.is_reverse,
            ),
            header=header,
        )
        segment.set_tag("MD", str(self.length), value_type="Z")
        segment.set_tag("NM", 0, value_type="i")

        if self.methylated_sites and self.sequence:
            mm_tag = generate_mm_tag(
                self.sequence,
                self.methylated_sites,
                self.is_reverse,
            )
            segment.set_tag("MM", mm_tag, value_type="Z")

        return segment


@dataclass
class MethylationSimulator:
    """Main simulator class for generating methylation-aware reads."""

    chromosomes: List[SequencedChromosome]
    reference_genome: ReferenceGenomeProvider

    def simulate_reads(
        self,
        output_file: str,
        seed: Optional[int] = None,
        is_sorted: bool = True,
    ) -> None:
        """Simulate reads and write to a BAM file.

        Args:
            output_file: Path to output BAM file
            seed: Random seed for reproducibility
            is_sorted: Whether to sort the BAM file after writing
        """
        if seed is not None:
            random_seed(seed)

        header = self.create_header()
        with AlignmentFile(output_file, "wb", header=header) as out_bam:
            logger.info("Beginning read simulation...")
            for chrom in self.chromosomes:
                logger.debug(f"Simulating reads for chromosome: {chrom.name}")
                for template in chrom.generate_reads():
                    read = SimulatedRead.from_template(
                        template=template,
                        chrom=chrom.name,
                        reference_genome=self.reference_genome,
                    )
                    out_bam.write(read.to_aligned_segment(header))
            logger.info("Read simulation complete.")

        if is_sorted:
            logger.info(f"Sorting output file: {output_file}")
            pysam.sort(
                "-o", output_file, output_file, "--write-index", catch_stdout=False
            )

    def create_header(self) -> AlignmentHeader:
        """Create a SAM/BAM header based on the simulated chromosomes."""
        try:
            tool_version = version("pymethyl2sam")
        except PackageNotFoundError:
            tool_version = "unknown"

        header_dict = {
            "HD": {"VN": "1.6", "SO": "coordinate"},
            "SQ": [
                {"SN": chrom.name, "LN": chrom.length} for chrom in self.chromosomes
            ],
            "RG": [],
            "PG": [
                {
                    "ID": "pymethyl2sam",
                    "VN": tool_version,
                    "CL": "pymethyl2sam",
                }
            ],
        }
        return AlignmentHeader.from_dict(header_dict)

    @property
    def total_reads(self) -> int:
        """Total number of reads across all chromosomes and regions."""
        return sum(
            region.read_generator.strategy.total_reads
            for chrom in self.chromosomes
            for region in chrom.regions
        )

    @property
    def total_methylation_sites(self) -> int:
        """Total number of methylation sites across all chromosomes."""
        return sum(len(chrom.cpg_sites) for chrom in self.chromosomes)
