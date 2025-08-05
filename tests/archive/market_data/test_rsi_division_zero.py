"""
Test RSI division by zero edge cases.

This test validates that RSI calculations handle edge cases gracefully
without throwing division by zero errors.
"""
import pytest
import pandas as pd
from decimal import Decimal
from src.market_data.market_data_service import MarketDataService


@pytest.fixture
def market_data_service():
    """Fixture for MarketDataService instance."""
    return MarketDataService()


def test_rsi_only_rising_prices(market_data_service):
    """Test RSI with only rising prices (no losses)."""
    # Create data where price only rises (only gains, no losses)
    rising_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 
                    110, 111, 112, 113, 114, 115]  # 16 points for RSI(14)
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'open': rising_prices,
        'high': [p + 0.5 for p in rising_prices],
        'low': [p - 0.5 for p in rising_prices],
        'close': rising_prices,
        'volume': [1000] * 16
    })
    
    # Should not raise division by zero error
    rsi = market_data_service._calculate_rsi(df, 14)
    
    # RSI should be a valid number (likely close to 100 for only rising prices)
    assert isinstance(rsi, (int, float, Decimal))
    assert 0 <= float(rsi) <= 100
    # For only rising prices, RSI should be high
    assert float(rsi) >= 90


def test_rsi_only_falling_prices(market_data_service):
    """Test RSI with only falling prices (no gains)."""
    # Create data where price only falls (no gains, only losses)
    falling_prices = [115, 114, 113, 112, 111, 110, 109, 108, 107, 106,
                     105, 104, 103, 102, 101, 100]  # 16 points for RSI(14)
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'open': falling_prices,
        'high': [p + 0.5 for p in falling_prices],
        'low': [p - 0.5 for p in falling_prices],
        'close': falling_prices,
        'volume': [1000] * 16
    })
    
    # Should not raise division by zero error
    rsi = market_data_service._calculate_rsi(df, 14)
    
    # RSI should be a valid number (likely close to 0 for only falling prices)
    assert isinstance(rsi, (int, float, Decimal))
    assert 0 <= float(rsi) <= 100
    # For only falling prices, RSI should be low
    assert float(rsi) <= 10


def test_rsi_no_price_movement(market_data_service):
    """Test RSI with no price movement (all same prices)."""
    # Create data where price never changes
    static_prices = [100] * 16  # 16 identical prices
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'open': static_prices,
        'high': static_prices,
        'low': static_prices,
        'close': static_prices,
        'volume': [1000] * 16
    })
    
    # Should not raise division by zero error
    rsi = market_data_service._calculate_rsi(df, 14)
    
    # RSI should be a valid number (likely 50 or NaN for no movement)
    assert isinstance(rsi, (int, float, Decimal)) or pd.isna(rsi)
    if not pd.isna(rsi):
        assert 0 <= float(rsi) <= 100


def test_rsi_minimal_data(market_data_service):
    """Test RSI with minimal data (less than required period)."""
    # Create data with less than 14 periods
    prices = [100, 101, 102, 103, 104, 105]  # Only 6 points
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=6, freq='h'),
        'open': prices,
        'high': [p + 0.5 for p in prices],
        'low': [p - 0.5 for p in prices],
        'close': prices,
        'volume': [1000] * 6
    })
    
    # Should not raise division by zero error
    rsi = market_data_service._calculate_rsi(df, 14)
    
    # RSI should be a valid number or NaN for insufficient data
    assert isinstance(rsi, (int, float, Decimal)) or pd.isna(rsi)
    if not pd.isna(rsi):
        assert 0 <= float(rsi) <= 100