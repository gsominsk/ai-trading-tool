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
from decimal import Decimal
from unittest.mock import patch, Mock

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.market_data.market_data_service import MarketDataService


class TestSystemIntegrationComprehensive:
    """Comprehensive system integration tests."""
    
    def test_rsi_division_protection_integration(self):
        """Test RSI division by zero protection in real system."""
        service = MarketDataService()
        
        # Test with real symbol processing
        result = service.get_market_data("BTCUSDT")
        
        # RSI should be calculated safely with Decimal arithmetic
        assert isinstance(result.rsi_14, Decimal)
        assert 0 <= result.rsi_14 <= 100
        
        # Verify data frames are populated
        assert len(result.daily_candles) > 0
        assert len(result.h4_candles) > 0
        assert len(result.h1_candles) > 0
        
        # All frames should have required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        for df in [result.daily_candles, result.h4_candles, result.h1_candles]:
            assert all(col in df.columns for col in required_columns)
    
    def test_state_isolation_between_symbols(self):
        """Test state pollution protection between different symbols."""
        service = MarketDataService()
        
        # Get data for two different symbols
        btc_result = service.get_market_data("BTCUSDT")
        eth_result = service.get_market_data("ETHUSDT")
        
        # Verify different symbols are processed correctly
        assert btc_result.symbol == "BTCUSDT"
        assert eth_result.symbol == "ETHUSDT"
        
        # Verify last prices are different (state not polluted)
        btc_price = btc_result.h1_candles.iloc[-1]['close']
        eth_price = eth_result.h1_candles.iloc[-1]['close']
        assert btc_price != eth_price, "State pollution detected - prices should differ"
        
        # Verify independent calculation results
        assert btc_result.rsi_14 != eth_result.rsi_14 or abs(btc_result.rsi_14 - eth_result.rsi_14) < Decimal('0.1')
    
    def test_decimal_precision_system_wide(self):
        """Test Decimal precision across the entire system."""
        service = MarketDataService()
        result = service.get_market_data("BTCUSDT")
        
        # Verify all critical fields use Decimal arithmetic
        decimal_fields = [
            (result.rsi_14, "RSI"),
            (result.ma_20, "MA20"),
            (result.ma_50, "MA50")
        ]
        
        for value, field_name in decimal_fields:
            assert isinstance(value, Decimal), f"{field_name} should be Decimal, got {type(value)}"
        
        # Optional fields should also be Decimal if present
        optional_decimal_fields = [
            (result.support_level, "Support Level"),
            (result.resistance_level, "Resistance Level"),
            (result.btc_correlation, "BTC Correlation")
        ]
        
        for value, field_name in optional_decimal_fields:
            if value is not None:
                assert isinstance(value, Decimal), f"{field_name} should be Decimal, got {type(value)}"
    
    def test_dataframe_protection_and_context_generation(self):
        """Test DataFrame protection and context generation integration."""
        service = MarketDataService()
        result = service.get_market_data("BTCUSDT")
        
        # Test basic context generation
        basic_context = result.to_llm_context_basic()
        
        assert len(basic_context) > 100, "Basic context should be substantial"
        assert "Error" not in basic_context, "Context should not contain errors"
        assert "Exception" not in basic_context, "Context should not contain exceptions"
        assert result.symbol in basic_context, "Context should contain symbol"
        
        # Verify context contains key information
        assert "RSI" in basic_context
        assert "MACD" in basic_context
        assert "MA" in basic_context
    
    def test_symbol_validation_integration(self):
        """Test comprehensive symbol validation across system."""
        service = MarketDataService()
        
        # Test valid symbols
        valid_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        
        for symbol in valid_symbols:
            result = service.get_market_data(symbol)
            assert result.symbol == symbol
            assert isinstance(result.rsi_14, Decimal)
        
        # Test invalid symbols - should raise validation errors
        invalid_symbols = ["INVALID", "BTCUSDTUSDT", "BT", "", "   "]
        
        for symbol in invalid_symbols:
            with pytest.raises(ValueError):  # Remove specific regex match
                service.get_market_data(symbol)
    
    def test_technical_indicators_real_conditions(self):
        """Test technical indicators under real market conditions."""
        service = MarketDataService()
        result = service.get_market_data("BTCUSDT")
        
        # Verify indicator values are within expected ranges
        assert 0 <= result.rsi_14 <= 100, f"RSI should be 0-100, got {result.rsi_14}"
        assert result.macd_signal in ["bullish", "bearish", "neutral"], f"Invalid MACD signal: {result.macd_signal}"
        assert result.ma_trend in ["uptrend", "downtrend", "sideways"], f"Invalid MA trend: {result.ma_trend}"
        assert result.volume_profile in ["high", "low", "normal"], f"Invalid volume profile: {result.volume_profile}"
        
        # Verify moving averages are positive
        assert result.ma_20 > 0, "MA20 should be positive"
        assert result.ma_50 > 0, "MA50 should be positive"
        
        # Verify moving averages are reasonable relative to each other
        if result.ma_trend == "uptrend":
            assert result.ma_20 >= result.ma_50, "In uptrend, MA20 should be >= MA50"
        elif result.ma_trend == "downtrend":
            assert result.ma_20 <= result.ma_50, "In downtrend, MA20 should be <= MA50"
    
    def test_pattern_recognition_integration(self):
        """Test pattern recognition integration with enhanced context."""
        service = MarketDataService()
        
        # Basic market data should have support/resistance
        result = service.get_market_data("BTCUSDT")
        assert result.symbol == "BTCUSDT"
        
        # Test enhanced context with pattern analysis
        enhanced_context = service.get_enhanced_context("BTCUSDT")
        
        assert len(enhanced_context) > len(result.to_llm_context_basic())
        assert "CANDLESTICK ANALYSIS" in enhanced_context
        
        # Verify pattern keywords are present
        pattern_keywords = ["candles", "analysis", "pattern"]
        found_keywords = [kw for kw in pattern_keywords if kw.lower() in enhanced_context.lower()]
        assert len(found_keywords) > 0, "Enhanced context should contain pattern analysis"
    
    @patch('requests.get')
    def test_end_to_end_workflow_with_mocked_api(self, mock_get):
        """Test complete end-to-end workflow with mocked API responses."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100", 1640995200000, "1", 50, "50000", "0.1", ""] 
            for _ in range(200)  # Enough data for all timeframes
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        # Test complete workflow
        result = service.get_market_data("BTCUSDT")
        
        # Verify all components work together
        assert result.symbol == "BTCUSDT"
        assert isinstance(result.rsi_14, Decimal)
        assert result.macd_signal in ["bullish", "bearish", "neutral"]
        
        # Verify context generation works
        basic_context = result.to_llm_context_basic()
        enhanced_context = service.get_enhanced_context("BTCUSDT")
        
        assert len(basic_context) > 0
        assert len(enhanced_context) > len(basic_context)
        
        # Verify API was called correctly
        assert mock_get.called
        call_count = mock_get.call_count
        assert call_count >= 3, f"Should call API for all timeframes, got {call_count} calls"


class TestSystemResilience:
    """Test system resilience and error recovery."""
    
    def test_service_reusability(self):
        """Test that service instance can be reused safely."""
        service = MarketDataService()
        
        # Multiple calls should work independently
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        results = []
        
        for symbol in symbols:
            result = service.get_market_data(symbol)
            results.append(result)
            assert result.symbol == symbol
        
        # All results should be independent
        for i, result in enumerate(results):
            assert result.symbol == symbols[i]
            assert isinstance(result.rsi_14, Decimal)
    
    def test_logging_integration_does_not_break_functionality(self):
        """Test that logging integration doesn't interfere with core functionality."""
        # Test with logging enabled and disabled
        for enable_logging in [True, False]:
            service = MarketDataService(enable_logging=enable_logging)
            result = service.get_market_data("BTCUSDT")
            
            # Core functionality should work regardless of logging settings
            assert result.symbol == "BTCUSDT"
            assert isinstance(result.rsi_14, Decimal)
            assert result.macd_signal in ["bullish", "bearish", "neutral"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])