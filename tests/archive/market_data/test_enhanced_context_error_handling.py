"""
Test error handling in enhanced context methods.
Verifies graceful degradation when individual analysis components fail.
"""

import pytest
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService, MarketDataSet


class TestEnhancedContextErrorHandling:
    """Test error handling in enhanced context methods."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = MarketDataService()
        
    def create_valid_market_data(self) -> MarketDataSet:
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
    
    def test_get_enhanced_context_market_data_failure(self):
        """Test enhanced context when market data fetch fails."""
        with patch.object(self.service, 'get_market_data') as mock_get_data:
            mock_get_data.side_effect = Exception("API connection failed")
            
            result = self.service.get_enhanced_context("ETHUSDT")
            
            assert "CRITICAL ERROR" in result
            assert "API connection failed" in result
            assert "ETHUSDT" in result
            assert "Network connectivity" in result
    
    def test_get_enhanced_context_enhanced_analysis_failure(self):
        """Test enhanced context when enhanced analysis fails but basic context works."""
        market_data = self.create_valid_market_data()
        
        with patch.object(self.service, 'get_market_data') as mock_get_data:
            mock_get_data.return_value = market_data
            
            with patch.object(self.service, '_select_key_candles') as mock_select:
                mock_select.side_effect = Exception("Key candles selection failed")
                
                result = self.service.get_enhanced_context("ETHUSDT")
                
                # Should contain basic context
                assert "MARKET DATA ANALYSIS FOR ETHUSDT" in result
                assert "RSI(14): 55.50" in result
                
                # Should contain error message about enhanced analysis
                assert "Enhanced analysis unavailable" in result
                assert "Key candles selection failed" in result
                assert "Fallback: Basic market data provided above" in result
    
    def test_get_enhanced_context_individual_component_failures(self):
        """Test enhanced context when individual analysis components fail."""
        market_data = self.create_valid_market_data()
        
        with patch.object(self.service, 'get_market_data') as mock_get_data:
            mock_get_data.return_value = market_data
            
            # Mock key candles to return valid data
            key_candles = [[datetime.now(timezone.utc).timestamp(), 100, 105, 95, 102, 1000] for _ in range(5)]
            
            with patch.object(self.service, '_select_key_candles') as mock_select:
                mock_select.return_value = key_candles
                
                # Mock individual components to fail
                with patch.object(self.service, '_analyze_recent_trend') as mock_trend:
                    mock_trend.side_effect = Exception("Trend analysis error")
                    
                    with patch.object(self.service, '_identify_patterns') as mock_patterns:
                        mock_patterns.side_effect = Exception("Pattern analysis error")
                        
                        result = self.service.get_enhanced_context("ETHUSDT")
                        
                        # Should contain basic context
                        assert "MARKET DATA ANALYSIS FOR ETHUSDT" in result
                        assert "CANDLESTICK ANALYSIS" in result
                        
                        # Should contain error messages for failed components
                        assert "Recent Trend: Analysis failed (Trend analysis error" in result
                        assert "Patterns: Pattern analysis failed (Pattern analysis error" in result
    
    def test_select_key_candles_error_handling(self):
        """Test _select_key_candles error handling."""
        # Test with invalid data
        result = self.service._select_key_candles([])
        assert result == []
        
        result = self.service._select_key_candles(None)
        assert result == []
        
        # Test with malformed candles
        malformed_candles = [
            ["invalid", "data", "structure"],
            [1, 2, 3],  # Too few elements
        ]
        result = self.service._select_key_candles(malformed_candles)
        assert isinstance(result, list)  # Should not crash
    
    def test_analyze_recent_trend_error_handling(self):
        """Test _analyze_recent_trend error handling."""
        # Test with insufficient data
        result = self.service._analyze_recent_trend([])
        assert result == "Insufficient data"
        
        result = self.service._analyze_recent_trend([[1, 100, 105, 95, 102, 1000]])
        assert result == "Insufficient data"
        
        # Test with invalid candle data
        invalid_candles = [
            ["invalid", "data", "in", "candle", "format"],
            [1, 2, 3, "invalid", 5],
            [1, 2, 3, 4, None]
        ]
        result = self.service._analyze_recent_trend(invalid_candles)
        assert "failed" in result.lower() or "insufficient" in result.lower()
    
    def test_identify_patterns_error_handling(self):
        """Test _identify_patterns error handling."""
        # Test with empty data
        result = self.service._identify_patterns([])
        assert result == []
        
        # Test with invalid candle data
        invalid_candles = [
            ["invalid", "data", "structure"],
            [1, "invalid", 3, 4, 5],
            [1, 2, 3, 4, None]
        ]
        result = self.service._identify_patterns(invalid_candles)
        assert isinstance(result, list)  # Should not crash
    
    def test_analyze_sr_tests_error_handling(self):
        """Test _analyze_sr_tests error handling."""
        # Test with invalid inputs - empty candles and None levels
        result = self.service._analyze_sr_tests([], None, None)
        assert "Invalid data" in result
        
        # Test with negative support/resistance levels (need valid candles)
        valid_candles = [[1, 100, 105, 95, 102, 1000]]
        result = self.service._analyze_sr_tests(valid_candles, Decimal('-1'), Decimal('100'))
        assert "Invalid S/R levels" in result
        
        result = self.service._analyze_sr_tests(valid_candles, Decimal('0'), Decimal('100'))
        assert "Invalid S/R levels" in result
        
        # Test with invalid candle data
        invalid_candles = [
            ["invalid", "data"],
            [1, 2, "invalid", 4, 5]
        ]
        result = self.service._analyze_sr_tests(invalid_candles, Decimal('100'), Decimal('150'))
        assert "No recent S/R tests" in result or "failed" in result.lower()
    
    def test_analyze_volume_relationship_error_handling(self):
        """Test _analyze_volume_relationship error handling."""
        # Test with insufficient data
        result = self.service._analyze_volume_relationship([])
        assert result == "Insufficient data"
        
        result = self.service._analyze_volume_relationship([[1, 100, 105, 95, 102, 1000]])
        assert result == "Insufficient data"
        
        # Test with invalid candle data
        invalid_candles = [
            ["invalid", "data", "structure"],
            [1, 2, 3, 4, "invalid"],
            [1, 2, 3, 4, None]
        ]
        result = self.service._analyze_volume_relationship(invalid_candles)
        assert "failed" in result.lower() or "insufficient" in result.lower()
    
    def test_find_pattern_candles_error_handling(self):
        """Test _find_pattern_candles error handling."""
        # Test with empty data
        result = self.service._find_pattern_candles([])
        assert result == []
        
        # Test with invalid candle data
        invalid_candles = [
            ["invalid", "data"],
            [1, "invalid", 3, 4, 5],
            [1, 2, 3, 4, None]
        ]
        result = self.service._find_pattern_candles(invalid_candles)
        assert isinstance(result, list)  # Should not crash
    
    def test_enhanced_context_graceful_degradation(self):
        """Test that enhanced context provides graceful degradation."""
        market_data = self.create_valid_market_data()
        
        with patch.object(self.service, 'get_market_data') as mock_get_data:
            mock_get_data.return_value = market_data
            
            # Mock some components to fail, others to succeed
            key_candles = [[datetime.now(timezone.utc).timestamp(), 100, 105, 95, 102, 1000] for _ in range(5)]
            
            with patch.object(self.service, '_select_key_candles') as mock_select:
                mock_select.return_value = key_candles
                
                with patch.object(self.service, '_analyze_recent_trend') as mock_trend:
                    mock_trend.return_value = "Strong Uptrend"  # This works
                    
                    with patch.object(self.service, '_identify_patterns') as mock_patterns:
                        mock_patterns.side_effect = Exception("Pattern error")  # This fails
                        
                        with patch.object(self.service, '_analyze_sr_tests') as mock_sr:
                            mock_sr.return_value = "No recent S/R tests"  # This works
                            
                            with patch.object(self.service, '_analyze_volume_relationship') as mock_volume:
                                mock_volume.side_effect = Exception("Volume error")  # This fails
                                
                                result = self.service.get_enhanced_context("ETHUSDT")
                                
                                # Should contain successful components
                                assert "Recent Trend: Strong Uptrend" in result
                                assert "S/R Tests: No recent S/R tests" in result
                                
                                # Should contain error messages for failed components
                                assert "Patterns: Pattern analysis failed (Pattern error" in result
                                assert "Volume Analysis: Analysis failed (Volume error" in result
    
    def test_enhanced_context_with_missing_support_resistance(self):
        """Test enhanced context when support/resistance levels are missing."""
        market_data = self.create_valid_market_data()
        market_data.support_level = None
        market_data.resistance_level = None
        
        with patch.object(self.service, 'get_market_data') as mock_get_data:
            mock_get_data.return_value = market_data
            
            key_candles = [[datetime.now(timezone.utc).timestamp(), 100, 105, 95, 102, 1000] for _ in range(5)]
            
            with patch.object(self.service, '_select_key_candles') as mock_select:
                mock_select.return_value = key_candles
                
                result = self.service.get_enhanced_context("ETHUSDT")
                
                assert "S/R Tests: Support/resistance levels unavailable" in result


def main():
    """Run error handling tests."""
    print("=" * 70)
    print("🚀 TESTING: Enhanced Context Error Handling")
    print("=" * 70)
    
    # Run the tests
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()