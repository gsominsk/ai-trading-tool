"""
Error Architecture Integration Tests

Comprehensive integration tests for error handling across the system:
- SymbolValidationError integration with MarketDataService
- NetworkError handling with fallbacks and structured context
- ProcessingError graceful degradation scenarios
- ErrorContext and trace ID functionality across operations
- Logging integration points verification
"""

import pytest
import requests
from unittest.mock import patch, Mock, MagicMock
from decimal import Decimal
import pandas as pd
from datetime import datetime, timedelta, timezone

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


class TestSymbolValidationErrorIntegration:
    """Test SymbolValidationError integration with MarketDataService."""
    
    def test_invalid_symbol_format_integration(self):
        """Test that invalid symbol formats raise SymbolValidationError with proper context."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(SymbolValidationError) as exc_info:
            service.get_market_data("INVALID", trace_id="test_trace")
        
        error = exc_info.value
        assert isinstance(error, SymbolValidationError)
        assert isinstance(error, ValidationError)  # Inheritance check
        assert isinstance(error, ValueError)  # Backward compatibility
        
        # Check rich context
        assert error.symbol == "INVALID"
        assert error.field_name == "symbol"
        assert error.expected_format == "Valid trading pair format (e.g., BTCUSDT)"
        assert "Invalid symbol format" in str(error)
        
        # Check trace ID integration
        assert hasattr(error, 'context')
        assert hasattr(error.context, 'trace_id')
        assert error.context.trace_id == "test_trace"
        
        # Check context dictionary
        context_dict = error.get_context()
        assert context_dict['error_type'] == 'SymbolValidationError'
        assert context_dict['symbol'] == 'INVALID'
        assert context_dict['operation'] == 'validation'
    
    def test_empty_symbol_integration(self):
        """Test empty symbol handling with proper error context."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(SymbolValidationError) as exc_info:
            service.get_market_data("", trace_id="test_trace")
        
        error = exc_info.value
        assert error.symbol == ""
        assert "non-empty string" in str(error)
        assert error.context.operation == "symbol_validation"
    
    def test_multiple_usdt_occurrences_integration(self):
        """Test symbol with multiple USDT occurrences."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(SymbolValidationError) as exc_info:
            service.get_market_data("USDTUSDT", trace_id="test_trace")
        
        error = exc_info.value
        assert "Multiple USDT occurrences" in str(error)
        assert error.symbol == "USDTUSDT"
    
    def test_symbol_too_long_integration(self):
        """Test symbol validation for overly long symbols."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(SymbolValidationError) as exc_info:
            service.get_market_data("VERYLONGCOINUSDT", trace_id="test_trace")
        
        error = exc_info.value
        assert "Symbol too long" in str(error)
        assert error.symbol == "VERYLONGCOINUSDT"
    
    def test_base_currency_validation_integration(self):
        """Test base currency validation integration."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        test_cases = [
            "12USDT",      # Numbers in base currency
            "btcUSdt",     # Lowercase letters
            "AB USDT",     # Space in symbol
            "A1USDT",      # Mixed alphanumeric
        ]
        
        for invalid_symbol in test_cases:
            with pytest.raises(SymbolValidationError) as exc_info:
                service.get_market_data(invalid_symbol, trace_id="test_trace")
            
            error = exc_info.value
            assert error.symbol == invalid_symbol
            assert "Invalid base currency" in str(error) or "Invalid symbol format" in str(error)
    
    def test_existing_test_pattern_compatibility(self):
        """Test that our exceptions work with existing test patterns."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Test the pattern from test_symbol_validation_comprehensive.py
        invalid_symbols = ["BTC", "ETHBTC", "btcusdt", "", "TOOLONGUSDT"]
        
        for symbol in invalid_symbols:
            # The existing pattern expects ValueError to be raised
            try:
                # This will use existing service validation
                service._validate_symbol_input(symbol)
                pytest.fail(f"Symbol {symbol} should raise ValueError")
            except ValueError:
                # This should pass (backward compatibility maintained)
                pass
            except Exception as e:
                pytest.fail(f"Expected ValueError for {symbol}, got {type(e).__name__}: {e}")


