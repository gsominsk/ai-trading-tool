"""
Test for real BTC correlation calculation (no more hardcoded mock values).
Verifies that correlation is calculated using actual market data.
"""

import pytest
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService


class TestBTCCorrelationReal:
    """Test real BTC correlation calculation implementation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.service = MarketDataService()
    
    def _create_mock_klines_data(self, symbol, prices):
        """Create mock klines data for testing."""
        data = []
        for i, price in enumerate(prices):
            data.append({
                'timestamp': datetime.utcnow() - timedelta(hours=len(prices)-i),
                'open': price,
                'high': price + 1,
                'low': price - 1,
                'close': price,
                'volume': 1000 + i
            })
        return pd.DataFrame(data)
    
    def test_btc_correlation_for_btc_itself(self):
        """Test that BTC correlation returns None for BTCUSDT symbol."""
        df = self._create_mock_klines_data("BTCUSDT", [100, 101, 102, 103, 104])
        correlation = self.service._calculate_btc_correlation("BTCUSDT", df)
        assert correlation is None
    
    @patch.object(MarketDataService, '_get_klines')
    def test_btc_correlation_perfect_positive(self, mock_get_klines):
        """Test BTC correlation with perfect positive correlation."""
        # Create identical price movements (need 10+ points for correlation)
        eth_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
        btc_prices = [50000, 50500, 51000, 51500, 52000, 52500, 53000, 53500, 54000, 54500, 55000, 55500]
        
        eth_df = self._create_mock_klines_data("ETHUSDT", eth_prices)
        btc_df = self._create_mock_klines_data("BTCUSDT", btc_prices)
        
        mock_get_klines.return_value = btc_df
        
        correlation = self.service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        assert correlation is not None
        assert isinstance(correlation, Decimal)
        assert correlation == Decimal('1.000')  # Perfect positive correlation
        mock_get_klines.assert_called_once_with("BTCUSDT", "1h", len(eth_df))
    
    @patch.object(MarketDataService, '_get_klines')
    def test_btc_correlation_perfect_negative(self, mock_get_klines):
        """Test BTC correlation with perfect negative correlation."""
        # Create opposite price movements (need 10+ points for correlation)
        eth_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
        btc_prices = [55500, 55000, 54500, 54000, 53500, 53000, 52500, 52000, 51500, 51000, 50500, 50000]
        
        eth_df = self._create_mock_klines_data("ETHUSDT", eth_prices)
        btc_df = self._create_mock_klines_data("BTCUSDT", btc_prices)
        
        mock_get_klines.return_value = btc_df
        
        correlation = self.service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        assert correlation is not None
        assert isinstance(correlation, Decimal)
        assert correlation == Decimal('-1.000')  # Perfect negative correlation
    
    @patch.object(MarketDataService, '_get_klines')
    def test_btc_correlation_no_correlation(self, mock_get_klines):
        """Test BTC correlation with no correlation (random data)."""
        # Create random price movements (need 10+ points for correlation)
        eth_prices = [100, 102, 101, 103, 99, 105, 98, 104, 97, 106, 101, 102]
        btc_prices = [50000, 49500, 51000, 50200, 50800, 49800, 51200, 50300, 50900, 49600, 51100, 50400]
        
        eth_df = self._create_mock_klines_data("ETHUSDT", eth_prices)
        btc_df = self._create_mock_klines_data("BTCUSDT", btc_prices)
        
        mock_get_klines.return_value = btc_df
        
        correlation = self.service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        assert correlation is not None
        assert isinstance(correlation, Decimal)
        assert -Decimal('1.0') <= correlation <= Decimal('1.0')  # Valid correlation range
    
    @patch.object(MarketDataService, '_get_klines')
    def test_btc_correlation_insufficient_data(self, mock_get_klines):
        """Test BTC correlation with insufficient data points."""
        # Create very small datasets
        eth_prices = [100, 101]  # Only 2 data points
        btc_prices = [50000, 50500]
        
        eth_df = self._create_mock_klines_data("ETHUSDT", eth_prices)
        btc_df = self._create_mock_klines_data("BTCUSDT", btc_prices)
        
        mock_get_klines.return_value = btc_df
        
        correlation = self.service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        assert correlation is None  # Should return None for insufficient data
    
    @patch.object(MarketDataService, '_get_klines')
    def test_btc_correlation_constant_prices(self, mock_get_klines):
        """Test BTC correlation with constant prices (NaN correlation)."""
        # Create constant prices (no variance, need 10+ points)
        eth_prices = [100] * 12
        btc_prices = [50000] * 12
        
        eth_df = self._create_mock_klines_data("ETHUSDT", eth_prices)
        btc_df = self._create_mock_klines_data("BTCUSDT", btc_prices)
        
        mock_get_klines.return_value = btc_df
        
        correlation = self.service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        assert correlation == Decimal('0.0')  # Should handle NaN correlation gracefully
    
    @patch.object(MarketDataService, '_get_klines')
    def test_btc_correlation_api_failure(self, mock_get_klines):
        """Test BTC correlation when BTC data fetch fails."""
        eth_df = self._create_mock_klines_data("ETHUSDT", [100, 101, 102, 103, 104])
        
        # Mock API failure
        mock_get_klines.side_effect = Exception("API connection failed")
        
        correlation = self.service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        assert correlation is None  # Should return None on API failure
    
    @patch.object(MarketDataService, '_get_klines')
    def test_btc_correlation_mismatched_data_lengths(self, mock_get_klines):
        """Test BTC correlation with different data lengths."""
        # Create datasets with different lengths (both > 10)
        eth_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
        btc_prices = [50000, 50500, 51000, 51500, 52000, 52500, 53000, 53500, 54000, 54500]  # Shorter dataset
        
        eth_df = self._create_mock_klines_data("ETHUSDT", eth_prices)
        btc_df = self._create_mock_klines_data("BTCUSDT", btc_prices)
        
        mock_get_klines.return_value = btc_df
        
        correlation = self.service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        assert correlation is not None
        assert isinstance(correlation, Decimal)
        # Should use minimum length (3 data points)
    
    @patch.object(MarketDataService, '_get_klines')
    def test_btc_correlation_bounds_clamping(self, mock_get_klines):
        """Test that correlation values are properly clamped to [-1, 1] range."""
        eth_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
        btc_prices = [50000, 50500, 51000, 51500, 52000, 52500, 53000, 53500, 54000, 54500, 55000, 55500]
        
        eth_df = self._create_mock_klines_data("ETHUSDT", eth_prices)
        btc_df = self._create_mock_klines_data("BTCUSDT", btc_prices)
        
        mock_get_klines.return_value = btc_df
        
        correlation = self.service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        assert correlation is not None
        assert -Decimal('1.0') <= correlation <= Decimal('1.0')
    
    @patch.object(MarketDataService, '_get_klines')
    def test_btc_correlation_decimal_precision(self, mock_get_klines):
        """Test that correlation is returned as Decimal with proper precision."""
        eth_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
        btc_prices = [50000, 50500, 51000, 51500, 52000, 52500, 53000, 53500, 54000, 54500, 55000, 55500]
        
        eth_df = self._create_mock_klines_data("ETHUSDT", eth_prices)
        btc_df = self._create_mock_klines_data("BTCUSDT", btc_prices)
        
        mock_get_klines.return_value = btc_df
        
        correlation = self.service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        assert correlation is not None
        assert isinstance(correlation, Decimal)
        # Check that precision is limited to 3 decimal places
        assert str(correlation).count('.') <= 1
        if '.' in str(correlation):
            decimal_places = len(str(correlation).split('.')[1])
            assert decimal_places <= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])