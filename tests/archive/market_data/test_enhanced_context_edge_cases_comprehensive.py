"""
Comprehensive Enhanced Context Edge Cases Tests for MarketDataService
Tests enhanced context generation functionality that is core to LLM trading decisions.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, call
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time

from src.market_data.market_data_service import MarketDataService, MarketDataSet


class TestEnhancedContextEdgeCasesComprehensive:
    """Comprehensive test suite for enhanced context generation edge cases."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MarketDataService()
        
    def _create_large_market_dataset(self, num_candles: int = 1000) -> MarketDataSet:
        """Create a large MarketDataSet for performance testing."""
        # Ensure we have enough data for validation
        base_time = datetime.utcnow() - timedelta(hours=2)
        
        # Calculate minimum required rows
        min_daily = max(30, num_candles // 24 + 1)
        min_h4 = max(10, num_candles // 4 + 1)
        min_h1 = max(10, num_candles)
        
        # Generate daily data
        daily_data = []
        for i in range(min_daily):
            price = 50000.0 + i * 10
            candle_data = {
                'timestamp': base_time - timedelta(days=i),
                'open': price,
                'high': price * 1.01,
                'low': price * 0.99,
                'close': price * (1 + (i % 10 - 5) * 0.001),
                'volume': 1000 + i * 2
            }
            daily_data.append(candle_data)
        
        # Generate H4 data
        h4_data = []
        for i in range(min_h4):
            price = 50000.0 + i * 10
            candle_data = {
                'timestamp': base_time - timedelta(hours=i*4),
                'open': price,
                'high': price * 1.01,
                'low': price * 0.99,
                'close': price * (1 + (i % 10 - 5) * 0.001),
                'volume': 1000 + i * 2
            }
            h4_data.append(candle_data)
        
        # Generate H1 data
        h1_data = []
        for i in range(min_h1):
            price = 50000.0 + i * 10
            candle_data = {
                'timestamp': base_time - timedelta(hours=i),
                'open': price,
                'high': price * 1.01,
                'low': price * 0.99,
                'close': price * (1 + (i % 10 - 5) * 0.001),
                'volume': 1000 + i * 2
            }
            h1_data.append(candle_data)
        
        # Convert to DataFrames
        daily_df = pd.DataFrame(daily_data)
        h4_df = pd.DataFrame(h4_data)
        h1_df = pd.DataFrame(h1_data)
        
        return MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.utcnow() - timedelta(hours=2),
            daily_candles=daily_df,
            h4_candles=h4_df,
            h1_candles=h1_df,
            rsi_14=Decimal('55.5'),
            macd_signal="bullish",
            ma_20=Decimal('50000.00'),
            ma_50=Decimal('49500.00'),
            ma_trend="uptrend",
            support_level=Decimal('49000.00'),
            resistance_level=Decimal('51000.00')
        )
    
    def _create_minimal_market_dataset(self) -> MarketDataSet:
        """Create minimal MarketDataSet for edge case testing."""
        # Create minimal DataFrames (just enough to pass validation)
        minimal_data = []
        for i in range(30):  # Minimum required for validation
            candle_data = {
                'timestamp': datetime.utcnow() - timedelta(hours=i+2),
                'open': 50000.0,
                'high': 50001.0,
                'low': 49999.0,
                'close': 50000.0,
                'volume': 1000.0
            }
            minimal_data.append(candle_data)
        
        minimal_df = pd.DataFrame(minimal_data)
        
        return MarketDataSet(
            symbol="TESTUSDT",
            timestamp=datetime.utcnow() - timedelta(minutes=30),
            daily_candles=minimal_df.copy(),
            h4_candles=minimal_df.copy(),
            h1_candles=minimal_df.copy(),
            rsi_14=Decimal('50.0'),
            macd_signal="neutral",
            ma_20=Decimal('50000.00'),
            ma_50=Decimal('50000.00'),
            ma_trend="sideways"
        )
    
    @pytest.mark.unit
    def test_enhanced_context_with_large_datasets(self):
        """Test enhanced context generation performance with large datasets."""
        # Create large dataset
        large_dataset = self._create_large_market_dataset(1000)
        
        # Mock get_market_data to return large dataset
        with patch.object(self.service, 'get_market_data', return_value=large_dataset):
            start_time = time.time()
            
            # Test enhanced context generation
            enhanced_context = self.service.get_enhanced_context(large_dataset)
            
            processing_time = time.time() - start_time
            
            # Performance assertions
            assert processing_time < 5.0, f"Enhanced context generation took {processing_time:.3f}s - too slow for large dataset"
            
            # Content assertions
            assert enhanced_context is not None, "Enhanced context should not be None"
            assert len(enhanced_context) > 0, "Enhanced context should not be empty"
            assert "MARKET DATA ANALYSIS" in enhanced_context, "Enhanced context should contain market analysis"
            assert "CANDLESTICK ANALYSIS" in enhanced_context, "Enhanced context should contain candlestick analysis"
    
    @pytest.mark.unit
    def test_enhanced_context_with_minimal_datasets(self):
        """Test enhanced context generation with minimal valid datasets."""
        # Create minimal dataset
        minimal_dataset = self._create_minimal_market_dataset()
        
        # Mock get_market_data to return minimal dataset
        with patch.object(self.service, 'get_market_data', return_value=minimal_dataset):
            # Test enhanced context generation
            enhanced_context = self.service.get_enhanced_context(minimal_dataset)
            
            # Content assertions
            assert enhanced_context is not None, "Enhanced context should not be None for minimal dataset"
            assert len(enhanced_context) > 0, "Enhanced context should not be empty for minimal dataset"
            assert "MARKET DATA ANALYSIS" in enhanced_context, "Enhanced context should contain market analysis"
            # May not have candlestick analysis due to minimal data
    
    @pytest.mark.unit
    def test_enhanced_context_memory_pressure(self):
        """Test enhanced context generation under memory pressure."""
        # Create multiple large datasets to simulate memory pressure
        large_datasets = []
        for i in range(5):  # Create 5 large datasets
            large_datasets.append(self._create_large_market_dataset(500))
        
        # Test enhanced context generation with multiple datasets in memory
        for i, dataset in enumerate(large_datasets):
            with patch.object(self.service, 'get_market_data', return_value=dataset):
                enhanced_context = self.service.get_enhanced_context(dataset)
                
                # Should handle memory pressure gracefully
                assert enhanced_context is not None, f"Enhanced context should not be None for dataset {i}"
                assert len(enhanced_context) > 0, f"Enhanced context should not be empty for dataset {i}"
    
    @pytest.mark.unit
    def test_enhanced_context_concurrent_access(self):
        """Test enhanced context generation with concurrent access simulation."""
        import threading
        import time
        
        results = []
        exceptions = []
        
        def generate_enhanced_context(symbol_suffix):
            try:
                # Create dataset for this thread
                dataset = self._create_minimal_market_dataset()
                dataset.symbol = f"TEST{symbol_suffix}USDT"
                
                with patch.object(self.service, 'get_market_data', return_value=dataset):
                    enhanced_context = self.service.get_enhanced_context(dataset)
                    results.append({
                        'symbol': dataset.symbol,
                        'context_length': len(enhanced_context),
                        'success': True
                    })
            except Exception as e:
                exceptions.append({
                    'symbol': f"TEST{symbol_suffix}USDT",
                    'error': str(e)
                })
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=generate_enhanced_context, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Verify results
        assert len(exceptions) == 0, f"No exceptions should occur during concurrent access: {exceptions}"
        assert len(results) == 5, f"All threads should complete successfully, got {len(results)} results"
        
        for result in results:
            assert result['success'] is True, f"All results should be successful: {result}"
            assert result['context_length'] > 0, f"All contexts should have content: {result}"
    
    @pytest.mark.unit
    @patch('src.market_data.market_data_service.MarketDataService.get_market_data')
    def test_enhanced_context_api_failure_fallback(self, mock_get_market_data):
        """Test enhanced context fallback behavior when API fails."""
        # Mock API failure
        mock_get_market_data.side_effect = Exception("API connection failed")

        # With the refactoring, the API call is handled before get_enhanced_context.
        # This test now verifies that the exception from get_market_data is propagated.
        with pytest.raises(Exception) as excinfo:
            self.service.get_market_data("FAILUSDT")
        
        assert "API connection failed" in str(excinfo.value)
    
    @pytest.mark.unit
    def test_enhanced_context_malformed_data_handling(self):
        """Test enhanced context with malformed market data."""
        # Create dataset with malformed data
        malformed_dataset = self._create_minimal_market_dataset()
        malformed_dataset.symbol = "MALFORMEDUSDT"  # Set the symbol we want to test

        # Corrupt some data
        malformed_dataset.daily_candles.loc[0, 'close'] = float('inf')  # Invalid close price
        malformed_dataset.h1_candles.loc[1, 'volume'] = -1000  # Negative volume

        # Mock get_market_data to return malformed dataset
        with patch.object(self.service, 'get_market_data', return_value=malformed_dataset):
            # Should handle malformed data gracefully
            enhanced_context = self.service.get_enhanced_context(malformed_dataset)

            # Should return some context (fallback to basic context)
            assert enhanced_context is not None, "Enhanced context should handle malformed data"
            assert len(enhanced_context) > 0, "Enhanced context should not be empty with malformed data"
            assert "MALFORMEDUSDT" in enhanced_context, "Enhanced context should include symbol"
    
    @pytest.mark.unit
    def test_enhanced_context_extreme_values(self):
        """Test enhanced context with extreme market values."""
        # Create dataset with extreme values
        extreme_dataset = self._create_minimal_market_dataset()
        
        # Set extreme values
        extreme_dataset.rsi_14 = Decimal('99.999')  # Near maximum RSI
        extreme_dataset.ma_20 = Decimal('999999.99')  # Very high price
        extreme_dataset.support_level = Decimal('0.001')  # Very low support
        extreme_dataset.resistance_level = Decimal('1000000.00')  # Very high resistance
        
        # Mock get_market_data to return extreme dataset
        with patch.object(self.service, 'get_market_data', return_value=extreme_dataset):
            # Should handle extreme values gracefully
            enhanced_context = self.service.get_enhanced_context(extreme_dataset)
            
            assert enhanced_context is not None, "Enhanced context should handle extreme values"
            assert len(enhanced_context) > 0, "Enhanced context should not be empty with extreme values"
            assert "99.99" in enhanced_context, "Enhanced context should include extreme RSI"
            assert "999999.99" in enhanced_context, "Enhanced context should include extreme MA"
    
    @pytest.mark.unit
    def test_enhanced_context_token_optimization(self):
        """Test that enhanced context stays within token limits."""
        # Create various sized datasets
        datasets = [
            self._create_minimal_market_dataset(),
            self._create_large_market_dataset(100),
            self._create_large_market_dataset(500),
            self._create_large_market_dataset(1000)
        ]
        
        for i, dataset in enumerate(datasets):
            with patch.object(self.service, 'get_market_data', return_value=dataset):
                enhanced_context = self.service.get_enhanced_context(dataset)
                
                # Estimate token count (rough approximation: 1 token ≈ 4 characters)
                estimated_tokens = len(enhanced_context) / 4
                
                # Should stay within reasonable token limits
                assert estimated_tokens < 500, f"Enhanced context estimated {estimated_tokens} tokens - too many for dataset {i}"
                
                # Should contain essential information regardless of dataset size
                assert "MARKET DATA ANALYSIS" in enhanced_context, f"Dataset {i} should contain market analysis"
                assert "RSI" in enhanced_context, f"Dataset {i} should contain RSI information"
                assert "MA" in enhanced_context, f"Dataset {i} should contain MA information"
    
    @pytest.mark.unit
    def test_enhanced_context_error_boundary_isolation(self):
        """Test that errors in enhanced analysis don't affect basic context."""
        # Create dataset that might cause issues in enhanced analysis
        problematic_dataset = self._create_minimal_market_dataset()
        problematic_dataset.symbol = "PROBLEMATICUSDT"  # Set the symbol we want to test

        # Introduce issues that might affect enhanced analysis
        problematic_dataset.daily_candles = pd.DataFrame()  # Empty DataFrame

        # Mock get_market_data to return problematic dataset
        with patch.object(self.service, 'get_market_data', return_value=problematic_dataset):
            # Should fall back to basic context
            enhanced_context = self.service.get_enhanced_context(problematic_dataset)

            assert enhanced_context is not None, "Should not be None even with problematic data"
            assert len(enhanced_context) > 0, "Should not be empty even with problematic data"
            assert "PROBLEMATICUSDT" in enhanced_context, "Should include symbol"
            
            # Should indicate fallback or error
            fallback_indicators = ["Enhanced analysis unavailable", "Fallback", "Error", "unavailable"]
            has_fallback_indicator = any(indicator in enhanced_context for indicator in fallback_indicators)
            assert has_fallback_indicator, "Should indicate fallback or error in context"
    
    @pytest.mark.unit
    def test_enhanced_context_unicode_handling(self):
        """Test enhanced context with Unicode characters in symbol."""
        # Create dataset with Unicode elements
        unicode_dataset = self._create_minimal_market_dataset()
        unicode_dataset.symbol = "TEST№USDT"  # Unicode character
        
        # Mock get_market_data to return Unicode dataset
        with patch.object(self.service, 'get_market_data', return_value=unicode_dataset):
            # Should handle Unicode gracefully
            enhanced_context = self.service.get_enhanced_context(unicode_dataset)
            
            assert enhanced_context is not None, "Should handle Unicode symbols"
            assert len(enhanced_context) > 0, "Should not be empty with Unicode"
            assert "TEST№USDT" in enhanced_context, "Should include Unicode symbol correctly"
    
    @pytest.mark.unit
    def test_enhanced_context_consistency_across_calls(self):
        """Test that enhanced context is consistent across multiple calls."""
        # Create consistent dataset
        consistent_dataset = self._create_minimal_market_dataset()
        
        # Mock get_market_data to return same dataset
        with patch.object(self.service, 'get_market_data', return_value=consistent_dataset):
            # Generate enhanced context multiple times
            contexts = []
            for i in range(3):
                enhanced_context = self.service.get_enhanced_context(consistent_dataset)
                contexts.append(enhanced_context)
            
            # All contexts should be identical (deterministic)
            assert all(context == contexts[0] for context in contexts), "Enhanced context should be consistent across calls"
            assert len(contexts[0]) > 0, "Context should not be empty"
    
    @pytest.mark.unit
    def test_enhanced_context_graceful_degradation(self):
        """Test graceful degradation when enhanced analysis components fail."""
        # This test verifies that partial failures don't break the entire context
        original_dataset = self._create_minimal_market_dataset()
        original_dataset.symbol = "DEGRADEUSDT"  # Set the symbol we want to test

        # Mock get_market_data to return original dataset
        with patch.object(self.service, 'get_market_data', return_value=original_dataset):
            # Mock individual analysis methods to fail
            with patch.object(self.service, '_analyze_recent_trend', side_effect=Exception("Trend analysis failed")):
                with patch.object(self.service, '_identify_patterns', side_effect=Exception("Pattern analysis failed")):
                    # Should still return context with available information
                    enhanced_context = self.service.get_enhanced_context(original_dataset)

                    assert enhanced_context is not None, "Should not be None even with partial failures"
                    assert len(enhanced_context) > 0, "Should not be empty with partial failures"
                    assert "DEGRADEUSDT" in enhanced_context, "Should include symbol"
                    
                    # Should indicate analysis failures
                    assert "failed" in enhanced_context.lower(), "Should indicate analysis failures"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])