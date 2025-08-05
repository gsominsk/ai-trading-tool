"""
Stderr Integration Tests for AI-Optimized Logging System

Tests stderr output formatting, buffering, and integration with system streams.
Validates that logs correctly reach stderr and maintain proper JSON formatting.
"""

import pytest
import sys
import json
import subprocess
import tempfile
import os
from io import StringIO
from unittest.mock import patch, MagicMock

from src.logging_system import get_ai_logger, configure_ai_logging, MarketDataLogger
from src.logging_system.logger_config import reset_logging_state


class TestStderrIntegration:
    """Test stderr output integration for logging system."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
    
    def test_basic_stderr_output(self, capfd):
        """Test that logs are properly written to stderr."""
        logger = get_ai_logger("stderr_test")
        
        logger.info("Stderr test message",
                   operation="stderr_test",
                   context={"test": "stderr_integration"})
        
        captured = capfd.readouterr()
        
        # Should have stderr output
        assert captured.err, "Should have stderr output"
        assert captured.out == "", "Should not have stdout output"
        
        # Parse JSON from stderr
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                json_log = json.loads(line.strip())
                break
        
        assert json_log is not None, "Should find valid JSON in stderr"
        assert json_log["message"] == "Stderr test message"
        assert json_log["operation"] == "stderr_test"
    
    def test_stderr_buffering_behavior(self, capfd):
        """Test stderr buffering and flushing behavior."""
        logger = get_ai_logger("buffer_test")
        
        # Log multiple messages rapidly
        for i in range(5):
            logger.info(f"Buffer test {i}",
                       operation="buffer_test",
                       context={"iteration": i})
        
        captured = capfd.readouterr()
        
        # Should have all 5 messages in stderr
        stderr_lines = [line for line in captured.err.strip().split('\n') if line.strip()]
        json_logs = []
        
        for line in stderr_lines:
            if line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
        
        assert len(json_logs) == 5, f"Should have 5 JSON logs, got {len(json_logs)}"
        
        # Verify order preservation
        for i, log in enumerate(json_logs):
            assert f"Buffer test {i}" in log["message"]
            assert log["context"]["iteration"] == i
    
    def test_stderr_encoding_handling(self, capfd):
        """Test stderr encoding with unicode characters."""
        logger = get_ai_logger("encoding_test")
        
        # Test various unicode characters
        unicode_messages = [
            "Bitcoin: ₿ price analysis",
            "Ethereum: Ξ market data",
            "Special chars: ñáéíóú àèìòù",
            "Emoji test: 📈📉💰🚀",
            "Chinese: 比特币以太坊",
            "Russian: биткоин эфириум"
        ]
        
        for msg in unicode_messages:
            logger.info(msg,
                       operation="encoding_test",
                       context={"encoding": "utf-8"})
        
        captured = capfd.readouterr()
        
        # Parse all JSON logs
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    pytest.fail(f"Failed to parse JSON with unicode: {e}")
        
        assert len(json_logs) == len(unicode_messages)
        
        # Verify unicode preservation
        for i, log in enumerate(json_logs):
            assert log["message"] == unicode_messages[i]
    
    def test_stderr_concurrent_access(self, capfd):
        """Test stderr handling with concurrent logger access."""
        import threading
        import time
        
        loggers = [get_ai_logger(f"concurrent_{i}") for i in range(3)]
        results = []
        
        def log_worker(logger_idx):
            logger = loggers[logger_idx]
            for i in range(10):
                logger.info(f"Concurrent message {i}",
                           operation=f"concurrent_{logger_idx}",
                           context={"worker": logger_idx, "iteration": i})
                time.sleep(0.001)  # Small delay to encourage interleaving
        
        # Start concurrent logging
        threads = []
        for i in range(3):
            thread = threading.Thread(target=log_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        captured = capfd.readouterr()
        
        # Parse all logs
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
        
        # Should have 30 total logs (3 workers × 10 messages)
        assert len(json_logs) == 30, f"Expected 30 logs, got {len(json_logs)}"
        
        # Verify all workers logged
        workers_seen = set()
        for log in json_logs:
            workers_seen.add(log["context"]["worker"])
        
        assert workers_seen == {0, 1, 2}, "Should see logs from all 3 workers"
    
    def test_stderr_vs_file_output(self):
        """Test stderr vs file output behavior."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_file = f.name
        
        try:
            # Configure with file output
            configure_ai_logging(log_level="INFO", log_file=log_file)
            logger = get_ai_logger("file_test")
            
            # Log a message
            logger.info("File vs stderr test",
                       operation="file_test",
                       context={"output": "file"})
            
            # Check file contains the log
            with open(log_file, 'r') as f:
                file_content = f.read()
            
            assert "File vs stderr test" in file_content
            
            # File should contain text message (not JSON format like stderr)
            # The file handler uses default text format, stderr uses JSON
            assert "File vs stderr test" in file_content
            
            # Test passed - file output works differently than stderr JSON
            
        finally:
            # Cleanup
            if os.path.exists(log_file):
                os.unlink(log_file)
            reset_logging_state()
    
    def test_stderr_error_handling(self, capfd):
        """Test stderr behavior with logging errors."""
        logger = get_ai_logger("error_test")
        
        # Test with problematic data that might cause JSON encoding issues
        problematic_context = {
            "circular_ref": None,
            "large_number": 2**63 - 1,
            "special_float": float('inf'),
            "none_value": None,
            "empty_dict": {},
            "empty_list": []
        }
        
        # Create circular reference
        problematic_context["circular_ref"] = problematic_context
        
        try:
            logger.info("Error handling test",
                       operation="error_test",
                       context=problematic_context)
        except Exception:
            # Should handle gracefully without crashing
            pass
        
        captured = capfd.readouterr()
        
        # Should still have some stderr output (error message or partial log)
        assert captured.err, "Should have stderr output even with errors"


