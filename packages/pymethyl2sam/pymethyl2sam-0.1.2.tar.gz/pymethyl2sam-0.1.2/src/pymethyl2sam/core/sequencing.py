from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import randint
from typing import Iterable

from pymethyl2sam.core.genomics import (
    MethylationSite,
    StrandOrientation,
    GenomicInterval,
)


@dataclass(frozen=True)
class ReadQuality:
    """Quality scores for sequencing and mapping."""

    sequencing_score: int = 32
    mapping_score: int = 100

    def __post_init__(self):
        if not 0 <= self.sequencing_score <= 50:
            raise ValueError("sequencing_score must be in the range [0, 50].")
        if not 0 <= self.mapping_score <= 255:
            raise ValueError("mapping_score must be in the range [0, 255].")


@dataclass(frozen=True, order=True)
class ReadTemplate(GenomicInterval):
    """Template for generating a single read with quality and methylation sites."""

    quality: ReadQuality
    local_methylated_sites: list[MethylationSite]


@dataclass(frozen=True)
class ReadGenerationStrategy(ABC):
    """Abstract base class for read generation strategies."""

    @abstractmethod
    def generate_read_intervals(
        self, region: GenomicInterval, read_length: int
    ) -> Iterable[GenomicInterval]:
        pass

    @property
    @abstractmethod
    def total_reads(self) -> int:
        pass


@dataclass(frozen=True)
class PatternedReadData:
    """Data class representing a single read pattern with offset and orientation."""

    offset: int
    orientation: StrandOrientation


@dataclass(frozen=True)
class PatternStrategy(ReadGenerationStrategy):
    data: Iterable[PatternedReadData]

    def generate_read_intervals(
        self, region: GenomicInterval, read_length: int
    ) -> Iterable[GenomicInterval]:
        for read in self.data:
            start = region.start + read.offset
            yield GenomicInterval(
                start=start,
                end=start + read_length,
                is_reverse=read.orientation.to_is_reverse(),
            )

    @property
    def total_reads(self) -> int:
        return len(list(self.data))

    @staticmethod
    def from_offset_orientation_pairs(
        offsets: Iterable[int], orientations: Iterable[StrandOrientation | str]
    ) -> PatternStrategy:
        """Create a PatternStrategy from paired offsets and orientations.

        Args:
            offsets: Iterable of offset positions
            orientations: Iterable of strand orientations (can be strings or StrandOrientation)

        Returns:
            PatternStrategy configured with the provided data
        """
        data = [
            PatternedReadData(
                offset=offset,
                orientation=(
                    orientation
                    if isinstance(orientation, StrandOrientation)
                    else StrandOrientation(orientation)
                ),
            )
            for offset, orientation in zip(offsets, orientations)
        ]
        return PatternStrategy(data)

    @staticmethod
    def from_offsets(
        offsets: Iterable[int], orientation: StrandOrientation
    ) -> PatternStrategy:
        """Create a PatternStrategy from offsets with a single orientation.

        Args:
            offsets: Iterable of offset positions
            orientation: Single strand orientation for all reads

        Returns:
            PatternStrategy configured with the provided data
        """
        data = [
            PatternedReadData(
                offset=offset,
                orientation=orientation,
            )
            for offset in offsets
        ]
        return PatternStrategy(data)


@dataclass(frozen=True)
class RandomStrategy(ReadGenerationStrategy):
    """Strategy for generating reads at random positions."""

    reads_per_region: int = 200
    orientation: StrandOrientation = StrandOrientation.RANDOM

    def __post_init__(self):
        if self.reads_per_region <= 0:
            raise ValueError("reads_per_region must be a positive integer.")

    def generate_read_intervals(
        self, region: GenomicInterval, read_length: int
    ) -> Iterable[GenomicInterval]:
        min_start = max(region.start - read_length + 1, 0)
        max_start = region.end + read_length - 1
        for _ in range(self.reads_per_region):
            start = randint(min_start, max_start)
            yield GenomicInterval(
                start=start,
                end=start + read_length,
                is_reverse=self.orientation.to_is_reverse(),
            )

    @property
    def total_reads(self) -> int:
        return self.reads_per_region


@dataclass(frozen=True)
class EmptyStrategy(ReadGenerationStrategy):
    """Strategy that generates no reads."""

    def generate_read_intervals(
        self, region: GenomicInterval, read_length: int
    ) -> Iterable[GenomicInterval]:
        return []

    @property
    def total_reads(self) -> int:
        return 0


@dataclass(frozen=True)
class ReadGenerator:
    """Generates reads using a specified strategy."""

    strategy: ReadGenerationStrategy
    read_length: int = 150
    quality: ReadQuality = ReadQuality()

    def __post_init__(self):
        if self.read_length <= 0:
            raise ValueError("read_length must be a positive integer.")

    def generate_reads(
        self,
        region: GenomicInterval,
        cpg_sites: Iterable[MethylationSite],
    ) -> Iterable[ReadTemplate]:
        for interval in self.strategy.generate_read_intervals(region, self.read_length):
            local_methylated_sites = [
                site.with_position(site.position - interval.start)
                for site in cpg_sites
                if interval.contains(site.position)
            ]
            yield ReadTemplate(
                quality=self.quality,
                local_methylated_sites=local_methylated_sites,
                **interval.__dict__,
            )

    def __repr__(self):
        """Return a string representation of the ReadGenerator."""

        def format_value(val) -> str:
            """Format a value for display in the representation."""
            if isinstance(val, list) and len(val) == 1:
                val = val[0]
            if (
                isinstance(val, str)
                and val.isascii()
                and 0 < len(val) <= 3
                and val.isprintable()
            ):
                return val
            return repr(val)

        parts = [
            f"{key.replace('_', ' ')}:{format_value(value)}"
            for key, value in self.__dict__.items()
        ]
        return f"{self.__class__.__name__}({', '.join(parts)})"
