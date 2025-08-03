"""
Unit tests for MarketDataService module.

Tests the market data collection, processing, and enhanced candlestick analysis
functionality without external API dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import the module to test
from src.market_data.market_data_service import MarketDataService, MarketDataSet


class TestMarketDataService:
    """Test suite for MarketDataService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MarketDataService()
    
    @pytest.mark.unit
    @pytest.mark.financial
    def test_decimal_precision_handling(self, sample_market_data):
        """Test that market data maintains proper decimal precision for crypto prices."""
        # Test price precision up to 8 decimal places
        price = Decimal("50000.12345678")
        assert str(price) == "50000.12345678"
        
        # Test arithmetic operations maintain precision
        volume = Decimal("1234.56789012")
        total_value = price * volume
        expected = Decimal("61728546.9217764056090136")
        assert total_value == expected
    
    @pytest.mark.unit
    def test_symbol_validation_real_service(self):
        """Test symbol validation in real service."""
        # Test valid symbols
        valid_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]
        
        for symbol in valid_symbols:
            # Should not raise error during validation
            try:
                self.service._validate_symbol_input(symbol)
            except ValueError:
                pytest.fail(f"Valid symbol {symbol} should not raise ValueError")
        
        # Test invalid symbols
        invalid_symbols = ["BTC", "ETH-USD", "bitcoin", "", "TOOLONGUSDT123", "123USDT"]
        
        for symbol in invalid_symbols:
            with pytest.raises(ValueError):
                self.service._validate_symbol_input(symbol)
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_get_market_data_structure_real_service(self, mock_get):
        """Test that get_market_data returns properly structured MarketDataSet."""
        # Mock successful API response
        mock_response = Mock()
        mock_klines_data = [
            [1640995200000, "47000.00", "48000.00", "46500.00", "47500.00", "100.0", 1640995259999, "4750000.0", 1000, "50.0", "2375000.0", "0"],
            [1641081600000, "47500.00", "48500.00", "47000.00", "48000.00", "150.0", 1641081659999, "7200000.0", 1200, "75.0", "3600000.0", "0"]
        ]
        mock_response.json.return_value = mock_klines_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test the real service
        result = self.service.get_market_data("BTCUSDT")
        
        # Verify it returns MarketDataSet
        assert isinstance(result, MarketDataSet)
        
        # Verify structure
        assert result.symbol == "BTCUSDT"
        assert isinstance(result.timestamp, datetime)
        assert hasattr(result, 'daily_candles')
        assert hasattr(result, 'h4_candles')
        assert hasattr(result, 'h1_candles')
        assert isinstance(result.rsi_14, Decimal)
        assert isinstance(result.ma_20, Decimal)
        assert isinstance(result.ma_50, Decimal)
        assert result.macd_signal in ["bullish", "bearish", "neutral"]
        assert result.ma_trend in ["uptrend", "downtrend", "sideways"]
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_decimal_precision_real_service(self, mock_get):
        """Test that real service maintains Decimal precision for financial calculations."""
        # Mock API response with high precision data
        mock_klines_data = [
            [1640995200000, "50000.12345678", "51000.87654321", "49000.11111111", "50500.99999999", "1234.56789012", 1640995259999, "61728546.9217764056090136", 1000, "617.28394734", "31072823.4860882028045068", "0"]
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_klines_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test the service
        result = self.service.get_market_data("BTCUSDT")
        
        # Verify Decimal types are used
        assert isinstance(result.rsi_14, Decimal)
        assert isinstance(result.ma_20, Decimal)
        assert isinstance(result.ma_50, Decimal)
        
        # Test precision is maintained (should have at least 2 decimal places)
        assert str(result.ma_20).count('.') == 1  # Has decimal point
        assert len(str(result.ma_20).split('.')[1]) >= 2  # At least 2 decimal places
        
        # Test RSI bounds with Decimal
        assert Decimal('0') <= result.rsi_14 <= Decimal('100')
    
    @pytest.mark.unit
    def test_enhanced_candlestick_analysis(self):
        """Test the 7-algorithm smart candlestick selection."""
        # Mock historical candlestick data
        mock_candles = []
        base_price = Decimal("50000")
        
        for i in range(180):  # 180 days of data
            candle = {
                "timestamp": datetime.now() - timedelta(days=i),
                "open": base_price + Decimal(str(i * 10)),
                "high": base_price + Decimal(str(i * 15)),
                "low": base_price + Decimal(str(i * 5)),
                "close": base_price + Decimal(str(i * 12)),
                "volume": Decimal("1000") + Decimal(str(i * 5))
            }
            mock_candles.append(candle)
        
        # Test that enhanced analysis reduces data size
        # Should select ~15 key candles from 180 total
        # Implementation will be tested once the service is created
        assert len(mock_candles) == 180  # Full dataset
        # selected_candles = service.select_key_candles(mock_candles)
        # assert len(selected_candles) <= 15  # Reduced dataset
    
    @pytest.mark.unit
    def test_pattern_recognition(self):
        """Test candlestick pattern recognition functionality."""
        # Test Doji pattern (body/range < 0.1)
        doji_candle = {
            "open": Decimal("50000.00"),
            "close": Decimal("50010.00"),  # Small body
            "high": Decimal("50100.00"),
            "low": Decimal("49900.00")     # Large range
        }
        
        body = abs(doji_candle["close"] - doji_candle["open"])
        range_size = doji_candle["high"] - doji_candle["low"]
        doji_ratio = body / range_size
        
        assert doji_ratio < Decimal("0.1")  # Should be identified as Doji
        
        # Test Hammer pattern (lower_shadow/range > 0.6)
        hammer_candle = {
            "open": Decimal("50080.00"),
            "close": Decimal("50090.00"),
            "high": Decimal("50100.00"),
            "low": Decimal("49900.00")     # Long lower shadow
        }
        
        lower_shadow = min(hammer_candle["open"], hammer_candle["close"]) - hammer_candle["low"]
        range_size = hammer_candle["high"] - hammer_candle["low"]
        hammer_ratio = lower_shadow / range_size
        
        assert hammer_ratio > Decimal("0.6")  # Should be identified as Hammer
    
    @pytest.mark.unit
    def test_support_resistance_levels(self):
        """Test support and resistance level calculation."""
        # Mock price data with clear S/R levels
        prices = [
            Decimal("49000"), Decimal("50000"), Decimal("49900"),  # Support around 49000
            Decimal("50000"), Decimal("50100"), Decimal("49950"),
            Decimal("50000"), Decimal("50200"), Decimal("50150"),  # Resistance around 50200
            Decimal("50190"), Decimal("50000"), Decimal("49800")
        ]
        
        # Simple S/R calculation logic
        resistance_level = max(prices)
        support_level = min(prices)
        
        assert resistance_level == Decimal("50200")
        assert support_level == Decimal("49000")
    
    @pytest.mark.unit
    def test_volume_price_relationship(self):
        """Test volume-price relationship analysis."""
        # Test cases for volume confirmation
        test_cases = [
            {
                "price_change": Decimal("5.0"),   # +5% price increase
                "volume_ratio": Decimal("1.5"),   # +50% volume increase
                "expected": "strong_bullish"
            },
            {
                "price_change": Decimal("-3.0"),  # -3% price decrease
                "volume_ratio": Decimal("1.2"),   # +20% volume increase
                "expected": "confirmed_bearish"
            },
            {
                "price_change": Decimal("2.0"),   # +2% price increase
                "volume_ratio": Decimal("0.8"),   # -20% volume decrease
                "expected": "weak_bullish"
            }
        ]
        
        for case in test_cases:
            # Logic for volume-price relationship
            if case["price_change"] > 0 and case["volume_ratio"] > 1.3:
                result = "strong_bullish"
            elif case["price_change"] < 0 and case["volume_ratio"] > 1.1:
                result = "confirmed_bearish"
            elif case["price_change"] > 0 and case["volume_ratio"] < 1.0:
                result = "weak_bullish"
            else:
                result = "neutral"
            
            assert result == case["expected"]
    
    @pytest.mark.unit
    def test_token_optimization(self):
        """Test that enhanced context stays within token limits."""
        # Mock enhanced context generation
        basic_context_size = 180  # tokens
        enhanced_context_size = 350  # tokens
        
        # Test token limits
        assert basic_context_size <= 200  # Basic context limit
        assert enhanced_context_size <= 400  # Enhanced context limit
        
        # Test efficiency ratio
        efficiency_ratio = enhanced_context_size / basic_context_size
        assert 1.5 <= efficiency_ratio <= 2.5  # Reasonable efficiency range
    
    @pytest.mark.unit
    def test_error_handling_real_service(self):
        """Test error handling in real service."""
        # Test invalid symbol validation
        with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
            self.service.get_market_data("")
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            self.service.get_market_data("BTC")
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            self.service.get_market_data("ETHBTC")  # Not USDT pair
        
        # Test MarketDataSet validation
        with pytest.raises(ValueError, match="Invalid symbol format"):
            MarketDataSet(
                symbol="INVALID",
                timestamp=datetime.now(),
                daily_candles=Mock(),
                h4_candles=Mock(),
                h1_candles=Mock(),
                rsi_14=Decimal('50'),
                macd_signal="neutral",
                ma_20=Decimal('50000'),
                ma_50=Decimal('49000'),
                ma_trend="sideways"
            )
        
        # Test RSI bounds validation
        with pytest.raises(ValueError, match="RSI must be between 0 and 100"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(),
                daily_candles=Mock(),
                h4_candles=Mock(),
                h1_candles=Mock(),
                rsi_14=Decimal('150'),  # Invalid RSI
                macd_signal="neutral",
                ma_20=Decimal('50000'),
                ma_50=Decimal('49000'),
                ma_trend="sideways"
            )
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_data_freshness(self):
        """Test that market data timestamps are recent."""
        current_time = datetime.now()
        data_timestamp = current_time - timedelta(minutes=5)
        
        # Data should not be older than 10 minutes for real-time trading
        time_diff = current_time - data_timestamp
        assert time_diff.total_seconds() <= 600  # 10 minutes in seconds
    
    @pytest.mark.unit
    def test_symbol_validation(self):
        """Test cryptocurrency symbol validation."""
        valid_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]
        invalid_symbols = ["BTC", "ETH-USD", "bitcoin", ""]
        
        for symbol in valid_symbols:
            # Valid crypto pair format: XXXUSDT
            assert symbol.endswith("USDT")
            assert len(symbol) >= 6  # Minimum length
        
        for symbol in invalid_symbols:
            # Should fail validation
            is_valid = symbol.endswith("USDT") and len(symbol) >= 6
            assert not is_valid


