"""
Core Market Data Service Unit Tests

Consolidated from 26 archived test files covering:
- Basic functionality validation
- Symbol validation  
- Data quality checks
- Decimal precision patterns
- Technical indicators (RSI, MACD, MA)
- Volume profile analysis
- Error handling patterns
"""

import pytest
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService, MarketDataSet


class TestMarketDataServiceCore:
    """Core unit tests for MarketDataService functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = MarketDataService()
    
    # =================
    # SYMBOL VALIDATION
    # =================
    
    def test_symbol_validation_valid_symbols(self):
        """Test validation of valid crypto symbols."""
        valid_symbols = [
            "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "SOLUSDT",
            "LINKUSDT", "ATOMUSDT", "AVAXUSDT", "MATICUSDT", "ALGOUSDT"
        ]
        
        for symbol in valid_symbols:
            # Should not raise exception
            self.service._validate_symbol_input(symbol)
    
    def test_symbol_validation_invalid_formats(self):
        """Test rejection of invalid symbol formats."""
        invalid_symbols = [
            ("", "Empty string"),
            ("BTC", "No USDT suffix"),
            ("ETHBTC", "Wrong suffix"),
            ("btcusdt", "Lowercase"),
            ("BTC123USDT", "Contains digits"),
            ("BTC-USDT", "Contains hyphen"),
            ("USDTUSDT", "USDT at start"),
            ("TOOLONGUSDT", "Too long base")
        ]
        
        for symbol, reason in invalid_symbols:
            with pytest.raises(ValueError):
                self.service._validate_symbol_input(symbol)
    
    # =================
    # DECIMAL PRECISION
    # =================
    
    def test_decimal_patterns_financial_precision(self):
        """Test that financial calculations use Decimal precision."""
        # Test recent trend analysis with high precision
        candles = [
            [0, "50000.123456789012345", "50100.000000000", "49900.000000000", "50000.123456789012345", "1000"],
            [0, "50000.123456789012345", "50150.000000000", "49950.000000000", "50050.234567890123456", "1000"],
            [0, "50050.234567890123456", "50200.000000000", "50000.000000000", "50100.345678901234567", "1000"],
        ]
        
        result = self.service._analyze_recent_trend(candles)
        assert result == "Strong Uptrend"
        
        # Test S/R analysis with high precision
        resistance_level = Decimal('50000.123456789012345')
        support_level = Decimal('49000.987654321098765')
        
        sr_result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        assert isinstance(sr_result, str)
    
    def test_decimal_boundary_precision(self):
        """Test decimal precision at calculation boundaries."""
        # Test with microscopic price differences
        candles = [
            [0, "50000.000000000000000000", "50000.100000000", "49999.900000000", "50000.000000000000000001", "1000"],
            [0, "50000.000000000000000001", "50000.100000000", "49999.900000000", "50000.000000000000000002", "1000"],
            [0, "50000.000000000000000002", "50000.100000000", "49999.900000000", "50000.000000000000000003", "1000"],
        ]
        
        result = self.service._analyze_recent_trend(candles)
        assert result == "Strong Uptrend"  # Decimal handles microscopic differences
    
    # =================
    # RSI CALCULATIONS
    # =================
    
    def test_rsi_division_by_zero_protection(self):
        """Test RSI calculation protection against division by zero."""
        # Only rising prices (loss = 0)
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
        
        rsi_rising = self.service._calculate_rsi(df_rising, 14)
        assert isinstance(rsi_rising, Decimal)
        assert rsi_rising == Decimal('100.0')  # Maximum RSI for only gains
        
        # Only falling prices (gain = 0)
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
        
        rsi_falling = self.service._calculate_rsi(df_falling, 14)
        assert isinstance(rsi_falling, Decimal)
        assert rsi_falling == Decimal('0.0')  # Minimum RSI for only losses
        
        # Constant prices (both gain and loss = 0)
        constant_prices = [100] * 16
        
        df_constant = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=16, freq='h'),
            'close': constant_prices,
            'open': constant_prices,
            'high': [p + 0.5 for p in constant_prices],
            'low': [p - 0.5 for p in constant_prices],
            'volume': [1000] * 16
        })
        
        rsi_constant = self.service._calculate_rsi(df_constant, 14)
        assert isinstance(rsi_constant, Decimal)
        assert rsi_constant == Decimal('50.0')  # Neutral RSI for no movement
    
    def test_rsi_normal_calculation(self):
        """Test RSI with normal mixed price data."""
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
        
        rsi_mixed = self.service._calculate_rsi(df_mixed, 14)
        assert isinstance(rsi_mixed, Decimal)
        assert Decimal('0') <= rsi_mixed <= Decimal('100')
    
    # =================
    # VOLUME PROFILE
    # =================
    
    def test_volume_profile_high_volume(self):
        """Test detection of high volume profile."""
        # Historical low, recent high (ratio > 1.5)
        volumes = [1000.0] * 20 + [2000.0] * 24
        
        df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=44, freq='1H'),
            'open': [50000.0] * 44,
            'high': [50100.0] * 44,
            'low': [49900.0] * 44,
            'close': [50000.0] * 44,
            'volume': volumes
        })
        
        result = self.service._analyze_volume_profile(df)
        assert result == "high"
    
    def test_volume_profile_low_volume(self):
        """Test detection of low volume profile."""
        # Historical high, recent low (ratio < 0.5)
        volumes = [2000.0] * 20 + [800.0] * 24
        
        df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=44, freq='1H'),
            'open': [50000.0] * 44,
            'high': [50100.0] * 44,
            'low': [49900.0] * 44,
            'close': [50000.0] * 44,
            'volume': volumes
        })
        
        result = self.service._analyze_volume_profile(df)
        assert result == "low"
    
    def test_volume_profile_normal_volume(self):
        """Test detection of normal volume profile."""
        # Consistent volume (0.5 <= ratio <= 1.5)
        volumes = [1000.0] * 44
        
        df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=44, freq='1H'),
            'open': [50000.0] * 44,
            'high': [50100.0] * 44,
            'low': [49900.0] * 44,
            'close': [50000.0] * 44,
            'volume': volumes
        })
        
        result = self.service._analyze_volume_profile(df)
        assert result == "normal"
    
    def test_volume_profile_zero_volume_protection(self):
        """Test volume profile protection against zero volume."""
        # Zero historical volume
        volumes = [0.0] * 20 + [1000.0] * 24
        
        df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=44, freq='1H'),
            'open': [50000.0] * 44,
            'high': [50100.0] * 44,
            'low': [49900.0] * 44,
            'close': [50000.0] * 44,
            'volume': volumes
        })
        
        result = self.service._analyze_volume_profile(df)
        assert result in ["high", "normal"]  # Should handle gracefully
        
        # All zero volume
        volumes_zero = [0.0] * 44
        
        df_zero = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=44, freq='1H'),
            'open': [50000.0] * 44,
            'high': [50100.0] * 44,
            'low': [49900.0] * 44,
            'close': [50000.0] * 44,
            'volume': volumes_zero
        })
        
        result_zero = self.service._analyze_volume_profile(df_zero)
        assert result_zero == "normal"  # Default for no meaningful comparison
    
    # =================
    # DATA QUALITY
    # =================
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        empty_df = pd.DataFrame()
        
        # Should handle empty DataFrame gracefully
        rsi_result = self.service._calculate_rsi(empty_df, 14)
        assert isinstance(rsi_result, Decimal)
        assert rsi_result == Decimal('50.0')  # Default neutral value
    
    def test_insufficient_data_handling(self):
        """Test handling of insufficient data."""
        # Less than required periods
        short_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='h'),
            'close': [100, 101, 102, 103, 104],
            'open': [100, 101, 102, 103, 104],
            'high': [100.5, 101.5, 102.5, 103.5, 104.5],
            'low': [99.5, 100.5, 101.5, 102.5, 103.5],
            'volume': [1000] * 5
        })
        
        rsi_short = self.service._calculate_rsi(short_data, 14)
        assert isinstance(rsi_short, Decimal)
        assert rsi_short == Decimal('50.0')  # Default for insufficient data
    
    def test_recent_trend_analysis_patterns(self):
        """Test recent trend analysis with various patterns."""
        # Strong uptrend
        uptrend_candles = [
            [0, "50000.000000000", "50100.000000000", "49900.000000000", "50000.000000000", "1000"],
            [0, "50000.000000000", "50100.000000000", "49900.000000000", "50050.000000000", "1000"],
            [0, "50050.000000000", "50100.000000000", "49900.000000000", "50100.000000000", "1000"],
        ]
        assert self.service._analyze_recent_trend(uptrend_candles) == "Strong Uptrend"
        
        # Strong downtrend
        downtrend_candles = [
            [0, "50100.000000000", "50200.000000000", "50000.000000000", "50100.000000000", "1000"],
            [0, "50100.000000000", "50150.000000000", "49950.000000000", "50050.000000000", "1000"],
            [0, "50050.000000000", "50100.000000000", "49900.000000000", "50000.000000000", "1000"],
        ]
        assert self.service._analyze_recent_trend(downtrend_candles) == "Strong Downtrend"
        
        # Sideways movement
        sideways_candles = [
            [0, "50000.000000000", "50100.000000000", "49900.000000000", "50000.000000000", "1000"],
            [0, "50000.000000000", "50100.000000000", "49900.000000000", "50025.000000000", "1000"],
            [0, "50025.000000000", "50100.000000000", "49900.000000000", "50000.000000000", "1000"],
        ]
        assert self.service._analyze_recent_trend(sideways_candles) == "Sideways"
        
        # Insufficient data
        short_candles = [
            [0, "50000.000000000", "50100.000000000", "49900.000000000", "50000.000000000", "1000"],
            [0, "50000.000000000", "50100.000000000", "49900.000000000", "50050.000000000", "1000"],
        ]
        assert self.service._analyze_recent_trend(short_candles) == "Insufficient data"
    
    def test_sr_tests_analysis(self):
        """Test support/resistance tests analysis."""
        resistance_level = Decimal('55000')
        support_level = Decimal('50000')
        
        # Multiple tests of both levels
        candles = [
            [0, "54500.000000000", "55000.000000000", "54000.000000000", "54800.000000000", "1000"],  # R test
            [0, "54800.000000000", "54999.999999999", "54200.000000000", "54900.000000000", "1000"],  # R test
            [0, "52000.000000000", "53000.000000000", "50000.000000000", "52500.000000000", "1000"],  # S test
            [0, "51000.000000000", "52000.000000000", "50100.000000000", "51500.000000000", "1000"],  # S test
            [0, "50500.000000000", "51500.000000000", "49999.999999999", "51000.000000000", "1000"],  # S test
        ]
        
        result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        assert result == "R:2 tests, S:3 tests"
        
        # No tests found
        no_test_candles = [
            [0, "55000.000000000", "56000.000000000", "54000.000000000", "55500.000000000", "1000"],
            [0, "55500.000000000", "56500.000000000", "54500.000000000", "56000.000000000", "1000"],
        ]
        
        no_test_result = self.service._analyze_sr_tests(no_test_candles, support_level, resistance_level)
        assert no_test_result == "No recent S/R tests"


@pytest.mark.unit
@pytest.mark.performance
class TestMarketDataPerformance:
    """Performance tests for MarketDataService."""
    
    def setup_method(self):
        """Setup for each test method."""
        import psutil
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
    
    @patch('requests.get')
    def test_api_response_processing_performance(self, mock_get):
        """Test API response processing speed."""
        import time
        
        # Mock large dataset response
        large_dataset = [[
            int(time.time() * 1000) - (200 - i) * 3600000,
            f"{50000 + i * 10}",
            f"{50000 + i * 10 + 500}",
            f"{50000 + i * 10 - 300}",
            f"{50000 + i * 10 + 100}",
            f"{1000 + i * 5}",
            int(time.time() * 1000) - (200 - i) * 3600000,
            "1000000",
            100,
            "500000",
            "250000",
            "0"
        ] for i in range(200)]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_dataset
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        start_time = time.time()
        result = service.get_market_data("BTCUSDT")
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Performance requirement: < 2 seconds for 200 data points
        assert processing_time < 2.0, f"Processing too slow: {processing_time:.2f}s"
        assert isinstance(result, MarketDataSet)
        
        print(f"✅ API processing: {processing_time:.2f}s for 200 data points")
    
    @patch('requests.get')
    def test_rsi_calculation_performance(self, mock_get):
        """Test RSI calculation performance with large datasets."""
        import time
        
        # Create dataset for RSI calculation
        large_dataset = [[
            int(time.time() * 1000) - (500 - i) * 3600000,
            f"{50000 + i * 2 + (i % 10) - 5}",  # Varying prices
            f"{50000 + i * 2 + (i % 10)}",
            f"{50000 + i * 2 + (i % 10) - 10}",
            f"{50000 + i * 2 + (i % 10) - 2}",
            f"{1000 + i * 3}",
            int(time.time() * 1000) - (500 - i) * 3600000,
            "1000000",
            100,
            "500000",
            "250000",
            "0"
        ] for i in range(500)]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_dataset
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        start_time = time.time()
        result = service.get_market_data("BTCUSDT")
        rsi_calculation_time = time.time() - start_time
        
        # Performance requirement: RSI calculation < 3 seconds for 500 points
        assert rsi_calculation_time < 3.0, f"RSI calculation too slow: {rsi_calculation_time:.2f}s"
        assert isinstance(result.rsi_14, Decimal)
        
        print(f"✅ RSI calculation: {rsi_calculation_time:.2f}s for 500 data points")
    
    @patch('requests.get')
    def test_memory_efficiency_during_operations(self, mock_get):
        """Test memory efficiency during multiple operations."""
        import time
        
        # Setup mock for consistent responses
        dataset = [[
            int(time.time() * 1000) - (100 - i) * 3600000,
            f"{50000 + i}",
            f"{50000 + i + 100}",
            f"{50000 + i - 100}",
            f"{50000 + i + 50}",
            f"{1000}",
            int(time.time() * 1000) - (100 - i) * 3600000,
            "1000000",
            100,
            "500000",
            "250000",
            "0"
        ] for i in range(100)]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = dataset
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        # Perform multiple operations and monitor memory
        for i in range(10):
            result = service.get_market_data("BTCUSDT")
            basic_context = result.to_llm_context_basic()
            
            # Check memory every few operations
            if i % 3 == 2:
                current_memory = self.process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - self.initial_memory
                
                # Memory should not grow excessively
                assert memory_increase < 100, f"Memory usage too high: {memory_increase:.1f}MB"
        
        final_memory = self.process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - self.initial_memory
        
        print(f"✅ Memory usage for 10 operations: +{total_increase:.1f}MB")
        assert total_increase < 100, f"Total memory increase too high: {total_increase:.1f}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])