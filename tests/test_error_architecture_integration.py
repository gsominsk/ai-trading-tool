"""
Error Architecture Phase 3 - Integration Tests

Comprehensive integration tests for MarketDataService error handling with
the new structured exception hierarchy. Tests actual error scenarios including
SymbolValidationError, NetworkError, and ProcessingError integration.

Test Coverage:
- SymbolValidationError integration with rich context
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
from datetime import datetime, timedelta

from src.market_data.market_data_service import MarketDataService, MarketDataSet
from src.market_data.exceptions import (
    ErrorContext,
    MarketDataError,
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
        service = MarketDataService()
        
        with pytest.raises(SymbolValidationError) as exc_info:
            service.get_market_data("INVALID")
        
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
        assert error.context.trace_id.startswith("err_")
        
        # Check context dictionary
        context_dict = error.get_context()
        assert context_dict['error_type'] == 'SymbolValidationError'
        assert context_dict['symbol'] == 'INVALID'
        assert context_dict['operation'] == 'validation'
    
    def test_empty_symbol_integration(self):
        """Test empty symbol handling with proper error context."""
        service = MarketDataService()
        
        with pytest.raises(SymbolValidationError) as exc_info:
            service.get_market_data("")
        
        error = exc_info.value
        assert error.symbol == ""
        assert "non-empty string" in str(error)
        assert error.context.operation == "validation"
    
    def test_multiple_usdt_occurrences_integration(self):
        """Test symbol with multiple USDT occurrences."""
        service = MarketDataService()
        
        with pytest.raises(SymbolValidationError) as exc_info:
            service.get_market_data("USDTUSDT")
        
        error = exc_info.value
        assert "Multiple USDT occurrences" in str(error)
        assert error.symbol == "USDTUSDT"
    
    def test_symbol_too_long_integration(self):
        """Test symbol validation for overly long symbols."""
        service = MarketDataService()
        
        with pytest.raises(SymbolValidationError) as exc_info:
            service.get_market_data("VERYLONGCOINUSDT")
        
        error = exc_info.value
        assert "Symbol too long" in str(error)
        assert error.symbol == "VERYLONGCOINUSDT"
    
    def test_base_currency_validation_integration(self):
        """Test base currency validation integration."""
        service = MarketDataService()
        test_cases = [
            "12USDT",      # Numbers in base currency
            "btcUSdt",     # Lowercase letters
            "AB USDT",     # Space in symbol
            "A1USDT",      # Mixed alphanumeric
        ]
        
        for invalid_symbol in test_cases:
            with pytest.raises(SymbolValidationError) as exc_info:
                service.get_market_data(invalid_symbol)
            
            error = exc_info.value
            assert error.symbol == invalid_symbol
            assert "Invalid base currency" in str(error) or "Invalid symbol format" in str(error)


class TestNetworkErrorIntegration:
    """Test NetworkError handling with fallbacks and structured context."""
    
    @patch('requests.get')
    def test_api_timeout_integration(self, mock_get):
        """Test API timeout handling with proper NetworkError context."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        service = MarketDataService()
        
        with pytest.raises(APIConnectionError) as exc_info:
            service.get_market_data("BTCUSDT")
        
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
        assert context_dict['timeout_duration'] == 30
    
    @patch('requests.get')
    def test_connection_error_integration(self, mock_get):
        """Test connection error handling with structured context."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")
        service = MarketDataService()
        
        with pytest.raises(APIConnectionError) as exc_info:
            service.get_market_data("BTCUSDT")
        
        error = exc_info.value
        assert "Failed to connect" in str(error)
        assert error.operation == "get_klines"
        
        # Check connection-specific context
        context_dict = error.get_context()
        assert 'connection_error' in context_dict
        assert "Network unreachable" in context_dict['connection_error']
    
    @patch('requests.get')
    def test_rate_limit_error_integration(self, mock_get):
        """Test rate limiting error with retry context."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        with pytest.raises(RateLimitError) as exc_info:
            service.get_market_data("BTCUSDT")
        
        error = exc_info.value
        assert isinstance(error, RateLimitError)
        assert isinstance(error, NetworkError)
        
        # Check rate limit specific context
        assert error.status_code == 429
        assert error.retry_after == '60'
        assert "rate limit exceeded" in str(error)
        
        context_dict = error.get_context()
        assert context_dict['rate_limit_type'] == 'request_weight'
        assert context_dict['retry_after'] == '60'
    
    @patch('requests.get')
    def test_api_server_error_integration(self, mock_get):
        """Test API server error (5xx) handling."""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("503 Service Unavailable")
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        with pytest.raises(APIConnectionError) as exc_info:
            service.get_market_data("BTCUSDT")
        
        error = exc_info.value
        assert "server error: 503" in str(error)
        assert error.status_code == 503
        
        context_dict = error.get_context()
        assert context_dict['status_code'] == 503
    
    @patch('requests.get')
    def test_invalid_symbol_api_error_integration(self, mock_get):
        """Test 404 error for invalid symbol."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Symbol not found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        with pytest.raises(APIResponseError) as exc_info:
            service.get_market_data("BTCUSDT")
        
        error = exc_info.value
        assert isinstance(error, APIResponseError)
        assert "not found" in str(error)
        assert error.status_code == 404
        
        context_dict = error.get_context()
        assert 'response_body' in context_dict
        assert context_dict['response_body'] == "Symbol not found"
    
    @patch('requests.get')
    def test_malformed_api_response_integration(self, mock_get):
        """Test malformed API response handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Empty response instead of list
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        with pytest.raises(APIResponseError) as exc_info:
            service.get_market_data("BTCUSDT")
        
        error = exc_info.value
        assert "Empty or invalid response" in str(error)
        assert error.status_code == 200
        
        context_dict = error.get_context()
        assert 'response_body' in context_dict


