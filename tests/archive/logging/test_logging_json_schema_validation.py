"""
JSON Schema Validation Tests for AI-Optimized Logging System
Ensures structured integrity of JSON logs for AI analysis
"""

import pytest
import json
import jsonschema
from jsonschema import validate, ValidationError
from src.logging_system import (
    configure_ai_logging,
    get_ai_logger,
    MarketDataLogger,
    flow_operation,
    get_trace_id
)


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
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_log = json.loads(line.strip())
                    break
                except json.JSONDecodeError:
                    continue
        
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
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
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
        stderr_lines = captured.err.strip().split('\n')
        json_logs = []
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
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
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_log = json.loads(line.strip())
                    break
                except json.JSONDecodeError:
                    continue
        
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
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    log_data = json.loads(line.strip())
                    if log_data.get("flow"):
                        json_log = log_data
                        break
                except json.JSONDecodeError:
                    continue
        
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
        stderr_lines = captured.err.strip().split('\n')
        trace_ids = []
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    log_data = json.loads(line.strip())
                    trace_ids.append(log_data.get("trace_id"))
                except json.JSONDecodeError:
                    continue
        
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
        stderr_lines = captured.err.strip().split('\n')
        exception_log = None
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    log_data = json.loads(line.strip())
                    if "exception" in log_data:
                        exception_log = log_data
                        break
                except json.JSONDecodeError:
                    continue
        
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


class TestJSONSchemaEdgeCases:
    """Test JSON schema validation edge cases."""
    
    def setup_method(self):
        """Setup for each test."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
    
    def test_empty_optional_fields_schema(self, capfd):
        """Test schema validation with empty optional fields."""
        logger = get_ai_logger("empty_fields_test")
        
        logger.info("Empty fields test",
                   operation="empty_test",
                   context={},  # Empty context
                   tags=[],     # Empty tags
                   flow={})     # Empty flow
        
        captured = capfd.readouterr()
        
        # Find and validate log
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_log = json.loads(line.strip())
                    break
                except json.JSONDecodeError:
                    continue
        
        assert json_log is not None, "Should find valid JSON log"
        
        # Should still be valid with empty optional fields
        schema = TestJSONSchemaValidation().ai_log_schema
        try:
            validate(instance=json_log, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Log with empty optional fields should be valid: {e.message}")
    
    def test_missing_optional_fields_schema(self, capfd):
        """Test schema validation with missing optional fields."""
        logger = get_ai_logger("missing_fields_test")
        
        # Log with only required fields
        logger.info("Minimal log test", operation="minimal")
        
        captured = capfd.readouterr()
        
        # Find and validate log
        stderr_lines = captured.err.strip().split('\n')
        json_log = None
        for line in stderr_lines:
            if line.strip() and line.strip().startswith('{"'):
                try:
                    json_log = json.loads(line.strip())
                    break
                except json.JSONDecodeError:
                    continue
        
        assert json_log is not None, "Should find valid JSON log"
        
        # Should be valid with only required fields
        schema = TestJSONSchemaValidation().ai_log_schema
        try:
            validate(instance=json_log, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Minimal log should be valid: {e.message}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])