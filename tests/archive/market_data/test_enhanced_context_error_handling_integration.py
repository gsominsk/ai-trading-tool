"""
Manual test for enhanced context error handling.
Verifies graceful degradation when individual analysis components fail.
"""

import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService, MarketDataSet


def create_valid_market_data() -> MarketDataSet:
    """Create valid MarketDataSet for testing."""
    # Create valid DataFrames
    timestamps = [datetime.now(timezone.utc) - timedelta(hours=i) for i in range(50, 0, -1)]
    
    daily_data = pd.DataFrame({
        'timestamp': timestamps,
        'open': [100 + i for i in range(50)],
        'high': [105 + i for i in range(50)],
        'low': [95 + i for i in range(50)],
        'close': [102 + i for i in range(50)],
        'volume': [1000 + i*10 for i in range(50)]
    })
    
    h4_data = daily_data.copy()
    h1_data = daily_data.copy()
    
    return MarketDataSet(
        symbol="ETHUSDT",
        timestamp=datetime.now(timezone.utc),
        daily_candles=daily_data,
        h4_candles=h4_data,
        h1_candles=h1_data,
        rsi_14=Decimal('55.5'),
        macd_signal="bullish",
        ma_20=Decimal('120.5'),
        ma_50=Decimal('118.2'),
        ma_trend="uptrend",
        btc_correlation=Decimal('0.75'),
        volume_profile="normal",
        support_level=Decimal('100.0'),
        resistance_level=Decimal('150.0')
    )


def test_complete_market_data_failure():
    """Test when get_market_data completely fails."""
    print("🟡 Testing complete market data failure...")
    
    service = MarketDataService()
    
    with patch.object(service, 'get_market_data') as mock_get_data:
        mock_get_data.side_effect = Exception("API connection completely failed")
        
        try:
            market_data = service.get_market_data("ETHUSDT")
            result = service.get_enhanced_context(market_data)
            print(f"   ❌ ERROR: Should raise ProcessingError for complete failure, got result")
            return False
        except Exception as e:
            if "ProcessingError" in str(type(e)) and "API connection completely failed" in str(e):
                print("   ✅ Complete failure handled correctly (raised ProcessingError)")
                print("   📊 Error contains proper context and trace information")
                return True
            else:
                print(f"   ❌ ERROR: Unexpected exception type: {type(e)}, message: {e}")
                return False


def test_enhanced_analysis_failure_with_basic_fallback():
    """Test when enhanced analysis fails but basic context works."""
    print("\n🟡 Testing enhanced analysis failure with basic fallback...")
    
    service = MarketDataService()
    market_data = create_valid_market_data()
    
    with patch.object(service, 'get_market_data') as mock_get_data:
        mock_get_data.return_value = market_data
        
        with patch.object(service, '_select_key_candles') as mock_select:
            mock_select.side_effect = Exception("Key candles selection failed")
            
            result = service.get_enhanced_context(market_data)
            
            if ("MARKET DATA ANALYSIS FOR ETHUSDT" in result and
                "RSI(14): 55.50" in result and
                "Enhanced analysis unavailable" in result):
                print("   ✅ Graceful fallback to basic context")
                print("   📊 Enhanced analysis error reported, basic data preserved")
                return True
            else:
                print("   ❌ ERROR: Fallback not working properly")
                return False


def test_individual_component_failures():
    """Test when individual analysis components fail."""
    print("\n🟡 Testing individual component failures...")
    
    service = MarketDataService()
    market_data = create_valid_market_data()
    
    with patch.object(service, 'get_market_data') as mock_get_data:
        mock_get_data.return_value = market_data
        
        # Mock key candles to return valid data
        key_candles = [[datetime.now(timezone.utc).timestamp(), 100, 105, 95, 102, 1000] for _ in range(5)]
        
        with patch.object(service, '_select_key_candles') as mock_select:
            mock_select.return_value = key_candles
            
            # Mock individual components to fail
            with patch.object(service, '_analyze_recent_trend') as mock_trend:
                mock_trend.side_effect = Exception("Trend analysis error")
                
                with patch.object(service, '_identify_patterns') as mock_patterns:
                    mock_patterns.side_effect = Exception("Pattern analysis error")
                    
                    result = service.get_enhanced_context(market_data)
                    
                    if ("CANDLESTICK ANALYSIS" in result and
                        "Recent Trend: Analysis failed (Trend analysis error" in result and
                        "Patterns: Pattern analysis failed (Pattern analysis error" in result):
                        print("   ✅ Individual component failures handled gracefully")
                        print("   📊 Each component reports its own error")
                        return True
                    else:
                        print("   ❌ ERROR: Individual failures not handled properly")
                        return False