class TestProcessingErrorIntegration:
    """Test ProcessingError graceful degradation scenarios."""
    
    def test_btc_correlation_processing_error(self):
        """Test BTC correlation calculation with insufficient data."""
        service = MarketDataService()
        
        # Create minimal DataFrame that will pass basic validation but fail correlation
        minimal_data = {
            'timestamp': pd.date_range('2023-01-01', periods=5, freq='1H'),
            'open': [100.0] * 5,
            'high': [101.0] * 5,
            'low': [99.0] * 5,
            'close': [100.0] * 5,
            'volume': [1000.0] * 5
        }
        minimal_df = pd.DataFrame(minimal_data)
        
        with patch.object(service, '_get_klines') as mock_get_klines:
            # First call for ETH data - return minimal data
            # Second call for BTC data - return insufficient data
            mock_get_klines.side_effect = [
                minimal_df,  # daily_data for ETH
                minimal_df,  # h4_data for ETH  
                minimal_df,  # h1_data for ETH
                minimal_df.iloc[:5]  # BTC data with insufficient points
            ]
            
            with pytest.raises(DataInsufficientError) as exc_info:
                service.get_market_data("ETHUSDT")
            
            error = exc_info.value
            assert isinstance(error, DataInsufficientError)
            assert isinstance(error, ProcessingError)
            
            # Check processing-specific context
            assert error.required_periods == 10
            assert error.available_periods == 5
            assert "Insufficient data for BTC correlation" in str(error)
            
            context_dict = error.get_context()
            assert context_dict['operation'] == 'btc_correlation'
            assert 'required_data' in context_dict
            assert 'available_data' in context_dict
    
    @patch('requests.get')
    def test_unexpected_processing_error_wrapping(self, mock_get):
        """Test that unexpected errors are wrapped in ProcessingError."""
        # Mock successful API response but cause error in DataFrame processing
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100"],  # Valid data
            [1640998800000, "invalid", "51000", "49000", "50500", "100"]  # Invalid open price
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        with pytest.raises(APIResponseError) as exc_info:
            service.get_market_data("BTCUSDT")
        
        error = exc_info.value
        assert isinstance(error, APIResponseError)
        assert "Invalid numeric data" in str(error)
    
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
                timestamp=datetime.utcnow(),
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
                timestamp=datetime.utcnow(),
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


