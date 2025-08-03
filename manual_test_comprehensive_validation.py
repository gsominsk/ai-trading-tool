"""
Manual test for comprehensive validation functionality in MarketDataSet.__post_init__.
Tests real-world scenarios and edge cases to verify validation works correctly.
"""

import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from src.market_data.market_data_service import MarketDataSet


def create_valid_dataframe(num_rows=50):
    """Create a valid DataFrame for testing."""
    data = []
    base_price = 100.0
    
    for i in range(num_rows):
        # Create realistic OHLC data
        open_price = base_price + (i * 0.1)
        high_price = open_price + 2.0
        low_price = open_price - 1.5
        close_price = open_price + 0.5
        volume = 1000.0 + (i * 10)
        
        data.append({
            'timestamp': datetime.utcnow() - timedelta(hours=num_rows-i),
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(data)


def test_valid_creation():
    """Test that valid MarketDataSet can be created successfully."""
    print("🟢 Testing valid MarketDataSet creation...")
    
    try:
        market_data = MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=create_valid_dataframe(50),
            h4_candles=create_valid_dataframe(30),
            h1_candles=create_valid_dataframe(20),
            rsi_14=Decimal('55.0'),
            macd_signal="bullish",
            ma_20=Decimal('102.50'),  # Significantly above MA50 for uptrend
            ma_50=Decimal('99.80'),
            ma_trend="uptrend",
            btc_correlation=Decimal('0.75'),
            fear_greed_index=60,
            volume_profile="normal",
            support_level=Decimal('95.00'),
            resistance_level=Decimal('105.00')
        )
        print(f"   ✅ Valid MarketDataSet created successfully")
        print(f"   📊 Symbol: {market_data.symbol}, RSI: {market_data.rsi_14}")
        return True
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False


def test_timestamp_validation():
    """Test timestamp validation edge cases."""
    print("\n🟡 Testing timestamp validation...")
    
    # Test too old timestamp
    try:
        old_timestamp = datetime.utcnow() - timedelta(days=35)
        MarketDataSet(
            symbol="BTCUSDT",
            timestamp=old_timestamp,
            daily_candles=create_valid_dataframe(),
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('100.0'),
            ma_50=Decimal('100.0'),
            ma_trend="sideways"
        )
        print("   ❌ ERROR: Should have failed for old timestamp")
        return False
    except ValueError as e:
        if "too old" in str(e):
            print("   ✅ Correctly rejected old timestamp")
        else:
            print(f"   ❌ Wrong error for old timestamp: {e}")
            return False
    
    # Test future timestamp
    try:
        future_timestamp = datetime.utcnow() + timedelta(hours=2)
        MarketDataSet(
            symbol="BTCUSDT",
            timestamp=future_timestamp,
            daily_candles=create_valid_dataframe(),
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('100.0'),
            ma_50=Decimal('100.0'),
            ma_trend="sideways"
        )
        print("   ❌ ERROR: Should have failed for future timestamp")
        return False
    except ValueError as e:
        if "too far in future" in str(e):
            print("   ✅ Correctly rejected future timestamp")
        else:
            print(f"   ❌ Wrong error for future timestamp: {e}")
            return False
    
    return True


def test_dataframe_validation():
    """Test DataFrame validation edge cases."""
    print("\n🟡 Testing DataFrame validation...")
    
    # Test empty DataFrame
    try:
        empty_df = pd.DataFrame()
        MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=empty_df,
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('100.0'),
            ma_50=Decimal('100.0'),
            ma_trend="sideways"
        )
        print("   ❌ ERROR: Should have failed for empty DataFrame")
        return False
    except ValueError as e:
        if "cannot be empty" in str(e):
            print("   ✅ Correctly rejected empty DataFrame")
        else:
            print(f"   ❌ Wrong error for empty DataFrame: {e}")
            return False
    
    # Test insufficient rows
    try:
        small_df = create_valid_dataframe(5)  # Less than minimum 30 for daily
        MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=small_df,
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('100.0'),
            ma_50=Decimal('100.0'),
            ma_trend="sideways"
        )
        print("   ❌ ERROR: Should have failed for insufficient rows")
        return False
    except ValueError as e:
        if "must have at least 30 rows" in str(e):
            print("   ✅ Correctly rejected insufficient rows")
        else:
            print(f"   ❌ Wrong error for insufficient rows: {e}")
            return False
    
    return True


