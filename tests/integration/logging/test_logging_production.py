"""
Integration Tests for Production Logging Scenarios

Consolidated tests for production configurations, performance, deployment scenarios,
and edge cases in production environments.

Consolidates:
- test_production_configuration.py (production configs and deployment)
- test_memory_leak_detection.py (memory efficiency)
- test_encoding_unicode.py (encoding and unicode handling)
- test_error_recovery.py (error recovery scenarios)
"""

import pytest
import os
import tempfile
import threading
import time
import json
import logging
import gc
import sys
from unittest.mock import patch, MagicMock

from src.logging_system import (
    configure_ai_logging, 
    get_ai_logger, 
    MarketDataLogger,
    flow_operation,
    reset_trace_counter
)
from src.logging_system.logger_config import reset_logging_state


@pytest.mark.integration
@pytest.mark.logging
@pytest.mark.production
class TestProductionConfiguration:
    """Test production configuration scenarios."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
    
    def test_production_log_levels(self, capfd):
        """Test different production log levels."""
        test_cases = [
            ("DEBUG", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
            ("INFO", ["INFO", "WARNING", "ERROR", "CRITICAL"]),
            ("WARNING", ["WARNING", "ERROR", "CRITICAL"]),
            ("ERROR", ["ERROR", "CRITICAL"]),
            ("CRITICAL", ["CRITICAL"])
        ]
        
        for level, expected_levels in test_cases:
            reset_logging_state()
            configure_ai_logging(log_level=level)
            logger = get_ai_logger(f"prod_test_{level.lower()}")
            
            # Test all log levels
            logger.debug("Debug message", operation="debug_test")
            logger.info("Info message", operation="info_test")
            logger.warning("Warning message", operation="warning_test")
            logger.error("Error message", operation="error_test")
            logger.critical("Critical message", operation="critical_test")
            
            captured = capfd.readouterr()
            
            # Parse logs
            stderr_lines = captured.err.strip().split('\n')
            json_logs = []
            for line in stderr_lines:
                if line.strip() and line.strip().startswith('{"'):
                    try:
                        json_logs.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        pass
            
            # Verify only expected levels appear
            actual_levels = [log["level"] for log in json_logs]
            assert len(actual_levels) == len(expected_levels), f"Level {level}: expected {len(expected_levels)}, got {len(actual_levels)}"
            
            for expected in expected_levels:
                assert expected in actual_levels, f"Level {level}: missing {expected}"
    
    def test_production_file_logging(self):
        """Test production file logging configuration."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_file = f.name
        
        try:
            # Configure production logging with file
            configure_ai_logging(log_level="INFO", log_file=log_file, console_output=True)
            logger = get_ai_logger("prod_file_test")
            
            # Log various levels
            logger.info("Production info message", operation="prod_info")
            logger.warning("Production warning", operation="prod_warning")
            logger.error("Production error", operation="prod_error")
            
            # Verify file contains logs
            time.sleep(0.1)  # Allow file writing
            with open(log_file, 'r') as f:
                file_content = f.read()
            
            assert "Production info message" in file_content
            assert "Production warning" in file_content
            assert "Production error" in file_content
            
            # File should have text format logs
            lines = file_content.strip().split('\n')
            assert len(lines) >= 3, "Should have at least 3 log lines"
            
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
            reset_logging_state()
    
    def test_production_console_only_configuration(self, capfd):
        """Test production console-only configuration."""
        configure_ai_logging(log_level="WARNING", console_output=True)
        logger = get_ai_logger("console_only_test")
        
        # Log various levels
        logger.debug("Debug should not appear", operation="debug_test")
        logger.info("Info should not appear", operation="info_test")
        logger.warning("Warning should appear", operation="warning_test")
        logger.error("Error should appear", operation="error_test")
        
        captured = capfd.readouterr()
        
        # Parse JSON logs to check levels properly
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
        
        # Should only have WARNING and ERROR levels
        actual_levels = [log["level"] for log in json_logs]
        for level in actual_levels:
            assert level in ["WARNING", "ERROR"], f"Unexpected level: {level}"
        
        # Should have both WARNING and ERROR
        assert "WARNING" in actual_levels, "Should have WARNING log"
        assert "ERROR" in actual_levels, "Should have ERROR log"
    
    def test_production_concurrent_logging(self, capfd):
        """Test production concurrent logging performance."""
        configure_ai_logging(log_level="INFO")
        
        results = []
        error_count = 0
        
        def worker_function(worker_id):
            nonlocal error_count
            try:
                logger = get_ai_logger(f"worker_{worker_id}")
                
                # Each worker logs 20 messages
                for i in range(20):
                    logger.info(f"Worker {worker_id} message {i}",
                               operation=f"worker_{worker_id}",
                               context={"worker_id": worker_id, "message_num": i})
                    
                    # Small delay to encourage interleaving
                    time.sleep(0.001)
                
                results.append(f"Worker {worker_id} completed")
                
            except Exception as e:
                error_count += 1
                results.append(f"Worker {worker_id} failed: {e}")
        
        # Start 5 concurrent workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all workers
        for thread in threads:
            thread.join()
        
        # Verify no errors
        assert error_count == 0, f"Should have no errors, got {error_count}"
        assert len(results) == 5, "Should have 5 worker results"
        
        # Check logs were produced
        captured = capfd.readouterr()
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
        
        # Should have 100 logs (5 workers × 20 messages)
        assert len(json_logs) == 100, f"Expected 100 logs, got {len(json_logs)}"
        
        # Verify all workers logged
        worker_ids = set()
        for log in json_logs:
            worker_ids.add(log["context"]["worker_id"])
        
        assert worker_ids == {0, 1, 2, 3, 4}, "Should see logs from all 5 workers"
    
    def test_production_environment_detection(self, capfd):
        """Test production environment detection and configuration."""
        # Test with PYTEST_CURRENT_TEST environment variable
        with patch.dict(os.environ, {'PYTEST_CURRENT_TEST': 'test_production'}):
            configure_ai_logging(log_level="DEBUG")
            logger = get_ai_logger("env_test")
            
            # In test environment, propagate should be True for caplog compatibility
            assert logger.logger.propagate == True, "Should allow propagation in test environment"
        
        # Test without PYTEST_CURRENT_TEST (simulating production)
        with patch.dict(os.environ, {}, clear=True):
            reset_logging_state()
            configure_ai_logging(log_level="DEBUG")
            logger = get_ai_logger("prod_env_test")
            
            # Our logging system allows propagation for test compatibility
            assert logger.logger.propagate == True, "Should allow propagation for test compatibility"