class TestErrorContextAndTraceIDFunctionality:
    """Test ErrorContext and trace ID functionality across operations."""
    
    def test_trace_id_generation_and_propagation(self):
        """Test trace ID generation and propagation across operations."""
        service = MarketDataService()
        
        # Generate trace ID
        trace_id = service._generate_trace_id("test_operation")
        assert trace_id.startswith("test_operation_")
        assert len(trace_id) == len("test_operation_") + 8  # operation + 8 hex chars
        assert service._current_trace_id == trace_id
    
    def test_error_context_creation(self):
        """Test ErrorContext creation with system information."""
        context = ErrorContext(operation="test_operation")
        
        # Check required fields
        assert hasattr(context, 'trace_id')
        assert hasattr(context, 'operation')
        assert hasattr(context, 'timestamp')
        assert hasattr(context, 'system_info')
        assert hasattr(context, 'stack_trace')
        
        # Check trace ID format
        assert context.trace_id.startswith("err_")
        assert len(context.trace_id) == 12  # "err_" + 8 hex chars
        
        # Check timestamp format (ISO format with Z)
        assert context.timestamp.endswith("Z")
        
        # Check system info structure
        system_info = context.system_info
        assert 'python_version' in system_info
        assert 'platform' in system_info
        assert 'trace_id' in system_info
        assert 'timestamp' in system_info
        
        # Check stack trace
        assert isinstance(context.stack_trace, list)
        assert len(context.stack_trace) > 0
    
    def test_error_context_to_dict(self):
        """Test ErrorContext to_dict conversion for logging."""
        context = ErrorContext(trace_id="test_123", operation="test_op")
        context_dict = context.to_dict()
        
        required_keys = ['trace_id', 'operation', 'timestamp', 'system_info', 'stack_depth']
        for key in required_keys:
            assert key in context_dict
        
        assert context_dict['trace_id'] == "test_123"
        assert context_dict['operation'] == "test_op"
        assert isinstance(context_dict['stack_depth'], int)
        assert context_dict['stack_depth'] > 0
    
    def test_market_data_error_context_integration(self):
        """Test MarketDataError context integration."""
        context = ErrorContext(trace_id="test_456", operation="test_operation")
        error = MarketDataError(
            message="Test error message",
            context=context,
            operation="test_operation",
            symbol="BTCUSDT",
            additional_field="test_value"
        )
        
        # Check basic properties
        assert error.message == "Test error message"
        assert error.context == context
        assert error.operation == "test_operation"
        assert error.symbol == "BTCUSDT"
        assert error.additional_context['additional_field'] == "test_value"
        
        # Check string representation
        error_str = str(error)
        assert "Test error message" in error_str
        assert "[trace_id: test_456]" in error_str
        assert "[symbol: BTCUSDT]" in error_str
        
        # Check context dictionary
        context_dict = error.get_context()
        assert context_dict['error_type'] == 'MarketDataError'
        assert context_dict['message'] == 'Test error message'
        assert context_dict['operation'] == 'test_operation'
        assert context_dict['symbol'] == 'BTCUSDT'
        assert context_dict['additional_field'] == 'test_value'
        assert context_dict['trace_id'] == 'test_456'
    
    @patch('requests.get')
    def test_trace_id_propagation_through_operations(self, mock_get):
        """Test trace ID propagation through multiple operation calls."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        service = MarketDataService()
        
        with pytest.raises(APIConnectionError) as exc_info:
            service.get_market_data("BTCUSDT")
        
        error = exc_info.value
        
        # Check that trace ID was generated and propagated
        assert hasattr(error, 'context')
        assert hasattr(error.context, 'trace_id')
        trace_id = error.context.trace_id
        
        # Trace ID should be consistent across the operation
        assert service._current_trace_id == trace_id
        
        # Error context should include the trace ID
        context_dict = error.get_context()
        assert context_dict['trace_id'] == trace_id


class TestLoggingIntegrationPoints:
    """Test logging integration points preparation (without actual logging)."""
    
    def test_logging_enabled_configuration(self):
        """Test logging enabled configuration."""
        service = MarketDataService(enable_logging=True)
        assert service._enable_logging is True
        
        # Test that logging methods are called (they should pass silently)
        service._log_operation_start("test_operation", test_param="value")
        service._log_operation_success("test_operation", result="success")
        service._log_operation_error("test_operation", Exception("test"), error_type="test")
    
    def test_fail_fast_configuration(self):
        """Test fail-fast vs recovery strategy configuration."""
        # Test fail-fast enabled
        service_fail_fast = MarketDataService(fail_fast=True)
        assert service_fail_fast._fail_fast is True
        
        # Test fail-fast disabled (recovery mode)
        service_recovery = MarketDataService(fail_fast=False)
        assert service_recovery._fail_fast is False
        
        # Check critical vs recoverable operations classification
        assert "symbol_validation" in service_recovery._critical_failures
        assert "api_connection" in service_recovery._critical_failures
        assert "btc_correlation" in service_recovery._recoverable_operations
        assert "volume_profile" in service_recovery._recoverable_operations
    
    def test_operation_metrics_tracking(self):
        """Test operation metrics tracking for future logging integration."""
        service = MarketDataService()
        
        # Simulate operation metrics tracking
        service._log_operation_start("test_operation")
        assert "test_operation" in service._operation_metrics
        assert service._operation_metrics["test_operation"]["count"] == 1
        assert service._operation_metrics["test_operation"]["errors"] == 0
        
        # Simulate error tracking
        service._log_operation_error("test_operation", Exception("test"))
        assert service._operation_metrics["test_operation"]["errors"] == 1
    
    @patch('requests.get')
    def test_enhanced_context_error_handling_integration(self, mock_get):
        """Test enhanced context error handling with fallback to basic context."""
        # Mock successful basic data but fail enhanced analysis
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100"] for _ in range(50)
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        # This should succeed and provide basic context even if enhanced analysis fails
        try:
            result = service.get_enhanced_context("BTCUSDT")
            assert isinstance(result, str)
            assert "BTCUSDT" in result
            # Should contain basic market data even if enhanced analysis fails
            assert "MARKET DATA ANALYSIS" in result
        except Exception as e:
            # If it fails completely, it should be a structured error
            assert isinstance(e, (ValidationError, NetworkError, ProcessingError))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])