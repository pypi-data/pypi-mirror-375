"""Error model for simulating sequencing errors and mutations."""

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ErrorParameters:
    """Parameters for error simulation."""

    mismatch_rate: float
    insertion_rate: float
    deletion_rate: float

    def __post_init__(self):
        """Validate error parameters."""
        if not 0 <= self.mismatch_rate <= 1:
            raise ValueError("Mismatch rate must be between 0 and 1")
        if not 0 <= self.insertion_rate <= 1:
            raise ValueError("Insertion rate must be between 0 and 1")
        if not 0 <= self.deletion_rate <= 1:
            raise ValueError("Deletion rate must be between 0 and 1")


class ErrorModel:
    """Handles sequencing error simulation and mutations."""

    def __init__(self, parameters: ErrorParameters):
        """Initialize error model.

        Args:
            parameters: Error simulation parameters
        """
        self.parameters = parameters
        self._mismatch_bases = {
            "A": ["C", "G", "T"],
            "C": ["A", "G", "T"],
            "G": ["A", "C", "T"],
            "T": ["A", "C", "G"],
            "N": ["A", "C", "G", "T"],  # Handle 'N' bases
        }

    def introduce_errors(self, sequence: str) -> Tuple[str, List[Dict]]:
        """Introduce sequencing errors into a sequence.

        Args:
            sequence: Original DNA sequence

        Returns:
            Tuple of (modified_sequence, error_log)
        """
        modified_sequence = list(sequence)
        error_log = []
        i = 0
        total_error_rate = (
            self.parameters.mismatch_rate
            + self.parameters.insertion_rate
            + self.parameters.deletion_rate
        )

        while i < len(modified_sequence):
            # First, determine if any error should occur at this position
            if random.random() < total_error_rate:
                error_type = self._choose_error_type()
                base = modified_sequence[i]

                if error_type == "mismatch":
                    new_base = random.choice(
                        self._mismatch_bases.get(base, ["A", "C", "G", "T"])
                    )
                    modified_sequence[i] = new_base
                    error_log.append(
                        {
                            "position": i,
                            "type": "mismatch",
                            "original": base,
                            "new": new_base,
                        }
                    )
                elif error_type == "insertion":
                    inserted_base = random.choice(["A", "C", "G", "T"])
                    modified_sequence.insert(i, inserted_base)
                    error_log.append(
                        {"position": i, "type": "insertion", "inserted": inserted_base}
                    )
                    i += 1  # Skip the newly inserted base to avoid cascading errors
                elif error_type == "deletion":
                    deleted_base = modified_sequence.pop(i)
                    error_log.append(
                        {"position": i, "type": "deletion", "deleted": deleted_base}
                    )
                    continue  # Loop again at the same index `i` on the now-shorter list
            i += 1
        return "".join(modified_sequence), error_log

    def _choose_error_type(self) -> str:
        """Choose an error type based on the relative rates of configured errors.

        Returns:
            Error type ("mismatch", "insertion", or "deletion")
        """
        total_rate = (
            self.parameters.mismatch_rate
            + self.parameters.insertion_rate
            + self.parameters.deletion_rate
        )
        if total_rate == 0:
            return "none"  # No errors to choose from

        # Normalize rates to create a probability distribution
        norm_mismatch = self.parameters.mismatch_rate / total_rate
        norm_insertion = self.parameters.insertion_rate / total_rate
        rand = random.random()

        if rand < norm_mismatch:
            return "mismatch"
        if rand < norm_mismatch + norm_insertion:
            return "insertion"
        return "deletion"

    @staticmethod
    def calculate_quality_scores(
        sequence_length: int, base_quality: int = 30
    ) -> List[int]:
        """Calculate quality scores for a sequence.

        Args:
            sequence_length: Length of the sequence
            base_quality: Base quality score (Phred scale)

        Returns:
            List of quality scores
        """
        if sequence_length < 0:
            raise ValueError("Sequence length cannot be negative.")
        return [base_quality] * sequence_length

    def introduce_methylation_errors(
        self, methylation_sites: List[Dict], error_rate: float = 0.01
    ) -> List[Dict]:
        """Introduce errors in methylation detection.

        Args:
            methylation_sites: List of methylation site dictionaries
            error_rate: Rate of methylation detection errors

        Returns:
            Modified list of methylation sites without altering the original.
        """
        if not 0 <= error_rate <= 1:
            raise ValueError("Methylation error rate must be between 0 and 1")

        modified_sites = []
        for site in methylation_sites:
            site_copy = site.copy()  # Avoid modifying the original list of dicts
            if random.random() < error_rate:
                # Flip methylation state
                site_copy["detected"] = not site_copy.get("detected", True)
                site_copy["error"] = True
            else:
                site_copy["error"] = False
            modified_sites.append(site_copy)
        return modified_sites

    def simulate_sequencing_artifacts(
        self, sequence: str, position: int
    ) -> Tuple[str, Dict]:
        """Simulate sequencing artifacts at a specific position.

        Args:
            sequence: DNA sequence
            position: Position to introduce artifact

        Returns:
            Tuple of (modified_sequence, artifact_info)
        """
        if not 0 <= position < len(sequence):
            raise ValueError("Position must be a valid index in the sequence.")

        artifact_types = ["stutter", "dropout", "amplification_bias"]
        artifact_type = random.choice(artifact_types)
        modified_sequence = list(sequence)
        artifact_info = {"type": artifact_type, "position": position}

        if artifact_type == "stutter":
            base = modified_sequence[position]
            modified_sequence.insert(position, base)
            artifact_info["repeated_base"] = base
        elif artifact_type == "dropout":
            deleted_base = modified_sequence.pop(position)
            artifact_info["deleted_base"] = deleted_base
        elif artifact_type == "amplification_bias":
            base_to_change = modified_sequence[position]
            bias_bases = ["A", "T"]  # Example bias
            if base_to_change not in bias_bases:
                new_base = random.choice(bias_bases)
                modified_sequence[position] = new_base
                artifact_info["original_base"] = base_to_change
                artifact_info["biased_base"] = new_base
        return "".join(modified_sequence), artifact_info
