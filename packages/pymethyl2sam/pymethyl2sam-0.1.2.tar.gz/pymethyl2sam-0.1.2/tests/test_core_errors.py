"""
Tests for the sequencing error simulation module.
Pylint-compliant and follows best practices for testing.
"""

# pylint: disable=redefined-outer-name, protected-access

from unittest.mock import patch

import pytest

from pymethyl2sam.core.errors import ErrorModel, ErrorParameters


# --- Tests for ErrorParameters ---
class TestErrorParameters:
    """Tests for the ErrorParameters dataclass."""

    def test_successful_creation(self):
        """Test that valid parameters create an object successfully."""
        params = ErrorParameters(
            mismatch_rate=0.1, insertion_rate=0.05, deletion_rate=0.02
        )
        assert params.mismatch_rate == 0.1

    @pytest.mark.parametrize(
        "rate_name, rate_value",
        [
            ("mismatch_rate", -0.1),
            ("mismatch_rate", 1.1),
            ("insertion_rate", -0.1),
            ("deletion_rate", 1.1),
        ],
    )
    def test_invalid_rates_raise_error(self, rate_name, rate_value):
        """Test that rates outside the [0, 1] range raise a ValueError."""
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            ErrorParameters(
                mismatch_rate=0.1 if rate_name != "mismatch_rate" else rate_value,
                insertion_rate=0.1 if rate_name != "insertion_rate" else rate_value,
                deletion_rate=0.1 if rate_name != "deletion_rate" else rate_value,
            )


# --- Tests for ErrorModel ---
class TestErrorModel:
    """Tests for the ErrorModel class."""

    @patch("pymethyl2sam.core.errors.random.random")
    def test_introduce_errors_no_errors(self, mock_random):
        """Test that no errors are introduced if random values are high."""
        params = ErrorParameters(
            mismatch_rate=0.1, insertion_rate=0.1, deletion_rate=0.1
        )
        model = ErrorModel(parameters=params)
        mock_random.return_value = 0.9  # Higher than total error rate (0.3)
        sequence = "ATGC"
        mod_seq, log = model.introduce_errors(sequence)
        assert mod_seq == sequence
        assert not log

    @patch("pymethyl2sam.core.errors.random.random")
    def test_introduce_errors_guaranteed_mismatch(self, mock_random):
        """Test a guaranteed mismatch error."""
        params = ErrorParameters(
            mismatch_rate=1.0, insertion_rate=0.0, deletion_rate=0.0
        )
        model = ErrorModel(parameters=params)
        # 1st random call: < 1.0 (triggers error), 2nd: < 1.0 (chooses mismatch)
        mock_random.side_effect = [0.1, 0.1]
        with patch("pymethyl2sam.core.errors.random.choice", return_value="T"):
            mod_seq, log = model.introduce_errors("A")
            assert mod_seq == "T"
            assert len(log) == 1
            assert log[0]["type"] == "mismatch"
            assert log[0]["original"] == "A"
            assert log[0]["new"] == "T"

    @patch("pymethyl2sam.core.errors.random.random")
    def test_introduce_errors_guaranteed_insertion(self, mock_random):
        """Test a guaranteed insertion error."""
        params = ErrorParameters(
            mismatch_rate=0.0, insertion_rate=1.0, deletion_rate=0.0
        )
        model = ErrorModel(parameters=params)
        # 1st random call: < 1.0 (triggers error), 2nd: > 0.0 (chooses insertion)
        mock_random.side_effect = [0.1, 0.5]
        with patch("pymethyl2sam.core.errors.random.choice", return_value="C"):
            mod_seq, log = model.introduce_errors("A")
            assert mod_seq == "CA"
            assert len(log) == 1
            assert log[0]["type"] == "insertion"
            assert log[0]["inserted"] == "C"

    @patch("pymethyl2sam.core.errors.random.random")
    def test_introduce_errors_guaranteed_deletion(self, mock_random):
        """Test a guaranteed deletion error for every character."""
        params = ErrorParameters(
            mismatch_rate=0.0, insertion_rate=0.0, deletion_rate=1.0
        )
        model = ErrorModel(parameters=params)
        # For sequence "AG", the loop runs twice. Each time an error is triggered,
        # requiring two random numbers per original base due to the 'continue'.
        mock_random.side_effect = [0.1, 0.9, 0.1, 0.9]
        mod_seq, log = model.introduce_errors("AG")
        assert mod_seq == ""
        assert len(log) == 2
        assert log[0] == {"position": 0, "type": "deletion", "deleted": "A"}
        assert log[1] == {"position": 0, "type": "deletion", "deleted": "G"}

    def test_calculate_quality_scores(self):
        """Test the static calculate_quality_scores method."""
        scores = ErrorModel.calculate_quality_scores(5, base_quality=40)
        assert scores == [40, 40, 40, 40, 40]
        with pytest.raises(ValueError):
            ErrorModel.calculate_quality_scores(-1)

    @patch("pymethyl2sam.core.errors.random.random")
    def test_introduce_methylation_errors(self, mock_random):
        """Test the introduction of methylation detection errors."""
        model = ErrorModel(ErrorParameters(0, 0, 0))
        sites = [{"pos": 10, "detected": True}, {"pos": 20, "detected": False}]

        # --- Test error case ---
        mock_random.return_value = 0.005  # Lower than error rate
        mod_sites = model.introduce_methylation_errors(sites, error_rate=0.01)
        # Check that original list is not modified
        assert sites[0]["detected"] is True
        # Check new list
        assert mod_sites[0]["detected"] is False  # Flipped
        assert mod_sites[0]["error"] is True
        assert mod_sites[1]["detected"] is True  # Flipped
        assert mod_sites[1]["error"] is True

        # --- Test no error case ---
        mock_random.return_value = 0.9  # Higher than error rate
        mod_sites = model.introduce_methylation_errors(sites, error_rate=0.01)
        assert mod_sites[0]["detected"] is True
        assert mod_sites[0]["error"] is False
        assert mod_sites[1]["detected"] is False
        assert mod_sites[1]["error"] is False

    @patch("pymethyl2sam.core.errors.random.choice")
    def test_simulate_sequencing_artifacts(self, mock_choice):
        """Test the simulation of specific sequencing artifacts."""
        model = ErrorModel(ErrorParameters(0, 0, 0))
        sequence = "ATGC"

        # Test stutter
        mock_choice.return_value = "stutter"
        mod_seq, info = model.simulate_sequencing_artifacts(sequence, 1)
        assert mod_seq == "ATTGC"
        assert info["type"] == "stutter"

        # Test dropout
        mock_choice.return_value = "dropout"
        mod_seq, info = model.simulate_sequencing_artifacts(sequence, 1)
        assert mod_seq == "AGC"
        assert info["type"] == "dropout"

        # Test invalid position
        with pytest.raises(ValueError, match="Position must be a valid index"):
            model.simulate_sequencing_artifacts(sequence, 4)
