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
import logging
from src.logging_system import MarketDataLogger, get_flow_id, configure_ai_logging, reset_trace_counter


class TestTraceIdIntegration:
    """Test suite for trace_id auto-generation in MarketDataLogger."""
    
    def teardown_method(self):
        """Cleanup after each test."""
        reset_trace_counter()

    def test_auto_generation_with_symbol(self, caplog):
        """Test that trace_id is auto-generated when symbol is provided."""
        reset_trace_counter()
        logger = MarketDataLogger("test_module")

        with caplog.at_level(logging.INFO):
            # Test operation start with symbol - should auto-generate trace_id
            logger.log_operation_start(
                operation="get_market_data",
                symbol="BTCUSDT",
                context={"test": "auto_generation"}
            )
        
        # Verify log contains expected information
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "get_market_data" in record.message
        assert hasattr(record, 'trace_id')
        assert "flow_btc" in record.trace_id  # Auto-generated trace_id for BTC symbol
        
        print(f"✓ Auto-generation test passed. Log record trace_id: {record.trace_id}")
    
    def test_different_symbols_different_trace_ids(self, caplog):
        """Test that different symbols generate different trace_ids."""
        reset_trace_counter()
        logger = MarketDataLogger("test_module")

        with caplog.at_level(logging.INFO):
            # Log operations for different symbols
            logger.log_operation_start(
                operation="get_market_data",
                symbol="BTCUSDT",
                context={"test": "symbol_1"}
            )
            
            logger.log_operation_start(
                operation="get_market_data",
                symbol="ETHUSDT",
                context={"test": "symbol_2"}
            )
        
        # Verify log contains expected information
        assert len(caplog.records) == 2
        trace_ids = [record.trace_id for record in caplog.records]
        
        # Should contain different trace_ids for different symbols
        assert any("flow_btc" in tid for tid in trace_ids)
        assert any("flow_eth" in tid for tid in trace_ids)
        assert all("get_market_data" in record.message for record in caplog.records)
        
        print(f"✓ Different symbols test passed. Log contains trace_ids: {trace_ids}")
    
    def test_operation_complete_with_context_symbol(self, caplog):
        """Test that operation complete uses symbol from context for trace_id."""
        reset_trace_counter()
        logger = MarketDataLogger("test_module")

        with caplog.at_level(logging.INFO):
            # Test completion logging with symbol in context
            logger.log_operation_complete(
                operation="get_market_data",
                context={"symbol": "BTCUSDT", "result": "success"},
                processing_time_ms=100
            )
        
        # Verify log contains expected information
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "completed successfully" in record.message
        assert hasattr(record, 'trace_id')
        assert "flow_btc" in record.trace_id  # Auto-generated from context symbol
        
        print(f"✓ Operation complete test passed. Context symbol used for trace_id: {record.trace_id}")
    
    def test_explicit_trace_id_not_overridden(self, caplog):
        """Test that explicitly provided trace_id is not overridden."""
        reset_trace_counter()
        logger = MarketDataLogger("test_module")
        explicit_trace_id = "explicit_test_trace_123"
        
        with caplog.at_level(logging.INFO):
            # Use explicit trace_id - should not be auto-generated
            logger.log_operation_start(
                operation="get_market_data",
                symbol="BTCUSDT",
                context={"test": "explicit_trace"},
                trace_id=explicit_trace_id
            )
        
        # Verify log contains expected information
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert hasattr(record, 'trace_id')
        assert record.trace_id == explicit_trace_id
        
        print(f"✓ Explicit trace_id test passed. Used explicit: {record.trace_id}")
    
    def test_no_symbol_no_auto_generation(self, caplog):
        """Test that no trace_id is auto-generated when no symbol is provided."""
        reset_trace_counter()
        logger = MarketDataLogger("test_module")

        with caplog.at_level(logging.INFO):
            # Log operation without symbol - should not auto-generate
            logger.log_operation_start(
                operation="system_startup",
                context={"test": "no_symbol"}
            )
        
        # Verify log contains expected information
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "system_startup" in record.message
        assert hasattr(record, 'trace_id')
        assert record.trace_id is not None
        assert "flow_" not in record.trace_id  # Should use fallback, not symbol-based
        assert "trd_" in record.trace_id
        
        print(f"✓ No symbol test passed. Used fallback trace_id: {record.trace_id}")


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
    
    def test_marketdata_service_pattern(self, caplog):
        """Test integration pattern similar to MarketDataService usage."""
        logger = MarketDataLogger("MarketDataService")
        
        with caplog.at_level(logging.INFO):
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
        log_records = caplog.records
        trace_ids = [record.trace_id for record in log_records]
        messages = [record.message for record in log_records]
        
        # Should contain all symbols with their respective trace_ids
        assert any("flow_btc" in tid for tid in trace_ids)
        assert any("flow_eth" in tid for tid in trace_ids)
        assert any("flow_ada" in tid for tid in trace_ids)
        
        # Should have both start and complete operations
        assert messages.count("get_market_data initiated") >= 3
        assert messages.count("get_market_data completed successfully") >= 3
        
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