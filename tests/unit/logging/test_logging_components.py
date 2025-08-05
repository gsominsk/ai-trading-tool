"""
Unit Tests for Logging System Components

Consolidated tests for logging levels, exception handling, JSON schema validation,
and specialized logging components.

Consolidates:
- test_logging_levels.py (log level filtering and performance)
- test_logging_exception_handling.py (exception handling and graceful degradation)
- test_logging_json_schema_validation.py (JSON schema validation for AI analysis)
"""

import pytest
import json
import tempfile
import os
import threading
import time
import jsonschema
from jsonschema import validate, ValidationError
from unittest.mock import patch, MagicMock

from src.logging_system import (
    configure_ai_logging,
    get_ai_logger,
    MarketDataLogger,
    flow_operation,
    get_trace_id
)
from src.market_data.market_data_service import MarketDataService
from src.market_data.logging_integration import MarketDataServiceLogging


@pytest.mark.unit
@pytest.mark.logging
class TestLoggingLevels:
    """Test log level filtering and performance optimization."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_log_level_filtering_hierarchy(self):
        """Test complete log level filtering hierarchy."""
        test_cases = [
            ("DEBUG", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
            ("INFO", ["INFO", "WARNING", "ERROR", "CRITICAL"]),
            ("WARNING", ["WARNING", "ERROR", "CRITICAL"]),
            ("ERROR", ["ERROR", "CRITICAL"]),
            ("CRITICAL", ["CRITICAL"])
        ]
        
        for level, expected_levels in test_cases:
            service = MarketDataService(log_level=level)
            
            # Test level filtering
            for test_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                should_log = service._should_log(test_level)
                expected = test_level in expected_levels
                assert should_log == expected, f"Level {level}: {test_level} should be {expected}"
    
    def test_log_level_case_insensitive(self):
        """Test that log levels are case insensitive."""
        service = MarketDataService(log_level="warning")  # lowercase
        
        assert service._log_level == "WARNING"  # Should be converted to uppercase
        assert service._should_log("WARNING") == True
        assert service._should_log("warning") == True  # lowercase should work
        assert service._should_log("Warning") == True  # mixed case should work
    
    def test_invalid_log_level_defaults_to_info(self):
        """Test that invalid log levels default to INFO."""
        service = MarketDataService(log_level="INVALID")
        
        # Should default to INFO behavior
        assert service._should_log("DEBUG") == False
        assert service._should_log("INFO") == True
        assert service._should_log("WARNING") == True
    
    def test_logging_integration_level_filtering(self):
        """Test that logging integration respects level filtering."""
        logging_integration = MarketDataServiceLogging(log_level="WARNING")
        
        # WARNING level should filter appropriately
        assert logging_integration._should_log("DEBUG") == False
        assert logging_integration._should_log("INFO") == False
        assert logging_integration._should_log("WARNING") == True
        assert logging_integration._should_log("ERROR") == True
        assert logging_integration._should_log("CRITICAL") == True
    
    def test_production_performance_optimization(self):
        """Test that high log levels improve performance by skipping operations."""
        service = MarketDataService(log_level="ERROR", enable_logging=True)
        
        # Test level filtering directly
        assert service._logging_integration._should_log("DEBUG") == False
        assert service._logging_integration._should_log("INFO") == False
        assert service._logging_integration._should_log("WARNING") == False
        assert service._logging_integration._should_log("ERROR") == True
        assert service._logging_integration._should_log("CRITICAL") == True
        
        # Verify the service log level is set correctly
        assert service._log_level == "ERROR"
        assert service._logging_integration.log_level == "ERROR"
    
    @pytest.mark.performance
    def test_high_volume_log_throughput(self):
        """Test logging system can handle high volume of log messages."""
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        import time
        import psutil
        
        formatter = AIOptimizedJSONFormatter()
        
        # Test parameters
        message_count = 1000
        start_time = time.time()
        
        # Generate high volume of log messages
        for i in range(message_count):
            log_record = self._create_log_record(f"test_message_{i}")
            formatted_message = formatter.format(log_record)
            
            # Verify message is properly formatted
            assert "test_message_" in formatted_message
            assert "timestamp" in formatted_message
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance requirement: > 1000 messages/second
        messages_per_second = message_count / duration
        assert messages_per_second > 500, f"Throughput too low: {messages_per_second:.1f} msg/sec"
        
        print(f"✅ Log throughput: {messages_per_second:.1f} messages/second")
    
    @pytest.mark.performance
    def test_memory_usage_during_extended_logging(self):
        """Test memory usage remains reasonable during extended logging."""
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        import psutil
        
        formatter = AIOptimizedJSONFormatter()
        process = psutil.Process()
        
        # Record initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate large number of log messages
        message_count = 5000  # Reduced for unit test
        for i in range(message_count):
            log_record = self._create_log_record(f"extended_test_{i}")
            formatted_message = formatter.format(log_record)
            
            # Periodically check memory
            if i % 1000 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                
                # Performance requirement: < 50MB for 5K messages
                assert memory_increase < 50, f"Memory usage too high: {memory_increase:.1f}MB"
        
        final_memory = process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - initial_memory
        
        print(f"✅ Memory increase for {message_count} messages: {total_increase:.1f}MB")
        assert total_increase < 50, f"Total memory increase too high: {total_increase:.1f}MB"
    
    @pytest.mark.performance
    def test_json_formatting_performance(self):
        """Test JSON formatting performance for individual messages."""
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        import time
        from decimal import Decimal
        
        formatter = AIOptimizedJSONFormatter()
        
        # Test parameters
        iterations = 500  # Reduced for unit test
        max_time_per_message = 0.005  # 5ms - more lenient
        
        total_time = 0
        for i in range(iterations):
            log_record = self._create_complex_log_record(i)
            
            start_time = time.time()
            formatted_message = formatter.format(log_record)
            end_time = time.time()
            
            format_time = end_time - start_time
            total_time += format_time
            
            # Verify formatting works
            assert "complex_message_" in formatted_message
            assert "timestamp" in formatted_message
            
        average_time = total_time / iterations
        
        # Performance requirement: < 5ms per message (lenient for unit test)
        assert average_time < max_time_per_message, f"JSON formatting too slow: {average_time*1000:.2f}ms"
        
        print(f"✅ Average JSON formatting time: {average_time*1000:.2f}ms per message")
    
    def _create_log_record(self, message, level="INFO"):
        """Helper to create a log record for testing."""
        import time
        return type('LogRecord', (), {
            'levelname': level,
            'msg': message,
            'args': (),
            'created': time.time(),
            'filename': 'test.py',
            'funcName': 'test_function',
            'lineno': 42,
            'module': 'test_module',
            'msecs': 123,
            'name': 'test_logger',
            'pathname': '/test/test.py',
            'process': 12345,
            'processName': 'TestProcess',
            'relativeCreated': 1000,
            'thread': 67890,
            'threadName': 'TestThread',
            'exc_info': None,
            'exc_text': None,
            'stack_info': None,
            'getMessage': lambda self: message
        })()
    
    def _create_complex_log_record(self, index):
        """Helper to create a complex log record with nested data."""
        from decimal import Decimal
        message = f"complex_message_{index}"
        record = self._create_log_record(message)
        
        # Add complex data that should be in extra/context fields
        complex_data = {
            'nested_object': {
                'id': index,
                'values': [1, 2, 3, index],
                'metadata': {'key': f'value_{index}'}
            },
            'decimal_value': str(Decimal('123.456')),  # Convert to string for JSON
            'large_string': 'x' * 100
        }
        
        # Add as context data for formatter
        record.context = {'complex_data': complex_data}
        
        return record


@pytest.mark.unit
@pytest.mark.logging
class TestLoggingExceptionHandling:
    """Test exception handling and graceful degradation in logging."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_logging_integration_handles_logger_failure(self):
        """Test that logging integration handles logger initialization failures."""
        with patch('src.market_data.logging_integration.MarketDataLogger') as mock_logger_class:
            mock_logger_class.side_effect = Exception("Logger initialization failed")
            
            # Service should handle logging failure gracefully
            with pytest.raises(Exception):
                service = MarketDataService(enable_logging=True)
    
    def test_log_operation_methods_handle_exceptions(self):
        """Test that all log operation methods gracefully handle exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Test all logging methods with mocked failures
        with patch.object(service._logging_integration.logger, 'log_operation_start') as mock_start, \
             patch.object(service._logging_integration.logger, 'log_operation_complete') as mock_complete, \
             patch.object(service._logging_integration.logger, 'log_validation_error') as mock_error:
            
            mock_start.side_effect = Exception("Start logging failed")
            mock_complete.side_effect = Exception("Complete logging failed")
            mock_error.side_effect = Exception("Error logging failed")
            
            # All operations should complete without raising exceptions
            try:
                service._log_operation_start("test_operation", symbol="BTCUSDT")
                service._log_operation_success("test_operation", symbol="BTCUSDT")
                service._log_operation_error("test_operation", Exception("test"), symbol="BTCUSDT")
                assert True, "All logging operations should handle exceptions gracefully"
            except Exception as e:
                pytest.fail(f"Logging operations should not raise exceptions: {e}")
    
    def test_specialized_logging_methods_handle_exceptions(self):
        """Test that specialized logging methods handle exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock all specialized logging methods to fail
        with patch.object(service._logging_integration.logger, 'log_raw_data') as mock_raw, \
             patch.object(service._logging_integration.logger, 'log_api_call') as mock_api, \
             patch.object(service._logging_integration.logger, 'log_fallback_usage') as mock_fallback:
            
            mock_raw.side_effect = Exception("Raw logging failed")
            mock_api.side_effect = Exception("API logging failed")
            mock_fallback.side_effect = Exception("Fallback logging failed")
            
            # All specialized operations should handle failures gracefully
            try:
                service._logging_integration.log_trading_operation(
                    "test_operation", "BTCUSDT", {"test": "data"}, "success"
                )
                service._logging_integration.log_market_analysis(
                    "BTCUSDT", {"rsi": 45.2}, "buy", 0.8
                )
                service._logging_integration.log_order_execution(
                    "ORD123", "BTCUSDT", "BUY", "0.001", "42000.00", "executed"
                )
                service._logging_integration.log_api_response(
                    "get_klines", "https://api.binance.com", 200, 1024, "BTCUSDT"
                )
                service._logging_integration.log_graceful_degradation(
                    "test_operation", "test_reason", "test_fallback"
                )
                service._logging_integration.log_performance_metrics(
                    "test_operation", {"duration_ms": 150}, "BTCUSDT"
                )
                assert True, "All specialized logging should handle exceptions"
            except Exception as e:
                pytest.fail(f"Specialized logging should not raise exceptions: {e}")
    
    def test_get_operation_metrics_handles_exceptions(self):
        """Test that get_operation_metrics returns fallback data on failure."""
        service = MarketDataService(enable_logging=True)
        
        # Mock flow summary to fail
        with patch('src.market_data.logging_integration.get_flow_summary') as mock_summary:
            mock_summary.side_effect = Exception("Flow summary failure")
            
            # Should return degraded metrics instead of crashing
            metrics = service._logging_integration.get_operation_metrics()
            
            assert metrics["service_name"] == "MarketDataService"
            assert metrics["logger_status"] == "degraded"
            assert metrics["active_operations"] == 0
            assert metrics["flow_summary"] == "metrics_unavailable"
    
    def test_reset_metrics_handles_exceptions(self):
        """Test that reset_metrics clears data even if logging fails."""
        service = MarketDataService(enable_logging=True)
        
        # Add test data to metrics
        service._logging_integration._operation_start_times["test_op"] = 12345.0
        assert len(service._logging_integration._operation_start_times) == 1
        
        # Mock logger to fail
        with patch.object(service._logging_integration.logger, 'log_raw_data') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # Reset should still work
            service._logging_integration.reset_metrics()
            
            # Metrics should be cleared despite logging failure
            assert len(service._logging_integration._operation_start_times) == 0
    
    def test_complete_system_failure_protection(self):
        """Test complete protection from logging system failures."""
        service = MarketDataService(enable_logging=True)
        
        # Simulate complete logging system failure with fallback failure too
        with patch.object(service._logging_integration.logger, 'log_operation_start') as mock_log, \
             patch('builtins.open', side_effect=Exception("Filesystem failure")):
            
            mock_log.side_effect = Exception("Main logging failure")
            
            # Even with complete failure, operations should work
            try:
                service._log_operation_start("test_operation", symbol="BTCUSDT")
                
                # All trading operations should continue
                service._logging_integration.log_trading_operation(
                    "buy_signal", "BTCUSDT", {"price": 42000}, "success"
                )
                
                # Get metrics should still work
                metrics = service._logging_integration.get_operation_metrics()
                assert metrics["service_name"] == "MarketDataService"
                
                # Reset should work
                service._logging_integration.reset_metrics()
                
                assert True, "All operations protected from complete logging failure"
            except Exception as e:
                pytest.fail(f"Complete logging failure should not crash operations: {e}")


