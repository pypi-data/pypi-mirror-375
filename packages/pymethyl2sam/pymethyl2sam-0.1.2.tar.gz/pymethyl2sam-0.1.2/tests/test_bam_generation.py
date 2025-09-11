"""
Preface:

This test suite was created to systematically validate the behavior of BAM file generation
via the `pymethyl2sam` simulation pipeline. The core purpose of these tests is to demonstrate
that AI-generated code related to methylation read simulation is currently **not functioning
as expected**.

Each test isolates a specific property or expectation—such as read alignment, MM tag presence,
or methylation site consistency—to make discrepancies between the expected and actual output
explicit and reproducible.

Many of these tests are intentionally marked with `@pytest.mark.xfail` to indicate known
failures, allowing this suite to serve both as a regression tracking tool and as a foundation
for future debugging or reimplementation efforts.
"""

import math
from typing import cast

import pytest
from pysam.libcalignmentfile import AlignmentFile

from pymethyl2sam import MethylationSimulator
from pymethyl2sam.core import MethylationSite
from pymethyl2sam.core.genomics import ModificationType
from pymethyl2sam.core.reference_genome import ConstantReferenceGenome
from pymethyl2sam.core.sequencing import ReadGenerator, PatternStrategy, RandomStrategy
from pymethyl2sam.simulator import SequencedChromosome, SequencedRegion
from pymethyl2sam.simulator.summary import get_simulation_summary


# pylint: disable=W0621,R0801
@pytest.fixture
def pattern_based_simulation(tmp_path):
    bam_path = str(tmp_path / "pattern_sim.bam")
    simulator = MethylationSimulator(
        reference_genome=ConstantReferenceGenome(),
        chromosomes=[
            SequencedChromosome(
                name="chr1",
                length=500,
                regions=[
                    SequencedRegion(
                        start=0,
                        end=300,
                        read_generator=ReadGenerator(
                            read_length=50,
                            strategy=PatternStrategy.from_offset_orientation_pairs(
                                offsets=[50, 100, 250], orientations=["+", "-", "+"]
                            ),
                        ),
                    )
                ],
                cpg_sites=[
                    MethylationSite(50, "CG", ModificationType("5mC"), 1.0),
                    MethylationSite(60, "CG", ModificationType("5mC"), 1.0),
                    MethylationSite(105, "CG", ModificationType("5mC"), 1.0),
                    # outside the reads coverage
                    MethylationSite(300, "CG", ModificationType("5mC"), 1.0),
                ],
            )
        ],
    )
    simulator.simulate_reads(bam_path)
    summary = get_simulation_summary(bam_path)
    return simulator, summary, bam_path


def test_pattern_total_read_count(pattern_based_simulation):
    simulator, stats, _ = pattern_based_simulation
    assert stats["total_reads"] == simulator.total_reads


def test_pattern_read_start_alignment(pattern_based_simulation):
    simulator, _, bam_file = pattern_based_simulation
    region = simulator.chromosomes[0].regions[0]
    pattern_strategy = cast(PatternStrategy, region.read_generator.strategy)
    expected_reference_start = [
        x.offset + region.interval.start for x in pattern_strategy.data
    ]
    with AlignmentFile(bam_file, "rb") as bam:
        actual_reference_start = [read.reference_start for read in list(bam)]
    assert sorted(actual_reference_start) == sorted(expected_reference_start)


@pytest.mark.parametrize(
    "index, has_tag",
    [
        (0, True),
        (1, True),
        (2, False),
    ],
)
def test_pattern_mm_tag(pattern_based_simulation, index, has_tag):
    _, _, bam_file = pattern_based_simulation
    with AlignmentFile(bam_file, "rb") as bam:
        reads = list(bam)
    assert reads[index].has_tag("MM") == has_tag


