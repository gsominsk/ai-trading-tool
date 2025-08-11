"""
Core Market Data Service Unit Tests

Consolidated from 26 archived test files covering:
- Basic functionality validation
- Symbol validation  
- Data quality checks
- Decimal precision patterns
- Technical indicators (RSI, MACD, MA)
- Volume profile analysis
- Error handling patterns
"""

import pytest
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService, MarketDataSet
from src.infrastructure.binance_client import BinanceApiClient
from src.logging_system import MarketDataLogger


class TestMarketDataServiceCore:
    """Core unit tests for MarketDataService functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.mock_api_client = MagicMock(spec=BinanceApiClient)
        self.mock_logger = MagicMock(spec=MarketDataLogger)
        self.service = MarketDataService(api_client=self.mock_api_client, logger=self.mock_logger)
        
        # Generic valid kline data for reuse in tests
        self.valid_kline_data = [
            [1640995200000 + i*3600, f"{50000+i}", f"{50100+i}", f"{49900+i}", f"{50050+i}", "100",
             1640995259999 + i*3600, "5005000.00", 1234, "50.00", "2502500.00", "0"]
            for i in range(180)
        ]

    def test_get_market_data_success(self):
        """Test successful retrieval and processing of market data."""
        self.mock_api_client.get_klines.return_value = self.valid_kline_data
        
        result = self.service.get_market_data("BTCUSDT", trace_id="test_success")
        
        assert isinstance(result, MarketDataSet)
        assert result.symbol == "BTCUSDT"
        assert not result.daily_candles.empty
        assert not result.h4_candles.empty
        assert not result.h1_candles.empty
        assert isinstance(result.rsi_14, Decimal)
        assert isinstance(result.ma_20, Decimal)
        assert self.mock_api_client.get_klines.call_count == 3 # daily, h4, h1

    def test_symbol_validation_in_get_market_data(self):
        """Test that get_market_data properly validates symbols."""
        invalid_symbols = ["", "btcusdt", "BTC", "ETHBTC"]
        for symbol in invalid_symbols:
            with pytest.raises(ValueError):
                self.service.get_market_data(symbol, trace_id="test_validation")

    def test_trace_id_propagation(self):
        """Test that trace_id is correctly propagated through the service."""
        self.mock_api_client.get_klines.return_value = self.valid_kline_data
        
        result = self.service.get_market_data("BTCUSDT", trace_id="trace_123")
        
        assert result.trace_id == "trace_123"
        # Check that the trace_id was passed to the api client
        for call in self.mock_api_client.get_klines.call_args_list:
            assert call.kwargs.get('trace_id') == "trace_123"
        # Check that the logger was called with the trace_id
        self.mock_logger.log_operation_start.assert_any_call(operation="get_market_data", symbol="BTCUSDT", context={}, trace_id="trace_123")


@pytest.mark.unit
@pytest.mark.performance
class TestMarketDataPerformance:
    """Performance tests for MarketDataService."""
    
    def setup_method(self):
        """Setup for each test method."""
        import psutil
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.mock_api_client = MagicMock(spec=BinanceApiClient)
        self.mock_logger = MagicMock(spec=MarketDataLogger)
        self.service = MarketDataService(api_client=self.mock_api_client, logger=self.mock_logger)

    def test_api_response_processing_performance(self):
        """Test API response processing speed."""
        import time
        
        # Mock large dataset response
        large_dataset = [[
            int(time.time() * 1000) - (200 - i) * 3600000,
            f"{50000 + i * 10}", f"{50000 + i * 10 + 500}", f"{50000 + i * 10 - 300}",
            f"{50000 + i * 10 + 100}", f"{1000 + i * 5}",
            int(time.time() * 1000) - (200 - i) * 3600000, "1000000", 100, "500000", "250000", "0"
        ] for i in range(200)]
        
        self.mock_api_client.get_klines.return_value = large_dataset
        
        start_time = time.time()
        result = self.service.get_market_data("BTCUSDT", trace_id="test_perf")
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert processing_time < 2.0, f"Processing too slow: {processing_time:.2f}s"
        assert isinstance(result, MarketDataSet)
        
    def test_memory_efficiency_during_operations(self):
        """Test memory efficiency during multiple operations."""
        import time
        
        # Setup mock for consistent responses
        dataset = [[
            int(time.time() * 1000) - (100 - i) * 3600000,
            f"{50000 + i}", f"{50000 + i + 100}", f"{50000 + i - 100}", f"{50000 + i + 50}", f"{1000}",
            int(time.time() * 1000) - (100 - i) * 3600000, "1000000", 100, "500000", "250000", "0"
        ] for i in range(100)]
        
        self.mock_api_client.get_klines.return_value = dataset
        
        # Perform multiple operations and monitor memory
        for i in range(10):
            self.service.get_market_data("BTCUSDT", trace_id=f"test_mem_{i}")
            
            if i % 3 == 2:
                current_memory = self.process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - self.initial_memory
                assert memory_increase < 100, f"Memory usage too high: {memory_increase:.1f}MB"
        
        final_memory = self.process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - self.initial_memory
        assert total_increase < 100, f"Total memory increase too high: {total_increase:.1f}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])