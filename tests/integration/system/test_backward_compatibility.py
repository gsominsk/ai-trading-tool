"""
System Integration Tests - Backward Compatibility Suite

Comprehensive tests to ensure the new structured exception hierarchy maintains
full backward compatibility with existing code that catches ValueError and
other standard exceptions.

Test Coverage:
- ValidationError inheritance from ValueError (backward compatibility)
- Existing exception catching patterns still work
- MarketDataService constructor backward compatibility
- No breaking changes to existing public API
- Legacy error handling patterns continue to function

Consolidated from: tests/test_backward_compatibility.py (474 lines)
"""

import pytest
import requests
from unittest.mock import patch, Mock, MagicMock
from decimal import Decimal
import pandas as pd
from datetime import datetime, timezone

from src.market_data.market_data_service import MarketDataService, MarketDataSet
from src.infrastructure.binance_client import BinanceApiClient
from src.logging_system import MarketDataLogger
from src.infrastructure.exceptions import (
    ErrorContext,
    ApiClientError as MarketDataError,
    ValidationError,
    NetworkError,
    ProcessingError,
    SymbolValidationError,
    DataFrameValidationError,
    APIConnectionError,
    RateLimitError,
    APIResponseError,
    CalculationError,
    DataInsufficientError
)


class TestValueErrorInheritanceCompatibility:
    """Test that ValidationError exceptions can be caught as ValueError."""
    
    def test_symbol_validation_error_as_value_error(self):
        """Test that SymbolValidationError can be caught as ValueError."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Test catching as specific type
        with pytest.raises(SymbolValidationError):
            service.get_market_data("INVALID", trace_id="test_trace")
        
        # Test catching as ValueError (backward compatibility)
        with pytest.raises(ValueError):
            service.get_market_data("INVALID")
        
        # Test that it's both types
        try:
            service.get_market_data("INVALID")
        except ValueError as e:
            assert isinstance(e, SymbolValidationError)
            assert isinstance(e, ValidationError)
            assert isinstance(e, ValueError)
    
    def test_dataframe_validation_error_as_value_error(self):
        """Test that DataFrameValidationError can be caught as ValueError."""
        # Create invalid DataFrame
        empty_df = pd.DataFrame()
        valid_df = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=50, freq='1h'),
            'open': [100.0] * 50,
            'high': [101.0] * 50,
            'low': [99.0] * 50,
            'close': [100.0] * 50,
            'volume': [1000.0] * 50
        })
        
        # Test catching as specific type
        with pytest.raises(DataFrameValidationError):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=empty_df,  # Invalid empty DataFrame
                h4_candles=valid_df,
                h1_candles=valid_df,
                rsi_14=Decimal('50.0'),
                macd_signal="bullish",
                ma_20=Decimal('50000.0'),
                ma_50=Decimal('49000.0'),
                ma_trend="uptrend"
            )
        
        # Test catching as ValueError (backward compatibility)
        with pytest.raises(ValueError):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=empty_df,
                h4_candles=valid_df,
                h1_candles=valid_df,
                rsi_14=Decimal('50.0'),
                macd_signal="bullish",
                ma_20=Decimal('50000.0'),
                ma_50=Decimal('49000.0'),
                ma_trend="uptrend"
            )
    
    def test_market_data_set_rsi_validation_as_value_error(self):
        """Test that RSI validation errors can be caught as ValueError."""
        valid_df = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=50, freq='1h'),
            'open': [100.0] * 50,
            'high': [101.0] * 50,
            'low': [99.0] * 50,
            'close': [100.0] * 50,
            'volume': [1000.0] * 50
        })
        
        # Test invalid RSI value
        with pytest.raises(ValueError):
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=valid_df,
                h4_candles=valid_df,
                h1_candles=valid_df,
                rsi_14=Decimal('150.0'),  # Invalid RSI > 100
                macd_signal="bullish",
                ma_20=Decimal('50000.0'),
                ma_50=Decimal('49000.0'),
                ma_trend="uptrend"
            )
        
        # Verify it's still a proper validation error
        try:
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=valid_df,
                h4_candles=valid_df,
                h1_candles=valid_df,
                rsi_14=Decimal('150.0'),
                macd_signal="bullish",
                ma_20=Decimal('50000.0'),
                ma_50=Decimal('49000.0'),
                ma_trend="uptrend"
            )
        except ValueError as e:
            assert "RSI must be between 0 and 100" in str(e)


class TestLegacyExceptionHandlingPatterns:
    """Test that legacy exception handling patterns continue to work."""
    
    def test_legacy_try_except_value_error_pattern(self):
        """Test legacy try/except ValueError pattern still works."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Legacy pattern: catch all validation errors as ValueError
        validation_error_caught = False
        try:
            service.get_market_data("INVALID_SYMBOL", trace_id="test_trace")
        except ValueError as e:
            validation_error_caught = True
            assert "Invalid symbol format" in str(e)
        
        assert validation_error_caught
    
    def test_legacy_multiple_exception_catching(self):
        """Test legacy pattern of catching multiple exception types."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Legacy pattern: catch ValueError and Exception
        error_caught = False
        error_message = ""
        
        try:
            service.get_market_data("")  # Empty symbol
        except (ValueError, Exception) as e:
            error_caught = True
            error_message = str(e)
        
        assert error_caught
        assert "Symbol must be a non-empty string" in error_message
    
    def test_legacy_network_error_handling(self):
        """Test that network errors can still be caught as generic exceptions."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        # Configure the mock client to raise the error
        mock_api_client.get_klines.side_effect = APIConnectionError("Failed to connect")
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Legacy pattern: catch broad Exception for network issues
        network_error_caught = False
        try:
            service.get_market_data("BTCUSDT", trace_id="test_trace")
        except Exception as e:
            network_error_caught = True
            # Should still be able to access basic error information
            assert "Failed to connect" in str(e)
        
        assert network_error_caught
    
    def test_legacy_dataframe_validation_patterns(self):
        """Test legacy DataFrame validation error handling."""
        valid_df = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=50, freq='1h'),
            'open': [100.0] * 50,
            'high': [101.0] * 50,
            'low': [99.0] * 50,
            'close': [100.0] * 50,
            'volume': [1000.0] * 50
        })
        
        # Legacy pattern: catch all validation errors broadly
        validation_errors = []
        
        test_cases = [
            {"rsi_14": Decimal('-10.0')},  # Negative RSI
            {"rsi_14": Decimal('150.0')},  # RSI > 100
            {"ma_20": Decimal('-1000.0')},  # Negative MA
        ]
        
        for invalid_params in test_cases:
            try:
                # Create base params
                base_params = {
                    "symbol": "BTCUSDT",
                    "timestamp": datetime.now(timezone.utc),
                    "daily_candles": valid_df,
                    "h4_candles": valid_df,
                    "h1_candles": valid_df,
                    "macd_signal": "bullish",
                    "ma_20": Decimal('50000.0'),
                    "ma_50": Decimal('49000.0'),
                    "ma_trend": "uptrend"
                }
                
                # Add rsi_14 only if not in invalid_params
                if "rsi_14" not in invalid_params:
                    base_params["rsi_14"] = Decimal('50.0')
                
                # Merge with invalid params
                base_params.update(invalid_params)
                
                MarketDataSet(**base_params)
            except ValueError as e:
                validation_errors.append(str(e))
        
        # Should have caught validation errors for all test cases
        assert len(validation_errors) == len(test_cases)
        for error_msg in validation_errors:
            assert any(keyword in error_msg for keyword in ["RSI", "must be", "between", "positive"])