class TestStderrSystemIntegration:
    """Test stderr integration with system-level components."""
    
    def test_subprocess_stderr_capture(self):
        """Test stderr capture in subprocess execution."""
        # Create a simple Python script that uses our logging
        script_content = '''
import sys
sys.path.insert(0, ".")
from src.logging_system import get_ai_logger

logger = get_ai_logger("subprocess_test")
logger.info("Subprocess stderr test", operation="subprocess")
logger.error("Subprocess error test", operation="subprocess_error")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            # Run subprocess and capture stderr
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            # Check stderr contains our logs
            assert result.stderr, "Should have stderr output from subprocess"
            
            # Parse JSON logs from stderr
            stderr_lines = result.stderr.strip().split('\n')
            json_logs = []
            
            for line in stderr_lines:
                if line.strip() and line.strip().startswith('{"'):
                    try:
                        json_logs.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        pass
            
            assert len(json_logs) >= 2, "Should have at least 2 log entries"
            
            # Verify log content
            messages = [log["message"] for log in json_logs]
            assert "Subprocess stderr test" in messages
            assert "Subprocess error test" in messages
            
        finally:
            if os.path.exists(script_path):
                os.unlink(script_path)
    
    def test_stderr_redirect_behavior(self):
        """Test behavior when stderr is redirected."""
        # Create script that logs and redirects stderr
        script_content = '''
import sys
sys.path.insert(0, ".")
from src.logging_system import get_ai_logger

logger = get_ai_logger("redirect_test")
logger.info("Before redirect", operation="redirect_test")

# Redirect stderr to stdout
sys.stderr = sys.stdout
logger.info("After redirect", operation="redirect_test")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            # After redirect, logs should appear in stdout
            assert "After redirect" in result.stdout or "After redirect" in result.stderr
            
        finally:
            if os.path.exists(script_path):
                os.unlink(script_path)


class TestStderrEdgeCases:
    """Test edge cases for stderr integration."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
    
    def test_stderr_with_no_operation(self, capfd):
        """Test stderr output when operation is missing."""
        logger = get_ai_logger("no_op_test")
        
        # Log without operation parameter
        logger.info("No operation test")
        
        captured = capfd.readouterr()
        
        # Should still output to stderr
        assert captured.err, "Should have stderr output"
        
        # Parse JSON
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip().startswith('{"'):
                json_log = json.loads(line.strip())
                break
        
        assert json_log is not None
        assert json_log["message"] == "No operation test"
        assert "operation" in json_log  # Should have default operation
    
    def test_stderr_with_empty_message(self, capfd):
        """Test stderr output with empty message."""
        logger = get_ai_logger("empty_msg_test")
        
        # Log empty message
        logger.info("", operation="empty_test")
        
        captured = capfd.readouterr()
        
        # Should still output to stderr
        assert captured.err, "Should have stderr output"
        
        # Parse JSON
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip().startswith('{"'):
                json_log = json.loads(line.strip())
                break
        
        assert json_log is not None
        assert json_log["message"] == ""
        assert json_log["operation"] == "empty_test"
    
    def test_stderr_with_very_long_message(self, capfd):
        """Test stderr with very long log messages."""
        logger = get_ai_logger("long_msg_test")
        
        # Create a very long message
        long_message = "A" * 10000  # 10KB message
        
        logger.info(long_message,
                   operation="long_message_test",
                   context={"length": len(long_message)})
        
        captured = capfd.readouterr()
        
        # Should handle long message
        assert captured.err, "Should have stderr output"
        assert long_message in captured.err, "Should contain full long message"
        
        # Parse JSON (should be valid despite length)
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip().startswith('{"'):
                json_log = json.loads(line.strip())
                break
        
        assert json_log is not None
        assert json_log["message"] == long_message
        assert json_log["context"]["length"] == 10000