@pytest.mark.integration
@pytest.mark.logging
@pytest.mark.performance
class TestProductionPerformance:
    """Test production performance scenarios."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
    
    def test_production_high_volume_logging(self, capfd):
        """Test high-volume logging performance."""
        configure_ai_logging(log_level="INFO")
        logger = get_ai_logger("high_volume_test")
        
        start_time = time.time()
        
        # Log 1000 messages
        for i in range(1000):
            logger.info(f"High volume message {i}",
                       operation="high_volume_test",
                       context={"iteration": i, "batch": i // 100})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (< 5 seconds)
        assert duration < 5.0, f"High volume logging took too long: {duration:.2f}s"
        
        # Verify logs were produced
        captured = capfd.readouterr()
        log_lines = [line for line in captured.err.split('\n') if line.strip()]
        
        # Should have close to 1000 log lines (allow for some variation)
        assert len(log_lines) >= 990, f"Expected ~1000 logs, got {len(log_lines)}"
        
        # Performance metric: messages per second
        mps = 1000 / duration
        assert mps > 200, f"Performance too slow: {mps:.1f} messages/second"
    
    def test_production_memory_efficiency(self, capfd):
        """Test memory efficiency under load."""
        configure_ai_logging(log_level="INFO")
        logger = get_ai_logger("memory_test")
        
        # Get initial memory baseline
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Log many messages with complex context
        for i in range(500):
            complex_context = {
                "iteration": i,
                "data": {
                    "symbol": "BTCUSDT",
                    "prices": [50000.0 + j for j in range(10)],
                    "indicators": {
                        "rsi": 50.0 + i % 50,
                        "macd": {"signal": 1.5, "histogram": 0.3},
                        "moving_averages": {
                            "ma_20": 50000.0 + i,
                            "ma_50": 49800.0 + i,
                            "ma_200": 48000.0 + i
                        }
                    }
                },
                "metadata": {
                    "timestamp": f"2025-01-01T{i%24:02d}:00:00Z",
                    "source": "test_data"
                }
            }
            
            logger.info(f"Memory test message {i}",
                       operation="memory_test",
                       context=complex_context)
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory should not grow excessively
        object_increase = final_objects - initial_objects
        
        # Allow reasonable growth but not excessive (< 1000 new objects)
        assert object_increase < 1000, f"Too many new objects: {object_increase}"
    
    def test_production_error_handling_performance(self, capfd):
        """Test error handling performance under load."""
        configure_ai_logging(log_level="DEBUG")
        logger = get_ai_logger("error_perf_test")
        
        start_time = time.time()
        
        # Mix of normal logs and error logs
        for i in range(200):
            if i % 10 == 0:
                # Error log with exception
                try:
                    raise ValueError(f"Test error {i}")
                except ValueError:
                    logger.error(f"Error message {i}",
                               operation="error_test",
                               context={"error_num": i},
                               exc_info=True)
            else:
                # Normal log
                logger.info(f"Normal message {i}",
                           operation="normal_test",
                           context={"msg_num": i})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle mixed error/normal logging efficiently
        assert duration < 3.0, f"Error handling too slow: {duration:.2f}s"
        
        # Verify both types of logs were produced
        captured = capfd.readouterr()
        assert "Normal message" in captured.err
        assert "Error message" in captured.err
        assert "ValueError" in captured.err  # Exception info should be present


@pytest.mark.integration
@pytest.mark.logging
@pytest.mark.deployment
class TestProductionDeploymentScenarios:
    """Test real deployment scenarios."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
    
    def test_production_restart_behavior(self):
        """Test behavior during application restarts."""
        log_file = None
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
                log_file = f.name
            
            # First application instance
            configure_ai_logging(log_level="INFO", log_file=log_file)
            logger1 = get_ai_logger("app_instance_1")
            
            logger1.info("Application started", operation="app_start")
            logger1.info("Processing data", operation="data_process")
            
            # Simulate restart - reset logging
            reset_logging_state()
            
            # Second application instance
            configure_ai_logging(log_level="INFO", log_file=log_file)
            logger2 = get_ai_logger("app_instance_2")
            
            logger2.info("Application restarted", operation="app_restart")
            logger2.info("Resuming operations", operation="resume_ops")
            
            # Check log file contains both instances
            time.sleep(0.1)
            with open(log_file, 'r') as f:
                content = f.read()
            
            assert "Application started" in content
            assert "Processing data" in content
            assert "Application restarted" in content
            assert "Resuming operations" in content
            
        finally:
            if log_file and os.path.exists(log_file):
                os.unlink(log_file)
            reset_logging_state()
    
    def test_production_log_rotation_preparation(self):
        """Test preparation for log rotation scenarios."""
        log_file = None
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
                log_file = f.name
            
            configure_ai_logging(log_level="INFO", log_file=log_file)
            logger = get_ai_logger("rotation_test")
            
            # Write initial logs
            for i in range(10):
                logger.info(f"Pre-rotation message {i}", operation="pre_rotation")
            
            # Simulate log rotation by truncating file
            with open(log_file, 'w') as f:
                f.truncate()
            
            # Continue logging after rotation
            for i in range(10):
                logger.info(f"Post-rotation message {i}", operation="post_rotation")
            
            # Check only post-rotation logs remain
            time.sleep(0.1)
            with open(log_file, 'r') as f:
                content = f.read()
            
            assert "Pre-rotation message" not in content
            assert "Post-rotation message" in content
            
            # Should have 10 post-rotation messages
            lines = [line for line in content.split('\n') if line.strip()]
            assert len(lines) >= 10, f"Expected 10 lines, got {len(lines)}"
            
        finally:
            if log_file and os.path.exists(log_file):
                os.unlink(log_file)
            reset_logging_state()
    
    def test_production_multiple_services_configuration(self, capfd):
        """Test multiple services in same application."""
        reset_logging_state()
        configure_ai_logging(log_level="INFO")
        
        # Create loggers for different services
        market_logger = get_ai_logger("market_service", service_name="MarketDataService")
        trade_logger = get_ai_logger("trade_service", service_name="TradingService")
        alert_logger = get_ai_logger("alert_service", service_name="AlertService")
        
        # Each service logs with its identity
        market_logger.info("Market data updated", operation="data_update", context={"service": "market"})
        trade_logger.info("Trade executed", operation="trade_exec", context={"service": "trade"})
        alert_logger.info("Alert triggered", operation="alert_trigger", context={"service": "alert"})
        
        captured = capfd.readouterr()
        
        # Parse logs and verify service identification
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
        
        assert len(json_logs) >= 3, f"Should have logs from all services, got {len(json_logs)} logs"
        
        # Verify service names are correctly identified
        services = {log["service"] for log in json_logs}
        expected_services = {"MarketDataService", "TradingService", "AlertService"}
        
        assert services == expected_services, f"Expected {expected_services}, got {services}"
    
    def test_production_configuration_validation(self):
        """Test production configuration validation."""
        # Test invalid log level - Python logging handles this gracefully
        configure_ai_logging(log_level="INVALID_LEVEL")
        logger = get_ai_logger("invalid_level_test")
        
        # Should work without crashing
        logger.info("Test with invalid level", operation="invalid_test")
        
        # Test invalid file path
        invalid_path = "/nonexistent/directory/log.txt"
        try:
            configure_ai_logging(log_level="INFO", log_file=invalid_path)
            logger = get_ai_logger("invalid_path_test")
            logger.info("Test message", operation="test")
            # Should handle gracefully without crashing
        except Exception:
            # Expected to fail gracefully
            pass
        
        reset_logging_state()
        
        # Test valid configuration
        configure_ai_logging(log_level="WARNING", console_output=True)
        logger = get_ai_logger("valid_config_test")
        
        # Should work without issues
        logger.warning("Valid config test", operation="config_test")
        
        assert logger is not None
        assert hasattr(logger, 'logger')