@pytest.mark.parametrize(
    "index,exp_base,exp_strand,exp_site_pos", [(0, "C", 0, [0, 10]), (1, "C", 0, [6])]
)
def test_pattern_modified_bases(
    pattern_based_simulation, index, exp_base, exp_strand, exp_site_pos
):
    _, _, bam_file = pattern_based_simulation
    with AlignmentFile(bam_file, "rb") as bam:
        read = list(bam)[index]
        for (
            canonical_base,
            strand,
            modification,
        ), bases in read.modified_bases.items():
            assert canonical_base == exp_base
            assert modification == "m"
            assert strand == exp_strand
            assert [pos for pos, _ in bases] == exp_site_pos


def test_pattern_total_methylation_site_count(pattern_based_simulation):
    _, stats, _ = pattern_based_simulation
    expected_count = 3
    assert stats["total_methylation_sites"] == expected_count


@pytest.fixture
def random_mode_simulation(tmp_path):
    bam_path = str(tmp_path / "random_sim.bam")
    simulator = MethylationSimulator(
        chromosomes=[
            SequencedChromosome(
                name="chr1",
                length=10_000,
                regions=[
                    SequencedRegion(
                        start=100,
                        end=450,
                        read_generator=ReadGenerator(
                            strategy=RandomStrategy(reads_per_region=2000),
                            read_length=50,
                        ),
                    )
                ],
                cpg_sites=[
                    MethylationSite(position=150, methylation_prob=1.0),
                    MethylationSite(position=200, methylation_prob=1.0),
                ],
            )
        ],
        reference_genome=ConstantReferenceGenome(),
    )
    simulator.simulate_reads(bam_path, seed=42)
    summary = get_simulation_summary(bam_path)
    return simulator, summary, bam_path


@pytest.fixture
def random_mode_simulation_low_prob(tmp_path):
    bam_path = str(tmp_path / "random_sim.bam")
    simulator = MethylationSimulator(
        chromosomes=[
            SequencedChromosome(
                name="chr1",
                length=10_000,
                regions=[
                    SequencedRegion(
                        start=100,
                        end=450,
                        read_generator=ReadGenerator(
                            strategy=RandomStrategy(reads_per_region=2000),
                            read_length=50,
                        ),
                    )
                ],
                cpg_sites=[
                    MethylationSite(position=150, methylation_prob=0.1),
                    MethylationSite(position=200, methylation_prob=0.25),
                ],
            )
        ],
        reference_genome=ConstantReferenceGenome(),
    )
    simulator.simulate_reads(bam_path, seed=42)
    summary = get_simulation_summary(bam_path)
    return simulator, summary, bam_path


def test_random_total_read_count(random_mode_simulation):
    simulator, stats, _ = random_mode_simulation
    assert stats["total_reads"] == simulator.total_reads


def test_random_methylation_ratio(random_mode_simulation):
    _, stats, _ = random_mode_simulation
    observed_ratio = stats["reads_with_methylation"] / stats["total_reads"]
    n_sites = stats["total_methylation_sites"]
    read_length = 50
    region_length = 350
    tolerance = 0.07

    expected_ratio = n_sites * read_length / (region_length + 2 * read_length)
    assert math.isclose(observed_ratio, expected_ratio, abs_tol=tolerance), (
        f"Methylation ratio {observed_ratio:.3f} not within "
        f"±{tolerance} of expected {expected_ratio:.2f}"
    )


def test_random_methylation_ratio_low_prob(random_mode_simulation_low_prob):
    _, stats, _ = random_mode_simulation_low_prob
    observed_ratio = stats["reads_with_methylation"] / stats["total_reads"]
    n_sites = stats["total_methylation_sites"]
    read_length = 50
    region_length = 350
    prob = (0.1 + 0.25) / 2
    tolerance = 0.07

    expected_ratio = prob * n_sites * read_length / (region_length + 2 * read_length)
    assert math.isclose(observed_ratio, expected_ratio, abs_tol=tolerance), (
        f"Methylation ratio {observed_ratio:.3f} not within "
        f"±{tolerance} of expected {expected_ratio:.2f}"
    )


def test_random_total_methylation_sites_match(random_mode_simulation):
    simulator, stats, _ = random_mode_simulation
    assert stats["total_methylation_sites"] == simulator.total_methylation_sites