class TestNetworkErrorIntegration:
    """Test NetworkError handling with fallbacks and structured context."""
    
    def test_api_timeout_integration(self):
        """Test API timeout handling with proper NetworkError context."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        # Configure the mock client to raise the exception
        mock_api_client.get_klines.side_effect = APIConnectionError(
            "Request timed out",
            operation="get_klines",
            endpoint="https://api.binance.com/api/v3/klines",
            context_data={"timeout_duration": 30}
        )
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(APIConnectionError) as exc_info:
            service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        error = exc_info.value
        assert isinstance(error, APIConnectionError)
        assert isinstance(error, NetworkError)
        assert isinstance(error, MarketDataError)
        
        # Check timeout-specific context
        assert "timed out" in str(error)
        assert error.operation == "get_klines"
        assert hasattr(error, 'endpoint')
        assert "api.binance.com" in error.endpoint
        
        # Check error context
        context_dict = error.get_context()
        assert context_dict['error_type'] == 'APIConnectionError'
        assert 'timeout_duration' in context_dict
        assert context_dict.get('timeout_duration') == 30
    
    def test_connection_error_integration(self):
        """Test connection error handling with structured context."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        mock_api_client.get_klines.side_effect = APIConnectionError(
            "Failed to connect to endpoint",
            operation="get_klines",
            context_data={"connection_error": "Network unreachable"}
        )
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(APIConnectionError) as exc_info:
            service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        error = exc_info.value
        assert "Failed to connect" in str(error)
        assert error.operation == "get_klines"
        
        # Check connection-specific context
        context_dict = error.get_context()
        assert 'connection_error' in context_dict
        assert "Network unreachable" in context_dict.get('connection_error')
    
    def test_rate_limit_error_integration(self):
        """Test rate limiting error with retry context."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        mock_api_client.get_klines.side_effect = RateLimitError(
            "API rate limit exceeded",
            retry_after=60,
            context_data={'rate_limit_type': 'request_weight'}
        )
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(RateLimitError) as exc_info:
            service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        error = exc_info.value
        assert isinstance(error, RateLimitError)
        assert isinstance(error, NetworkError)
        
        # Check rate limit specific context
        assert error.status_code == 429
        assert error.retry_after == 60
        assert "rate limit exceeded" in str(error)
        
        context_dict = error.get_context()
        assert context_dict['rate_limit_type'] == 'request_weight'
        assert context_dict['retry_after'] == 60
    
    def test_api_server_error_integration(self):
        """Test API server error (5xx) handling."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        mock_api_client.get_klines.side_effect = APIConnectionError(
            "API server error: 503",
            operation="get_klines",
            status_code=503
        )
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(APIConnectionError) as exc_info:
            service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        error = exc_info.value
        assert "server error: 503" in str(error)
        assert error.status_code == 503
        
        context_dict = error.get_context()
        assert context_dict['status_code'] == 503
    
    def test_invalid_symbol_api_error_integration(self):
        """Test 404 error for invalid symbol."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        mock_api_client.get_klines.side_effect = APIResponseError(
            "Symbol not found",
            status_code=404,
            response_body="Symbol not found"
        )
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(APIResponseError) as exc_info:
            service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        error = exc_info.value
        assert isinstance(error, APIResponseError)
        assert "not found" in str(error)
        assert error.status_code == 404
        
        context_dict = error.get_context()
        assert 'response_body' in context_dict
        assert context_dict['response_body'] == "Symbol not found"
    
    def test_malformed_api_response_integration(self):
        """Test malformed API response handling."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        # Simulate the client raising an error due to bad response format
        mock_api_client.get_klines.side_effect = APIResponseError(
            "Empty or invalid response from API",
            status_code=200,
            response_body="{}"
        )
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(APIResponseError) as exc_info:
            service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        error = exc_info.value
        assert "Empty or invalid response" in str(error)
        assert error.status_code == 200
        
        context_dict = error.get_context()
        assert 'response_body' in context_dict


