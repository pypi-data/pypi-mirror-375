"""
Tests for the sequencing simulation module, including strategies and generators.
Pylint-compliant and follows best practices for testing.
"""

# pylint: disable=redefined-outer-name, protected-access

from unittest.mock import patch

import pytest

from pymethyl2sam.core.sequencing import (
    EmptyStrategy,
    GenomicInterval,
    MethylationSite,
    PatternedReadData,
    PatternStrategy,
    RandomStrategy,
    ReadGenerator,
    ReadQuality,
    ReadTemplate,
    StrandOrientation,
)


# --- Fixtures ---
@pytest.fixture
def base_region():
    """Provides a standard GenomicInterval for use in tests."""
    return GenomicInterval(start=1000, end=2000, is_reverse=False)


@pytest.fixture
def cpg_sites_in_region():
    """Provides a list of MethylationSites within the base_region."""
    return [
        MethylationSite(position=1050),  # Inside first read
        MethylationSite(position=1150),  # Inside second read
        MethylationSite(position=1250),  # Inside third read
        MethylationSite(position=2100),  # Outside all reads
    ]


# --- Tests for ReadQuality ---
class TestReadQuality:
    """Tests for the ReadQuality data class."""

    def test_successful_creation(self):
        """Test that a valid ReadQuality object can be created."""
        quality = ReadQuality(sequencing_score=35, mapping_score=60)
        assert quality.sequencing_score == 35
        assert quality.mapping_score == 60

    @pytest.mark.parametrize(
        "score, expected_error",
        [
            (-1, "sequencing_score must be in the range \\[0, 50\\]."),
            (51, "sequencing_score must be in the range \\[0, 50\\]."),
        ],
    )
    def test_invalid_sequencing_score_raises_error(self, score, expected_error):
        """Test that an invalid sequencing_score raises a ValueError."""
        with pytest.raises(ValueError, match=expected_error):
            ReadQuality(sequencing_score=score)

    @pytest.mark.parametrize(
        "score, expected_error",
        [
            (-1, "mapping_score must be in the range \\[0, 255\\]."),
            (256, "mapping_score must be in the range \\[0, 255\\]."),
        ],
    )
    def test_invalid_mapping_score_raises_error(self, score, expected_error):
        """Test that an invalid mapping_score raises a ValueError."""
        with pytest.raises(ValueError, match=expected_error):
            ReadQuality(mapping_score=score)


# --- Tests for ReadTemplate ---
def test_read_template_creation():
    """Test successful creation of a ReadTemplate object."""
    quality = ReadQuality()
    sites = [MethylationSite(position=10)]
    template = ReadTemplate(
        start=100,
        end=250,
        is_reverse=False,
        quality=quality,
        local_methylated_sites=sites,
    )
    assert template.start == 100
    assert template.length == 150
    assert template.quality == quality
    assert template.local_methylated_sites == sites


# --- Tests for Strategies ---
class TestPatternStrategy:
    """Tests for the PatternStrategy class."""

    def test_generate_read_intervals(self, base_region):
        """Test that read intervals are generated according to the pattern."""
        data = [
            PatternedReadData(offset=10, orientation=StrandOrientation.FORWARD),
            PatternedReadData(offset=20, orientation=StrandOrientation.BACKWARD),
        ]
        strategy = PatternStrategy(data)
        read_length = 150
        intervals = list(strategy.generate_read_intervals(base_region, read_length))

        assert len(intervals) == 2
        # First read
        assert intervals[0].start == 1010  # 1000 + 10
        assert intervals[0].end == 1160  # 1010 + 150
        assert intervals[0].is_reverse is False
        # Second read
        assert intervals[1].start == 1020  # 1000 + 20
        assert intervals[1].end == 1170  # 1020 + 150
        assert intervals[1].is_reverse is True

    def test_total_reads(self):
        """Test the total_reads property."""
        data = [
            PatternedReadData(offset=i, orientation=StrandOrientation.FORWARD)
            for i in range(5)
        ]
        strategy = PatternStrategy(data)
        assert strategy.total_reads == 5

    def test_from_offsets(self):
        """Test the from_offsets static method."""
        strategy = PatternStrategy.from_offsets(
            offsets=[10, 20], orientation=StrandOrientation.FORWARD
        )
        assert strategy.total_reads == 2
        assert all(
            read.orientation == StrandOrientation.FORWARD for read in strategy.data
        )

    def test_from_offset_orientation_pairs(self):
        """Test the from_offset_orientation_pairs static method."""
        strategy = PatternStrategy.from_offset_orientation_pairs(
            offsets=[10, 20], orientations=["+", "-"]
        )
        intervals = list(strategy.data)
        assert strategy.total_reads == 2
        assert intervals[0].orientation == StrandOrientation.FORWARD
        assert intervals[1].orientation == StrandOrientation.BACKWARD


