from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


# Methylation modifications
class ModificationType(Enum):
    C5MC = "5mC"
    C5HMC = "5hmC"
    C5FC = "5fC"
    C5CAC = "5caC"


class StrandOrientation(Enum):
    FORWARD = "+"
    BACKWARD = "-"
    RANDOM = "?"

    def to_is_reverse(self) -> bool:
        if self is StrandOrientation.FORWARD:
            return False
        if self is StrandOrientation.BACKWARD:
            return True
        if self is StrandOrientation.RANDOM:
            return random.choice([True, False])
        raise ValueError(f"Unsupported strand orientation: {self}")

    def __repr__(self):
        return self.value


@dataclass(frozen=True)
class Chromosome:
    """
    Represents a simulated chromosome with defined CpG sites and simulation regions.
    """

    name: str
    length: int


@dataclass(frozen=True, order=True)
class MethylationSite:
    """
    Represents a CpG site in a genome with a probability of being methylated.
    """

    position: int  # Zero-based position in reference
    context: str = "CG"  # Methylation context (e.g., "CG", "CHG")
    modification: ModificationType = ModificationType("5mC")
    methylation_prob: float = 0.5

    def __post_init__(self):
        """Validate methylation site parameters."""
        if not 0.0 <= self.methylation_prob <= 1.0:
            raise ValueError(
                f"methylation_prob must be in [0, 1], got {self.methylation_prob}"
            )
        if self.position < 0:
            raise ValueError("Position must be non-negative")
        if not self.context:
            raise ValueError("Context cannot be empty")

    def with_position(self, new_position: int) -> MethylationSite:
        return MethylationSite(
            methylation_prob=self.methylation_prob,
            position=new_position,
            context=self.context,
            modification=self.modification,
        )

    def get_cytosine_position(self, is_reverse_strand: bool):
        return self.position + 1 if is_reverse_strand else self.position


@dataclass(frozen=True)
class GenomicInterval:
    """
    Represents a genomic interval using half-open coordinates [start, end).

    Attributes:
        start (int): Start coordinate (inclusive).
        end (int): End coordinate (exclusive).
    """

    start: int  # inclusive
    end: int  # exclusive (half-open)
    is_reverse: bool

    def __post_init__(self):
        """Validate region parameters after initialization."""
        if self.start < 0:
            raise ValueError("Start position must be non-negative")
        if self.end < self.start:
            raise ValueError("End position must not be smaller than start position")

    @property
    def length(self) -> int:
        """Return the length of the region (0-based, half-open)."""
        return self.end - self.start

    def contains(self, position: int) -> bool:
        """
        Check if a specific position is within the region.

        Args:
            position (int): Genomic position to check.

        Returns:
            bool: True if the position is within the region.
        """
        # pylint: disable=W0511
        # TODO: validate consistency on BW strand
        return self.start <= position < self.end
