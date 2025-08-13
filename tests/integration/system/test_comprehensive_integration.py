#!/usr/bin/env python3
"""
System Integration Tests - Comprehensive Testing Suite

This module contains comprehensive integration tests that verify the complete
system functionality after all bugfixes and improvements. Tests cover:
- RSI division protection and decimal arithmetic
- State isolation between different symbols  
- Technical indicators in real conditions
- DataFrame protection and validation
- Symbol validation across the system
- Pattern recognition integration
- End-to-end system workflows

Consolidated from: tests/test_all_fixes_comprehensive.py (261 lines)
"""

import sys
import os
import pytest
import json
from decimal import Decimal
from unittest.mock import patch, Mock, MagicMock

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.market_data.market_data_service import MarketDataService
from src.infrastructure.binance_client import BinanceApiClient
from src.logging_system import MarketDataLogger


class TestSystemIntegrationComprehensive:
    """Comprehensive system integration tests."""

    def setup_method(self):
        """Setup a mock API client and service for each test."""
        self.mock_api_client = MagicMock(spec=BinanceApiClient)
        self.mock_logger = MagicMock()
        self.service = MarketDataService(api_client=self.mock_api_client, logger=self.mock_logger)

    def _create_klines_data(self, count=50, base_price=50000, direction=1):
        """Helper to create valid klines data."""
        return [
            [1640995200000 + i*3600000, str(base_price + (i * direction)), str(base_price + (i * direction) + 100),
             str(base_price + (i * direction) - 100), str(base_price + (i * direction) + 50), "1000.0",
             1640995259999 + i*3600000, str((base_price + (i * direction) + 50) * 1000), 100,
             "500.0", str((base_price + (i * direction) + 50) * 500), "0"]
            for i in range(count)
        ]

    def test_rsi_division_protection_integration(self):
        """Test RSI division by zero protection in real system."""
        self.mock_api_client.get_klines.return_value = self._create_klines_data(100)
        result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        assert isinstance(result.rsi_14, Decimal)
        assert 0 <= result.rsi_14 <= 100
        assert len(result.daily_candles) > 0
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        assert all(col in result.daily_candles.columns for col in required_columns)

    def test_state_isolation_between_symbols(self):
        """Test state pollution protection between different symbols."""
        btc_data = self._create_klines_data(100, 50000, direction=1)  # Upward trend
        eth_data = self._create_klines_data(100, 3000, direction=-1) # Downward trend
        self.mock_api_client.get_klines.side_effect = [
            btc_data, btc_data, btc_data,  # First call for BTCUSDT
            eth_data, eth_data, eth_data,  # Second call for ETHUSDT
            btc_data                       # Correlation call for BTC data during ETH processing
        ]
    
        btc_result = self.service.get_market_data("BTCUSDT", trace_id="test_trace_btc")
        eth_result = self.service.get_market_data("ETHUSDT", trace_id="test_trace_eth")
    
        assert btc_result.symbol == "BTCUSDT"
        assert eth_result.symbol == "ETHUSDT"
        btc_price = btc_result.h1_candles.iloc[-1]['close']
        eth_price = eth_result.h1_candles.iloc[-1]['close']
        assert btc_price != eth_price, "State pollution detected"
        assert btc_result.rsi_14 != eth_result.rsi_14, "RSI values should differ for different trends"

    def test_decimal_precision_system_wide(self):
        """Test Decimal precision across the entire system."""
        self.mock_api_client.get_klines.return_value = self._create_klines_data(100)
        result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        decimal_fields = [result.rsi_14, result.ma_20, result.ma_50, result.support_level, result.resistance_level]
        for value in decimal_fields:
            assert isinstance(value, Decimal)
        if result.btc_correlation is not None:
            assert isinstance(result.btc_correlation, Decimal)

    def test_dataframe_protection_and_context_generation(self):
        """Test DataFrame protection and context generation integration."""
        self.mock_api_client.get_klines.return_value = self._create_klines_data(100)
        result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        json_context = result.to_json_context()
        assert len(json_context) > 100
        
        # Validate the JSON structure
        data = json.loads(json_context)
        assert "symbol" in data
        assert "primary_indicators" in data
        assert "raw_candles" in data
        assert "h1" in data["raw_candles"]
        assert isinstance(data["raw_candles"]["h1"], list)
        assert len(data["raw_candles"]["h1"]) > 0

    def test_symbol_validation_integration(self):
        """Test comprehensive symbol validation across system."""
        self.mock_api_client.get_klines.return_value = self._create_klines_data(100)
        
        valid_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        for symbol in valid_symbols:
            result = self.service.get_market_data(symbol, trace_id="test_trace")
            assert result.symbol == symbol
        
        from src.infrastructure.exceptions import SymbolValidationError
        invalid_symbols = ["INVALID", "BTCUSDTUSDT", "BT", "", "   "]
        for symbol in invalid_symbols:
            with pytest.raises(SymbolValidationError):
                self.service.get_market_data(symbol, trace_id="test_trace")

    def test_technical_indicators_real_conditions(self):
        """Test technical indicators under real market conditions."""
        self.mock_api_client.get_klines.return_value = self._create_klines_data(100)
        result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        assert 0 <= result.rsi_14 <= 100
        assert result.macd_signal in ["bullish", "bearish", "neutral"]
        assert result.ma_trend in ["uptrend", "downtrend", "sideways"]
        assert result.ma_20 > 0 and result.ma_50 > 0

    def test_pattern_recognition_integration(self):
        """Test pattern recognition integration with enhanced context."""
        self.mock_api_client.get_klines.return_value = self._create_klines_data(100)
        result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        enhanced_context = self.service.get_enhanced_context(result)

        assert "CANDLESTICK ANALYSIS" in enhanced_context
        assert "Recent Trend" in enhanced_context
        assert "Patterns" in enhanced_context
        assert len(enhanced_context) > 100

    def test_end_to_end_workflow_with_mocked_api(self):
        """Test complete end-to-end workflow with mocked API responses."""
        self.mock_api_client.get_klines.return_value = self._create_klines_data(200)

        result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")

        assert result.symbol == "BTCUSDT"
        assert isinstance(result.rsi_14, Decimal)
        assert result.macd_signal in ["bullish", "bearish", "neutral"]

        json_context = result.to_json_context()
        data = json.loads(json_context)
        assert data["symbol"] == "BTCUSDT"

        enhanced_context = self.service.get_enhanced_context(result)
        # Enhanced context is now a separate analysis, not a wrapper for JSON.
        # We just check that it's a meaningful string.
        assert "Enhanced Analysis" in enhanced_context
        assert len(enhanced_context) > 50

        assert self.mock_api_client.get_klines.call_count >= 3