def test_graceful_degradation_mixed_success():
    """Test graceful degradation with mixed success/failure."""
    print("\n🟡 Testing graceful degradation with mixed success...")
    
    service = MarketDataService()
    market_data = create_valid_market_data()
    
    with patch.object(service, 'get_market_data') as mock_get_data:
        mock_get_data.return_value = market_data
        
        key_candles = [[datetime.now(timezone.utc).timestamp(), 100, 105, 95, 102, 1000] for _ in range(5)]
        
        with patch.object(service, '_select_key_candles') as mock_select:
            mock_select.return_value = key_candles
            
            with patch.object(service, '_analyze_recent_trend') as mock_trend:
                mock_trend.return_value = "Strong Uptrend"  # This works
                
                with patch.object(service, '_identify_patterns') as mock_patterns:
                    mock_patterns.side_effect = Exception("Pattern error")  # This fails
                    
                    with patch.object(service, '_analyze_sr_tests') as mock_sr:
                        mock_sr.return_value = "No recent S/R tests"  # This works
                        
                        with patch.object(service, '_analyze_volume_relationship') as mock_volume:
                            mock_volume.side_effect = Exception("Volume error")  # This fails
                            
                            result = service.get_enhanced_context(market_data)
                            
                            if ("Recent Trend: Strong Uptrend" in result and
                                "S/R Tests: No recent S/R tests" in result and
                                "Patterns: Pattern analysis failed (Pattern error" in result and
                                "Volume Analysis: Analysis failed (Volume error" in result):
                                print("   ✅ Mixed success/failure handled perfectly")
                                print("   📊 Working components succeed, failing ones report errors")
                                return True
                            else:
                                print("   ❌ ERROR: Mixed scenarios not handled properly")
                                return False


def test_invalid_candle_data_handling():
    """Test handling of invalid candle data."""
    print("\n🟡 Testing invalid candle data handling...")
    
    service = MarketDataService()
    
    # Test individual methods with invalid data
    tests_passed = 0
    total_tests = 4
    
    # Test _select_key_candles
    result = service._select_key_candles([])
    if result == []:
        tests_passed += 1
        print("   ✅ _select_key_candles handles empty data")
    
    # Test _analyze_recent_trend
    result = service._analyze_recent_trend([["invalid", "data"]])
    if "failed" in result.lower() or "insufficient" in result.lower():
        tests_passed += 1
        print("   ✅ _analyze_recent_trend handles invalid data")
    
    # Test _identify_patterns
    result = service._identify_patterns([["invalid", "data"]])
    if isinstance(result, list):
        tests_passed += 1
        print("   ✅ _identify_patterns handles invalid data")
    
    # Test _analyze_sr_tests
    result = service._analyze_sr_tests([], None, None)
    if "Invalid data" in result:
        tests_passed += 1
        print("   ✅ _analyze_sr_tests handles invalid data")
    
    if tests_passed == total_tests:
        print("   📊 All individual methods handle invalid data gracefully")
        return True
    else:
        print(f"   ❌ ERROR: {total_tests - tests_passed} methods failed invalid data handling")
        return False


def test_missing_support_resistance_levels():
    """Test handling when support/resistance levels are missing."""
    print("\n🟡 Testing missing support/resistance levels...")
    
    service = MarketDataService()
    market_data = create_valid_market_data()
    market_data.support_level = None
    market_data.resistance_level = None
    
    with patch.object(service, 'get_market_data') as mock_get_data:
        mock_get_data.return_value = market_data
        
        key_candles = [[datetime.now(timezone.utc).timestamp(), 100, 105, 95, 102, 1000] for _ in range(5)]
        
        with patch.object(service, '_select_key_candles') as mock_select:
            mock_select.return_value = key_candles
            
            result = service.get_enhanced_context(market_data)
            
            if "S/R Tests: Support/resistance levels unavailable" in result:
                print("   ✅ Missing S/R levels handled gracefully")
                print("   📊 Reports unavailable levels instead of crashing")
                return True
            else:
                print("   ❌ ERROR: Missing S/R levels not handled properly")
                return False


def main():
    """Run all manual tests for enhanced context error handling."""
    print("=" * 70)
    print("🚀 MANUAL TEST: Enhanced Context Error Handling")
    print("=" * 70)
    
    tests = [
        test_complete_market_data_failure,
        test_enhanced_analysis_failure_with_basic_fallback,
        test_individual_component_failures,
        test_graceful_degradation_mixed_success,
        test_invalid_candle_data_handling,
        test_missing_support_resistance_levels
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 ENHANCED CONTEXT ERROR HANDLING RESULTS: {passed}/{total} PASSED")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced context methods have comprehensive error handling")
        print("✅ Graceful degradation works at all levels")
        print("✅ Individual component failures don't crash the system")
        print("✅ Basic context fallback always available")
        print("✅ Production-ready error handling implemented")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  Review error handling implementation")
    
    print("=" * 70)
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)