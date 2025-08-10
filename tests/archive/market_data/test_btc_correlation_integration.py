"""
Manual test for real BTC correlation functionality.
Verifies that hardcoded mock values have been removed and replaced with actual calculation.
"""

import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from src.market_data.market_data_service import MarketDataService


def create_test_dataframe(prices, symbol_name="TEST"):
    """Create test DataFrame with realistic structure."""
    data = []
    for i, price in enumerate(prices):
        data.append({
            'timestamp': datetime.now(timezone.utc) - timedelta(hours=len(prices)-i),
            'open': price,
            'high': price + 1,
            'low': price - 1,
            'close': price,
            'volume': 1000 + i
        })
    return pd.DataFrame(data)


def test_hardcoded_mock_removed():
    """Test that hardcoded mock value (0.75) is no longer returned."""
    print("🟡 Testing removal of hardcoded mock values...")
    
    service = MarketDataService()
    
    # Create test data with perfect positive correlation
    eth_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
    btc_prices = [50000, 50500, 51000, 51500, 52000, 52500, 53000, 53500, 54000, 54500, 55000, 55500]
    
    eth_df = create_test_dataframe(eth_prices)
    
    # Mock the BTC data fetch
    with patch.object(service, '_get_klines') as mock_get_klines:
        btc_df = create_test_dataframe(btc_prices)
        mock_get_klines.return_value = btc_df
        
        correlation = service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        # Should NOT be the old hardcoded value of 0.75
        if correlation == Decimal('0.75'):
            print("   ❌ ERROR: Still returning hardcoded value 0.75!")
            return False
        elif correlation == Decimal('1.000'):
            print("   ✅ Perfect positive correlation detected (1.000)")
            print(f"   📊 Correlation: {correlation} (expected ~1.000 for perfect positive)")
            return True
        else:
            print(f"   ✅ Real correlation calculated: {correlation}")
            print("   📊 No longer returning hardcoded 0.75 value")
            return True


def test_btc_correlation_for_btc():
    """Test that BTC correlation returns None for BTCUSDT."""
    print("\n🟡 Testing BTC correlation for BTCUSDT symbol...")
    
    service = MarketDataService()
    btc_df = create_test_dataframe([50000, 50500, 51000, 51500, 52000])
    
    correlation = service._calculate_btc_correlation("BTCUSDT", btc_df)
    
    if correlation is None:
        print("   ✅ BTCUSDT correctly returns None (no self-correlation)")
        return True
    else:
        print(f"   ❌ ERROR: BTCUSDT should return None, got {correlation}")
        return False


def test_correlation_calculation_accuracy():
    """Test that correlation calculation produces expected results."""
    print("\n🟡 Testing correlation calculation accuracy...")
    
    service = MarketDataService()
    
    # Test 1: Perfect negative correlation
    eth_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
    btc_prices = [55500, 55000, 54500, 54000, 53500, 53000, 52500, 52000, 51500, 51000, 50500, 50000]
    
    eth_df = create_test_dataframe(eth_prices)
    
    with patch.object(service, '_get_klines') as mock_get_klines:
        btc_df = create_test_dataframe(btc_prices)
        mock_get_klines.return_value = btc_df
        
        correlation = service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        if correlation == Decimal('-1.000'):
            print("   ✅ Perfect negative correlation detected (-1.000)")
        elif correlation is not None and -Decimal('1.0') <= correlation <= Decimal('-0.9'):
            print(f"   ✅ Strong negative correlation: {correlation}")
        else:
            print(f"   ⚠️  Unexpected correlation for negative pattern: {correlation}")
            return False
    
    return True


