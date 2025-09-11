"""Constants used throughout the package."""

from typing import Dict

_ORIG_BASES = "ACGTacgt"
_COMP_BASES = "TGCAtgca"
COMPLEMENT_TABLE: Dict[int, int] = str.maketrans(_ORIG_BASES, _COMP_BASES)

INSTRUMENT = "A00000"
RUN_NUMBER = 1
FLOWCELL_ID = "ABCD1234"

# Strand orientations
STRANDS = ["+", "-"]

# SAM/BAM tag names
MM_TAG = "MM"  # Methylation modification
ML_TAG = "ML"  # Methylation level

# Default values
DEFAULT_COVERAGE = 10.0
DEFAULT_READ_LENGTH = 100
DEFAULT_ERROR_RATE = 0.005
DEFAULT_METHYLATION_RATIO = 0.7
DEFAULT_BASE_QUALITY = 30

# File extensions
SUPPORTED_GENOME_FORMATS = [".fasta", ".fa", ".fna"]
SUPPORTED_TEMPLATE_FORMATS = [".yaml", ".yml", ".json"]
SUPPORTED_CONFIG_FORMATS = [".yaml", ".yml", ".json"]

# Coordinate system
COORDINATE_SYSTEM = "zero-based"
INTERVAL_FORMAT = "half-open"  # [start, end)

# Error types
ERROR_TYPES = ["mismatch", "insertion", "deletion"]

# Quality score ranges
MIN_QUALITY_SCORE = 0
MAX_QUALITY_SCORE = 93

# SAM/BAM flags
SAM_FLAG_PAIRED = 1
SAM_FLAG_PROPER_PAIR = 2
SAM_FLAG_UNMAP = 4
SAM_FLAG_MUNMAP = 8
SAM_FLAG_REVERSE = 16
SAM_FLAG_MREVERSE = 32
SAM_FLAG_READ1 = 64
SAM_FLAG_READ2 = 128
SAM_FLAG_SECONDARY = 256
SAM_FLAG_QCFAIL = 512
SAM_FLAG_DUP = 1024
SAM_FLAG_SUPPLEMENTARY = 2048
