"""
Test CLI output channel separation.

Validates that logs go to stderr while data goes to stdout.
"""

import sys
from io import StringIO
from unittest.mock import patch

from chirality.lib.logging import (
    log_info,
    log_error,
    log_success,
    log_progress,
    output_data,
    log_with_prefix,
    log_stats,
)


def test_log_functions_use_stderr():
    """Test that all log functions write to stderr."""
    # Capture stderr
    with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        log_info("Test info message")
        log_error("Test error message")
        log_success("Test success message")
        log_progress("Test progress message")
        log_with_prefix("PREFIX", "Test prefixed message")

        stderr_output = mock_stderr.getvalue()

        # All messages should appear in stderr
        assert "Test info message" in stderr_output
        assert "❌ Test error message" in stderr_output
        assert "✓ Test success message" in stderr_output
        assert "🔄 Test progress message" in stderr_output
        assert "PREFIX Test prefixed message" in stderr_output


def test_output_data_uses_stdout():
    """Test that output_data writes to stdout."""
    # Capture stdout
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        output_data("test_data_output")

        stdout_output = mock_stdout.getvalue()
        assert "test_data_output" in stdout_output


def test_log_stats_uses_stderr():
    """Test that log_stats writes to stderr with formatting."""
    stats = {"cells_computed": 10, "cells_cached": 5, "total_time": 120.5}

    with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        log_stats(stats)

        stderr_output = mock_stderr.getvalue()

        # Should contain formatted stats
        assert "  - cells_computed: 10" in stderr_output
        assert "  - cells_cached: 5" in stderr_output
        assert "  - total_time: 120.5" in stderr_output


def test_log_stats_with_custom_prefix():
    """Test log_stats with custom prefix."""
    stats = {"test_key": "test_value"}

    with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        log_stats(stats, prefix="***")

        stderr_output = mock_stderr.getvalue()
        assert "*** test_key: test_value" in stderr_output


def test_channel_separation():
    """Test that stderr and stdout remain separate."""
    # Test simultaneous output to both channels
    with (
        patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        patch("sys.stderr", new_callable=StringIO) as mock_stderr,
    ):

        # Log to stderr
        log_info("This is a log message")
        log_error("This is an error")

        # Output data to stdout
        output_data("kernel_hash_abc123")
        output_data("phase1_complete")

        stdout_content = mock_stdout.getvalue()
        stderr_content = mock_stderr.getvalue()

        # Data should only be in stdout
        assert "kernel_hash_abc123" in stdout_content
        assert "phase1_complete" in stdout_content
        assert "kernel_hash_abc123" not in stderr_content
        assert "phase1_complete" not in stderr_content

        # Logs should only be in stderr
        assert "This is a log message" in stderr_content
        assert "❌ This is an error" in stderr_content
        assert "This is a log message" not in stdout_content
        assert "❌ This is an error" not in stdout_content


def test_emoji_formatting():
    """Test that emoji prefixes are applied correctly."""
    with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        log_error("Test error")
        log_success("Test success")
        log_progress("Test progress")

        stderr_output = mock_stderr.getvalue()

        # Check emoji prefixes
        assert "❌ Test error" in stderr_output
        assert "✓ Test success" in stderr_output
        assert "🔄 Test progress" in stderr_output
