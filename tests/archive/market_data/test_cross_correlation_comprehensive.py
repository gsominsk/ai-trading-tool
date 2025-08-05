"""
Comprehensive Cross-Correlation Analysis Tests for MarketDataService
Tests BTC correlation calculation functionality that is critical for trading decisions.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, call
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.market_data.market_data_service import MarketDataService


class TestCrossCorrelationAnalysisComprehensive:
    """Comprehensive test suite for BTC correlation analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MarketDataService()
        
    def _generate_correlated_data(self, btc_prices: List[float], correlation: float, 
                                 noise_level: float = 0.1) -> List[float]:
        """Generate price data with specified correlation to BTC prices."""
        import random
        import math
        
        # Set seed for reproducible tests
        random.seed(42)
        
        correlated_prices = []
        base_price = 100.0  # Starting price for test asset
        
        for i, btc_price in enumerate(btc_prices):
            if i == 0:
                correlated_prices.append(base_price)
                continue
            
            # Calculate BTC return
            btc_return = (btc_price - btc_prices[i-1]) / btc_prices[i-1]
            
            # Generate correlated return
            correlated_return = correlation * btc_return + noise_level * (random.random() - 0.5)
            
            # Calculate new price
            new_price = correlated_prices[-1] * (1 + correlated_return)
            correlated_prices.append(new_price)
        
        return correlated_prices
    
    def _create_klines_data(self, prices: List[float], start_time: datetime = None) -> List[List]:
        """Create klines data from price list."""
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=len(prices))
        
        klines = []
        for i, price in enumerate(prices):
            timestamp = int((start_time + timedelta(hours=i)).timestamp() * 1000)
            
            # Create realistic OHLC from single price
            open_price = price
            close_price = price * (1 + (i % 10 - 5) * 0.001)  # Small variations
            high_price = max(open_price, close_price) * 1.002
            low_price = min(open_price, close_price) * 0.998
            volume = 1000 + i * 10
            
            kline = [
                timestamp,                          # timestamp
                f"{open_price:.8f}",               # open
                f"{high_price:.8f}",               # high
                f"{low_price:.8f}",                # low
                f"{close_price:.8f}",              # close
                f"{volume:.8f}",                   # volume
                timestamp + 3599999,                # close_time
                f"{volume * close_price:.8f}",     # quote_asset_volume
                1000 + i,                          # number_of_trades
                f"{volume * 0.6:.8f}",             # taker_buy_base_asset_volume
                f"{volume * close_price * 0.6:.8f}", # taker_buy_quote_asset_volume
                "0"                                 # ignore
            ]
            klines.append(kline)
        
        return klines
    
    @pytest.mark.unit
    @patch('src.market_data.market_data_service.MarketDataService._get_klines')
    def test_perfect_positive_correlation(self, mock_get_klines):
        """Test correlation calculation with perfectly correlated data."""
        # Generate perfectly correlated data
        btc_prices = [50000.0 + i * 100 for i in range(50)]  # Trending up
        eth_prices = self._generate_correlated_data(btc_prices, 1.0, 0.0)  # Perfect correlation
        
        # Create mock data
        btc_klines = self._create_klines_data(btc_prices)
        eth_klines = self._create_klines_data(eth_prices)
        
        def mock_side_effect(*args, **kwargs):
            symbol = kwargs.get('symbol') or args[0] if args else 'BTCUSDT'
            mock_response = Mock()
            if symbol == 'BTCUSDT':
                mock_response = btc_klines
            else:
                mock_response = eth_klines
            return pd.DataFrame(mock_response, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
        
        mock_get_klines.side_effect = mock_side_effect
        
        # Create test DataFrame
        eth_df = pd.DataFrame(eth_klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        eth_df['close'] = pd.to_numeric(eth_df['close'])
        
        # Test correlation calculation
        correlation = self.service._calculate_btc_correlation('ETHUSDT', eth_df)
        
        # Should be very close to 1.0 (perfect positive correlation)
        assert correlation is not None, "Correlation should not be None for valid data"
        assert isinstance(correlation, Decimal), "Correlation should be Decimal type"
        assert correlation > Decimal('0.95'), f"Perfect correlation should be > 0.95, got {correlation}"
        assert correlation <= Decimal('1.0'), f"Correlation should not exceed 1.0, got {correlation}"
    
    @pytest.mark.unit
    def test_btc_correlation_returns_none_for_btc(self):
        """Test that BTC correlation returns None for BTCUSDT symbol."""
        # Create dummy DataFrame (won't be used)
        dummy_df = pd.DataFrame({
            'close': [50000.0, 50100.0, 50200.0],
            'timestamp': [1, 2, 3]
        })
        
        # Test correlation calculation for BTC itself
        correlation = self.service._calculate_btc_correlation('BTCUSDT', dummy_df)
        
        # Should return None for BTC itself
        assert correlation is None, "BTC correlation with itself should return None"
    
    @pytest.mark.unit
    @patch('src.market_data.market_data_service.MarketDataService._get_klines')
    def test_insufficient_data_handling(self, mock_get_klines):
        """Test correlation calculation with insufficient data points."""
        from src.market_data.exceptions import DataInsufficientError
        
        # Create very small datasets
        btc_prices = [50000.0, 50100.0]  # Only 2 data points
        eth_prices = [3000.0, 3010.0]
        
        btc_klines = self._create_klines_data(btc_prices)
        eth_klines = self._create_klines_data(eth_prices)
        
        def mock_side_effect(*args, **kwargs):
            symbol = kwargs.get('symbol') or args[0] if args else 'BTCUSDT'
            if symbol == 'BTCUSDT':
                mock_response = btc_klines
            else:
                mock_response = eth_klines
            return pd.DataFrame(mock_response, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
        
        mock_get_klines.side_effect = mock_side_effect
        
        # Create small test DataFrame
        small_df = pd.DataFrame(eth_klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        small_df['close'] = pd.to_numeric(small_df['close'])
        
        # Test correlation calculation with insufficient data - should raise DataInsufficientError
        with pytest.raises(DataInsufficientError) as exc_info:
            self.service._calculate_btc_correlation('ETHUSDT', small_df)
        
        # Verify error details
        error = exc_info.value
        assert "Insufficient data for BTC correlation" in str(error)
        assert error.required_periods == 10
        assert error.available_periods == 2
    
    @pytest.mark.unit
    @patch('src.market_data.market_data_service.MarketDataService._get_klines')
    def test_api_failure_handling(self, mock_get_klines):
        """Test correlation calculation when BTC data fetch fails."""
        from src.market_data.exceptions import ProcessingError
        
        # Mock API failure for BTC data
        mock_get_klines.side_effect = Exception("API connection failed")
        
        # Create test DataFrame for alt coin
        test_data = {
            'close': [3000.0 + i * 10 for i in range(20)],
            'timestamp': [i * 3600000 for i in range(20)]
        }
        test_df = pd.DataFrame(test_data)
        
        # Test correlation calculation with API failure - should raise ProcessingError
        with pytest.raises(ProcessingError) as exc_info:
            self.service._calculate_btc_correlation('ETHUSDT', test_df)
        
        # Verify error details
        error = exc_info.value
        assert "Unexpected error during BTC correlation calculation" in str(error)
        assert "API connection failed" in str(error)
    
    @pytest.mark.unit
    def test_empty_dataframe_handling(self):
        """Test correlation calculation with empty DataFrame."""
        from src.market_data.exceptions import APIConnectionError
        
        # Create empty DataFrame
        empty_df = pd.DataFrame(columns=['close', 'timestamp'])
        
        # Test correlation calculation with empty data - should raise APIConnectionError due to limit=0
        with pytest.raises(APIConnectionError) as exc_info:
            self.service._calculate_btc_correlation('ETHUSDT', empty_df)
        
        # Verify error details
        error = exc_info.value
        assert "Network request failed" in str(error)
        assert "400 Client Error" in str(error)
    
    @pytest.mark.unit
    @patch('src.market_data.market_data_service.MarketDataService._get_klines')
    def test_decimal_precision_maintained(self, mock_get_klines):
        """Test that correlation calculation maintains Decimal precision."""
        # Generate test data
        btc_prices = [50000.123456 + i * 0.001234 for i in range(20)]
        eth_prices = self._generate_correlated_data(btc_prices, 0.8, 0.05)
        
        btc_klines = self._create_klines_data(btc_prices)
        eth_klines = self._create_klines_data(eth_prices)
        
        def mock_side_effect(*args, **kwargs):
            symbol = kwargs.get('symbol') or args[0] if args else 'BTCUSDT'
            if symbol == 'BTCUSDT':
                mock_response = btc_klines
            else:
                mock_response = eth_klines
            return pd.DataFrame(mock_response, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
        
        mock_get_klines.side_effect = mock_side_effect
        
        # Create test DataFrame
        eth_df = pd.DataFrame(eth_klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        eth_df['close'] = pd.to_numeric(eth_df['close'])
        
        # Test correlation calculation
        correlation = self.service._calculate_btc_correlation('ETHUSDT', eth_df)
        
        # Verify Decimal precision
        assert isinstance(correlation, Decimal), "Correlation must be Decimal type for financial precision"
        
        # Verify precision (should have 3 decimal places as per quantize in code)
        decimal_places = str(correlation).split('.')
        if len(decimal_places) > 1:
            assert len(decimal_places[1]) <= 3, f"Correlation should have max 3 decimal places, got {correlation}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])