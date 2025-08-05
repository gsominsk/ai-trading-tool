"""
Critical Fixes Tests for AI-Optimized Logging System
Tests for stderr output, thread safety, TRACE level, and handler duplication fixes
"""

import pytest
import json
import io
import sys
import threading
import time
import logging
from unittest.mock import patch, MagicMock
from src.logging_system import (
    configure_ai_logging,
    get_ai_logger,
    MarketDataLogger,
    flow_operation,
    get_trace_id,
    reset_trace_counter
)


class TestStderrOutput:
    """Test that JSON logs go to stderr for AI searchability."""
    
    def test_stderr_output_configuration(self, capfd):
        """Test that logs are directed to stderr."""
        configure_ai_logging(log_level="DEBUG", console_output=True)
        logger = get_ai_logger("stderr_test")
        
        # Log a message
        logger.info("Test stderr output", 
                   operation="test_stderr",
                   context={"test": "stderr_validation"})
        
        # Capture stdout and stderr
        captured = capfd.readouterr()
        
        # JSON logs should be in stderr, not stdout
        assert captured.out == "", "No output should go to stdout"
        assert captured.err != "", "JSON logs should go to stderr"
        
        # Verify stderr contains JSON (may have multiple lines in test mode)
        stderr_lines = captured.err.strip().split('\n')
        json_found = False
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json.loads(line.strip())
                    json_found = True
                    break
                except json.JSONDecodeError:
                    continue
        
        assert json_found, "stderr should contain at least one valid JSON log entry"
    
    def test_ai_searchable_json_structure(self, capfd):
        """Test that JSON structure is AI-searchable."""
        configure_ai_logging(log_level="DEBUG", console_output=True)
        logger = get_ai_logger("ai_search_test")
        
        logger.info("AI searchable test",
                   operation="ai_search",
                   context={"symbol": "BTCUSDT", "operation_type": "market_data"},
                   tags=["api_call", "market_data", "btc"])
        
        captured = capfd.readouterr()
        
        # Find JSON line in stderr output
        stderr_lines = captured.err.strip().split('\n')
        log_data = None
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    log_data = json.loads(line.strip())
                    break
                except json.JSONDecodeError:
                    continue
        
        assert log_data is not None, "Should find valid JSON log in stderr"
        
        # Verify AI-searchable fields
        assert "timestamp" in log_data
        assert "level" in log_data
        assert "service" in log_data
        assert "operation" in log_data
        assert "context" in log_data
        assert "tags" in log_data
        assert "trace_id" in log_data
        
        # Verify semantic tags for AI
        assert "api_call" in log_data["tags"]
        assert "market_data" in log_data["tags"]


class TestThreadSafety:
    """Test thread safety of logger configuration."""
    
    def test_concurrent_logger_creation(self):
        """Test that concurrent logger creation is thread-safe."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        
        loggers = {}
        errors = []
        
        def create_logger(worker_id):
            try:
                logger_name = f"worker_{worker_id}"
                logger = get_ai_logger(logger_name)
                loggers[worker_id] = logger
                
                # Log some messages to ensure logger works
                for i in range(5):
                    logger.info(f"Message {i} from worker {worker_id}")
                    
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_logger, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(loggers) == 10, "All loggers should be created"
        
        # Verify all loggers are unique instances for same name
        logger1 = get_ai_logger("test_logger")
        logger2 = get_ai_logger("test_logger")
        assert logger1 is logger2, "Same name should return same logger instance"
    
    def test_concurrent_logging_operations(self):
        """Test concurrent logging operations don't interfere."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        
        messages_logged = []
        errors = []
        
        def log_worker(worker_id):
            try:
                logger = get_ai_logger(f"concurrent_worker_{worker_id}")
                for i in range(20):
                    trace_id = get_trace_id()
                    logger.info(f"Worker {worker_id} message {i}",
                               operation="concurrent_test",
                               trace_id=trace_id)
                    messages_logged.append((worker_id, i, trace_id))
                    
            except Exception as e:
                errors.append(e)
        
        # Start multiple workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors and all messages logged
        assert len(errors) == 0, f"Concurrent logging errors: {errors}"
        assert len(messages_logged) == 100, "All 100 messages should be logged"
        
        # Verify trace IDs are unique
        trace_ids = [msg[2] for msg in messages_logged]
        assert len(trace_ids) == len(set(trace_ids)), "All trace IDs should be unique"