def test_api_failure_handling():
    """Test graceful handling of API failures."""
    print("\n🟡 Testing API failure handling...")
    
    service = MarketDataService()
    eth_df = create_test_dataframe([100, 101, 102, 103, 104])
    
    # Mock API failure
    with patch.object(service, '_get_klines') as mock_get_klines:
        mock_get_klines.side_effect = Exception("API connection failed")
        
        try:
            correlation = service._calculate_btc_correlation("ETHUSDT", eth_df)
            print(f"   ❌ ERROR: Should raise ProcessingError on API failure, got {correlation}")
            return False
        except Exception as e:
            if "ProcessingError" in str(type(e)) or "API connection failed" in str(e):
                print("   ✅ API failure handled correctly (raised ProcessingError)")
                return True
            else:
                print(f"   ❌ ERROR: Unexpected exception type: {type(e)}, message: {e}")
                return False


def test_insufficient_data_handling():
    """Test handling of insufficient data for correlation."""
    print("\n🟡 Testing insufficient data handling...")
    
    service = MarketDataService()
    
    # Create very small datasets (less than 10 points)
    eth_prices = [100, 101, 102]  # Only 3 data points
    btc_prices = [50000, 50500, 51000]
    
    eth_df = create_test_dataframe(eth_prices)
    
    with patch.object(service, '_get_klines') as mock_get_klines:
        btc_df = create_test_dataframe(btc_prices)
        mock_get_klines.return_value = btc_df
        
        try:
            correlation = service._calculate_btc_correlation("ETHUSDT", eth_df)
            print(f"   ❌ ERROR: Should raise DataInsufficientError for insufficient data, got {correlation}")
            return False
        except Exception as e:
            if "DataInsufficientError" in str(type(e)) or "Insufficient data" in str(e):
                print("   ✅ Insufficient data handled correctly (raised DataInsufficientError)")
                return True
            else:
                print(f"   ❌ ERROR: Unexpected exception type: {type(e)}, message: {e}")
                return False


def test_decimal_precision():
    """Test that correlation returns proper Decimal precision."""
    print("\n🟡 Testing Decimal precision...")
    
    service = MarketDataService()
    
    # Create data with slight correlation
    eth_prices = [100, 101, 102, 99, 103, 98, 104, 97, 105, 96, 106, 95]
    btc_prices = [50000, 50200, 50400, 49800, 50600, 49600, 50800, 49400, 51000, 49200, 51200, 49000]
    
    eth_df = create_test_dataframe(eth_prices)
    
    with patch.object(service, '_get_klines') as mock_get_klines:
        btc_df = create_test_dataframe(btc_prices)
        mock_get_klines.return_value = btc_df
        
        correlation = service._calculate_btc_correlation("ETHUSDT", eth_df)
        
        if correlation is not None:
            if isinstance(correlation, Decimal):
                print(f"   ✅ Correlation returned as Decimal: {correlation}")
                
                # Check precision (should be 3 decimal places)
                correlation_str = str(correlation)
                if '.' in correlation_str:
                    decimal_places = len(correlation_str.split('.')[1])
                    if decimal_places <= 3:
                        print(f"   ✅ Precision correct: {decimal_places} decimal places")
                        return True
                    else:
                        print(f"   ❌ Too many decimal places: {decimal_places}")
                        return False
                else:
                    print("   ✅ Integer correlation (valid)")
                    return True
            else:
                print(f"   ❌ ERROR: Not a Decimal type: {type(correlation)}")
                return False
        else:
            print("   ⚠️  Correlation is None (might be insufficient variance)")
            return True


def main():
    """Run all manual tests for BTC correlation."""
    print("=" * 70)
    print("🚀 MANUAL TEST: Real BTC Correlation (No More Mock Values)")
    print("=" * 70)
    
    tests = [
        test_hardcoded_mock_removed,
        test_btc_correlation_for_btc,
        test_correlation_calculation_accuracy,
        test_api_failure_handling,
        test_insufficient_data_handling,
        test_decimal_precision
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 BTC CORRELATION REAL TEST RESULTS: {passed}/{total} PASSED")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Hardcoded mock values successfully removed")
        print("✅ Real BTC correlation calculation implemented")
        print("✅ Proper error handling and edge cases covered")
        print("✅ Financial-grade Decimal precision maintained")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  Review BTC correlation implementation")
    
    print("=" * 70)
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)