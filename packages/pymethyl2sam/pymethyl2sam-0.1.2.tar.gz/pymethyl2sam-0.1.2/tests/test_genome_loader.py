"""Tests for the GenomeLoader class."""

# pylint: disable=redefined-outer-name

import pytest
from pymethyl2sam.io import GenomeLoader


@pytest.fixture
def fasta_content():
    """Sample FASTA content with three chromosomes."""
    return (
        ">chr1 description of chromosome 1\n"
        "GATTACA\n"
        "GATTACA\n"
        ">chr2\n"
        "CATCAT\n"
        ">chrM mitochondrial DNA\n"
        "ACGT\n"
    )


@pytest.fixture
def temp_fasta_file(tmp_path, fasta_content):
    """Creates a temporary FASTA file with sample content."""
    path = tmp_path / "test_genome.fa"
    path.write_text(fasta_content)
    return str(path)


@pytest.fixture
def empty_fasta_file(tmp_path):
    """Creates an empty temporary FASTA file."""
    path = tmp_path / "empty.fa"
    path.touch()
    return str(path)


def test_load_all_sequences(temp_fasta_file):
    """Loads all chromosomes from a valid FASTA file."""
    loader = GenomeLoader()
    genome = loader.load_genome(temp_fasta_file)

    assert genome["file"] == temp_fasta_file
    assert genome["sequences"].keys() == {"chr1", "chr2", "chrM"}
    assert genome["sequences"]["chr1"] == "GATTACAGATTACA"
    assert genome["sequences"]["chr2"] == "CATCAT"
    assert genome["sequences"]["chrM"] == "ACGT"
    assert genome["total_length"] == 14 + 6 + 4


def test_load_specific_chromosome(temp_fasta_file):
    """Loads only the specified chromosome."""
    loader = GenomeLoader()
    genome = loader.load_genome(temp_fasta_file, chromosome="chr1")

    assert genome["sequences"].keys() == {"chr1"}
    assert genome["sequences"]["chr1"] == "GATTACAGATTACA"
    assert genome["total_length"] == 14


def test_load_file_not_found():
    """Raises FileNotFoundError when the file does not exist."""
    loader = GenomeLoader()
    with pytest.raises(
        FileNotFoundError, match="Genome file not found: non_existent_file.fa"
    ):
        loader.load_genome("non_existent_file.fa")


def test_load_empty_file(empty_fasta_file):
    """Raises ValueError for an empty FASTA file."""
    loader = GenomeLoader()
    with pytest.raises(ValueError, match="No sequences found in genome file"):
        loader.load_genome(empty_fasta_file)


def test_load_missing_chromosome(temp_fasta_file):
    """Raises ValueError when the requested chromosome is not found."""
    loader = GenomeLoader()
    with pytest.raises(ValueError, match="Chromosome chrX not found in genome file"):
        loader.load_genome(temp_fasta_file, chromosome="chrX")


def test_get_chromosome_list(temp_fasta_file):
    """Returns the list of chromosome names."""
    loader = GenomeLoader()
    chromosomes = loader.get_chromosome_list(temp_fasta_file)
    assert chromosomes == ["chr1", "chr2", "chrM"]


def test_get_sequence_length(temp_fasta_file):
    """Returns correct lengths for specific chromosomes."""
    loader = GenomeLoader()
    assert loader.get_sequence_length(temp_fasta_file, "chr1") == 14
    assert loader.get_sequence_length(temp_fasta_file, "chr2") == 6


def test_validate_valid_genome_file(temp_fasta_file):
    """Validates a well-formed FASTA file."""
    loader = GenomeLoader()
    result = loader.validate_genome_file(temp_fasta_file)

    assert result["file_exists"] is True
    assert result["total_sequences"] == 3
    assert result["total_length"] == 24
    assert sorted(result["chromosomes"]) == ["chr1", "chr2", "chrM"]
    assert not result["errors"]


def test_validate_missing_genome_file():
    """Handles validation of a missing file gracefully."""
    loader = GenomeLoader()
    result = loader.validate_genome_file("non_existent_file.fa")

    assert result["file_exists"] is False
    assert result["total_sequences"] == 0
    assert result["total_length"] == 0
    assert "File not found: non_existent_file.fa" in result["errors"]


def test_validate_runtime_error(monkeypatch, temp_fasta_file):
    """Simulates a runtime error during validation."""
    loader = GenomeLoader()

    def mock_load_genome(*args, **kwargs):
        raise RuntimeError("Simulated error")

    monkeypatch.setattr(loader, "load_genome", mock_load_genome)

    result = loader.validate_genome_file(temp_fasta_file)

    assert result["file_exists"] is True
    assert result["total_sequences"] == 0
    assert result["total_length"] == 0
    assert "Simulated error" in result["errors"][0]
