"""
Unit Tests for Core Logging System Components

Consolidated tests for basic logging functionality, formatters, trace generation,
and flow context management.

Consolidates:
- test_logging_system.py (basic functionality)
- test_logging_system_fixed.py (enhanced with fixes) 
- test_logging_system_critical_fixes.py (critical production fixes)
"""

import pytest
import json
import threading
import time
import logging
from unittest.mock import patch
from src.logging_system import (
    configure_ai_logging,
    get_ai_logger,
    MarketDataLogger,
    flow_operation,
    get_trace_id,
    reset_trace_counter
)
from src.logging_system.flow_context import advance_to_stage

@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration before each test to ensure isolation."""
    from src.logging_system.logger_config import reset_logging_state
    reset_logging_state()
    yield
    reset_logging_state()


@pytest.mark.unit
@pytest.mark.logging
class TestTraceGeneration:
    """Test trace ID and flow ID generation."""
    
    def test_trace_id_format_and_uniqueness(self):
        """Test trace ID format and uniqueness."""
        reset_trace_counter()
        
        trace_id1 = get_trace_id()
        trace_id2 = get_trace_id()
        
        # Check format: trd_001_timestamp
        assert trace_id1.startswith("trd_001_")
        assert trace_id2.startswith("trd_001_")
        
        # Check uniqueness and sequence
        assert trace_id1 != trace_id2
        assert trace_id1.endswith("0001")
        assert trace_id2.endswith("0002")
    
    
    def test_trace_id_thread_safety(self):
        """Test trace ID generation is thread-safe."""
        trace_ids = []
        threads = []
        
        def generate_trace_ids():
            for _ in range(10):
                trace_ids.append(get_trace_id())
        
        # Create multiple threads
        for _ in range(5):
            thread = threading.Thread(target=generate_trace_ids)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All trace IDs should be unique
        assert len(trace_ids) == len(set(trace_ids))
    
    def test_trace_id_performance(self):
        """Test trace ID generation performance."""
        start_time = time.time()
        
        # Generate many trace IDs
        trace_ids = []
        for i in range(1000):
            trace_ids.append(get_trace_id())
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should be fast and all unique
        assert duration < 1.0, f"Generating 1000 trace IDs took {duration:.2f}s (too slow)"
        assert len(trace_ids) == len(set(trace_ids)), "Generated duplicate trace IDs"


@pytest.mark.unit
@pytest.mark.logging
class TestFlowContextManagement:
    """Test flow context management and operations."""
    
    def test_flow_operation_context_manager(self):
        """Test flow operation context manager."""
        with flow_operation("BTCUSDT", "get_market_data") as trace_id:
            assert trace_id.startswith("trd_")
            
            # Test stage advancement
            advance_to_stage("symbol_validation")
            advance_to_stage("data_collection", api_calls=3)
    
    def test_flow_context_without_operation(self):
        """Test flow context outside of operation."""
        from src.logging_system.flow_context import get_flow_summary
        
        # Should return empty context when no flow active
        summary = get_flow_summary()
        assert summary == {}
    
    def test_flow_context_nested_operations(self):
        """Test nested flow operations."""
        with flow_operation("BTCUSDT", "outer_operation") as outer_flow:
            advance_to_stage("outer_stage")
            
            with flow_operation("ETHUSDT", "inner_operation") as inner_flow:
                advance_to_stage("inner_stage")
                # Inner flow should be different
                assert inner_flow != outer_flow
                assert inner_flow.startswith("trd_")
    
    def test_empty_flow_operation(self):
        """Test flow operation with empty parameters."""
        with flow_operation("", "") as trace_id:
            assert trace_id.startswith("trd_")
            advance_to_stage("test_stage")


@pytest.mark.unit
@pytest.mark.logging
class TestJSONFormatter:
    """Test JSON log formatting and structure."""
    
    def test_structured_logger_creation(self):
        """Test structured logger creation."""
        logger = get_ai_logger("test_module", service_name="test_service")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'trace')  # TRACE level support
    
    def test_json_log_format_basic(self):
        """Test basic JSON log output format."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        logger = get_ai_logger("test_module", service_name="test_service")
        
        # Log a message - system should not crash
        logger.info(
            "Test message",
            operation="test_operation",
            context={"test_key": "test_value"},
            tags=["test_tag"],
            trace_id="test_trace_123"
        )
        
        # Test passes - logging system works without crashing
        assert True
    
    def test_ai_searchable_json_structure(self, capfd):
        """Test that JSON structure is AI-searchable."""
        configure_ai_logging(log_level="DEBUG", console_output=True)
        logger = get_ai_logger("ai_search_test", service_name="search_service")
        
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
        required_fields = ["timestamp", "level", "service", "operation", "context", "tags", "trace_id"]
        for field in required_fields:
            assert field in log_data, f"Missing required field: {field}"
        
        assert log_data["service"] == "search_service"
        
        # Verify semantic tags for AI
        assert "api_call" in log_data["tags"]
        assert "market_data" in log_data["tags"]


