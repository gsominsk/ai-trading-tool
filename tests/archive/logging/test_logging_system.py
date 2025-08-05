"""
Tests for AI-Optimized Logging System
"""

import pytest
import json
import io
import sys
from unittest.mock import patch
from src.logging_system import (
    configure_ai_logging,
    get_ai_logger,
    MarketDataLogger,
    flow_operation,
    get_trace_id,
    get_flow_id,
    reset_trace_counter
)
from src.logging_system.flow_context import advance_to_stage


class TestTraceGenerator:
    """Test trace ID and flow ID generation."""
    
    def test_trace_id_generation(self):
        """Test trace ID format and uniqueness."""
        reset_trace_counter()
        
        trace_id1 = get_trace_id()
        trace_id2 = get_trace_id()
        
        # Check format: trd_001_timestamp
        assert trace_id1.startswith("trd_001_")
        assert trace_id2.startswith("trd_001_")
        
        # Check uniqueness
        assert trace_id1 != trace_id2
        
        # Check sequence
        assert trace_id1.endswith("0001")
        assert trace_id2.endswith("0002")
    
    def test_flow_id_generation(self):
        """Test flow ID format."""
        flow_id1 = get_flow_id("BTCUSDT")
        flow_id2 = get_flow_id("", "enhanced_context")
        
        # Check format
        assert flow_id1.startswith("flow_btc_")
        assert flow_id2.startswith("flow_enhanced_context_")
        
        # Check timestamp inclusion
        assert len(flow_id1.split("_")) == 3
        assert len(flow_id2.split("_")) == 4  # flow_enhanced_context_timestamp


class TestFlowContext:
    """Test flow context management."""
    
    def test_flow_operation_context_manager(self):
        """Test flow operation context manager."""
        with flow_operation("BTCUSDT", "get_market_data") as flow_id:
            assert flow_id.startswith("flow_btc_")
            
            # Test stage advancement
            advance_to_stage("symbol_validation")
            advance_to_stage("data_collection", api_calls=3)
    
    def test_flow_context_without_operation(self):
        """Test flow context outside of operation."""
        from src.logging_system.flow_context import get_flow_summary
        
        # Should return empty context when no flow active
        summary = get_flow_summary()
        assert summary == {}


class TestJSONFormatter:
    """Test JSON log formatting."""
    
    def test_structured_logger_creation(self):
        """Test structured logger creation."""
        logger = get_ai_logger("test_module")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'error')
    
    def test_json_log_format(self, capfd):
        """Test JSON log output format."""
        import logging
        from io import StringIO
        from src.logging_system.json_formatter import StructuredLogger, AIOptimizedJSONFormatter
        
        # Create a string buffer to capture logs
        log_capture = StringIO()
        
        # Create logger directly and patch its handler
        logger = StructuredLogger("test_module", "MarketDataService")
        
        # Replace the logger's handler with our test handler
        test_handler = logging.StreamHandler(log_capture)
        test_handler.setFormatter(AIOptimizedJSONFormatter("MarketDataService"))
        
        # Clear existing handlers and add our test handler
        logger.logger.handlers.clear()
        logger.logger.addHandler(test_handler)
        logger.logger.setLevel(logging.DEBUG)

        # Log a message
        logger.info(
            "Test message",
            operation="test_operation",
            context={"test_key": "test_value"},
            tags=["test_tag"],
            trace_id="test_trace_123"
        )

        # Get captured output
        output = log_capture.getvalue()

        # Should contain JSON structure
        assert "{" in output and "}" in output
        
        # Parse as JSON to verify structure
        try:
            # Extract JSON from log output (may have other formatting)
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            json_str = output[json_start:json_end]
            log_data = json.loads(json_str)
            
            # Verify required fields
            assert "timestamp" in log_data
            assert "level" in log_data
            assert "service" in log_data
            assert log_data["message"] == "Test message"
            assert log_data["operation"] == "test_operation"
            assert log_data["context"]["test_key"] == "test_value"
            assert "test_tag" in log_data["tags"]
            assert log_data["trace_id"] == "test_trace_123"
            
        except json.JSONDecodeError:
            pytest.fail(f"Log output is not valid JSON: {output}")


