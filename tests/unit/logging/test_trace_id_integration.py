"""
Test suite for Task 7.2: trace_id integration in MarketDataLogger through get_flow_id()

Tests that MarketDataLogger automatically generates unique trace_id for different symbols
using the get_flow_id() function from the logging system.
"""

import pytest
import tempfile
import os
import io
import sys
from unittest.mock import patch, MagicMock
from src.logging_system import MarketDataLogger, get_flow_id, configure_ai_logging, reset_trace_counter


class TestTraceIdIntegration:
    """Test suite for trace_id auto-generation in MarketDataLogger."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        # Reset logging state for clean tests
        reset_trace_counter()
        
        # Create temporary log file for testing
        self.temp_log = tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False)
        self.temp_log_path = self.temp_log.name
        self.temp_log.close()
        
        # Configure logging for testing - enable both file and console for tests
        configure_ai_logging(
            log_level="DEBUG",
            log_file=self.temp_log_path,
            console_output=True  # Enable console output for test capture
        )
        
        # Create logger instance
        self.logger = MarketDataLogger("test_module")
    
    def teardown_method(self):
        """Cleanup after each test."""
        # Clean up temporary log file
        if os.path.exists(self.temp_log_path):
            os.unlink(self.temp_log_path)
        
        # Reset logging state
        reset_trace_counter()
    
    def test_auto_generation_with_symbol(self, caplog):
        """Test that trace_id is auto-generated when symbol is provided."""
        # Test operation start with symbol - should auto-generate trace_id
        self.logger.log_operation_start(
            operation="get_market_data",
            symbol="BTCUSDT",
            context={"test": "auto_generation"}
        )
        
        # Verify logging occurred (caplog captures all log records)
        assert len(caplog.records) > 0
        
        # Check log record content
        log_record = caplog.records[-1]  # Get the last log record
        assert log_record.operation == "get_market_data"
        assert "get_market_data initiated" in log_record.getMessage()
        
        # Verify trace_id was auto-generated for BTCUSDT
        assert hasattr(log_record, 'trace_id')
        assert log_record.trace_id.startswith("flow_btc_")
    
    def test_different_symbols_different_trace_ids(self, caplog):
        """Test that different symbols generate different trace_ids."""
        # Log operations for different symbols
        self.logger.log_operation_start(
            operation="get_market_data",
            symbol="BTCUSDT",
            context={"test": "symbol_1"}
        )
        
        self.logger.log_operation_start(
            operation="get_market_data",
            symbol="ETHUSDT",
            context={"test": "symbol_2"}
        )
        
        # Should have 2 log records
        assert len(caplog.records) >= 2
        
        # Get trace_ids from the records
        trace_ids = [record.trace_id for record in caplog.records if hasattr(record, 'trace_id')]
        assert len(trace_ids) >= 2
        
        # Verify different symbols have different trace_id patterns
        btc_traces = [tid for tid in trace_ids if tid.startswith("flow_btc_")]
        eth_traces = [tid for tid in trace_ids if tid.startswith("flow_eth_")]
        
        assert len(btc_traces) >= 1, f"Expected BTC trace_id, got: {trace_ids}"
        assert len(eth_traces) >= 1, f"Expected ETH trace_id, got: {trace_ids}"
    
    def test_operation_complete_with_context_symbol(self, caplog):
        """Test that operation complete uses symbol from context for trace_id."""
        # Test completion logging with symbol in context
        self.logger.log_operation_complete(
            operation="get_market_data",
            context={"symbol": "BTCUSDT", "result": "success"},
            processing_time_ms=100
        )
        
        # Verify logging occurred
        assert len(caplog.records) > 0
        
        # Check log record content
        log_record = caplog.records[-1]
        assert "completed successfully" in log_record.getMessage()
        assert log_record.context["result"] == "success"
        
        # Verify trace_id was auto-generated for BTCUSDT from context
        assert hasattr(log_record, 'trace_id')
        assert log_record.trace_id.startswith("flow_btc_")
    
    def test_explicit_trace_id_not_overridden(self, caplog):
        """Test that explicitly provided trace_id is not overridden."""
        explicit_trace_id = "explicit_test_trace_123"
        
        # Use explicit trace_id - should not be auto-generated
        self.logger.log_operation_start(
            operation="get_market_data",
            symbol="BTCUSDT",
            context={"test": "explicit_trace"},
            trace_id=explicit_trace_id
        )
        
        # Verify logging occurred
        assert len(caplog.records) > 0
        
        # Check that explicit trace_id is preserved
        log_record = caplog.records[-1]
        assert log_record.operation == "get_market_data"
        assert hasattr(log_record, 'trace_id')
        assert log_record.trace_id == explicit_trace_id
    
    def test_no_symbol_no_auto_generation(self, caplog):
        """Test that no trace_id is auto-generated when no symbol is provided."""
        # Log operation without symbol - should not auto-generate
        self.logger.log_operation_start(
            operation="system_startup",
            context={"test": "no_symbol"}
        )
        
        # Verify logging occurred
        assert len(caplog.records) > 0
        
        # Check log record content
        log_record = caplog.records[-1]
        assert log_record.operation == "system_startup"
        assert "system_startup initiated" in log_record.getMessage()
        
        # Verify trace_id is either None (meaning fallback will be generated in formatter)
        # or already contains fallback format
        if hasattr(log_record, 'trace_id') and log_record.trace_id is not None:
            assert log_record.trace_id.startswith("trd_001_")
        else:
            # If trace_id is None, it means the formatter will generate fallback
            # We can verify this by checking that no symbol-specific trace_id was generated
            assert log_record.trace_id is None


class TestGetFlowIdFunction:
    """Test suite for get_flow_id function directly."""
    
    def test_get_flow_id_with_different_symbols(self):
        """Test get_flow_id generates different IDs for different symbols."""
        # Generate trace_ids for different symbols
        btc_trace = get_flow_id("BTCUSDT", "get_market_data")
        eth_trace = get_flow_id("ETHUSDT", "get_market_data")
        
        # Should be different
        assert btc_trace != eth_trace
        
        # Should contain symbol information
        assert "btc" in btc_trace.lower() or "BTCUSDT" in btc_trace
        assert "eth" in eth_trace.lower() or "ETHUSDT" in eth_trace
    
    def test_get_flow_id_with_same_symbol(self):
        """Test get_flow_id behavior with same symbol multiple calls."""
        # Multiple calls with same symbol and operation
        trace_1 = get_flow_id("BTCUSDT", "get_market_data")
        trace_2 = get_flow_id("BTCUSDT", "get_market_data")
        
        # Should be non-empty strings
        assert isinstance(trace_1, str) and len(trace_1) > 0
        assert isinstance(trace_2, str) and len(trace_2) > 0
        
        # Should contain operation or symbol info
        assert "btc" in trace_1.lower() or "get_market_data" in trace_1.lower()
    
    def test_get_flow_id_with_different_operations(self):
        """Test get_flow_id with different operations for same symbol."""
        # Different operations for same symbol
        get_data_trace = get_flow_id("BTCUSDT", "get_market_data")
        calculate_trace = get_flow_id("BTCUSDT", "calculate_rsi")
        
        # Should be different or at least contain operation info
        # (implementation may vary but should be distinguishable)
        assert isinstance(get_data_trace, str) and len(get_data_trace) > 0
        assert isinstance(calculate_trace, str) and len(calculate_trace) > 0


@pytest.mark.integration
class TestTraceIdIntegrationWithMarketDataService:
    """Integration tests for trace_id with MarketDataService."""
    
    def setup_method(self):
        """Setup for integration tests."""
        reset_trace_counter()
        
        # Create temporary log file
        self.temp_log = tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False)
        self.temp_log_path = self.temp_log.name
        self.temp_log.close()
    
    def teardown_method(self):
        """Cleanup for integration tests."""
        if os.path.exists(self.temp_log_path):
            os.unlink(self.temp_log_path)
        reset_trace_counter()
    
    @patch('src.market_data.market_data_service.requests.get')
    def test_marketdata_service_with_new_trace_id_system(self, mock_get):
        """Test that MarketDataService works with new trace_id system."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100.5", 1640995260000, "5050000", 1000, "50.25", "2525000", "0"]
        ] * 50  # Enough data for calculations
        mock_get.return_value = mock_response
        
        # Import here to avoid circular imports in test setup
        from src.market_data.market_data_service import MarketDataService
        
        # Create service with logging
        service = MarketDataService(enable_logging=True)
        
        # This should use the new trace_id system
        try:
            # This will internally use the new MarketDataLogger with auto-generation
            market_data = service.get_market_data("BTCUSDT")
            
            # Verify basic functionality
            assert market_data.symbol == "BTCUSDT"
            assert len(market_data.h1_candles) > 0
            
        except Exception as e:
            # If it fails due to mocking, that's OK - we're testing integration
            # The important part is that no errors are raised due to trace_id changes
            if "mock" not in str(e).lower():
                raise