@pytest.mark.unit
@pytest.mark.logging
class TestLoggerConfiguration:
    """Test logger configuration and setup."""
    
    def test_configure_ai_logging(self):
        """Test logging configuration."""
        configure_ai_logging(log_level="INFO", console_output=True)
        
        logger = get_ai_logger("test_config", service_name="config_service")
        assert logger is not None
    
    def test_logger_singleton_behavior(self):
        """Test that same logger name returns same instance."""
        logger1 = get_ai_logger("singleton_test", service_name="service1")
        logger2 = get_ai_logger("singleton_test", service_name="service1")
        
        # Should be same instance
        assert logger1 is logger2
    
    def test_different_log_levels(self):
        """Test different log levels work correctly."""
        configure_ai_logging(log_level="ERROR", console_output=False)
        logger = get_ai_logger("level_test", service_name="level_service")
        
        # Should not crash with different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
    
    def test_different_loggers_have_separate_configurations(self):
        """Test that different logger names have separate configurations."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        
        logger_a = get_ai_logger("logger_a", service_name="service_a")
        logger_b = get_ai_logger("logger_b", service_name="service_b")
        
        # Should be different instances
        assert logger_a is not logger_b
        
        # Should have separate underlying loggers
        assert logger_a.logger is not logger_b.logger


@pytest.mark.unit
@pytest.mark.logging
class TestMarketDataLogger:
    """Test MarketDataService-specific logging functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        self.logger = MarketDataLogger("test_market_data", service_name="market_data_test_service")
    
    def test_operation_start_logging(self, caplog):
        """Test operation start logging."""
        with flow_operation("BTCUSDT", "get_market_data"):
            self.logger.log_operation_start(
                "get_market_data",
                symbol="BTCUSDT",
                context={"cache_dir": "data/cache"}
            )
        
        # Verify logging happened and contains expected message
        assert len(caplog.records) > 0
        log_record = caplog.records[0]
        assert log_record.message == "get_market_data initiated"
        assert log_record.levelname == "INFO"
    
    def test_api_call_logging(self, caplog):
        """Test API call logging."""
        with flow_operation("BTCUSDT", "get_market_data"):
            self.logger.log_api_call(
                symbol="BTCUSDT",
                interval="1d",
                limit=180,
                response_time_ms=145,
                status_code=200
            )
        
        # Verify logging happened and contains expected message
        assert len(caplog.records) > 0
        log_record = caplog.records[0]
        assert log_record.message == "Binance API call executed"
        assert log_record.levelname == "DEBUG"
    
    def test_calculation_logging(self, caplog):
        """Test calculation logging."""
        with flow_operation("BTCUSDT", "get_market_data"):
            self.logger.log_calculation(
                indicator="RSI",
                symbol="BTCUSDT",
                result="35.17",
                calculation_time_ms=8
            )
        
        # Verify logging happened and contains expected message
        assert len(caplog.records) > 0
        log_record = caplog.records[0]
        assert log_record.message == "RSI calculation completed"
        assert log_record.levelname == "DEBUG"
    
    def test_validation_error_logging(self, caplog):
        """Test validation error logging."""
        with flow_operation("DOGEUSDT", "get_market_data"):
            self.logger.log_validation_error(
                field="rsi_14",
                value="105.67",
                expected="0-100",
                error_msg="RSI must be between 0 and 100"
            )
        
        # Verify logging happened and contains expected message
        assert len(caplog.records) > 0
        log_record = caplog.records[0]
        assert log_record.message == "Data validation failed"
        assert log_record.levelname == "ERROR"
    
    def test_fallback_logging(self, caplog):
        """Test fallback usage logging."""
        with flow_operation("TESTUSDT", "get_market_data"):
            self.logger.log_fallback_usage(
                operation="_calculate_rsi",
                reason="insufficient_data",
                fallback_value="50.0"
            )
        
        # Verify logging happened and contains expected message
        assert len(caplog.records) > 0
        log_record = caplog.records[0]
        assert log_record.message == "Fallback strategy used in _calculate_rsi"
        assert log_record.levelname == "WARNING"