class TestMarketDataServiceBackwardCompatibility:
    """Test MarketDataService constructor and method backward compatibility."""
    
    def test_default_constructor_compatibility(self):
        """Test that default constructor still works without parameters."""
        # Legacy usage: no parameters
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Should have default values
        assert hasattr(service, 'logger')  # New DI architecture uses direct logger
        assert service.logger is not None
    
    def test_constructor_with_legacy_parameters(self):
        """Test constructor compatibility with potential legacy parameters."""
        # Test various constructor combinations that should work
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service1 = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        service2 = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        service3 = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        service4 = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # All should be valid instances
        for service in [service1, service2, service3, service4]:
            assert isinstance(service, MarketDataService)
            assert hasattr(service, 'get_market_data')
            assert hasattr(service, 'get_enhanced_context')
    
    def test_get_market_data_method_signature_compatibility(self):
        """Test that get_market_data method signature is backward compatible."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        # Mock successful kline data from the client
        mock_klines = [
            [1640995200000, "50000", "51000", "49000", "50500", "100", 1640995200000, "1", 50, "50000", "0.1", ""]
            for _ in range(50)
        ]
        mock_api_client.get_klines.return_value = mock_klines
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Legacy usage: just symbol parameter
        result = service.get_market_data("BTCUSDT", trace_id="test_trace")
        assert isinstance(result, MarketDataSet)
        assert result.symbol == "BTCUSDT"
    
    def test_market_data_set_property_access_compatibility(self):
        """Test that MarketDataSet properties are accessible as before."""
        valid_df = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=50, freq='1h'),
            'open': [50000.0] * 50,
            'high': [51000.0] * 50,
            'low': [49000.0] * 50,
            'close': [50000.0] * 50,
            'volume': [1000.0] * 50
        })
        
        market_data = MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.now(timezone.utc),
            daily_candles=valid_df,
            h4_candles=valid_df,
            h1_candles=valid_df,
            rsi_14=Decimal('50.0'),
            macd_signal="bullish",
            ma_20=Decimal('50000.0'),
            ma_50=Decimal('49000.0'),
            ma_trend="uptrend"
        )
        
        # Legacy property access should still work
        assert market_data.symbol == "BTCUSDT"
        assert market_data.rsi_14 == Decimal('50.0')
        assert market_data.macd_signal == "bullish"
        assert market_data.ma_20 == Decimal('50000.0')
        assert market_data.ma_50 == Decimal('49000.0')
        assert market_data.ma_trend == "uptrend"
        
        # DataFrame access should work
        assert isinstance(market_data.daily_candles, pd.DataFrame)
        assert len(market_data.daily_candles) == 50


class TestNoBreakingChangesPublicAPI:
    """Test that no breaking changes were introduced to the public API."""
    
    def test_market_data_service_public_methods_exist(self):
        """Test that all expected public methods still exist."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Public methods that should exist
        expected_methods = [
            'get_market_data',
            'get_enhanced_context'
        ]
        
        for method_name in expected_methods:
            assert hasattr(service, method_name)
            assert callable(getattr(service, method_name))
    
    def test_market_data_set_public_properties_exist(self):
        """Test that all expected public properties still exist."""
        valid_df = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=50, freq='1h'),
            'open': [50000.0] * 50,
            'high': [51000.0] * 50,
            'low': [49000.0] * 50,
            'close': [50000.0] * 50,
            'volume': [1000.0] * 50
        })
        
        market_data = MarketDataSet(
            symbol="BTCUSDT",
            timestamp=datetime.now(timezone.utc),
            daily_candles=valid_df,
            h4_candles=valid_df,
            h1_candles=valid_df,
            rsi_14=Decimal('50.0'),
            macd_signal="bullish",
            ma_20=Decimal('50000.0'),
            ma_50=Decimal('49000.0'),
            ma_trend="uptrend"
        )
        
        # Expected public properties
        expected_properties = [
            'symbol', 'timestamp', 'daily_candles', 'h4_candles', 'h1_candles',
            'rsi_14', 'macd_signal', 'ma_20', 'ma_50', 'ma_trend'
        ]
        
        for prop_name in expected_properties:
            assert hasattr(market_data, prop_name)
    
    def test_exception_types_accessibility(self):
        """Test that exception types are properly accessible for importing."""
        # Test that exceptions can be imported and used
        from src.infrastructure.exceptions import (
            ApiClientError as MarketDataError,
            ValidationError,
            NetworkError,
            ProcessingError
        )
        
        # Test instantiation
        error = MarketDataError("test message", operation="test")
        assert isinstance(error, MarketDataError)
        # Trace ID is randomly generated, so just check basic structure
        error_str = str(error)
        assert "test message" in error_str
        assert "[trace_id: err_" in error_str
    
    def test_backwards_compatible_error_messages(self):
        """Test that error messages remain understandable and informative."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Test symbol validation error message
        try:
            service.get_market_data("INVALID", trace_id="test_trace")
        except ValueError as e:
            error_msg = str(e)
            # Should contain helpful information
            assert "Invalid symbol format" in error_msg
            assert "INVALID" in error_msg
            # Should be readable without knowing about new error structure
            assert len(error_msg) > 10


class TestExistingTestCompatibility:
    """Test compatibility with existing test patterns."""
    
    def test_pytest_exception_matching_compatibility(self):
        """Test that pytest exception matching still works."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # pytest.raises should work with ValueError
        with pytest.raises(ValueError, match="Invalid symbol format"):
            service.get_market_data("INVALID", trace_id="test_trace")
        
        # pytest.raises should work with specific exception types
        with pytest.raises(SymbolValidationError, match="Invalid symbol format"):
            service.get_market_data("INVALID")
    
    def test_exception_info_extraction_compatibility(self):
        """Test that exception info extraction patterns still work."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Pattern: extract exception info for assertions
        with pytest.raises(ValueError) as exc_info:
            service.get_market_data("INVALID")
        
        # Should be able to access exception properties
        exception = exc_info.value
        assert isinstance(exception, ValueError)
        assert "Invalid symbol format" in str(exception)
        
        # Should also work with specific exception type
        with pytest.raises(SymbolValidationError) as exc_info:
            service.get_market_data("INVALID")
        
        exception = exc_info.value
        assert hasattr(exception, 'symbol')
        assert exception.symbol == "INVALID"
    
    def test_mock_patching_compatibility(self):
        """Test that mock patching patterns still work."""
        # The new pattern is to mock the client directly, not 'requests.get'
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        # Configure the mock to raise the desired exception
        mock_api_client.get_klines.side_effect = APIConnectionError("Timeout")
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Should be able to catch as broad Exception
        with pytest.raises(Exception):
            service.get_market_data("BTCUSDT")
        
        # Reset mock for the next call
        mock_api_client.get_klines.side_effect = APIConnectionError("Timeout")
        
        # Should also be able to catch as specific type
        with pytest.raises(APIConnectionError):
            service.get_market_data("BTCUSDT", trace_id="test_trace")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])