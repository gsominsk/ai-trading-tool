"""
Comprehensive BTC Correlation Testing for MarketDataService
Tests the critical _calculate_btc_correlation() method that has NO current test coverage.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, call
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.market_data.market_data_service import MarketDataService


class TestBTCCorrelationComprehensive:
    """Comprehensive test suite for BTC correlation calculation."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MarketDataService()
        
    def _generate_test_klines(self, count: int = 50, base_price: float = 50000.0, 
                             correlation_factor: float = 0.8, volatility: float = 0.02) -> List[List[str]]:
        """Generate test klines with controlled correlation to BTC-like pattern."""
        klines = []
        current_time = int((datetime.utcnow() - timedelta(hours=count)).timestamp() * 1000)
        
        # Generate BTC-like base pattern
        btc_changes = []
        for i in range(count):
            # Create realistic price movements
            change_pct = (i % 20 - 10) * volatility  # ±2% movements
            btc_changes.append(change_pct)
        
        # Generate correlated price movements
        current_price = base_price
        for i in range(count):
            # Apply correlation with BTC pattern
            btc_change = btc_changes[i]
            correlated_change = btc_change * correlation_factor
            # Add some noise
            noise = (i % 7 - 3) * 0.005  # Small random component
            total_change = correlated_change + noise
            
            new_price = current_price * (1 + total_change)
            
            kline = [
                current_time + (i * 3600000),  # timestamp
                f"{current_price:.8f}",         # open
                f"{new_price * 1.01:.8f}",      # high
                f"{new_price * 0.99:.8f}",      # low
                f"{new_price:.8f}",             # close
                f"{1000 + i * 10:.8f}",         # volume
                current_time + (i * 3600000) + 3599999,  # close_time
                f"{(1000 + i * 10) * new_price:.8f}",    # quote_asset_volume
                1000 + i,                       # number_of_trades
                f"{(1000 + i * 10) * 0.6:.8f}", # taker_buy_base_asset_volume
                f"{(1000 + i * 10) * new_price * 0.6:.8f}", # taker_buy_quote_asset_volume
                "0"                             # ignore
            ]
            
            klines.append(kline)
            current_price = new_price
        
        return klines

    @pytest.mark.unit
    def test_btc_correlation_with_btcusdt_symbol_returns_none(self):
        """Test that BTC correlation returns None for BTCUSDT symbol."""
        # Create test DataFrame
        test_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=30, freq='h'),
            'open': [50000.0] * 30,
            'high': [50100.0] * 30,
            'low': [49900.0] * 30,
            'close': [50000.0] * 30,
            'volume': [1000.0] * 30
        })
        
        # Test that BTCUSDT returns None (no self-correlation)
        result = self.service._calculate_btc_correlation("BTCUSDT", test_df)
        
        assert result is None, "BTC correlation should return None for BTCUSDT symbol"
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_btc_correlation_high_correlation(self, mock_get):
        """Test calculation of high BTC correlation (>0.7)."""
        # Generate highly correlated data
        symbol_klines = self._generate_test_klines(50, 2000.0, correlation_factor=0.9)
        btc_klines = self._generate_test_klines(50, 50000.0, correlation_factor=1.0)
        
        # Create symbol DataFrame
        symbol_df = pd.DataFrame([
            {
                'timestamp': pd.to_datetime(k[0], unit='ms'),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5])
            } for k in symbol_klines
        ])
        
        # Mock BTC API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = btc_klines
        mock_get.return_value = mock_response
        
        # Test correlation calculation
        result = self.service._calculate_btc_correlation("ETHUSDT", symbol_df)
        
        # Should return high positive correlation
        assert result is not None, "Correlation should not be None for valid data"
        assert isinstance(result, Decimal), "Correlation should be Decimal type"
        assert result > Decimal('0.5'), f"High correlation expected, got {result}"
        assert Decimal('-1.0') <= result <= Decimal('1.0'), f"Correlation out of bounds: {result}"
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_btc_correlation_negative_correlation(self, mock_get):
        """Test calculation of negative BTC correlation."""
        # Generate negatively correlated data
        symbol_klines = self._generate_test_klines(50, 2000.0, correlation_factor=-0.8)
        btc_klines = self._generate_test_klines(50, 50000.0, correlation_factor=1.0)
        
        # Create symbol DataFrame
        symbol_df = pd.DataFrame([
            {
                'timestamp': pd.to_datetime(k[0], unit='ms'),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5])
            } for k in symbol_klines
        ])
        
        # Mock BTC API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = btc_klines
        mock_get.return_value = mock_response
        
        # Test correlation calculation
        result = self.service._calculate_btc_correlation("ETHUSDT", symbol_df)
        
        # Should return negative correlation
        assert result is not None, "Correlation should not be None for valid data"
        assert isinstance(result, Decimal), "Correlation should be Decimal type"
        assert result < Decimal('0.0'), f"Negative correlation expected, got {result}"
        assert Decimal('-1.0') <= result <= Decimal('1.0'), f"Correlation out of bounds: {result}"
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_btc_correlation_zero_correlation(self, mock_get):
        """Test calculation with zero correlation (random data)."""
        # Generate uncorrelated data
        symbol_klines = self._generate_test_klines(50, 2000.0, correlation_factor=0.0, volatility=0.05)
        btc_klines = self._generate_test_klines(50, 50000.0, correlation_factor=1.0)
        
        # Create symbol DataFrame
        symbol_df = pd.DataFrame([
            {
                'timestamp': pd.to_datetime(k[0], unit='ms'),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5])
            } for k in symbol_klines
        ])
        
        # Mock BTC API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = btc_klines
        mock_get.return_value = mock_response
        
        # Test correlation calculation
        result = self.service._calculate_btc_correlation("ETHUSDT", symbol_df)
        
        # Should return low correlation
        assert result is not None, "Correlation should not be None for valid data"
        assert isinstance(result, Decimal), "Correlation should be Decimal type"
        assert abs(result) < Decimal('0.5'), f"Low correlation expected, got {result}"
        assert Decimal('-1.0') <= result <= Decimal('1.0'), f"Correlation out of bounds: {result}"
    
    @pytest.mark.unit
    def test_btc_correlation_insufficient_data(self):
        """Test behavior with insufficient data."""
        from src.market_data.exceptions import DataInsufficientError
        
        # Create DataFrame with insufficient data
        insufficient_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=5, freq='h'),
            'open': [2000.0] * 5,
            'high': [2010.0] * 5,
            'low': [1990.0] * 5,
            'close': [2000.0] * 5,
            'volume': [1000.0] * 5
        })
        
        # Test with insufficient data - should raise DataInsufficientError
        with pytest.raises(DataInsufficientError) as exc_info:
            self.service._calculate_btc_correlation("ETHUSDT", insufficient_df)
        
        # Verify error details
        error = exc_info.value
        assert "Insufficient data for BTC correlation" in str(error)
        assert error.required_periods == 10
        assert error.available_periods == 5
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_btc_correlation_api_failure_handling(self, mock_get):
        """Test graceful handling of BTC API failures."""
        from src.market_data.exceptions import ProcessingError
        
        # Create valid symbol DataFrame
        symbol_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=30, freq='h'),
            'open': [2000.0] * 30,
            'high': [2010.0] * 30,
            'low': [1990.0] * 30,
            'close': [2000.0] * 30,
            'volume': [1000.0] * 30
        })
        
        # Mock API failure
        mock_get.side_effect = Exception("Network error")
        
        # Test graceful failure handling - should raise ProcessingError
        with pytest.raises(ProcessingError) as exc_info:
            self.service._calculate_btc_correlation("ETHUSDT", symbol_df)
        
        # Verify error details
        error = exc_info.value
        assert "Unexpected error during klines data processing" in str(error)
        assert "Network error" in str(error)
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_btc_correlation_constant_prices_handling(self, mock_get):
        """Test handling of constant prices (no variance)."""
        # Generate constant price data for symbol
        symbol_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=30, freq='h'),
            'open': [2000.0] * 30,
            'high': [2000.0] * 30,
            'low': [2000.0] * 30,
            'close': [2000.0] * 30,  # Constant prices
            'volume': [1000.0] * 30
        })
        
        # Generate constant BTC data
        btc_klines = []
        for i in range(30):
            btc_klines.append([
                int((datetime.utcnow() - timedelta(hours=30-i)).timestamp() * 1000),
                "50000.00000000", "50000.00000000", "50000.00000000", "50000.00000000",
                "1000.00000000", 0, "0", 0, "0", "0", "0"
            ])
        
        # Mock BTC API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = btc_klines
        mock_get.return_value = mock_response
        
        # Test with constant prices
        result = self.service._calculate_btc_correlation("ETHUSDT", symbol_df)
        
        # Should return 0.0 for constant prices (no correlation possible)
        assert result == Decimal('0.0'), f"Expected 0.0 for constant prices, got {result}"
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_btc_correlation_decimal_precision(self, mock_get):
        """Test that correlation maintains Decimal precision."""
        # Generate test data
        symbol_klines = self._generate_test_klines(30, 2000.0, correlation_factor=0.75)
        btc_klines = self._generate_test_klines(30, 50000.0, correlation_factor=1.0)
        
        # Create symbol DataFrame
        symbol_df = pd.DataFrame([
            {
                'timestamp': pd.to_datetime(k[0], unit='ms'),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5])
            } for k in symbol_klines
        ])
        
        # Mock BTC API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = btc_klines
        mock_get.return_value = mock_response
        
        # Test correlation calculation
        result = self.service._calculate_btc_correlation("ETHUSDT", symbol_df)
        
        # Verify Decimal type and precision
        assert isinstance(result, Decimal), f"Result should be Decimal, got {type(result)}"
        assert str(result).count('.') == 1, "Should have decimal point"
        
        # Check that result has proper precision (3 decimal places as per code)
        decimal_places = len(str(result).split('.')[1])
        assert decimal_places == 3, f"Expected 3 decimal places, got {decimal_places}"
    
    @pytest.mark.unit
    @patch('requests.get')
    def test_btc_correlation_bounds_clamping(self, mock_get):
        """Test that correlation is properly clamped to [-1, 1] bounds."""
        # This test verifies the bounds checking in the actual code
        symbol_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=30, freq='h'),
            'open': [2000.0] * 30,
            'high': [2010.0] * 30,
            'low': [1990.0] * 30,
            'close': [2005.0] * 30,
            'volume': [1000.0] * 30
        })
        
        # Generate BTC data
        btc_klines = self._generate_test_klines(30, 50000.0, correlation_factor=1.0)
        
        # Mock BTC API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = btc_klines
        mock_get.return_value = mock_response
        
        # Test correlation calculation
        result = self.service._calculate_btc_correlation("ETHUSDT", symbol_df)
        
        # Verify bounds
        assert result is not None, "Correlation should not be None"
        assert Decimal('-1.0') <= result <= Decimal('1.0'), f"Correlation out of bounds: {result}"
    
    @pytest.mark.unit
    @patch('requests.get') 
    def test_btc_correlation_data_alignment(self, mock_get):
        """Test that data is properly aligned between symbol and BTC."""
        # Create symbol DataFrame with specific length
        symbol_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=25, freq='h'),
            'open': [2000.0] * 25,
            'high': [2010.0] * 25,
            'low': [1990.0] * 25,
            'close': [2005.0] * 25,
            'volume': [1000.0] * 25
        })
        
        # Generate BTC data with different length
        btc_klines = self._generate_test_klines(30, 50000.0, correlation_factor=1.0)
        
        # Mock BTC API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = btc_klines
        mock_get.return_value = mock_response
        
        # Test correlation calculation
        result = self.service._calculate_btc_correlation("ETHUSDT", symbol_df)
        
        # Should handle length differences gracefully
        assert result is not None, "Should handle data length differences"
        assert isinstance(result, Decimal), "Should return Decimal result"
        assert Decimal('-1.0') <= result <= Decimal('1.0'), "Should return valid correlation"


def test_btc_correlation_integration():
    """Integration test for BTC correlation in real service usage."""
    service = MarketDataService()
    
    # Create realistic test data
    test_df = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=50, freq='h'),
        'open': [i * 10 + 2000 for i in range(50)],
        'high': [i * 10 + 2010 for i in range(50)],
        'low': [i * 10 + 1990 for i in range(50)],
        'close': [i * 10 + 2005 for i in range(50)],
        'volume': [1000 + i * 5 for i in range(50)]
    })
    
    # Test that function exists and is callable
    assert hasattr(service, '_calculate_btc_correlation'), "Service should have _calculate_btc_correlation method"
    assert callable(getattr(service, '_calculate_btc_correlation')), "Method should be callable"
    
    # Test with BTCUSDT (should return None)
    result_btc = service._calculate_btc_correlation("BTCUSDT", test_df)
    assert result_btc is None, "BTC correlation should return None for BTCUSDT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])