from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from functools import lru_cache
from urllib.request import urlretrieve
from urllib.error import URLError, HTTPError
from typing import Optional

from pysam.libcfaidx import FastxFile
from pysam import SamtoolsError  # more specific error

from pymethyl2sam.core.genomics import GenomicInterval


# pylint: disable=R0903
class ReferenceGenomeProvider(ABC):
    @abstractmethod
    def get_sequence(self, chromosome: str, region: GenomicInterval) -> str:
        """Get the reference sequence for a specific region."""


# pylint: disable=R0903
class ConstantReferenceGenome(ReferenceGenomeProvider):
    def get_sequence(self, chromosome: str, region: GenomicInterval) -> str:
        return "A" * region.length


# pylint: disable=R0903
class Hg38ReferenceGenome(ReferenceGenomeProvider):
    def __init__(
        self,
        base_url: str = "http://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/",
        cache_dir: str = "hg38_cache",
    ):
        self.base_url = base_url
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_sequence(self, chromosome: str, region: GenomicInterval) -> str:
        """Public method to get a sequence slice with boundary checks."""
        chromosome_sequence = self._get_full_chromosome_sequence(chromosome)
        if chromosome_sequence is None:
            raise FileNotFoundError(
                f"Could not retrieve sequence for chromosome '{chromosome}'. "
                f"Expected file: {chromosome}.fa.gz in {self.cache_dir}"
            )

        chromosome_length = len(chromosome_sequence)
        if region.end > chromosome_length:
            raise ValueError(
                f"Requested interval {region.start}-{region.end} is outside the "
                f"bounds of chromosome '{chromosome}' (length: {chromosome_length})."
            )

        return chromosome_sequence[region.start : region.end]

    @lru_cache(maxsize=32)
    def _get_full_chromosome_sequence(self, chromosome: str) -> Optional[str]:
        """
        Downloads, reads, and caches the entire sequence for a given chromosome.
        """
        fasta_filename = f"{chromosome}.fa.gz"
        fasta_path = os.path.join(self.cache_dir, fasta_filename)

        if not os.path.exists(fasta_path):
            try:
                logging.info(
                    f"Downloading {fasta_filename} to cache directory '{self.cache_dir}'..."
                )
                urlretrieve(self.base_url + fasta_filename, fasta_path)
            except (URLError, HTTPError) as e:
                raise FileNotFoundError(
                    f"Failed to download {fasta_filename}: {e.reason}"
                ) from e

        try:
            with FastxFile(fasta_path) as ref:
                for entry in ref:
                    if entry.name == chromosome:
                        logging.info(f"Caching full sequence for {entry.name}")
                        return entry.sequence
        except (OSError, SamtoolsError) as e:
            logging.error(f"Error reading FASTA file '{fasta_path}': {e}")

        return None
