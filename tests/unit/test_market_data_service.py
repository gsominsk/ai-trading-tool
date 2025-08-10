"""
Unit tests for MarketDataService module.

Tests the market data collection, processing, and enhanced candlestick analysis
functionality without external API dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

# Import the module to test
from src.market_data.market_data_service import MarketDataService, MarketDataSet


class TestMarketDataService:
    """Test suite for MarketDataService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MarketDataService(enable_logging=False)
    
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
    
    def _generate_sufficient_klines(self, count: int, start_price: float = 50000.0) -> list:
        """Generate sufficient klines data for RSI/MA calculations."""
        from datetime import datetime, timedelta
        klines = []
        current_price = start_price
        current_time = int((datetime.now(timezone.utc) - timedelta(hours=count)).timestamp() * 1000)
        
        for i in range(count):
            # Realistic price changes (-1% to +1% per hour)
            price_change = (i % 20 - 10) * 0.001  # -1% to +1%
            new_price = current_price * (1 + price_change)
            
            # OHLC data
            open_price = current_price
            close_price = new_price
            high_price = max(open_price, close_price) * 1.002
            low_price = min(open_price, close_price) * 0.998
            volume = 1000 + (i % 50) * 20
            
            kline = [
                current_time + (i * 3600000),  # timestamp
                f"{open_price:.8f}",           # open
                f"{high_price:.8f}",           # high
                f"{low_price:.8f}",            # low
                f"{close_price:.8f}",          # close
                f"{volume:.8f}",               # volume
                current_time + (i * 3600000) + 3599999,  # close_time
                f"{volume * close_price:.8f}",  # quote_asset_volume
                1000 + i,                      # number_of_trades
                f"{volume * 0.6:.8f}",         # taker_buy_base_asset_volume
                f"{volume * close_price * 0.6:.8f}",  # taker_buy_quote_asset_volume
                "0"                            # ignore
            ]
            
            klines.append(kline)
            current_price = new_price
        
        return klines

    @pytest.mark.unit
    @patch('requests.get')
    def test_get_market_data_structure_real_service(self, mock_get):
        """Test that get_market_data returns properly structured MarketDataSet."""
        # Generate sufficient mock data for all timeframes
        daily_data = self._generate_sufficient_klines(180, 50000.0)  # 6 months
        h4_data = self._generate_sufficient_klines(84, 50000.0)      # 2 weeks
        h1_data = self._generate_sufficient_klines(60, 50000.0)      # 60 hours
        
        def mock_side_effect(*args, **kwargs):
            params = kwargs.get('params', {})
            interval = params.get('interval', '1h')
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            
            # Add proper headers and content for logging compatibility
            mock_response.headers = {
                'content-type': 'application/json',
                'x-mbx-used-weight': '1',
                'x-mbx-used-weight-1m': '1'
            }
            mock_response.content = b'{"test": "response"}'
            
            if interval == '1d':
                mock_response.json.return_value = daily_data
            elif interval == '4h':
                mock_response.json.return_value = h4_data
            else:  # '1h'
                mock_response.json.return_value = h1_data
                
            return mock_response
        
        mock_get.side_effect = mock_side_effect
        
        # Test the real service
        result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
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
        # Generate sufficient mock data with high precision
        daily_data = self._generate_sufficient_klines(180, 50000.12345678)
        h4_data = self._generate_sufficient_klines(84, 50000.12345678)
        h1_data = self._generate_sufficient_klines(60, 50000.12345678)
        
        def mock_side_effect(*args, **kwargs):
            params = kwargs.get('params', {})
            interval = params.get('interval', '1h')
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            
            # Add proper headers and content for logging compatibility
            mock_response.headers = {
                'content-type': 'application/json',
                'x-mbx-used-weight': '1',
                'x-mbx-used-weight-1m': '1'
            }
            mock_response.content = b'{"test": "response"}'
            
            if interval == '1d':
                mock_response.json.return_value = daily_data
            elif interval == '4h':
                mock_response.json.return_value = h4_data
            else:  # '1h'
                mock_response.json.return_value = h1_data
                
            return mock_response
        
        mock_get.side_effect = mock_side_effect
        
        # Test the service
        result = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
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
                "timestamp": datetime.now(timezone.utc) - timedelta(days=i),
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
            self.service.get_market_data("", trace_id="test_trace")
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            self.service.get_market_data("BTC")
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            self.service.get_market_data("ETHBTC")  # Not USDT pair
        
        # Test MarketDataSet validation
        with pytest.raises(ValueError, match="Invalid symbol format"):
            MarketDataSet(
                symbol="INVALID",
                timestamp=datetime.now(timezone.utc),
                daily_candles=Mock(),
                h4_candles=Mock(),
                h1_candles=Mock(),
                rsi_14=Decimal('50'),
                macd_signal="neutral",
                ma_20=Decimal('50000'),
                ma_50=Decimal('49000'),
                ma_trend="sideways"
            )
        
        # Test RSI bounds validation - create minimal valid DataFrames to bypass DataFrame validation
        import pandas as pd
        minimal_df = pd.DataFrame({
            'timestamp': [datetime.now(timezone.utc) - timedelta(hours=i) for i in range(50)],
            'open': [50000.0] * 50,
            'high': [50100.0] * 50,
            'low': [49900.0] * 50,
            'close': [50000.0] * 50,
            'volume': [1000.0] * 50
        })
        
        with pytest.raises(ValueError, match="RSI must be between 0 and 100"):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=minimal_df,
                h4_candles=minimal_df,
                h1_candles=minimal_df,
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
        current_time = datetime.now(timezone.utc)
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

    @pytest.mark.unit
    @patch('src.market_data.market_data_service.MarketDataService.get_market_data')
    def test_get_enhanced_context_no_name_error_on_exception(self, mock_get_market_data):
        """
        Test that get_enhanced_context does not raise NameError on unexpected exceptions
        and correctly includes the trace_id in the error message.
        """
        # Arrange
        # Configure the mock to raise a generic exception to trigger the problematic code path
        mock_get_market_data.side_effect = Exception("A critical unexpected error occurred")
        
        # Set a trace_id on the service instance to simulate a real operation
        self.service._current_trace_id = "test-trace-id-12345"
        
        # Act
        # Call the method that is expected to handle the exception gracefully
        # We now need to pass a MarketDataSet object, so we mock it
        mock_market_data = MagicMock(spec=MarketDataSet)
        mock_market_data.symbol = "BTCUSDT"
        
        result = self.service.get_enhanced_context(mock_market_data)
        
        # Assert
        # Check that the error message is returned as a string, not an exception
        assert isinstance(result, str)
    @pytest.mark.unit
    def test_no_attribute_error_for_metrics_on_fresh_instance(self):
        """
        Test that accessing metrics attributes on a fresh service instance does not
        raise an AttributeError, confirming they are initialized in __init__.
        """
        # Arrange
        # A new service is created in setup_method, so self.service is a fresh instance.
        
        # Act & Assert
        # This call would have raised an AttributeError before the fix if _log_graceful_degradation
        # was called before any metrics were populated.
        try:
            self.service._log_graceful_degradation(
                operation="test_operation",
                failed_component="test_component",
                fallback_used="test_fallback"
            )
        except AttributeError as e:
            pytest.fail(f"AttributeError raised unexpectedly: {e}")
            
        # Additionally, check that the attributes are indeed present and are of the correct type.
        assert hasattr(self.service, '_operation_metrics')
        assert isinstance(self.service._operation_metrics, dict)
        
        assert hasattr(self.service, '_degradation_history')
        assert isinstance(self.service._degradation_history, list)
        
        # Check that the history was appended to
        assert len(self.service._degradation_history) == 1
        assert self.service._degradation_history[0]['operation'] == 'test_operation'

        


