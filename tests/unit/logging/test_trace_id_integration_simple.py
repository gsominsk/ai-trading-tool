"""
Simplified test for Task 7.2: trace_id integration in MarketDataLogger through get_flow_id()

Tests that MarketDataLogger automatically generates unique trace_id for different symbols
using the get_flow_id() function from the logging system.
"""

import pytest
import json
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
        
        # Capture stderr to test actual log output
        self.captured_logs = []
        
        # Create logger instance
        self.logger = MarketDataLogger("test_module")
    
    def teardown_method(self):
        """Cleanup after each test."""
        reset_trace_counter()
    
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_auto_generation_with_symbol(self, mock_stderr):
        """Test that trace_id is auto-generated when symbol is provided."""
        # Test operation start with symbol - should auto-generate trace_id
        self.logger.log_operation_start(
            operation="get_market_data",
            symbol="BTCUSDT",
            context={"test": "auto_generation"}
        )
        
        # Get captured log output
        log_output = mock_stderr.getvalue()
        
        # Verify log contains expected information
        assert "get_market_data" in log_output
        assert "flow_btc" in log_output  # Auto-generated trace_id for BTC symbol
        
        print(f"✓ Auto-generation test passed. Log output: {log_output.strip()}")
    
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_different_symbols_different_trace_ids(self, mock_stderr):
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
        
        # Get captured log output
        log_output = mock_stderr.getvalue()
        
        # Should contain different trace_ids for different symbols
        assert "flow_btc" in log_output
        assert "flow_eth" in log_output
        assert log_output.count("get_market_data") >= 2
        
        print(f"✓ Different symbols test passed. Log contains both flow_btc and flow_eth")
    
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_operation_complete_with_context_symbol(self, mock_stderr):
        """Test that operation complete uses symbol from context for trace_id."""
        # Test completion logging with symbol in context
        self.logger.log_operation_complete(
            operation="get_market_data",
            context={"symbol": "BTCUSDT", "result": "success"},
            processing_time_ms=100
        )
        
        # Get captured log output
        log_output = mock_stderr.getvalue()
        
        # Should contain completion information and auto-generated trace_id
        assert "completed successfully" in log_output
        assert "flow_btc" in log_output  # Auto-generated from context symbol
        
        print(f"✓ Operation complete test passed. Context symbol used for trace_id")
    
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_explicit_trace_id_not_overridden(self, mock_stderr):
        """Test that explicitly provided trace_id is not overridden."""
        explicit_trace_id = "explicit_test_trace_123"
        
        # Use explicit trace_id - should not be auto-generated
        self.logger.log_operation_start(
            operation="get_market_data",
            symbol="BTCUSDT",
            context={"test": "explicit_trace"},
            trace_id=explicit_trace_id
        )
        
        # Get captured log output
        log_output = mock_stderr.getvalue()
        
        # Should contain explicit trace_id, not auto-generated one
        assert explicit_trace_id in log_output
        assert "flow_btc" not in log_output  # Should NOT auto-generate when explicit provided
        
        print(f"✓ Explicit trace_id test passed. Used explicit: {explicit_trace_id}")
    
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_no_symbol_no_auto_generation(self, mock_stderr):
        """Test that no trace_id is auto-generated when no symbol is provided."""
        # Log operation without symbol - should not auto-generate
        self.logger.log_operation_start(
            operation="system_startup",
            context={"test": "no_symbol"}
        )
        
        # Get captured log output
        log_output = mock_stderr.getvalue()
        
        # Should contain operation but use fallback trace_id (not symbol-based)
        assert "system_startup" in log_output
        assert "flow_" not in log_output or "trd_" in log_output  # Should use fallback, not symbol-based
        
        print(f"✓ No symbol test passed. Used fallback trace_id")


class TestGetFlowIdFunction:
    """Test suite for get_flow_id function directly."""
    
    def setup_method(self):
        """Setup for get_flow_id tests."""
        reset_trace_counter()
    
    def teardown_method(self):
        """Cleanup for get_flow_id tests."""
        reset_trace_counter()
    
    def test_get_flow_id_with_different_symbols(self):
        """Test that get_flow_id generates different IDs for different symbols."""
        btc_id = get_flow_id("BTCUSDT", "get_market_data")
        eth_id = get_flow_id("ETHUSDT", "get_market_data")
        
        # Should be different IDs
        assert btc_id != eth_id
        assert "btc" in btc_id.lower()
        assert "eth" in eth_id.lower()
        
        print(f"✓ Different symbols generate different IDs: {btc_id} vs {eth_id}")
    
    def test_get_flow_id_with_same_symbol(self):
        """Test that get_flow_id generates same pattern for same symbol."""
        id1 = get_flow_id("BTCUSDT", "get_market_data")
        id2 = get_flow_id("BTCUSDT", "get_klines")
        
        # Should have same symbol pattern but different timestamps/operations
        assert "btc" in id1.lower()
        assert "btc" in id2.lower()
        
        print(f"✓ Same symbol generates consistent pattern: {id1}, {id2}")
    
    def test_get_flow_id_with_different_operations(self):
        """Test that get_flow_id works with different operations."""
        market_data_id = get_flow_id("BTCUSDT", "get_market_data")
        klines_id = get_flow_id("BTCUSDT", "get_klines")
        
        # Both should contain symbol pattern
        assert "btc" in market_data_id.lower()
        assert "btc" in klines_id.lower()
        
        print(f"✓ Different operations work: {market_data_id}, {klines_id}")


class TestTraceIdIntegrationWithMarketDataService:
    """Integration test with MarketDataService patterns."""
    
    def setup_method(self):
        """Setup for integration tests."""
        reset_trace_counter()
    
    def teardown_method(self):
        """Cleanup for integration tests."""
        reset_trace_counter()
    
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_marketdata_service_pattern(self, mock_stderr):
        """Test integration pattern similar to MarketDataService usage."""
        logger = MarketDataLogger("MarketDataService")
        
        # Simulate market data service operations
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        
        for symbol in symbols:
            # Start operation with symbol
            logger.log_operation_start(
                operation="get_market_data",
                symbol=symbol,
                context={"exchange": "binance", "timeframe": "1m"}
            )
            
            # Complete operation with context symbol
            logger.log_operation_complete(
                operation="get_market_data",
                context={
                    "symbol": symbol,
                    "result": "success",
                    "data_points": 100
                },
                processing_time_ms=150
            )
        
        # Get captured log output
        log_output = mock_stderr.getvalue()
        
        # Should contain all symbols with their respective trace_ids
        assert "flow_btc" in log_output
        assert "flow_eth" in log_output
        assert "flow_ada" in log_output
        
        # Should have both start and complete operations
        assert log_output.count("initiated") >= 3
        assert log_output.count("completed successfully") >= 3
        
        print(f"✓ MarketDataService integration test passed for {len(symbols)} symbols")


if __name__ == "__main__":
    # Quick test runner
    import sys
    
    print("Running trace_id integration tests...")
    
    # Test direct function
    test_func = TestGetFlowIdFunction()
    test_func.setup_method()
    test_func.test_get_flow_id_with_different_symbols()
    test_func.test_get_flow_id_with_same_symbol()
    test_func.test_get_flow_id_with_different_operations()
    test_func.teardown_method()
    
    print("\n✅ All trace_id integration tests completed successfully!")