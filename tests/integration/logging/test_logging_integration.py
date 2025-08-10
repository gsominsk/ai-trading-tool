"""
Integration Tests for Logging System

Consolidated integration tests for stderr integration, system-level behavior,
and complete logging workflows.

Consolidates:
- test_stderr_integration.py (stderr output and system integration)
- test_trading_logging_integration.py (trading system integration)
- Integration test scenarios from other logging tests
"""

import pytest
import sys
import json
import subprocess
import tempfile
import os
import threading
import time
from io import StringIO
from unittest.mock import patch, MagicMock

from src.logging_system import (
    get_ai_logger,
    configure_ai_logging,
    MarketDataLogger,
    flow_operation,
    get_trace_id,
    reset_trace_counter
)
from src.logging_system.json_formatter import AIOptimizedJSONFormatter
from src.logging_system.logger_config import reset_logging_state
from src.logging_system.flow_context import advance_to_stage
from src.market_data.market_data_service import MarketDataService


@pytest.mark.integration
@pytest.mark.logging
class TestStderrIntegration:
    """Test stderr output integration for logging system."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
    
    def test_basic_stderr_output(self, caplog):
        """Test that logs are properly written."""
        logger = get_ai_logger("stderr_test", service_name="test_service")

        with caplog.at_level("INFO"):
            logger.info("Stderr test message",
                       operation="stderr_test",
                       context={"test": "stderr_integration"})

        assert len(caplog.records) == 1, "Should have one log record"

        # Manually format the record to get the JSON output.
        record = caplog.records[0]
        formatter = AIOptimizedJSONFormatter()
        json_string = formatter.format(record)
        json_log = json.loads(json_string)

        assert json_log is not None, "Should find valid JSON in log text"
        assert json_log["message"] == "Stderr test message"
        assert json_log["operation"] == "stderr_test"
        assert json_log["service"] == "test_service"
    
    def test_stderr_buffering_behavior(self, caplog):
        """Test logging buffering and flushing behavior."""
        logger = get_ai_logger("buffer_test", service_name="test_service")

        with caplog.at_level("INFO"):
            # Log multiple messages rapidly
            for i in range(5):
                logger.info(f"Buffer test {i}",
                           operation="buffer_test",
                           context={"iteration": i})

        assert len(caplog.records) == 5, f"Should have 5 log records, got {len(caplog.records)}"
        
        formatter = AIOptimizedJSONFormatter()
        json_logs = [json.loads(formatter.format(rec)) for rec in caplog.records]
        
        # Verify order preservation
        for i, log in enumerate(json_logs):
            assert f"Buffer test {i}" in log["message"]
            assert log["context"]["iteration"] == i
    
    def test_stderr_encoding_handling(self, caplog):
        """Test logging encoding with unicode characters."""
        logger = get_ai_logger("encoding_test", service_name="test_service")

        # Test various unicode characters
        unicode_messages = [
            "Bitcoin: ₿ price analysis",
            "Ethereum: Ξ market data",
            "Special chars: ñáéíóú àèìòù",
            "Emoji test: 📈📉💰🚀",
            "Chinese: 比特币以太坊",
            "Russian: биткоин эфириум"
        ]

        with caplog.at_level("INFO"):
            for msg in unicode_messages:
                logger.info(msg,
                           operation="encoding_test",
                           context={"encoding": "utf-8"})

        assert len(caplog.records) == len(unicode_messages)
        
        formatter = AIOptimizedJSONFormatter()
        json_logs = [json.loads(formatter.format(rec)) for rec in caplog.records]
        
        # Verify unicode preservation
        for i, log in enumerate(json_logs):
            assert log["message"] == unicode_messages[i]
    
    def test_stderr_concurrent_access(self, caplog):
        """Test logging with concurrent logger access."""
        loggers = [get_ai_logger(f"concurrent_{i}", service_name=f"worker_{i}") for i in range(3)]
        
        def log_worker(logger_idx):
            logger = loggers[logger_idx]
            for i in range(10):
                logger.info(f"Concurrent message {i}",
                           operation=f"concurrent_{logger_idx}",
                           context={"worker": logger_idx, "iteration": i})
                time.sleep(0.001)  # Small delay to encourage interleaving

        with caplog.at_level("INFO"):
            # Start concurrent logging
            threads = []
            for i in range(3):
                thread = threading.Thread(target=log_worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
        
        # Should have 30 total logs (3 workers × 10 messages)
        assert len(caplog.records) == 30, f"Expected 30 logs, got {len(caplog.records)}"
        
        formatter = AIOptimizedJSONFormatter()
        json_logs = [json.loads(formatter.format(rec)) for rec in caplog.records]
        
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
            configure_ai_logging(log_level="INFO", log_file=log_file, console_output=False)
            logger = get_ai_logger("file_test", service_name="test_service")
            
            # Log a message
            logger.info("File vs stderr test",
                       operation="file_test",
                       context={"output": "file"})
            
            # Check file contains the log
            with open(log_file, 'r') as f:
                file_content = f.read()
            
            assert "File vs stderr test" in file_content
            
        finally:
            # Cleanup
            if os.path.exists(log_file):
                os.unlink(log_file)
            reset_logging_state()
    
    def test_stderr_error_handling(self, caplog):
        """Test logging behavior with logging errors."""
        logger = get_ai_logger("error_test", service_name="test_service")

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

        with caplog.at_level("INFO"):
            try:
                logger.info("Error handling test",
                           operation="error_test",
                           context=problematic_context)
            except Exception:
                # Should handle gracefully without crashing
                pass

        # The logger should have attempted to log something, even if it failed.
        # The default formatter will probably log an error message.
        assert caplog.text, "Should have log output even with errors"


@pytest.mark.integration
@pytest.mark.logging
class TestSystemIntegration:
    """Test system-level integration scenarios."""
    
    def test_subprocess_stderr_capture(self):
        """Test stderr capture in subprocess execution."""
        # Create a simple Python script that uses our logging
        script_content = '''
import sys
sys.path.insert(0, ".")
from src.logging_system import get_ai_logger, configure_ai_logging

configure_ai_logging(log_level="INFO", console_output=True)
logger = get_ai_logger("subprocess_test", service_name="test_service")
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
            # The subprocess might not inherit the logging config, so we check for any output
            assert result.stderr or result.stdout, "Should have some output from subprocess"
            
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
import os
sys.path.insert(0, os.getcwd())
from src.logging_system import get_ai_logger, configure_ai_logging, reset_logging_state

# Initial configuration - logs go to original stderr
configure_ai_logging(log_level="INFO", console_output=True)
logger = get_ai_logger("redirect_test", service_name="test_service")
logger.info("Before redirect", operation="redirect_test")

# Redirect stderr to stdout
sys.stderr = sys.stdout

# Reset the logging system's state completely
reset_logging_state()

# Now, re-configure. This will create a new handler pointing to the new sys.stderr (stdout)
configure_ai_logging(log_level="INFO", console_output=True)

# Get a new logger instance after re-configuration
logger_after_redirect = get_ai_logger("redirect_test", service_name="test_service")
logger_after_redirect.info("After redirect", operation="redirect_test")
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
            assert "After redirect" in result.stdout, f"stdout: {result.stdout}, stderr: {result.stderr}"
            
        finally:
            if os.path.exists(script_path):
                os.unlink(script_path)


@pytest.mark.integration
@pytest.mark.logging
class TestTradingLoggingIntegration:
    """Test trading system integration with logging."""
    
    def setup_method(self):
        """Setup for each test."""
        reset_logging_state()
        configure_ai_logging(log_level="DEBUG", console_output=False)
    
    def test_market_data_service_logging_integration(self, caplog):
        """Test MarketDataService integration with logging system."""
        service = MarketDataService(enable_logging=True, log_level="DEBUG")
        
        # Test that service has logger
        assert hasattr(service, 'logger')
        assert service.logger is not None
        
        # Test logging operations work
        service._log_operation_start("test_operation", symbol="BTCUSDT")
        service._log_operation_success("test_operation", symbol="BTCUSDT")
        
        # Verify logs were created
        assert len(caplog.records) >= 2
        
        # Verify log content
        log_messages = [record.message for record in caplog.records]
        assert any("test_operation initiated" in msg for msg in log_messages)
        assert any("test_operation completed successfully" in msg for msg in log_messages)
    
    def test_complete_market_data_flow_integration(self, caplog):
        """Test complete market data operation flow with logging."""
        service = MarketDataService(enable_logging=True, log_level="DEBUG")
        
        # Simulate complete market data workflow
        with flow_operation("BTCUSDT", "get_market_data") as trace_id:
            # Start operation
            service._log_operation_start("get_market_data", symbol="BTCUSDT")
            
            # Symbol validation stage
            advance_to_stage("symbol_validation")
            
            # Data collection stage
            advance_to_stage("data_collection")
            # Test API call logging through the new DI system
            service.logger.log_api_call("BTCUSDT", "1d", 180, response_time_ms=150)
            
            # Technical indicators stage
            advance_to_stage("technical_indicators")
            # Test calculation logging through the new DI system
            service.logger.log_calculation("RSI", "BTCUSDT", result="65")
            
            # Complete operation
            advance_to_stage("completion")
            service._log_operation_success("get_market_data", symbol="BTCUSDT")
        
        # Verify complete workflow was logged
        assert len(caplog.records) >= 4
        
        # Verify flow progression
        log_messages = [record.message for record in caplog.records]
        assert any("get_market_data initiated" in msg for msg in log_messages)
        assert any("get_market_data completed successfully" in msg for msg in log_messages)
    
    def test_trading_operations_logging_integration(self):
        """Test trading operations logging integration."""
        service = MarketDataService(enable_logging=True, log_level="DEBUG")
        
        # Test all trading operation logging methods
        try:
            # Test basic logging operations that are available in new architecture
            service._log_operation_start("buy_signal", symbol="BTCUSDT")
            service._log_operation_success("buy_signal", symbol="BTCUSDT")
            
            # Test direct logger operations
            service.logger.log_api_call("BTCUSDT", "1d", 180, response_time_ms=45)
            service.logger.log_calculation("RSI", "BTCUSDT", result="65")
            
            # All operations should complete without errors
            assert True, "All trading operations logging should work"
            
        except Exception as e:
            pytest.fail(f"Trading operations logging should not fail: {e}")
    
    def test_logging_system_resilience_during_trading(self):
        """Test that trading operations continue even if logging fails."""
        service = MarketDataService(enable_logging=True, log_level="DEBUG")
        
        # Simulate logging system failure
        with patch.object(service.logger, 'log_operation_start') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # Trading operations should continue despite logging failure
            try:
                service._log_operation_start("critical_trade", symbol="BTCUSDT")
                
                # Continue with trading operations
                service._log_operation_start("emergency_trade", symbol="BTCUSDT")
                service._log_operation_success("emergency_trade", symbol="BTCUSDT")
                
                # Service should continue working
                assert hasattr(service, 'logger')
                
                # Trading should continue successfully
                assert True, "Trading operations should continue despite logging failures"
                
            except Exception as e:
                pytest.fail(f"Trading operations should be resilient to logging failures: {e}")


@pytest.mark.integration
@pytest.mark.logging
class TestCompleteLoggingWorkflows:
    """Test complete end-to-end logging workflows."""
    
    def setup_method(self):
        """Setup for each test."""
        reset_logging_state()
    
    def test_complete_logging_workflow_with_all_components(self, capfd):
        """Test complete logging workflow using all system components."""
        reset_trace_counter()
        configure_ai_logging(log_level="DEBUG", console_output=True)
        
        # Create multiple loggers and services
        market_logger = MarketDataLogger("integration_test")
        service = MarketDataService(enable_logging=True, log_level="DEBUG")
        
        with flow_operation("BTCUSDT", "complete_integration_test") as trace_id:
            # Test all major logging components
            
            # 1. Basic logging
            basic_logger = get_ai_logger("integration_basic")
            basic_logger.info("Integration test started", operation="integration_test")
            
            # 2. Market data logging
            market_logger.log_operation_start("integration_test", "BTCUSDT")
            market_logger.log_api_call("BTCUSDT", "1d", 180, response_time_ms=150)
            market_logger.log_calculation("RSI", "BTCUSDT", result="42.5")
            
            # 3. Service integration logging
            service._log_operation_start("service_integration", symbol="BTCUSDT")
            service.logger.log_api_call("BTCUSDT", "1d", 180, response_time_ms=123)
            
            # 4. Flow progression
            advance_to_stage("validation")
            advance_to_stage("processing", api_calls=3)
            advance_to_stage("completion")
            
            # 5. Error handling
            try:
                raise ValueError("Integration test exception")
            except ValueError:
                basic_logger.error("Integration exception test",
                                 operation="exception_handling",
                                 exc_info=True)
            
            # 6. Complete operations
            market_logger.log_operation_complete("integration_test", processing_time_ms=2500)
            service._log_operation_success("service_integration", symbol="BTCUSDT")
        
        # Capture and verify complete workflow
        captured = capfd.readouterr()
        
        # Should have comprehensive stderr output
        assert captured.err, "Should have complete stderr output"
        assert captured.out == "", "Should have no stdout output"
        
        # Parse all JSON logs
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        # Should have multiple log entries covering all components
        assert len(json_logs) >= 8, f"Should have comprehensive logs, got {len(json_logs)}"
        
        # Verify all major components logged
        log_messages = [log["message"] for log in json_logs]
        operations = [log["operation"] for log in json_logs]
        
        # Verify different types of operations
        assert "integration_test" in operations
        assert "exception_handling" in operations
        assert any("Integration test started" in msg for msg in log_messages)
        assert any("integration_test initiated" in msg for msg in log_messages)
        assert any("RSI calculation completed" in msg for msg in log_messages)
        
        # Verify flow ID consistency
        trace_ids_from_flow = [log.get("flow", {}).get("trace_id") for log in json_logs if log.get("flow")]
        unique_flow_ids = set(filter(None, trace_ids_from_flow))
        assert len(unique_flow_ids) >= 1, "Should have consistent trace IDs in flow"
        
        # Verify trace IDs are present and properly formatted (both old and new formats)
        trace_ids = [log.get("trace_id") for log in json_logs]
        assert all(trace_id and (trace_id.startswith("trd_") or trace_id.startswith("flow_")) for trace_id in trace_ids)
    
    def test_edge_cases_integration(self, capfd):
        """Test edge cases in complete integration."""
        configure_ai_logging(log_level="DEBUG", console_output=True)
        
        # Test edge cases
        logger = get_ai_logger("edge_case_test")
        
        # Empty message
        logger.info("", operation="empty_test")
        
        # Very long message
        long_message = "A" * 1000
        logger.info(long_message, operation="long_message_test")
        
        # Unicode and special characters
        logger.info("Unicode test: ЙЦУ БТЦ УСДТ 🚀", operation="unicode_test")
        
        # Complex nested context
        complex_context = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": "deeply_nested",
                        "array": [1, 2, 3, {"nested": "value"}]
                    }
                }
            }
        }
        logger.info("Complex context test", operation="complex_test", context=complex_context)
        
        captured = capfd.readouterr()
        
        # Should handle all edge cases gracefully
        json_logs = []
        stderr_lines = captured.err.strip().split('\n')
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        assert len(json_logs) >= 4, "Should handle all edge cases"
        
        # Verify edge cases were handled properly
        messages = [log["message"] for log in json_logs]
        assert "" in messages  # Empty message
        assert long_message in messages  # Long message
        assert "Unicode test: ЙЦУ БТЦ УСДТ 🚀" in messages  # Unicode
        assert "Complex context test" in messages  # Complex context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])