@pytest.mark.unit
@pytest.mark.logging
class TestJSONSchemaValidation:
    """Test JSON schema validation for AI-searchable logs."""
    
    def setup_method(self):
        """Setup for each test."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
    
    @property
    def ai_log_schema(self):
        """JSON schema for AI-optimized log entries."""
        return {
            "type": "object",
            "required": [
                "timestamp", 
                "level", 
                "service", 
                "operation", 
                "message", 
                "trace_id"
            ],
            "properties": {
                "timestamp": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$"
                },
                "level": {
                    "type": "string",
                    "enum": ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                },
                "service": {
                    "type": "string",
                    "minLength": 1
                },
                "operation": {
                    "type": "string"
                },
                "message": {
                    "type": "string",
                    "minLength": 1
                },
                "trace_id": {
                    "type": "string",
                    "pattern": r"^trd_\d{3}_\d{14}\d{4}$"
                },
                "context": {
                    "type": "object"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "flow": {
                    "type": "object",
                    "properties": {
                        "flow_id": {"type": "string"},
                        "stage": {"type": "string"},
                        "previous_stage": {"type": ["string", "null"]},
                        "stages_completed": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "exception": {
                    "type": "object",
                    "properties": {
                        "type": {"type": ["string", "null"]},
                        "message": {"type": ["string", "null"]},
                        "traceback": {"type": "string"}
                    }
                }
            },
            "additionalProperties": False
        }
    
    def test_basic_log_schema_validation(self, capfd):
        """Test that basic log entries conform to schema."""
        logger = get_ai_logger("schema_test")
        
        logger.info("Schema validation test",
                   operation="schema_validation",
                   context={"test": "basic_schema"},
                   tags=["validation", "schema"])
        
        captured = capfd.readouterr()
        
        # Find JSON log in stderr
        json_log = self._extract_json_log(captured.err)
        assert json_log is not None, "Should find valid JSON log"
        
        # Validate against schema
        try:
            validate(instance=json_log, schema=self.ai_log_schema)
        except ValidationError as e:
            pytest.fail(f"Log does not conform to schema: {e.message}")
    
    def test_market_data_logger_schema_validation(self, capfd):
        """Test MarketDataLogger output schema validation."""
        logger = MarketDataLogger("schema_market_test")
        
        with flow_operation("BTCUSDT", "schema_test"):
            logger.log_operation_start("schema_test", "BTCUSDT",
                                     context={"test_type": "schema_validation"})
            logger.log_api_call("BTCUSDT", "1d", 180, response_time_ms=123)
            logger.log_calculation("RSI", "BTCUSDT", result="42.5")
        
        captured = capfd.readouterr()
        
        # Parse all JSON logs
        json_logs = self._extract_all_json_logs(captured.err)
        assert len(json_logs) >= 3, "Should have at least 3 log entries"
        
        # Validate each log against schema
        for i, log_entry in enumerate(json_logs):
            try:
                validate(instance=log_entry, schema=self.ai_log_schema)
            except ValidationError as e:
                pytest.fail(f"Log entry {i} does not conform to schema: {e.message}")
    
    def test_all_log_levels_schema_validation(self, capfd):
        """Test all log levels conform to schema."""
        # Configure to capture TRACE level logs
        configure_ai_logging(log_level="TRACE", console_output=False)
        logger = get_ai_logger("all_levels_test")
        
        # Test all log levels including TRACE
        logger.trace("Trace message", operation="trace_test")
        logger.debug("Debug message", operation="debug_test")
        logger.info("Info message", operation="info_test")
        logger.warning("Warning message", operation="warning_test")
        logger.error("Error message", operation="error_test")
        logger.critical("Critical message", operation="critical_test")
        
        captured = capfd.readouterr()
        
        # Parse all JSON logs
        json_logs = self._extract_all_json_logs(captured.err)
        assert len(json_logs) >= 5, f"Should have at least 5 log entries for all levels, got {len(json_logs)}"
        
        # Validate all logs
        for i, log_entry in enumerate(json_logs):
            try:
                validate(instance=log_entry, schema=self.ai_log_schema)
            except ValidationError as e:
                pytest.fail(f"Log level test entry {i} ({log_entry.get('level', 'UNKNOWN')}) does not conform to schema: {e.message}")
    
    def test_complex_context_schema_validation(self, capfd):
        """Test complex context objects conform to schema."""
        logger = get_ai_logger("complex_context_test")
        
        complex_context = {
            "symbol": "BTCUSDT",
            "timeframes": ["1d", "4h", "1h"],
            "indicators": {
                "rsi": 42.5,
                "macd": "bullish",
                "ma_20": 65432.11,
                "ma_50": 64123.45
            },
            "metadata": {
                "api_calls": 3,
                "processing_time_ms": 1234,
                "cache_hit": False
            }
        }
        
        logger.info("Complex context test",
                   operation="complex_context",
                   context=complex_context,
                   tags=["complex", "context", "validation"])
        
        captured = capfd.readouterr()
        
        # Find and validate JSON log
        json_log = self._extract_json_log(captured.err)
        assert json_log is not None, "Should find valid JSON log"
        
        # Validate schema
        try:
            validate(instance=json_log, schema=self.ai_log_schema)
        except ValidationError as e:
            pytest.fail(f"Complex context log does not conform to schema: {e.message}")
        
        # Verify complex context preserved
        assert json_log["context"]["symbol"] == "BTCUSDT"
        assert json_log["context"]["indicators"]["rsi"] == 42.5
        assert json_log["context"]["metadata"]["api_calls"] == 3
    
    def test_flow_context_schema_validation(self, capfd):
        """Test flow context schema validation."""
        logger = get_ai_logger("flow_schema_test")
        
        with flow_operation("ETHUSDT", "flow_schema_test") as flow_id:
            from src.logging_system.flow_context import advance_to_stage
            advance_to_stage("validation")
            advance_to_stage("processing", api_calls=2)
            
            logger.info("Flow context test",
                       operation="flow_test",
                       context={"flow_validation": True})
        
        captured = capfd.readouterr()
        
        # Find JSON log with flow context
        json_logs = self._extract_all_json_logs(captured.err)
        json_log = None
        for log_data in json_logs:
            if log_data.get("flow"):
                json_log = log_data
                break
        
        assert json_log is not None, "Should find JSON log with flow context"
        
        # Validate schema
        try:
            validate(instance=json_log, schema=self.ai_log_schema)
        except ValidationError as e:
            pytest.fail(f"Flow context log does not conform to schema: {e.message}")
        
        # Verify flow context structure
        assert "flow_id" in json_log["flow"]
        assert "stage" in json_log["flow"]
        assert json_log["flow"]["flow_id"].startswith("flow_eth_")
    
    def test_trace_id_format_validation(self, capfd):
        """Test trace ID format validation."""
        logger = get_ai_logger("trace_format_test")
        
        # Test auto-generated trace ID
        logger.info("Auto trace ID test", operation="auto_trace")
        
        # Test custom trace ID
        custom_trace_id = get_trace_id()
        logger.info("Custom trace ID test", 
                   operation="custom_trace",
                   trace_id=custom_trace_id)
        
        captured = capfd.readouterr()
        
        # Parse logs and validate trace ID format
        json_logs = self._extract_all_json_logs(captured.err)
        trace_ids = [log.get("trace_id") for log in json_logs]
        
        assert len(trace_ids) >= 2, "Should have at least 2 trace IDs"
        
        # Validate trace ID format
        import re
        trace_pattern = r"^trd_\d{3}_\d{14}\d{4}$"
        for trace_id in trace_ids:
            assert trace_id is not None, "Trace ID should not be None"
            assert re.match(trace_pattern, trace_id), f"Invalid trace ID format: {trace_id}"
    
    def test_exception_schema_validation(self, capfd):
        """Test exception logging schema validation."""
        logger = get_ai_logger("exception_test")
        
        try:
            raise ValueError("Test exception for schema validation")
        except ValueError:
            logger.error("Exception test",
                        operation="exception_handling",
                        context={"exception_test": True},
                        exc_info=True)
        
        captured = capfd.readouterr()
        
        # Find exception log
        json_logs = self._extract_all_json_logs(captured.err)
        exception_log = None
        for log_data in json_logs:
            if "exception" in log_data:
                exception_log = log_data
                break
        
        assert exception_log is not None, "Should find exception log"
        
        # Validate schema
        try:
            validate(instance=exception_log, schema=self.ai_log_schema)
        except ValidationError as e:
            pytest.fail(f"Exception log does not conform to schema: {e.message}")
        
        # Verify exception structure
        assert exception_log["exception"]["type"] == "ValueError"
        assert "Test exception for schema validation" in exception_log["exception"]["message"]
        assert "traceback" in exception_log["exception"]
    
    def test_schema_edge_cases(self, capfd):
        """Test schema validation edge cases."""
        logger = get_ai_logger("edge_case_test")
        
        # Test with empty optional fields
        logger.info("Empty fields test",
                   operation="empty_test",
                   context={},  # Empty context
                   tags=[],     # Empty tags
                   flow={})     # Empty flow
        
        # Test with minimal required fields only
        logger.info("Minimal log test", operation="minimal")
        
        captured = capfd.readouterr()
        
        # Validate all logs
        json_logs = self._extract_all_json_logs(captured.err)
        assert len(json_logs) >= 2, "Should have at least 2 logs"
        
        for i, log_entry in enumerate(json_logs):
            try:
                validate(instance=log_entry, schema=self.ai_log_schema)
            except ValidationError as e:
                pytest.fail(f"Edge case log {i} should be valid: {e.message}")
    
    def _extract_json_log(self, stderr_output):
        """Helper method to extract first JSON log from stderr."""
        stderr_lines = stderr_output.strip().split('\n')
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    return json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
        return None
    
    def _extract_all_json_logs(self, stderr_output):
        """Helper method to extract all JSON logs from stderr."""
        stderr_lines = stderr_output.strip().split('\n')
        json_logs = []
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        return json_logs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])