class TestMarketDataLogger:
    """Test MarketDataService-specific logging."""
    
    def setup_method(self):
        """Setup for each test."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        self.logger = MarketDataLogger("test_market_data")
    
    def test_operation_start_logging(self, capfd):
        """Test operation start logging."""
        import logging
        from io import StringIO
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        
        # Create a string buffer to capture logs
        log_capture = StringIO()
        
        # Create a handler for our buffer with JSON formatter
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(AIOptimizedJSONFormatter("MarketDataService"))
        
        # Add handler to the root logger temporarily
        root_logger = logging.getLogger()
        original_level = root_logger.level
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        
        try:
            with flow_operation("BTCUSDT", "get_market_data"):
                self.logger.log_operation_start(
                    "get_market_data",
                    symbol="BTCUSDT",
                    context={"cache_dir": "data/cache"}
                )
        finally:
            # Clean up
            root_logger.removeHandler(handler)
            root_logger.setLevel(original_level)

        # Get captured output
        output = log_capture.getvalue()
        # JSON logs contain the message in JSON format
        assert "get_market_data initiated" in output
        assert "BTCUSDT" in output or "btc" in output.lower()
    
    def test_api_call_logging(self, capfd):
        """Test API call logging."""
        import logging
        from io import StringIO
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        
        # Create a string buffer to capture logs
        log_capture = StringIO()
        
        # Create a handler for our buffer with JSON formatter
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(AIOptimizedJSONFormatter("MarketDataService"))
        
        # Add handler to the root logger temporarily
        root_logger = logging.getLogger()
        original_level = root_logger.level
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        
        try:
            with flow_operation("BTCUSDT", "get_market_data"):
                self.logger.log_api_call(
                    symbol="BTCUSDT",
                    interval="1d",
                    limit=180,
                    response_time_ms=145,
                    status_code=200
                )
        finally:
            # Clean up
            root_logger.removeHandler(handler)
            root_logger.setLevel(original_level)

        # Get captured output
        output = log_capture.getvalue()
        # JSON logs contain the message and context
        assert "Binance API call executed" in output
        assert "BTCUSDT" in output
        assert "1d" in output
    
    def test_calculation_logging(self, capfd):
        """Test calculation logging."""
        import logging
        from io import StringIO
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        
        # Create a string buffer to capture logs
        log_capture = StringIO()
        
        # Create a handler for our buffer with JSON formatter
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(AIOptimizedJSONFormatter("MarketDataService"))
        
        # Add handler to the root logger temporarily
        root_logger = logging.getLogger()
        original_level = root_logger.level
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        
        try:
            with flow_operation("BTCUSDT", "get_market_data"):
                self.logger.log_calculation(
                    indicator="RSI",
                    symbol="BTCUSDT",
                    result="35.17",
                    calculation_time_ms=8
                )
        finally:
            # Clean up
            root_logger.removeHandler(handler)
            root_logger.setLevel(original_level)

        # Get captured output
        output = log_capture.getvalue()
        # JSON logs contain the message and result data
        assert "RSI calculation completed" in output
        assert "35.17" in output
    
    def test_validation_error_logging(self, capfd):
        """Test validation error logging."""
        import logging
        from io import StringIO
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        
        # Create a string buffer to capture logs
        log_capture = StringIO()
        
        # Create a handler for our buffer with JSON formatter
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(AIOptimizedJSONFormatter("MarketDataService"))
        
        # Add handler to the root logger temporarily
        root_logger = logging.getLogger()
        original_level = root_logger.level
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        
        try:
            with flow_operation("DOGEUSDT", "get_market_data"):
                self.logger.log_validation_error(
                    field="rsi_14",
                    value="105.67",
                    expected="0-100",
                    error_msg="RSI must be between 0 and 100"
                )
        finally:
            # Clean up
            root_logger.removeHandler(handler)
            root_logger.setLevel(original_level)

        # Get captured output
        output = log_capture.getvalue()
        # JSON logs contain error message and context
        assert "Data validation failed" in output
        assert "105.67" in output
        assert "rsi_14" in output
    
    def test_fallback_logging(self, capfd):
        """Test fallback usage logging."""
        import logging
        from io import StringIO
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        
        # Create a string buffer to capture logs
        log_capture = StringIO()
        
        # Create a handler for our buffer with JSON formatter
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(AIOptimizedJSONFormatter("MarketDataService"))
        
        # Add handler to the root logger temporarily
        root_logger = logging.getLogger()
        original_level = root_logger.level
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        
        try:
            with flow_operation("TESTUSDT", "get_market_data"):
                self.logger.log_fallback_usage(
                    operation="_calculate_rsi",
                    reason="insufficient_data",
                    fallback_value="50.0"
                )
        finally:
            # Clean up
            root_logger.removeHandler(handler)
            root_logger.setLevel(original_level)

        # Get captured output
        output = log_capture.getvalue()
        # JSON logs contain fallback message and context
        assert "Fallback strategy used" in output
        assert "insufficient_data" in output
        assert "50.0" in output


class TestLoggerConfiguration:
    """Test logger configuration."""
    
    def test_configure_ai_logging(self):
        """Test logging configuration."""
        configure_ai_logging(log_level="INFO", console_output=True)
        
        logger = get_ai_logger("test_config")
        assert logger is not None
    
    def test_logger_singleton_behavior(self):
        """Test that same logger name returns same instance."""
        logger1 = get_ai_logger("singleton_test")
        logger2 = get_ai_logger("singleton_test")
        
        # Should be same instance
        assert logger1 is logger2


class TestIntegrationScenarios:
    """Test complete logging scenarios."""
    
    def test_complete_market_data_flow(self, capfd):
        """Test complete market data operation flow."""
        import logging
        from io import StringIO
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        
        # Create a string buffer to capture logs
        log_capture = StringIO()
        
        # Create a handler for our buffer with JSON formatter
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(AIOptimizedJSONFormatter("MarketDataService"))
        
        # Add handler to the root logger temporarily
        root_logger = logging.getLogger()
        original_level = root_logger.level
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        
        try:
            configure_ai_logging(log_level="DEBUG", console_output=True)
            logger = MarketDataLogger("integration_test")

            with flow_operation("BTCUSDT", "get_market_data") as flow_id:
                # Start operation
                logger.log_operation_start("get_market_data", symbol="BTCUSDT")

                # Symbol validation stage
                advance_to_stage("symbol_validation")

                # API calls stage
                advance_to_stage("data_collection")
                logger.log_api_call("BTCUSDT", "1d", 180, response_time_ms=145)

                # Technical indicators stage
                advance_to_stage("technical_indicators")
                logger.log_calculation("RSI", "BTCUSDT", result="35.17")

                # Complete operation
                advance_to_stage("completion")
                logger.log_operation_complete("get_market_data", processing_time_ms=4123)
        finally:
            # Clean up
            root_logger.removeHandler(handler)
            root_logger.setLevel(original_level)

        # Get captured output
        output = log_capture.getvalue()

        # Verify flow progression in logs
        assert "get_market_data initiated" in output
        assert "Binance API call executed" in output
        assert "RSI calculation completed" in output
        assert "get_market_data completed successfully" in output

        # Verify flow ID consistency
        assert flow_id in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])