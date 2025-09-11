"""
Tests for the BAM file simulation summary function.
Pylint-compliant and follows best practices for testing.
"""

# pylint: disable=redefined-outer-name, protected-access

from collections import defaultdict
from unittest.mock import MagicMock, patch

import pytest
from pysam import SamtoolsError

from pymethyl2sam.simulator.summary import get_simulation_summary


# --- Fixtures ---
@pytest.fixture
def mock_bam_file():
    """Creates a mock AlignmentFile object."""
    bamfile = MagicMock()
    bamfile.__enter__.return_value = bamfile
    return bamfile


@pytest.fixture
def mock_read_unmapped():
    """Creates a mock read that is unmapped."""
    read = MagicMock()
    read.is_unmapped = True
    return read


@pytest.fixture
def mock_read_mapped_no_methylation():
    """Creates a mock read that is mapped but has no methylation tags."""
    read = MagicMock()
    read.is_unmapped = False
    read.reference_id = 0
    read.has_tag.return_value = False
    read.modified_bases = {}
    return read


@pytest.fixture
def mock_read_mapped_with_methylation():
    """Creates a mock read with methylation data."""
    read = MagicMock()
    read.is_unmapped = False
    read.is_reverse = False
    read.reference_id = 1
    read.has_tag.return_value = True
    # Simulate modified_bases dictionary: {('C', 0, 'm'): [(10, 255), (20, 255)]}
    read.modified_bases = defaultdict(list, {("C", 0, "m"): [(10, 255), (20, 255)]})
    return read


# --- Test Cases ---
class TestGetSimulationSummary:
    """Tests for the get_simulation_summary function."""

    # Updated patch paths to target the new module location
    # pylint: disable=R0913, R0917
    @patch("pymethyl2sam.simulator.summary.AlignmentFile")
    @patch("pymethyl2sam.simulator.summary.get_read_to_reference_mapping")
    def test_full_summary_logic(
        self,
        mock_get_mapping,
        mock_alignment_file,
        mock_read_unmapped,
        mock_read_mapped_no_methylation,
        mock_read_mapped_with_methylation,
    ):
        """Test the full summary logic with a mix of read types."""
        mock_bam = mock_alignment_file.return_value.__enter__.return_value
        # Define the reads the mock BAM file will yield
        mock_bam.fetch.return_value = [
            mock_read_unmapped,
            mock_read_mapped_no_methylation,
            mock_read_mapped_with_methylation,
        ]
        # Define the chromosome names for the given reference IDs
        mock_bam.get_reference_name.side_effect = ["chr1", "chr2"]
        # Mock the read-to-reference mapping
        mock_get_mapping.return_value = {10: 1010, 20: 1020}

        summary = get_simulation_summary("dummy/path.bam")

        assert summary["total_reads"] == 3
        assert summary["reads_with_methylation"] == 1
        assert summary["chromosome_count"] == 2
        assert summary["regions_per_chromosome"]["chr1"] == 1
        assert summary["regions_per_chromosome"]["chr2"] == 1
        assert summary["total_methylation_sites"] == 2

    @patch("pymethyl2sam.simulator.summary.AlignmentFile")
    def test_empty_bam_file(self, mock_alignment_file):
        """Test with an empty (or no-read) BAM file."""
        mock_bam = mock_alignment_file.return_value.__enter__.return_value
        mock_bam.fetch.return_value = []  # No reads

        summary = get_simulation_summary("dummy/empty.bam")

        assert summary["total_reads"] == 0
        assert summary["reads_with_methylation"] == 0
        assert summary["chromosome_count"] == 0
        assert not summary["regions_per_chromosome"]
        assert summary["total_methylation_sites"] == 0

    @patch("pymethyl2sam.simulator.summary.AlignmentFile")
    def test_file_not_found_error(self, mock_alignment_file):
        """Test that FileNotFoundError is handled gracefully."""
        mock_alignment_file.side_effect = FileNotFoundError
        summary = get_simulation_summary("non/existent/file.bam")
        # Check that the stats dictionary is returned in its initial state
        assert summary["total_reads"] == 0

    @patch("pymethyl2sam.simulator.summary.AlignmentFile")
    def test_samtools_error(self, mock_alignment_file):
        """Test that SamtoolsError (e.g., corrupted file) is handled."""
        mock_alignment_file.side_effect = SamtoolsError("BAM file is corrupted")
        summary = get_simulation_summary("corrupted.bam")
        # Check that the stats dictionary is returned in its initial state
        assert summary["total_reads"] == 0
