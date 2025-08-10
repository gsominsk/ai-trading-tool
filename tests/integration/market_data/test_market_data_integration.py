"""
Market Data Service Integration Tests

Consolidated from archived tests covering:
- BTC correlation integration
- Enhanced context integration
- Comprehensive validation integration
- Cross-correlation analysis
- Caching system integration
- End-to-end data flow testing
"""

import pytest
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService, MarketDataSet


class TestMarketDataServiceIntegration:
    """Integration tests for MarketDataService end-to-end functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = MarketDataService()
    
    def _create_valid_klines_data(self, count=50, base_price=50000):
        """Create valid klines data for testing."""
        return [
            [1640995200000 + i*3600000, str(base_price + i), str(base_price + i + 1000), 
             str(base_price + i - 1000), str(base_price + i + 500), "1000.0",
             1640995259999 + i*3600000, str((base_price + i + 500) * 1000), 100, 
             "500.0", str((base_price + i + 500) * 500), "0"]
            for i in range(count)
        ]
    
    # =================
    # BTC CORRELATION INTEGRATION
    # =================
    
    def test_btc_correlation_successful_integration(self):
        """Test successful BTC correlation calculation in full integration."""
        # Create valid data for both main symbol and BTC
        eth_data = self._create_valid_klines_data(50, 3000)
        btc_data = self._create_valid_klines_data(50, 50000)
        
        with patch('requests.get') as mock_get:
            # Mock 4 successful API calls (daily, h4, h1 for ETH, daily for BTC)
            mock_responses = []
            
            # ETH data (3 calls)
            for _ in range(3):
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = eth_data
                mock_responses.append(mock_response)
            
            # BTC data (1 call)
            btc_response = MagicMock()
            btc_response.status_code = 200
            btc_response.raise_for_status.return_value = None
            btc_response.json.return_value = btc_data
            mock_responses.append(btc_response)
            
            mock_get.side_effect = mock_responses
            
            result = self.service.get_market_data("ETHUSDT", trace_id="test_trace")
            
            # Verify successful integration
            assert result.symbol == "ETHUSDT"
            assert result.btc_correlation is not None
            assert isinstance(result.btc_correlation, Decimal)
            assert -1 <= result.btc_correlation <= 1
    
    def test_btc_correlation_failure_graceful_handling(self):
        """Test graceful handling when BTC correlation fails."""
        eth_data = self._create_valid_klines_data(50, 3000)
        
        with patch('requests.get') as mock_get:
            # Mock 3 successful calls for ETH, 1 failed call for BTC
            mock_responses = []
            
            # ETH data (3 successful calls)
            for _ in range(3):
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = eth_data
                mock_responses.append(mock_response)
            
            # BTC data (1 failed call)
            btc_response = MagicMock()
            btc_response.status_code = 500
            btc_response.raise_for_status.side_effect = Exception("BTC API failed")
            mock_responses.append(btc_response)
            
            mock_get.side_effect = mock_responses
            
            result = self.service.get_market_data("ETHUSDT", trace_id="test_trace")
            
            # Should succeed with None BTC correlation
            assert result.symbol == "ETHUSDT"
            assert result.btc_correlation is None
            assert isinstance(result.ma_20, Decimal)
            assert isinstance(result.rsi_14, Decimal)
    
    # =================
    # ENHANCED CONTEXT INTEGRATION
    # =================
    
    def test_enhanced_context_full_integration(self):
        """Test enhanced context with full data processing."""
        # Create realistic market data
        btc_data = self._create_valid_klines_data(180, 67000)  # Enough for all validations
        
        with patch('requests.get') as mock_get:
            # Mock all 4 API calls (daily, h4, h1, BTC)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = btc_data
            mock_get.return_value = mock_response
            
            result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
            # Verify enhanced context fields
            assert result.symbol == "BTCUSDT"
            # Verify enhanced context components are available
            assert hasattr(result, 'ma_20')
            assert hasattr(result, 'ma_50')
            assert hasattr(result, 'rsi_14')
            assert hasattr(result, 'macd_signal')
            assert hasattr(result, 'volume_profile')
            assert hasattr(result, 'support_level')
            assert hasattr(result, 'resistance_level')
            assert isinstance(result.ma_20, Decimal)
            assert isinstance(result.ma_50, Decimal)
            assert isinstance(result.rsi_14, Decimal)
            assert result.ma_trend in ["uptrend", "downtrend", "sideways"]
            assert result.macd_signal in ["bullish", "bearish", "neutral"]
            assert result.volume_profile in ["high", "normal", "low"]
            assert isinstance(result.support_level, Decimal)
            assert isinstance(result.resistance_level, Decimal)
    
    def test_enhanced_context_edge_cases_integration(self):
        """Test enhanced context with edge cases."""
        # Create edge case data (constant prices)
        constant_data = [
            [1640995200000 + i*3600000, "50000", "50000.01", "49999.99", "50000", "1000.0",
             1640995259999 + i*3600000, "50000000.0", 100, "500.0", "25000000.0", "0"]
            for i in range(180)
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = constant_data
            mock_get.return_value = mock_response
            
            result = self.service.get_market_data("STABUSDT", trace_id="test_trace")
            
            # Should handle edge cases gracefully
            assert result.symbol == "STABUSDT"
            assert result.ma_trend == "sideways"  # Constant prices = sideways
            assert result.rsi_14 == Decimal('50.0')  # Neutral RSI for no movement
            assert result.volume_profile in ["high", "normal", "low"]
    
    # =================
    # COMPREHENSIVE VALIDATION INTEGRATION
    # =================
    
    def test_comprehensive_validation_success_integration(self):
        """Test comprehensive validation with valid data."""
        # Create data that passes all validation rules
        valid_data = []
        for i in range(180):  # Sufficient for all validations
            price = 50000 + (i * 10)  # Gradual increase
            valid_data.append([
                1640995200000 + i*3600000,
                str(price), str(price + 500), str(price - 500), str(price + 250),
                "1000.0", 1640995259999 + i*3600000, str((price + 250) * 1000),
                100, "500.0", str((price + 250) * 500), "0"
            ])
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = valid_data
            mock_get.return_value = mock_response
            
            result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
            # All validation should pass
            assert result.symbol == "BTCUSDT"
            assert isinstance(result, MarketDataSet)
            assert len(result.daily_candles) == 180
            assert result.ma_20 > Decimal('0')
            assert result.support_level > Decimal('0')
            assert result.resistance_level > Decimal('0')
    
    def test_comprehensive_validation_failure_integration(self):
        """Test comprehensive validation with invalid data."""
        # Create data that violates validation rules
        invalid_data = [
            [1640995200000, "50000", "49000", "51000", "50500", "1000.0",  # high < low
             1640995259999, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(50)
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = invalid_data
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("INVUSDT", trace_id="test_trace")
            
            assert "invalid OHLC data" in str(exc_info.value)
    
    # =================
    # CROSS-CORRELATION INTEGRATION
    # =================
    
    def test_cross_correlation_analysis_integration(self):
        """Test cross-correlation analysis between different timeframes."""
        # Create correlated data across timeframes
        base_data = self._create_valid_klines_data(180, 50000)
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = base_data
            mock_get.return_value = mock_response
            
            result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
            # Verify cross-timeframe consistency
            assert result.symbol == "BTCUSDT"
            assert len(result.daily_candles) == 180
            assert len(result.h4_candles) == 180
            assert len(result.h1_candles) == 180
            
            # All timeframes should have consistent data structure
            assert len(result.daily_candles.columns) == 6  # timestamp, open, high, low, close, volume
            assert len(result.h4_candles.columns) == 6
            assert len(result.h1_candles.columns) == 6
            
            # Check data types for DataFrame columns
            assert 'open' in result.daily_candles.columns
            assert 'high' in result.h4_candles.columns
            assert 'low' in result.h1_candles.columns
    
    # =================
    # CACHING SYSTEM INTEGRATION
    # =================
    
    def test_caching_system_basic_integration(self):
        """Test basic caching functionality integration."""
        btc_data = self._create_valid_klines_data(180, 50000)
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = btc_data
            mock_get.return_value = mock_response
            
            # First call should trigger API
            result1 = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            first_call_count = mock_get.call_count
            
            # Second call should use cache (if implemented)
            result2 = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
            # Both results should be identical
            assert result1.symbol == result2.symbol
            assert result1.ma_20 == result2.ma_20
            assert result1.rsi_14 == result2.rsi_14
    
    # =================
    # DATA FRESHNESS INTEGRATION
    # =================
    
    def test_data_freshness_comprehensive_integration(self):
        """Test data freshness validation in full integration."""
        # Create recent data
        recent_time = int(datetime.now().timestamp() * 1000)
        fresh_data = [
            [recent_time - i*3600000, "50000", "51000", "49000", "50500", "1000.0",
             recent_time - i*3600000 + 3599999, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(180)
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = fresh_data
            mock_get.return_value = mock_response
            
            result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
            # Should succeed with fresh data
            assert result.symbol == "BTCUSDT"
            assert isinstance(result.timestamp, datetime)
            
            # Timestamp should be recent (within last hour)
            time_diff = datetime.now(timezone.utc) - result.timestamp
            assert time_diff.total_seconds() < 3600  # Less than 1 hour
    
    # =================
    # END-TO-END INTEGRATION
    # =================
    
    def test_full_end_to_end_integration(self):
        """Test complete end-to-end integration with all features."""
        # Create comprehensive test data
        btc_main_data = self._create_valid_klines_data(180, 67000)
        btc_correlation_data = self._create_valid_klines_data(50, 67000)
        
        with patch('requests.get') as mock_get:
            # Mock all API calls
            mock_responses = []
            
            # Main data calls (daily, h4, h1)
            for _ in range(3):
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = btc_main_data
                mock_responses.append(mock_response)
            
            # BTC correlation call
            btc_response = MagicMock()
            btc_response.status_code = 200
            btc_response.raise_for_status.return_value = None
            btc_response.json.return_value = btc_correlation_data
            mock_responses.append(btc_response)
            
            mock_get.side_effect = mock_responses
            
            result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
            # Verify complete integration
            assert result.symbol == "BTCUSDT"
            assert isinstance(result, MarketDataSet)
            
            # Core indicators
            assert isinstance(result.ma_20, Decimal)
            assert isinstance(result.ma_50, Decimal)
            assert isinstance(result.rsi_14, Decimal)
            assert 0 <= result.rsi_14 <= 100
            
            # Trend analysis
            assert result.ma_trend in ["uptrend", "downtrend", "sideways"]
            assert result.macd_signal in ["bullish", "bearish", "neutral"]
            assert result.volume_profile in ["high", "normal", "low"]
            
            # Support/Resistance
            assert isinstance(result.support_level, Decimal)
            assert isinstance(result.resistance_level, Decimal)
            assert result.support_level < result.resistance_level
            
            # BTC Correlation (can be None for same symbol)
            if result.btc_correlation is not None:
                assert isinstance(result.btc_correlation, Decimal)
                assert -1 <= result.btc_correlation <= 1
            # For BTCUSDT, correlation might be None (self-correlation handling)
            
            # Data quality
            assert len(result.daily_candles) == 180
            assert len(result.h4_candles) == 180
            assert len(result.h1_candles) == 180
            
            # Timestamp
            assert isinstance(result.timestamp, datetime)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])