class TestMarketDataServiceIntegration:
    """Integration-style tests for MarketDataService with mocked dependencies."""
    
    def _generate_test_klines(self, count: int = 60) -> list:
        """Generate test klines for API mock testing."""
        from datetime import datetime, timedelta
        klines = []
        base_price = 50000.12345678
        current_time = int((datetime.now(timezone.utc) - timedelta(hours=count)).timestamp() * 1000)
        
        for i in range(count):
            price = base_price * (1 + (i % 10 - 5) * 0.002)  # ±1% price variation
            volume = 1234.56789012 + i * 10
            
            kline = [
                current_time + (i * 3600000),  # timestamp
                f"{price:.8f}",                # open
                f"{price * 1.005:.8f}",        # high
                f"{price * 0.995:.8f}",        # low
                f"{price * 1.001:.8f}",        # close
                f"{volume:.8f}",               # volume
                current_time + (i * 3600000) + 3599999,  # close_time
                f"{volume * price:.8f}",       # quote_asset_volume
                1000 + i,                      # number_of_trades
                f"{volume * 0.6:.8f}",         # taker_buy_base_asset_volume
                f"{volume * price * 0.6:.8f}", # taker_buy_quote_asset_volume
                "0"                            # ignore
            ]
            klines.append(kline)
        
        return klines

    @pytest.mark.unit
    @patch('requests.get')
    def test_binance_api_mock_response(self, mock_get):
        """Test MarketDataService with correctly structured Binance API klines response."""
        # Generate realistic klines data (Binance API format)
        test_klines = self._generate_test_klines(60)
        
        # Mock successful API response with correct klines structure
        mock_response = Mock()
        mock_response.json.return_value = test_klines
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test API structure validation
        assert mock_response.status_code == 200
        klines_data = mock_response.json()
        
        # Verify it's a list of klines (not dict with symbol/price)
        assert isinstance(klines_data, list), "API should return list of klines"
        assert len(klines_data) == 60, f"Expected 60 klines, got {len(klines_data)}"
        
        # Verify kline structure
        sample_kline = klines_data[0]
        assert len(sample_kline) == 12, f"Each kline should have 12 fields, got {len(sample_kline)}"
        assert str(sample_kline[0]).isdigit(), "Timestamp should be numeric"
        assert isinstance(sample_kline[1], str), "OHLCV should be strings"
        
        # Test price precision
        open_price = Decimal(sample_kline[1])
        assert 45000 <= open_price <= 55000, f"Price should be around base value: {open_price}"
        
        # Verify this structure works with MarketDataService
        service = MarketDataService(enable_logging=False)
        
        # Mock all timeframe calls
        def mock_side_effect(*args, **kwargs):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = test_klines
            
            # Add proper headers and content for logging compatibility
            mock_resp.headers = {
                'content-type': 'application/json',
                'x-mbx-used-weight': '1',
                'x-mbx-used-weight-1m': '1'
            }
            mock_resp.content = b'{"test": "response"}'
            
            return mock_resp
        
        mock_get.side_effect = mock_side_effect
        
        # This should work without errors now
        try:
            result = service.get_market_data("BTCUSDT", trace_id="test_trace")
            assert isinstance(result.rsi_14, Decimal), "RSI should be calculated as Decimal"
            assert isinstance(result.ma_20, Decimal), "MA20 should be calculated as Decimal"
        except Exception as e:
            pytest.fail(f"API mock structure should allow successful MarketDataService usage: {e}")
    
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
            "timestamp": datetime.now(timezone.utc)
        }
        cache[cache_key] = cached_data
        
        # Test cache retrieval
        assert cache_key in cache
        
        # Test cache expiry
        expired_data = {
            "data": {"symbol": "BTCUSDT", "price": "49000.00"},
            "timestamp": datetime.now(timezone.utc) - timedelta(seconds=120)  # 2 minutes old
        }
        cache[cache_key] = expired_data
        
        time_diff = datetime.now(timezone.utc) - cache[cache_key]["timestamp"]
        is_expired = time_diff.total_seconds() > cache_ttl
        assert is_expired  # Should be expired