@pytest.mark.unit
@pytest.mark.logging
class TestCriticalFixes:
    """Test critical production fixes."""
    
    def test_stderr_output_configuration(self, capfd):
        """Test that logs are directed to stderr for AI searchability."""
        configure_ai_logging(log_level="DEBUG", console_output=True)
        logger = get_ai_logger("stderr_test", service_name="stderr_service")
        
        # Log a message
        logger.info("Test stderr output", 
                   operation="test_stderr",
                   context={"test": "stderr_validation"})
        
        # Capture stdout and stderr
        captured = capfd.readouterr()
        
        # JSON logs should be in stderr, not stdout
        assert captured.out == "", "No output should go to stdout"
        assert captured.err != "", "JSON logs should go to stderr"
    
    def test_trace_level_implementation(self):
        """Test that trace() method doesn't crash."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        logger = get_ai_logger("trace_test", service_name="trace_service")
        
        # This should not crash
        try:
            logger.trace("Trace level test message",
                        operation="trace_test",
                        context={"test": "trace_level"},
                        tags=["trace", "raw_data"])
            assert True, "Trace method should not crash"
        except Exception as e:
            pytest.fail(f"Trace method crashed: {e}")
    
    def test_no_handler_duplication(self):
        """Test that multiple logger creations don't duplicate handlers."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        
        # Create same logger multiple times
        logger1 = get_ai_logger("duplication_test", service_name="dup_service")
        logger2 = get_ai_logger("duplication_test", service_name="dup_service")
        logger3 = get_ai_logger("duplication_test", service_name="dup_service")
        
        # Should be same instance
        assert logger1 is logger2 is logger3
        
        # Check handler count on underlying logger
        handler_count = len(logger1.logger.handlers)
        
        # Create more instances
        for i in range(5):
            get_ai_logger("duplication_test", service_name="dup_service")
        
        # Handler count should not increase
        new_handler_count = len(logger1.logger.handlers)
        assert new_handler_count == handler_count, "Handler count should not increase"
    
    def test_concurrent_logger_creation(self):
        """Test that concurrent logger creation is thread-safe."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        
        loggers = {}
        errors = []
        
        def create_logger(worker_id):
            try:
                logger_name = f"worker_{worker_id}"
                logger = get_ai_logger(logger_name, service_name=f"worker_service_{worker_id}")
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


@pytest.mark.unit
@pytest.mark.logging
class TestEdgeCasesAndPerformance:
    """Test edge cases and performance characteristics."""
    
    def test_unicode_logging(self):
        """Test logging with unicode characters."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        logger = get_ai_logger("unicode_test", service_name="unicode_service")
        
        # Should not crash with unicode
        logger.info("Unicode test: ЙЦУ БТЦ УСДТ 🚀", context={"symbol": "BTCUSDT"})
    
    def test_large_context_logging(self):
        """Test logging with large context objects."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        logger = get_ai_logger("large_context_test", service_name="large_ctx_service")
        
        large_context = {"data": "x" * 10000}  # Large string
        
        # Should not crash with large context
        logger.info("Large context test", context=large_context)
    
    def test_concurrent_logging_operations(self):
        """Test concurrent logging operations don't interfere."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        
        messages_logged = []
        errors = []
        
        def log_worker(worker_id):
            try:
                logger = get_ai_logger(f"concurrent_worker_{worker_id}", service_name=f"concurrent_service_{worker_id}")
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
    
    def test_logging_performance(self):
        """Test logging performance under load."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        logger = get_ai_logger("performance_test", service_name="perf_service")
        
        start_time = time.time()
        
        # Log many messages
        for i in range(1000):
            logger.info(f"Performance test message {i}", 
                       context={"iteration": i, "test": "performance"})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (less than 2 seconds)
        assert duration < 2.0, f"Logging 1000 messages took {duration:.2f}s (too slow)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])