def test_decimal_validation():
    """Test Decimal fields validation."""
    print("\n🟡 Testing Decimal validation...")
    
    # Test wrong type (float instead of Decimal)
    try:
        MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=create_valid_dataframe(),
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=100.0,  # Float instead of Decimal
            ma_50=Decimal('100.0'),
            ma_trend="sideways"
        )
        print("   ❌ ERROR: Should have failed for float instead of Decimal")
        return False
    except ValueError as e:
        if "must be Decimal" in str(e):
            print("   ✅ Correctly rejected float instead of Decimal")
        else:
            print(f"   ❌ Wrong error for float: {e}")
            return False
    
    # Test negative value
    try:
        MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=create_valid_dataframe(),
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('-100.0'),  # Negative value
            ma_50=Decimal('100.0'),
            ma_trend="sideways"
        )
        print("   ❌ ERROR: Should have failed for negative MA value")
        return False
    except ValueError as e:
        if "must be positive" in str(e):
            print("   ✅ Correctly rejected negative MA value")
        else:
            print(f"   ❌ Wrong error for negative MA: {e}")
            return False
    
    return True


def test_cross_field_consistency():
    """Test cross-field consistency validation."""
    print("\n🟡 Testing cross-field consistency...")
    
    # Test support > resistance
    try:
        MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=create_valid_dataframe(),
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('100.0'),
            ma_50=Decimal('100.0'),
            ma_trend="sideways",
            support_level=Decimal('110.0'),    # Higher than resistance (invalid)
            resistance_level=Decimal('105.0')
        )
        print("   ❌ ERROR: Should have failed for support > resistance")
        return False
    except ValueError as e:
        if "must be lower than resistance" in str(e):
            print("   ✅ Correctly rejected support > resistance")
        else:
            print(f"   ❌ Wrong error for support/resistance: {e}")
            return False
    
    # Test MA trend inconsistency
    try:
        MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=create_valid_dataframe(),
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('100.0'),  # Not significantly above MA50
            ma_50=Decimal('99.9'),
            ma_trend="uptrend"  # Inconsistent with MA values
        )
        print("   ❌ ERROR: Should have failed for MA trend inconsistency")
        return False
    except ValueError as e:
        if "not significantly above" in str(e):
            print("   ✅ Correctly rejected MA trend inconsistency")
        else:
            print(f"   ❌ Wrong error for MA trend: {e}")
            return False
    
    return True


def test_edge_cases():
    """Test additional edge cases."""
    print("\n🟡 Testing edge cases...")
    
    # Test BTC correlation out of range
    try:
        MarketDataSet(
            symbol="ETHUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=create_valid_dataframe(),
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('100.0'),
            ma_50=Decimal('100.0'),
            ma_trend="sideways",
            btc_correlation=Decimal('1.5')  # Out of range [-1, 1]
        )
        print("   ❌ ERROR: Should have failed for BTC correlation out of range")
        return False
    except ValueError as e:
        if "must be between -1 and 1" in str(e):
            print("   ✅ Correctly rejected BTC correlation out of range")
        else:
            print(f"   ❌ Wrong error for BTC correlation: {e}")
            return False
    
    # Test Fear & Greed index out of range
    try:
        MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.utcnow(),
            daily_candles=create_valid_dataframe(),
            h4_candles=create_valid_dataframe(),
            h1_candles=create_valid_dataframe(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('100.0'),
            ma_50=Decimal('100.0'),
            ma_trend="sideways",
            fear_greed_index=150  # Out of range [0, 100]
        )
        print("   ❌ ERROR: Should have failed for Fear & Greed index out of range")
        return False
    except ValueError as e:
        if "must be between 0 and 100" in str(e):
            print("   ✅ Correctly rejected Fear & Greed index out of range")
        else:
            print(f"   ❌ Wrong error for Fear & Greed index: {e}")
            return False
    
    return True


def main():
    """Run all manual validation tests."""
    print("=" * 70)
    print("🚀 MANUAL TEST: Comprehensive MarketDataSet Validation")
    print("=" * 70)
    
    tests = [
        test_valid_creation,
        test_timestamp_validation,
        test_dataframe_validation,
        test_decimal_validation,
        test_cross_field_consistency,
        test_edge_cases
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 COMPREHENSIVE VALIDATION TEST RESULTS: {passed}/{total} PASSED")
    
    if passed == total:
        print("🎉 ALL VALIDATION TESTS PASSED!")
        print("✅ MarketDataSet comprehensive validation is working correctly")
        print("✅ All edge cases and error conditions properly handled")
        print("✅ Financial data integrity protection active")
    else:
        print("❌ SOME VALIDATION TESTS FAILED!")
        print("⚠️  Review validation logic for failed test cases")
    
    print("=" * 70)
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)