class TestRandomStrategy:
    """Tests for the RandomStrategy class."""

    def test_invalid_reads_per_region_raises_error(self):
        """Test that non-positive reads_per_region raises a ValueError."""
        with pytest.raises(
            ValueError, match="reads_per_region must be a positive integer."
        ):
            RandomStrategy(reads_per_region=0)

    # Corrected patch target to where 'randint' is used.
    @patch("pymethyl2sam.core.sequencing.randint")
    def test_generate_read_intervals(self, mock_randint, base_region):
        """Test that random read intervals are generated correctly."""
        strategy = RandomStrategy(reads_per_region=3)
        read_length = 100
        # Mock randint to return predictable start positions
        mock_randint.side_effect = [1200, 1300, 1400]
        intervals = list(strategy.generate_read_intervals(base_region, read_length))

        assert len(intervals) == 3
        assert intervals[0].start == 1200
        assert intervals[1].start == 1300
        assert intervals[2].start == 1400
        assert all(i.length == read_length for i in intervals)

    def test_total_reads(self):
        """Test the total_reads property."""
        strategy = RandomStrategy(reads_per_region=50)
        assert strategy.total_reads == 50


class TestEmptyStrategy:
    """Tests for the EmptyStrategy class."""

    def test_generate_read_intervals(self, base_region):
        """Test that no intervals are generated."""
        strategy = EmptyStrategy()
        intervals = list(strategy.generate_read_intervals(base_region, 150))
        assert not intervals

    def test_total_reads(self):
        """Test that total_reads is zero."""
        strategy = EmptyStrategy()
        assert strategy.total_reads == 0


# --- Tests for ReadGenerator ---
class TestReadGenerator:
    """Tests for the ReadGenerator class."""

    def test_invalid_read_length_raises_error(self):
        """Test that non-positive read_length raises a ValueError."""
        with pytest.raises(ValueError, match="read_length must be a positive integer."):
            ReadGenerator(strategy=EmptyStrategy(), read_length=0)

    def test_generate_reads(self, base_region, cpg_sites_in_region):
        """Test the full read generation pipeline."""
        # Use a deterministic pattern strategy for this test
        pattern_data = [
            PatternedReadData(
                offset=0, orientation=StrandOrientation.FORWARD
            ),  # Read 1: 1000-1150
            PatternedReadData(
                offset=100, orientation=StrandOrientation.FORWARD
            ),  # Read 2: 1100-1250
            PatternedReadData(
                offset=200, orientation=StrandOrientation.FORWARD
            ),  # Read 3: 1200-1350
        ]
        strategy = PatternStrategy(pattern_data)
        generator = ReadGenerator(strategy=strategy, read_length=150)
        reads = list(generator.generate_reads(base_region, cpg_sites_in_region))

        assert len(reads) == 3

        # --- Verify Read 1 ---
        # Interval: 1000-1150. Contains site at 1050.
        assert reads[0].start == 1000
        assert len(reads[0].local_methylated_sites) == 1
        # Position should be relative to the read start (1050 - 1000 = 50)
        assert reads[0].local_methylated_sites[0].position == 50

        # --- Verify Read 2 ---
        # Interval: 1100-1250. Contains site at 1150.
        assert reads[1].start == 1100
        assert len(reads[1].local_methylated_sites) == 1
        # Position should be relative to the read start (1150 - 1100 = 50)
        assert reads[1].local_methylated_sites[0].position == 50

        # --- Verify Read 3 ---
        # Interval: 1200-1350. Contains site at 1250.
        assert reads[2].start == 1200
        assert len(reads[2].local_methylated_sites) == 1
        # Position should be relative to the read start (1250 - 1200 = 50)
        assert reads[2].local_methylated_sites[0].position == 50