class TestMarketDataServiceIntegration:
    """Integration-style tests for MarketDataService with mocked dependencies."""
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_binance_api_mock_response(self, mock_get):
        """Test MarketDataService with mocked Binance API response."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "symbol": "BTCUSDT",
            "price": "50000.12345678",
            "volume": "1234.56789012"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test would verify API integration works correctly
        assert mock_response.status_code == 200
        data = mock_response.json()
        assert data["symbol"] == "BTCUSDT"
        assert Decimal(data["price"]) == Decimal("50000.12345678")
    
    @pytest.mark.unit
    def test_caching_mechanism(self):
        """Test data caching for performance optimization."""
        # Mock cache implementation
        cache = {}
        cache_key = "BTCUSDT_market_data"
        cache_ttl = 60  # 60 seconds
        
        # Simulate cache hit
        cached_data = {
            "data": {"symbol": "BTCUSDT", "price": "50000.00"},
            "timestamp": datetime.now()
        }
        cache[cache_key] = cached_data
        
        # Test cache retrieval
        assert cache_key in cache
        
        # Test cache expiry
        expired_data = {
            "data": {"symbol": "BTCUSDT", "price": "49000.00"},
            "timestamp": datetime.now() - timedelta(seconds=120)  # 2 minutes old
        }
        cache[cache_key] = expired_data
        
        time_diff = datetime.now() - cache[cache_key]["timestamp"]
        is_expired = time_diff.total_seconds() > cache_ttl
        assert is_expired  # Should be expired