class TestProcessingErrorIntegration:
    """Test ProcessingError graceful degradation scenarios."""
    
    def test_btc_correlation_processing_error(self):
        """Test direct BTC correlation calculation with insufficient data raises DataInsufficientError."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)

        # Mock data for the main symbol (ETHUSDT) - must be sufficient to pass validation
        timestamps = pd.date_range('2023-01-01', periods=35, freq='H')
        valid_raw_data = [
            [ts.value // 10**6, 100, 101, 99, 100, 1000] + [0]*6
            for ts in timestamps
        ]
        
        # Mock insufficient data for the BTCUSDT call inside the correlation calculation
        insufficient_raw_data = [
            [pd.Timestamp(f'2023-01-01 0{i}:00:00').value // 10**6, 100, 101, 99, 100, 1000] + [0]*6
            for i in range(5) # Only 5 data points, less than the required 10
        ]

        # We expect 3 successful calls for ETHUSDT (1d, 4h, 1h) and 1 call for BTCUSDT (1h)
        # The BTCUSDT call will receive insufficient data.
        mock_api_client.get_klines.side_effect = [valid_raw_data, valid_raw_data, valid_raw_data, insufficient_raw_data]

        # The error should be raised because the fallback mechanism was removed.
        with pytest.raises(DataInsufficientError) as exc_info:
            service.get_market_data("ETHUSDT", trace_id="test_trace")
            
        error = exc_info.value
        assert isinstance(error, DataInsufficientError)
        assert isinstance(error, ProcessingError)
        
        # Check processing-specific context
        assert "Insufficient data for BTC correlation" in str(error)
        
        context_dict = error.get_context()
        assert context_dict['operation'] == 'btc_correlation'
        assert context_dict['required_periods'] == 10
        assert context_dict['available_periods'] == 5
    
    def test_unexpected_processing_error_wrapping(self):
        """Test that unexpected errors are wrapped in ProcessingError."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        # This data will cause a ValueError when converting to a DataFrame due to "invalid"
        malformed_kline_data = [
            [1640995200000, "50000", "51000", "49000", "50500", "100", 1640995200000, "1", 50, "50000", "0.1", ""],
            [1640998800000, "invalid", "51000", "49000", "50500", "100", 1640998800000, "1", 50, "50500", "0.1", ""]
        ]
        mock_api_client.get_klines.return_value = malformed_kline_data
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # The service should wrap the internal ValueError in a ProcessingError
        with pytest.raises(ProcessingError) as exc_info:
            service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        error = exc_info.value
        assert isinstance(error, ProcessingError)
        assert "Unexpected error during market data aggregation" in str(error)
        assert 'Unable to parse string "invalid"' in str(error)
    
    def test_market_data_set_validation_integration(self):
        """Test MarketDataSet validation errors integration."""
        # Test invalid RSI value
        invalid_data = {
            'timestamp': pd.date_range('2023-01-01', periods=50, freq='1H'),
            'open': [100.0] * 50,
            'high': [101.0] * 50,
            'low': [99.0] * 50,
            'close': [100.0] * 50,
            'volume': [1000.0] * 50
        }
        df = pd.DataFrame(invalid_data)
        
        with pytest.raises(ValueError) as exc_info:
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=df,
                h4_candles=df,
                h1_candles=df,
                rsi_14=Decimal('150.0'),  # Invalid RSI > 100
                macd_signal="bullish",
                ma_20=Decimal('50000.0'),
                ma_50=Decimal('49000.0'),
                ma_trend="uptrend"
            )
        
        assert "RSI must be between 0 and 100" in str(exc_info.value)
    
    def test_dataframe_validation_error_integration(self):
        """Test DataFrame validation error integration."""
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        valid_df = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=50, freq='1H'),
            'open': [100.0] * 50,
            'high': [101.0] * 50,
            'low': [99.0] * 50,
            'close': [100.0] * 50,
            'volume': [1000.0] * 50
        })
        
        with pytest.raises(DataFrameValidationError) as exc_info:
            MarketDataSet(
                symbol="BTCUSDT",
                timestamp=datetime.now(timezone.utc),
                daily_candles=empty_df,  # Empty DataFrame
                h4_candles=valid_df,
                h1_candles=valid_df,
                rsi_14=Decimal('50.0'),
                macd_signal="bullish",
                ma_20=Decimal('50000.0'),
                ma_50=Decimal('49000.0'),
                ma_trend="uptrend"
            )
        
        error = exc_info.value
        assert isinstance(error, DataFrameValidationError)
        assert isinstance(error, ValidationError)
        assert "daily_candles cannot be empty" in str(error)
        assert error.dataframe_type == "daily_candles"
        assert error.validation_type == "empty_check"


