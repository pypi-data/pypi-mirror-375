"""
Tests for the data classes and enums used in the simulation.
Pylint-compliant and follows best practices for testing.
"""

# pylint: disable=redefined-outer-name, protected-access

import random
from unittest.mock import patch

import pytest

from pymethyl2sam.core.genomics import (
    Chromosome,
    GenomicInterval,
    MethylationSite,
    ModificationType,
    StrandOrientation,
)

random.seed(42)


# --- Tests for StrandOrientation ---
class TestStrandOrientation:
    """Tests for the StrandOrientation enum."""

    def test_to_is_reverse_forward(self):
        """Test that FORWARD strand correctly returns False."""
        assert StrandOrientation.FORWARD.to_is_reverse() is False

    def test_to_is_reverse_backward(self):
        """Test that BACKWARD strand correctly returns True."""
        assert StrandOrientation.BACKWARD.to_is_reverse() is True

    @patch("random.choice")
    def test_to_is_reverse_random(self, mock_choice):
        """Test that RANDOM strand uses random.choice and can return both states."""
        # Test the case where random.choice returns True
        mock_choice.return_value = True
        assert StrandOrientation.RANDOM.to_is_reverse() is True
        mock_choice.assert_called_with([True, False])

        # Test the case where random.choice returns False
        mock_choice.return_value = False
        assert StrandOrientation.RANDOM.to_is_reverse() is False
        mock_choice.assert_called_with([True, False])

    def test_repr(self):
        """Test the string representation of the enum members."""
        assert repr(StrandOrientation.FORWARD) == "+"
        assert repr(StrandOrientation.BACKWARD) == "-"
        assert repr(StrandOrientation.RANDOM) == "?"


# --- Tests for Chromosome ---
def test_chromosome_creation():
    """Test successful creation of a Chromosome object."""
    chrom = Chromosome(name="chr1", length=1000)
    assert chrom.name == "chr1"
    assert chrom.length == 1000


# --- Tests for MethylationSite ---
class TestMethylationSite:
    """Tests for the MethylationSite data class."""

    def test_successful_creation(self):
        """Test that a valid MethylationSite can be created."""
        site = MethylationSite(
            position=100,
            context="CG",
            modification=ModificationType.C5MC,
            methylation_prob=0.8,
        )
        assert site.position == 100
        assert site.methylation_prob == 0.8
        assert site.context == "CG"

    def test_creation_with_defaults(self):
        """Test creation with default values."""
        site = MethylationSite(position=50)
        assert site.position == 50
        assert site.methylation_prob == 0.5
        assert site.context == "CG"
        assert site.modification == ModificationType.C5MC

    def test_invalid_methylation_prob_raises_error(self):
        """Test that a probability outside [0, 1] raises a ValueError."""
        with pytest.raises(
            ValueError, match="methylation_prob must be in \\[0, 1\\], got -0.1"
        ):
            MethylationSite(position=100, methylation_prob=-0.1)

        with pytest.raises(
            ValueError, match="methylation_prob must be in \\[0, 1\\], got 1.1"
        ):
            MethylationSite(position=100, methylation_prob=1.1)

    def test_negative_position_raises_error(self):
        """Test that a negative position raises a ValueError."""
        with pytest.raises(ValueError, match="Position must be non-negative"):
            MethylationSite(position=-1)

    def test_empty_context_raises_error(self):
        """Test that an empty context string raises a ValueError."""
        with pytest.raises(ValueError, match="Context cannot be empty"):
            MethylationSite(position=100, context="")

    def test_with_position(self):
        """Test the with_position method creates a new object correctly."""
        original_site = MethylationSite(position=100, methylation_prob=0.7)
        new_site = original_site.with_position(200)

        # Check that a new object was created
        assert original_site is not new_site

        # Check that the position was updated
        assert new_site.position == 200

        # Check that other attributes remain the same
        assert new_site.methylation_prob == original_site.methylation_prob
        assert new_site.context == original_site.context
        assert new_site.modification == original_site.modification

    def test_ordering(self):
        """Test that MethylationSite objects are sortable by position."""
        site1 = MethylationSite(position=200)
        site2 = MethylationSite(position=50)
        site3 = MethylationSite(position=100)

        sites = [site1, site2, site3]
        sorted_sites = sorted(sites)

        assert sorted_sites[0].position == 50
        assert sorted_sites[1].position == 100
        assert sorted_sites[2].position == 200


# --- Tests for GenomicInterval ---
class TestGenomicInterval:
    """Tests for the GenomicInterval data class."""

    def test_successful_creation(self):
        """Test that a valid GenomicInterval can be created."""
        interval = GenomicInterval(start=100, end=200, is_reverse=False)
        assert interval.start == 100
        assert interval.end == 200
        assert interval.is_reverse is False

    def test_negative_start_raises_error(self):
        """Test that a negative start position raises a ValueError."""
        with pytest.raises(ValueError, match="Start position must be non-negative"):
            GenomicInterval(start=-1, end=100, is_reverse=False)

    def test_end_before_start_raises_error(self):
        """Test that an end position smaller than start raises a ValueError."""
        with pytest.raises(
            ValueError, match="End position must not be smaller than start position"
        ):
            GenomicInterval(start=100, end=99, is_reverse=False)

    def test_length_property(self):
        """Test the length property for various intervals."""
        assert GenomicInterval(start=100, end=200, is_reverse=False).length == 100
        assert GenomicInterval(start=50, end=55, is_reverse=True).length == 5
        # Test zero-length interval
        assert GenomicInterval(start=10, end=10, is_reverse=False).length == 0

    @pytest.mark.parametrize(
        "position, expected",
        [
            (99, False),  # Before start
            (100, True),  # At start (inclusive)
            (150, True),  # Inside
            (199, True),  # Just before end
            (200, False),  # At end (exclusive)
            (201, False),  # After end
        ],
    )
    def test_contains(self, position, expected):
        """Test the contains method for various positions."""
        interval = GenomicInterval(start=100, end=200, is_reverse=False)
        assert interval.contains(position) is expected
