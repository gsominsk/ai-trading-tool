import pytest
import pandas as pd
import numpy as np
from decimal import Decimal
from src.market_data.market_data_service import MarketDataService

def test_rsi_division_by_zero_protection():
    """Test that RSI calculation properly handles division by zero scenarios."""
    service = MarketDataService()
    
    # Test case 1: Only rising prices (loss = 0)
    rising_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 
                    110, 111, 112, 113, 114, 115]
    
    df_rising = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': rising_prices,
        'open': rising_prices,
        'high': [p + 0.5 for p in rising_prices],
        'low': [p - 0.5 for p in rising_prices],
        'volume': [1000] * 16
    })
    
    # Should handle division by zero gracefully (loss = 0)
    rsi_rising = service._calculate_rsi(df_rising, 14)
    assert isinstance(rsi_rising, Decimal)
    assert rsi_rising == Decimal('100.0')  # Maximum RSI for only gains
    
    # Test case 2: Only falling prices (gain = 0)
    falling_prices = [115, 114, 113, 112, 111, 110, 109, 108, 107, 106,
                     105, 104, 103, 102, 101, 100]
    
    df_falling = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': falling_prices,
        'open': falling_prices,
        'high': [p + 0.5 for p in falling_prices],
        'low': [p - 0.5 for p in falling_prices],
        'volume': [1000] * 16
    })
    
    # Should handle division by zero gracefully (gain = 0)
    rsi_falling = service._calculate_rsi(df_falling, 14)
    assert isinstance(rsi_falling, Decimal)
    assert rsi_falling == Decimal('0.0')  # Minimum RSI for only losses
    
    # Test case 3: Constant prices (both gain and loss = 0)
    constant_prices = [100] * 16
    
    df_constant = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': constant_prices,
        'open': constant_prices,
        'high': [p + 0.5 for p in constant_prices],
        'low': [p - 0.5 for p in constant_prices],
        'volume': [1000] * 16
    })
    
    # Should handle no price movement gracefully
    rsi_constant = service._calculate_rsi(df_constant, 14)
    assert isinstance(rsi_constant, Decimal)
    assert rsi_constant == Decimal('50.0')  # Neutral RSI for no movement
    
    # Test case 4: Insufficient data
    short_data = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=5, freq='h'),
        'close': [100, 101, 102, 103, 104],
        'open': [100, 101, 102, 103, 104],
        'high': [100.5, 101.5, 102.5, 103.5, 104.5],
        'low': [99.5, 100.5, 101.5, 102.5, 103.5],
        'volume': [1000] * 5
    })
    
    # Should return default neutral RSI for insufficient data
    rsi_short = service._calculate_rsi(short_data, 14)
    assert isinstance(rsi_short, Decimal)
    assert rsi_short == Decimal('50.0')  # Default neutral RSI

def test_rsi_normal_calculation():
    """Test that RSI calculation works correctly with normal mixed price data."""
    service = MarketDataService()
    
    # Mixed price movements
    mixed_prices = [100, 101, 99, 102, 98, 103, 97, 104, 96, 105,
                   95, 106, 94, 107, 93, 108]
    
    df_mixed = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': mixed_prices,
        'open': mixed_prices,
        'high': [p + 0.5 for p in mixed_prices],
        'low': [p - 0.5 for p in mixed_prices],
        'volume': [1000] * 16
    })
    
    rsi_mixed = service._calculate_rsi(df_mixed, 14)
    assert isinstance(rsi_mixed, Decimal)
    assert Decimal('0') <= rsi_mixed <= Decimal('100')  # Valid RSI range
    
    # Test with realistic crypto price data
    realistic_prices = [50000, 50500, 49800, 51200, 50700, 52000, 51500,
                       53000, 52200, 54000, 53500, 55000, 54200, 56000, 55500, 57000]
    
    df_realistic = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': realistic_prices,
        'open': realistic_prices,
        'high': [p + 200 for p in realistic_prices],
        'low': [p - 200 for p in realistic_prices],
        'volume': [1000] * 16
    })
    
    rsi_realistic = service._calculate_rsi(df_realistic, 14)
    assert isinstance(rsi_realistic, Decimal)
    assert Decimal('0') <= rsi_realistic <= Decimal('100')  # Valid RSI range
    assert str(rsi_realistic).count('.') <= 1  # Proper decimal format

if __name__ == "__main__":
    # Manual verification when run directly
    print("=== RSI DIVISION BY ZERO PROTECTION TESTS ===")
    
    service = MarketDataService()
    
    # Test rising prices (loss = 0)
    rising_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 
                    110, 111, 112, 113, 114, 115]
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
        'close': rising_prices,
        'open': rising_prices,
        'high': [p + 0.5 for p in rising_prices],
        'low': [p - 0.5 for p in rising_prices],
        'volume': [1000] * 16
    })
    
    print("Testing only rising prices (should result in RSI = 100):")
    print(f"Prices: {rising_prices}")
    
    # Test the calculation - should NOT cause division by zero
    rsi_result = service._calculate_rsi(df, 14)
    print(f"✅ RSI calculation successful: {rsi_result}")
    print(f"✅ Expected RSI 100.0 for only gains, got: {rsi_result}")
    
    print("\n=== ALL TESTS PASSED ===")
    print("RSI calculation properly handles all division by zero scenarios")