class TestErrorContextIntegration:
    """Test ErrorContext and trace ID functionality across operations."""
    
    def test_trace_id_generation_and_propagation(self):
        """Test trace ID generation and propagation across operations."""
        from src.logging_system.trace_generator import get_trace_id
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Generate trace ID using new system
        trace_id = get_trace_id()
        assert trace_id.startswith("trd_")
        assert len(trace_id) > 20  # trd_ + session + timestamp + sequence
        # Note: _current_trace_id is not used in new architecture
    
    def test_trace_id_propagation_through_operations(self):
        """Test trace ID propagation through multiple operation calls."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        # Setup the mock to raise an error with a specific trace_id
        error_to_raise = APIConnectionError("Timeout")
        mock_api_client.get_klines.side_effect = error_to_raise
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        with pytest.raises(APIConnectionError) as exc_info:
            service.get_market_data("BTCUSDT", trace_id="test_trace_123")
        
        error = exc_info.value
        
        # Check that the original trace ID was propagated into the error
        assert hasattr(error, 'context')
        assert hasattr(error.context, 'trace_id')
        assert error.context.trace_id == "test_trace_123"
        
        # Error context should include the trace ID
        context_dict = error.get_context()
        assert context_dict['trace_id'] == "test_trace_123"


class TestLoggingIntegrationPoints:
    """Test logging integration points preparation (without actual logging)."""
    
    # NOTE: test_logging_enabled_configuration and test_fail_fast_configuration
    # have been removed as the attributes _enable_logging and _fail_fast
    # are no longer part of the MarketDataService design. Logging is implicitly
    # enabled by providing a logger, and fail-fast is handled by the caller.
    
    def test_operation_metrics_tracking(self):
        """Test operation metrics tracking for future logging integration."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # Test that logging methods are called (they should pass silently with current implementation)
        service._log_operation_start("test_operation")
        service._log_operation_success("test_operation", result="test_result")
        service._log_operation_error("test_operation", Exception("test"), error_type="test_error")
        
        # With current logging integration, these calls should complete without errors
        # Future implementation will include actual metrics tracking
        assert True  # Test passes if no exceptions are raised
    
    def test_enhanced_context_error_handling_integration(self):
        """Test enhanced context error handling with fallback to basic context."""
        mock_api_client = MagicMock(spec=BinanceApiClient)
        mock_logger = MagicMock(spec=MarketDataLogger)
        
        # Mock successful kline data
        mock_klines = [
            [1640995200000, "50000", "51000", "49000", "50500", "100", 1640995200000, "1", 50, "50000", "0.1", ""] for _ in range(50)
        ]
        mock_api_client.get_klines.return_value = mock_klines
        
        service = MarketDataService(api_client=mock_api_client, logger=mock_logger)
        
        # This should succeed and provide basic context even if enhanced analysis fails
        try:
            market_data = service.get_market_data("BTCUSDT", trace_id="test_trace_enh")
            
            # Now, simulate a failure within the enhanced context generation
            with patch.object(service, '_analyze_volume_relationship', side_effect=Exception("Volume relationship failed")):
                result = service.get_enhanced_context(market_data)
                
                assert isinstance(result, str)
                assert "BTCUSDT" in result
                # Should contain basic market data even if enhanced analysis fails
                assert "MARKET DATA ANALYSIS" in result
                assert "Volume Analysis: Analysis failed" in result # Check for graceful failure message
        except Exception as e:
            # If it fails completely, it should be a structured error
            pytest.fail(f"Service should not have failed completely, but got {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])