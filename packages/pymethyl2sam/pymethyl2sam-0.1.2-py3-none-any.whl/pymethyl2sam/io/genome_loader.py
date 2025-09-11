"""Genome loader for FASTA files."""

import os
from typing import Any, Dict, Optional, List

from ..utils.logging import setup_logging

logger = setup_logging(__name__)


class GenomeLoader:
    """Handles loading genome sequences from FASTA files."""

    def __init__(self):
        """Initialize genome loader."""

    def load_genome(
        self, genome_file: str, chromosome: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load genome sequences from FASTA file.

        Args:
            genome_file: Path to FASTA file
            chromosome: Specific chromosome to load (optional)

        Returns:
            Dictionary with genome data
        """
        if not os.path.exists(genome_file):
            raise FileNotFoundError(f"Genome file not found: {genome_file}")

        logger.info(f"Loading genome from: {genome_file}")

        sequences = {}
        current_chr = None
        current_seq = []

        with open(genome_file, "r", encoding="utf-8") as file_handle:
            for line in file_handle:
                line = line.strip()

                if line.startswith(">"):
                    # Save previous sequence
                    if current_chr and current_seq:
                        sequences[current_chr] = "".join(current_seq)

                    # Parse header
                    header = line[1:]  # Remove '>'
                    current_chr = self._parse_chromosome_name(header)
                    current_seq = []

                    # Skip if specific chromosome requested and this isn't it
                    if chromosome and current_chr != chromosome:
                        current_chr = None
                        current_seq = []

                elif current_chr and line:
                    current_seq.append(line.upper())

        # Save last sequence
        if current_chr and current_seq:
            sequences[current_chr] = "".join(current_seq)

        if chromosome and chromosome not in sequences:
            raise ValueError(f"Chromosome {chromosome} not found in genome file")

        if not sequences:
            raise ValueError(f"No sequences found in genome file: {genome_file}")

        genome_data = {
            "file": genome_file,
            "sequences": sequences,
            "total_length": sum(len(seq) for seq in sequences.values()),
        }

        logger.info(
            f"Loaded {len(sequences)} sequences with total length {genome_data['total_length']}"
        )
        return genome_data

    def _parse_chromosome_name(self, header: str) -> str:
        """Parse chromosome name from FASTA header.

        Args:
            header: FASTA header line

        Returns:
            Chromosome name
        """
        # Simple parsing - take first word after '>'
        # This can be enhanced for different header formats
        parts = header.split()
        if parts:
            return parts[0]
        return "unknown"

    def get_chromosome_list(self, genome_file: str) -> List[str]:
        """Get list of chromosomes in genome file.

        Args:
            genome_file: Path to FASTA file

        Returns:
            List of chromosome names
        """
        chromosomes = []

        with open(genome_file, "r", encoding="utf-8") as file_handle:
            for line in file_handle:
                if line.startswith(">"):
                    header = line[1:].strip()
                    chr_name = self._parse_chromosome_name(header)
                    chromosomes.append(chr_name)

        return chromosomes

    def get_sequence_length(self, genome_file: str, chromosome: str) -> int:
        """Get length of a specific chromosome.

        Args:
            genome_file: Path to FASTA file
            chromosome: Chromosome name

        Returns:
            Sequence length
        """
        genome_data = self.load_genome(genome_file, chromosome)
        if chromosome in genome_data["sequences"]:
            return len(genome_data["sequences"][chromosome])
        return 0

    def validate_genome_file(self, genome_file: str) -> Dict[str, Any]:
        """Validate genome file and return statistics.

        Args:
            genome_file: Path to FASTA file

        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "file_exists": False,
            "total_sequences": 0,
            "total_length": 0,
            "chromosomes": [],
            "errors": [],
        }

        try:
            if not os.path.exists(genome_file):
                validation_results["errors"].append(f"File not found: {genome_file}")
                return validation_results

            validation_results["file_exists"] = True

            genome_data = self.load_genome(genome_file)
            validation_results["total_sequences"] = len(genome_data["sequences"])
            validation_results["total_length"] = genome_data["total_length"]
            validation_results["chromosomes"] = list(genome_data["sequences"].keys())

        except RuntimeError as ex:
            validation_results["errors"].append(
                f"Error validating genome file: {str(ex)}"
            )

        return validation_results
