# pymethyl2sam

A Python package for simulating DNA methylation and generating synthetic NGS reads with methylation tags (MM/ML) in SAM/BAM format.

## Overview

pymethyl2sam provides a comprehensive framework for simulating DNA methylation patterns and generating synthetic next-generation sequencing reads with proper methylation tags. The package supports both stochastic (random) and deterministic (pattern-based) read generation modes, making it suitable for testing methylation analysis pipelines and educational purposes.

## Features

- **Dual Read Generation Modes**: Random (stochastic) and pattern-based (deterministic) simulation
- **Flexible Methylation Modeling**: Support for fully, partially, or unmethylated sites
- **Valid SAM/BAM Output**: Generates properly formatted files with MM/ML methylation tags
- **Configurable Parameters**: Coverage, read length, error rates, strand bias
- **Zero-based Coordinates**: Consistent with bioinformatics conventions
- **Extensible Architecture**: Modular, layered design for easy extension

## Installation

### From PyPI (when available)
```bash
pip install pymethyl2sam
```

### From Source
```bash
git clone https://github.com/yoni-w/pymethyl2sam.git
cd pymethyl2sam
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/yoni-w/pymethyl2sam.git
cd pymethyl2sam
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage (Random Mode)

```python
from pymethyl2sam import MethylationSimulator
from pymethyl2sam.core import MethylationSite
from pymethyl2sam.core.genomics import StrandOrientation
from pymethyl2sam.core.reference_genome import Hg38ReferenceGenome
from pymethyl2sam.core.sequencing import ReadGenerator, RandomStrategy
from pymethyl2sam.simulator import SequencedChromosome, SequencedRegion

# Create simulator with random read generation
simulator = MethylationSimulator(
    chromosomes=[
        SequencedChromosome(
            name="chr1",
            length=20_000,
            regions=[
                SequencedRegion(
                    start=10100,
                    end=10450,
                    read_generator=ReadGenerator(strategy=RandomStrategy()),
                )
            ],
            cpg_sites=[
                MethylationSite(position=10100, methylation_prob=1.0),
                MethylationSite(position=10149, methylation_prob=1.0),
                MethylationSite(position=10155, methylation_prob=0.0),
                MethylationSite(position=10200, methylation_prob=0.0),
                MethylationSite(position=10220, methylation_prob=1.0),
            ],
        )
    ],
    reference_genome=Hg38ReferenceGenome(),
)

# Generate reads and write to BAM
simulator.simulate_reads("output.bam")
```

### Pattern-Based Simulation

```python
from pymethyl2sam import MethylationSimulator
from pymethyl2sam.core import MethylationSite
from pymethyl2sam.core.genomics import StrandOrientation
from pymethyl2sam.core.reference_genome import Hg38ReferenceGenome
from pymethyl2sam.core.sequencing import ReadGenerator, PatternStrategy
from pymethyl2sam.simulator import SequencedChromosome, SequencedRegion

# Create simulator with pattern-based read generation
simulator = MethylationSimulator(
    chromosomes=[
        SequencedChromosome(
            name="chr1",
            length=20_000,
            regions=[
                SequencedRegion(
                    start=10100,
                    end=10250,
                    read_generator=ReadGenerator(
                        read_length=150,
                        strategy=PatternStrategy.from_offsets(
                            offsets=[0] * 10,
                            orientation=StrandOrientation.RANDOM,
                        ),
                    ),
                )
            ],
            cpg_sites=[
                MethylationSite(position=10100, methylation_prob=1.0),
                MethylationSite(position=10149, methylation_prob=1.0),
                MethylationSite(position=10155, methylation_prob=0.0),
                MethylationSite(position=10200, methylation_prob=0.0),
                MethylationSite(position=10220, methylation_prob=1.0),
            ],
        )
    ],
    reference_genome=Hg38ReferenceGenome(),
)

# Generate reads and write to BAM
simulator.simulate_reads("pattern_output.bam")
```

## Architecture

The package is organized in layers by functional responsibility:

- **core/**: Domain logic for methylation modeling, sequencing, and errors
- **simulator/**: Orchestration of read and methylation simulation
- **io/**: Parsers and I/O for FASTA, BED, YAML, JSON
- **utils/**: Logging, constants, shared helpers

### Core Components

- `MethylationSimulator`: Main class for orchestrating simulation
- `SequencedChromosome`: Represents a chromosome with defined regions and methylation sites
- `SequencedRegion`: Defines genomic regions where reads should be generated
- `ReadGenerator`: Handles read generation with different strategies (Random/Pattern)
- `MethylationSite`: Represents individual methylation sites with probabilities
- `ReferenceGenomeProvider`: Interface for accessing reference genome sequences

## Configuration Examples

### YAML Configuration Files

See `examples/config_random.yaml` and `examples/templates_pattern.yaml` for configuration file examples.

## Coordinate System

All genomic coordinates follow zero-based, half-open intervals `[start, end)`:

- A 5-base interval starting at position 100 is `[100, 105)`
- Read coordinates and methylation positions adhere to this system
- MM/ML tags follow strand-specific SAM/BAM conventions

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=pymethyl2sam --cov-report=html
```

## Development

### Code Formatting

```bash
black src/ tests/
```

### Linting

```bash
pylint src/pymethyl2sam/
```

### Pre-commit Hooks

```bash
pre-commit install
```

## Examples

See the `examples/` directory for complete working examples:

- `simulate_cpgs.py`: Demonstrates both random and pattern-based simulation
- `config_random.yaml`: YAML configuration for random mode
- `templates_pattern.yaml`: YAML template for pattern-based simulation

## Documentation

For detailed API documentation, visit: https://pymethyl2sam.readthedocs.io

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Citation

If you use pymethyl2sam in your research, please cite:

```
pymethyl2sam: A Python package for simulating DNA methylation and generating synthetic NGS reads
Yoni Weissler, 2025
```

## Support

- **Issues**: https://github.com/yoni-w/pymethyl2sam/issues
- **Documentation**: https://pymethyl2sam.readthedocs.io
- **Email**: yoni.weissler@gmail.com
