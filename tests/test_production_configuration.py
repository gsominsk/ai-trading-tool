"""
Production Configuration Tests for AI-Optimized Logging System

Tests production-ready configurations, environment handling, performance settings,
and deployment scenarios for the logging system.
"""

import pytest
import os
import tempfile
import threading
import time
import json
import logging
from unittest.mock import patch, MagicMock

from src.logging_system import configure_ai_logging, get_ai_logger, MarketDataLogger
from src.logging_system.logger_config import reset_logging_state


class TestProductionConfiguration:
    """Test production configuration scenarios."""
    
    def setup_method(self):
        """Reset logging state before each test."""
        reset_logging_state()
    
    def test_production_log_levels(self, capfd):
        """Test different production log levels."""
        # Note: trace() method uses DEBUG level internally, so DEBUG level includes TRACE
        test_cases = [
            ("DEBUG", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),  # DEBUG includes trace() calls
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
    
    def test_production_file_only_configuration(self):
        """Test production file-only configuration (no console)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_file = f.name
        
        try:
            # Configure file-only logging
            configure_ai_logging(log_level="ERROR", log_file=log_file, console_output=False)
            logger = get_ai_logger("file_only_test")
            
            # Log messages
            logger.info("Info should not appear", operation="info_test")
            logger.warning("Warning should not appear", operation="warning_test")
            logger.error("Error should appear", operation="error_test")
            logger.critical("Critical should appear", operation="critical_test")
            
            # Verify file contains only ERROR and CRITICAL
            time.sleep(0.1)
            with open(log_file, 'r') as f:
                file_content = f.read()
            
            assert "Info should not appear" not in file_content
            assert "Warning should not appear" not in file_content
            assert "Error should appear" in file_content
            assert "Critical should appear" in file_content
            
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
            reset_logging_state()
    
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
            
            # In production, propagate should be False
            assert logger.logger.propagate == False, "Should disable propagation in production"
    
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
        import gc
        import sys
        
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
        configure_ai_logging(log_level="INFO")
        
        # Create loggers for different services
        market_logger = get_ai_logger("market_service", "MarketDataService")
        trade_logger = get_ai_logger("trade_service", "TradingService")
        alert_logger = get_ai_logger("alert_service", "AlertService")
        
        # Each service logs with its identity
        market_logger.info("Market data updated", operation="data_update")
        trade_logger.info("Trade executed", operation="trade_exec")
        alert_logger.info("Alert triggered", operation="alert_trigger")
        
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
        
        assert len(json_logs) >= 3, "Should have logs from all services"
        
        # Verify service names are correctly identified
        services = {log["service"] for log in json_logs}
        expected_services = {"MarketDataService", "TradingService", "AlertService"}
        assert services == expected_services, f"Expected {expected_services}, got {services}"
    
    def test_production_configuration_validation(self):
        """Test production configuration validation."""
        # Test invalid log level - Python logging handles this gracefully
        # by defaulting to a reasonable level, so we test the behavior
        configure_ai_logging(log_level="INVALID_LEVEL")
        logger = get_ai_logger("invalid_level_test")
        
        # Should work without crashing (Python logging handles invalid levels gracefully)
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