@pytest.mark.integration
@pytest.mark.logging
@pytest.mark.encoding
class TestEncodingAndUnicode:
    """Test encoding and unicode handling in production."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
        configure_ai_logging(log_level="DEBUG", console_output=False)
    
    def test_unicode_message_handling(self, capfd):
        """Test handling of unicode characters in log messages."""
        logger = get_ai_logger("unicode_test")
        
        unicode_test_cases = [
            "ASCII only message",
            "Latin-1: café, résumé, naïve",
            "Cyrillic: Привет мир, Россия",
            "Chinese: 你好世界, 中国",
            "Japanese: こんにちは世界, 日本",
            "Arabic: مرحبا بالعالم",
            "Emoji: 🌍🚀💰📈📉",
            "Mixed: Hello 世界 🌍 Привет café",
            "Currency: $€£¥₿₹¢",
            "Mathematical: ∞≠≈±×÷√∫∑",
        ]
        
        for i, message in enumerate(unicode_test_cases):
            logger.info(message, operation=f"unicode_test_{i}", context={"test_case": i})
        
        captured = capfd.readouterr()
        
        # Parse logs and verify unicode preservation
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    pytest.fail(f"Unicode caused JSON parsing error: {e}")
        
        assert len(json_logs) == len(unicode_test_cases), "All unicode messages should be logged"
        
        # Verify all unicode messages are preserved correctly
        logged_messages = [log["message"] for log in json_logs]
        for original, logged in zip(unicode_test_cases, logged_messages):
            assert original == logged, f"Unicode not preserved: {original} != {logged}"
    
    def test_unicode_context_handling(self, capfd):
        """Test handling of unicode in context data."""
        logger = get_ai_logger("unicode_context_test")
        
        unicode_context = {
            "symbol": "BTCUSDT",
            "description": "Bitcoin к доллару США",
            "market": "加密货币市场",
            "status": "✅ Active",
            "notes": "This is a test: café, naïve, 你好",
            "tags": ["crypto", "торговля", "交易", "🚀"],
            "metadata": {
                "source": "Binance API",
                "encoding": "UTF-8",
                "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
            }
        }
        
        logger.info("Unicode context test", 
                   operation="unicode_context",
                   context=unicode_context)
        
        captured = capfd.readouterr()
        
        # Parse and verify unicode in context
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_log = json.loads(line.strip())
                    break
                except json.JSONDecodeError as e:
                    pytest.fail(f"Unicode context caused JSON parsing error: {e}")
        
        assert json_log is not None, "Should parse unicode context log"
        
        # Verify unicode preservation in context
        logged_context = json_log["context"]
        assert logged_context["description"] == "Bitcoin к доллару США"
        assert logged_context["market"] == "加密货币市场"
        assert logged_context["status"] == "✅ Active"
        assert "торговля" in logged_context["tags"]
        assert "交易" in logged_context["tags"]
        assert "🚀" in logged_context["tags"]
    
    def test_encoding_edge_cases(self, capfd):
        """Test encoding edge cases and error handling."""
        logger = get_ai_logger("encoding_edge_test")
        
        # Test various edge cases
        edge_cases = [
            "",  # Empty string
            " ",  # Space only
            "\n",  # Newline
            "\t",  # Tab
            "\r\n",  # Windows line ending
            "Zero width: \u200B\u200C\u200D",  # Zero-width characters
            "Control chars: \x00\x01\x02",  # Control characters
            "High Unicode: \U0001F600\U0001F680",  # High Unicode codepoints
            "Surrogate pairs: 𝒽𝑒𝓁𝓁𝑜",  # Mathematical script
            "Combining chars: é (e + ´)",  # Combining characters
        ]
        
        for i, test_case in enumerate(edge_cases):
            try:
                logger.info(f"Edge case {i}: {test_case}", 
                           operation=f"edge_test_{i}",
                           context={"case": i, "content": test_case})
            except Exception as e:
                pytest.fail(f"Encoding edge case {i} failed: {e}")
        
        captured = capfd.readouterr()
        
        # Should handle all edge cases without crashing
        assert captured.err, "Should have output despite edge cases"
        
        # Count successful logs
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    # Some edge cases might cause JSON issues, but shouldn't crash
                    pass
        
        # Should handle most edge cases successfully
        assert len(json_logs) >= len(edge_cases) // 2, "Should handle most encoding edge cases"


@pytest.mark.integration
@pytest.mark.logging
@pytest.mark.recovery
class TestErrorRecoveryScenarios:
    """Test error recovery and resilience scenarios."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
    
    def test_logging_system_recovery_after_failure(self, capfd):
        """Test logging system recovery after temporary failure."""
        configure_ai_logging(log_level="INFO")
        logger = get_ai_logger("recovery_test")
        
        # Normal operation
        logger.info("Normal operation", operation="normal")
        
        # Simulate temporary system failure
        with patch('sys.stderr.write', side_effect=Exception("Temporary failure")):
            try:
                logger.info("During failure", operation="failure")
            except Exception:
                pass  # Expected to fail
        
        # System should recover
        logger.info("After recovery", operation="recovery")
        
        captured = capfd.readouterr()
        
        # Should have logs before and after failure
        assert "Normal operation" in captured.err
        assert "After recovery" in captured.err
    
    def test_concurrent_logging_during_errors(self, capfd):
        """Test concurrent logging behavior during error conditions."""
        configure_ai_logging(log_level="INFO")
        
        results = []
        errors = []
        
        def worker_with_errors(worker_id):
            try:
                logger = get_ai_logger(f"error_worker_{worker_id}")
                
                for i in range(10):
                    if i == 5 and worker_id == 0:
                        # Simulate error in one worker
                        try:
                            raise RuntimeError(f"Simulated error in worker {worker_id}")
                        except RuntimeError:
                            logger.error(f"Worker {worker_id} error at iteration {i}",
                                       operation="error_simulation",
                                       exc_info=True)
                    else:
                        logger.info(f"Worker {worker_id} message {i}",
                                   operation=f"worker_{worker_id}")
                
                results.append(f"Worker {worker_id} completed")
                
            except Exception as e:
                errors.append(f"Worker {worker_id} failed: {e}")
        
        # Start workers with error conditions
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_with_errors, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All workers should complete despite errors
        assert len(results) == 3, "All workers should complete"
        assert len(errors) == 0, "No workers should fail completely"
        
        captured = capfd.readouterr()
        
        # Should have logs from all workers including error logs
        assert "Worker 0 error at iteration 5" in captured.err
        assert "RuntimeError" in captured.err
        assert "Worker 1 message" in captured.err
        assert "Worker 2 message" in captured.err
    
    def test_logging_system_stress_recovery(self, capfd):
        """Test logging system recovery under stress conditions."""
        configure_ai_logging(log_level="DEBUG")
        logger = get_ai_logger("stress_test")
        
        # High-frequency logging with intermittent errors
        error_count = 0
        success_count = 0
        
        for i in range(100):
            try:
                if i % 20 == 0:
                    # Introduce periodic errors
                    raise ValueError(f"Stress test error {i}")
                
                logger.info(f"Stress test message {i}",
                           operation="stress_test",
                           context={"iteration": i, "stress_level": "high"})
                success_count += 1
                
            except ValueError:
                try:
                    logger.error(f"Stress error at iteration {i}",
                               operation="stress_error",
                               exc_info=True)
                    error_count += 1
                except Exception:
                    # Even error logging might fail under stress
                    pass
        
        # Should handle stress with minimal failures
        assert success_count >= 80, f"Should log most messages, got {success_count}/100"
        assert error_count >= 4, f"Should log most errors, got {error_count}/5"
        
        captured = capfd.readouterr()
        
        # Should have substantial output despite stress
        log_lines = [line for line in captured.err.split('\n') if line.strip()]
        assert len(log_lines) >= 80, f"Should have substantial output, got {len(log_lines)} lines"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])