class TestTraceLevel:
    """Test TRACE level implementation fix."""
    
    def test_trace_level_no_crash(self):
        """Test that trace() method doesn't crash."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        logger = get_ai_logger("trace_test")
        
        # This should not crash
        try:
            logger.trace("Trace level test message",
                        operation="trace_test",
                        context={"test": "trace_level"},
                        tags=["trace", "raw_data"])
            assert True, "Trace method should not crash"
        except Exception as e:
            pytest.fail(f"Trace method crashed: {e}")
    
    def test_trace_level_behavior(self):
        """Test that trace level behaves correctly."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        logger = get_ai_logger("trace_behavior_test")
        
        # Test that trace method works without crashing and uses DEBUG level
        try:
            logger.trace("Raw API data trace",
                        operation="api_data_capture",
                        context={"raw_data": "sample_data"},
                        tags=["raw_data", "trace_level"])
            
            # Verify trace method completed successfully
            assert True, "Trace method completed without errors"
            
            # Verify underlying logger level compatibility
            assert logger.logger.getEffectiveLevel() <= logging.DEBUG, "Logger should handle DEBUG level"
            
        except Exception as e:
            pytest.fail(f"Trace method failed: {e}")


class TestHandlerDuplication:
    """Test handler duplication prevention."""
    
    def test_no_handler_duplication(self):
        """Test that multiple logger creations don't duplicate handlers."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        
        # Create same logger multiple times
        logger1 = get_ai_logger("duplication_test")
        logger2 = get_ai_logger("duplication_test")
        logger3 = get_ai_logger("duplication_test")
        
        # Should be same instance
        assert logger1 is logger2 is logger3
        
        # Check handler count on underlying logger
        handler_count = len(logger1.logger.handlers)
        
        # Create more instances
        for i in range(5):
            get_ai_logger("duplication_test")
        
        # Handler count should not increase
        new_handler_count = len(logger1.logger.handlers)
        assert new_handler_count == handler_count, "Handler count should not increase"
    
    def test_different_loggers_have_separate_handlers(self):
        """Test that different logger names have separate configurations."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        
        logger_a = get_ai_logger("logger_a")
        logger_b = get_ai_logger("logger_b")
        
        # Should be different instances
        assert logger_a is not logger_b
        
        # Should have separate underlying loggers
        assert logger_a.logger is not logger_b.logger


class TestCriticalFixesIntegration:
    """Integration tests for all critical fixes together."""
    
    def test_complete_logging_workflow_after_fixes(self, capfd):
        """Test complete logging workflow with all fixes applied."""
        reset_trace_counter()
        configure_ai_logging(log_level="DEBUG", console_output=True)
        
        # Create logger and use MarketDataLogger
        market_logger = MarketDataLogger("integration_test_fixed")
        
        with flow_operation("BTCUSDT", "complete_workflow_test") as flow_id:
            # Test all logging methods
            market_logger.log_operation_start("complete_workflow_test", "BTCUSDT")
            market_logger.log_api_call("BTCUSDT", "1d", 180, response_time_ms=150)
            market_logger.log_calculation("RSI", "BTCUSDT", result="42.5")
            
            # Test trace level (should not crash)
            logger = get_ai_logger("trace_integration_test")
            logger.trace("Raw data trace test", operation="trace_integration")
            
            market_logger.log_operation_complete("complete_workflow_test", 
                                                processing_time_ms=2500)
        
        # Capture and verify stderr output
        captured = capfd.readouterr()
        
        # Should have output in stderr
        assert captured.err != "", "Should have JSON logs in stderr"
        assert captured.out == "", "Should have no stdout output"
        
        # Find JSON lines in stderr output (filter out non-JSON lines)
        lines = captured.err.strip().split('\n')
        json_logs = []
        for line in lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        # Should have multiple log entries
        assert len(json_logs) >= 4, "Should have at least 4 log entries"
        
        # Verify all have required AI-searchable fields
        for log_entry in json_logs:
            assert "timestamp" in log_entry
            assert "trace_id" in log_entry
            assert "service" in log_entry
            assert "operation" in log_entry
    
    def test_performance_after_fixes(self):
        """Test that fixes don't degrade performance."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        
        start_time = time.time()
        
        # High-volume logging test
        logger = get_ai_logger("performance_test_fixed")
        for i in range(1000):
            logger.info(f"Performance test {i}",
                       operation="performance_validation",
                       context={"iteration": i})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should still be fast (less than 2 seconds for 1000 messages)
        assert duration < 2.0, f"Performance degraded: {duration:.2f}s for 1000 messages"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])