class TestSystemResilience:
    """Test system resilience and error recovery."""

    def setup_method(self):
        """Setup a mock API client and service for each test."""
        self.mock_api_client = MagicMock(spec=BinanceApiClient)
        self.mock_logger = MagicMock()
        self.service = MarketDataService(api_client=self.mock_api_client, logger=self.mock_logger)

    def _create_klines_data(self, count=50, base_price=50000):
        """Helper to create valid klines data."""
        return [
            [1640995200000 + i*3600000, str(base_price + i), str(base_price + i + 100),
             str(base_price + i - 100), str(base_price + i + 50), "1000.0",
             1640995259999 + i*3600000, str((base_price + i + 50) * 1000), 100,
             "500.0", str((base_price + i + 50) * 500), "0"]
            for i in range(count)
        ]

    def test_service_reusability(self):
        """Test that service instance can be reused safely."""
        self.mock_api_client.get_klines.return_value = self._create_klines_data(100)
        
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        results = []
        for symbol in symbols:
            result = self.service.get_market_data(symbol, trace_id=f"test_trace_{symbol}")
            results.append(result)
            assert result.symbol == symbol
        
        for i, result in enumerate(results):
            assert result.symbol == symbols[i]
            assert isinstance(result.rsi_14, Decimal)

    def test_logging_integration_does_not_break_functionality(self):
        """Test that logging integration doesn't interfere with core functionality."""
        self.mock_api_client.get_klines.return_value = self._create_klines_data(100)
        
        # Test with logging enabled
        service_with_log = MarketDataService(api_client=self.mock_api_client, logger=self.mock_logger)
        result_with_log = service_with_log.get_market_data("BTCUSDT", trace_id="test_trace")
        assert result_with_log.symbol == "BTCUSDT"
        
        # Test with logging disabled
        service_without_log = MarketDataService(api_client=self.mock_api_client, logger=None)
        result_without_log = service_without_log.get_market_data("BTCUSDT", trace_id="test_trace")
        assert result_without_log.symbol == "BTCUSDT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])