"""
Tests for the logging setup and configuration module.
Pylint-compliant and follows best practices for testing.
"""

# pylint: disable=redefined-outer-name, protected-access

import logging
from unittest.mock import patch

from pymethyl2sam.utils.logging import configure_logging, setup_logging


# --- Tests for setup_logging ---
class TestSetupLogging:
    """Tests for the setup_logging function."""

    def test_logger_creation_and_configuration(self):
        """Test that a new logger is created with the correct configuration."""
        logger_name = "test_logger_1"
        # Ensure the logger doesn't exist before the test
        logging.Logger.manager.loggerDict.pop(logger_name, None)

        logger = setup_logging(logger_name, level="DEBUG")

        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert logger.handlers[0].formatter is not None

    def test_idempotency(self):
        """Test that calling setup_logging again for the same logger does not add more handlers."""
        logger_name = "test_logger_2"
        # Ensure the logger doesn't exist before the test
        logging.Logger.manager.loggerDict.pop(logger_name, None)

        # First call
        logger1 = setup_logging(logger_name)
        assert len(logger1.handlers) == 1

        # Second call
        logger2 = setup_logging(logger_name)
        assert len(logger2.handlers) == 1
        assert logger1 is logger2  # Should be the same logger instance

    def test_default_log_level(self):
        """Test that the default log level is INFO."""
        logger_name = "test_logger_3"
        logging.Logger.manager.loggerDict.pop(logger_name, None)

        logger = setup_logging(logger_name)
        assert logger.level == logging.INFO


# --- Tests for configure_logging ---
class TestConfigureLogging:
    """Tests for the configure_logging function."""

    @patch("pymethyl2sam.utils.logging.logging.basicConfig")
    def test_basic_configuration(self, mock_basic_config):
        """Test basic logging configuration without a file."""
        configure_logging(level="WARNING")

        # Check that basicConfig was called
        mock_basic_config.assert_called_once()
        # Inspect the keyword arguments passed to basicConfig
        kwargs = mock_basic_config.call_args.kwargs
        assert kwargs["level"] == logging.WARNING
        # Check that a StreamHandler was created and NullHandler for the file
        assert any(isinstance(h, logging.StreamHandler) for h in kwargs["handlers"])
        assert any(isinstance(h, logging.NullHandler) for h in kwargs["handlers"])

    @patch("pymethyl2sam.utils.logging.logging.basicConfig")
    @patch("pymethyl2sam.utils.logging.logging.FileHandler")
    def test_configuration_with_log_file(self, mock_file_handler, mock_basic_config):
        """Test logging configuration with a specified log file."""
        log_file_path = "test.log"
        # Get a reference to the mock object that FileHandler() will return.
        # This is what should be in the handlers list.
        expected_handler_instance = mock_file_handler.return_value

        configure_logging(level="INFO", log_file=log_file_path)

        # Check that FileHandler was called with the correct path
        mock_file_handler.assert_called_once_with(log_file_path)

        # Check that basicConfig was called with the mock FileHandler instance
        kwargs = mock_basic_config.call_args.kwargs
        assert (
            expected_handler_instance in kwargs["handlers"]
        ), "Mock FileHandler instance not found in basicConfig handlers"
