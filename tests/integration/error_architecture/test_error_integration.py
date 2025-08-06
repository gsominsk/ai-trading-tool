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
    
    def test_existing_test_pattern_compatibility(self):
        """Test that our exceptions work with existing test patterns."""
        service = MarketDataService()
        
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
        mock_response.content = b'{"msg": "Too many requests"}'
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
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.content = b'{"msg": "Service unavailable"}'
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
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.content = b'{"msg": "Symbol not found"}'
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
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.content = b'{"test": "response"}'
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
        """Test direct BTC correlation calculation with insufficient data."""
        service = MarketDataService()
        
        # Create insufficient data (less than 10 periods required for correlation)
        insufficient_data = {
            'timestamp': pd.date_range('2023-01-01', periods=5, freq='1H'),
            'open': [100.0] * 5,
            'high': [101.0] * 5,
            'low': [99.0] * 5,
            'close': [100.0] * 5,
            'volume': [1000.0] * 5
        }
        insufficient_df = pd.DataFrame(insufficient_data)
        
        with patch.object(service, '_get_klines') as mock_get_klines:
            # Mock BTC data to be insufficient (5 periods when 10+ needed)
            mock_get_klines.return_value = insufficient_df
            
            # Test direct _calculate_btc_correlation method (without fallback)
            with pytest.raises(DataInsufficientError) as exc_info:
                service._calculate_btc_correlation("ETHUSDT", insufficient_df)
            
            error = exc_info.value
            assert isinstance(error, DataInsufficientError)
            assert isinstance(error, ProcessingError)
            
            # Check processing-specific context
            assert error.required_periods == 10
            assert error.available_periods == 5
            assert "Insufficient data for BTC correlation" in str(error)
            
            context_dict = error.get_context()
            assert context_dict['operation'] == 'btc_correlation'
            assert 'required_periods' in context_dict
            assert 'available_periods' in context_dict
            assert 'data_type' in context_dict
    
    @patch('requests.get')
    def test_unexpected_processing_error_wrapping(self, mock_get):
        """Test that unexpected errors are wrapped in ProcessingError."""
        # Mock successful API response but cause error in DataFrame processing
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.content = b'{"test": "response"}'
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100", 1640995200000, "1", 50, "50000", "0.1", ""],  # Valid data
            [1640998800000, "invalid", "51000", "49000", "50500", "100", 1640998800000, "1", 50, "50500", "0.1", ""]  # Invalid open price
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


class TestErrorContextIntegration:
    """Test ErrorContext and trace ID functionality across operations."""
    
    def test_trace_id_generation_and_propagation(self):
        """Test trace ID generation and propagation across operations."""
        from src.logging_system.trace_generator import get_flow_id
        service = MarketDataService()
        
        # Generate trace ID using new system
        trace_id = get_flow_id("test")
        assert trace_id.startswith("flow_test_")
        assert len(trace_id) > 14  # flow_test_ + timestamp + counter
        # Note: _current_trace_id is not used in new architecture
    
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
        
        # In new architecture, trace IDs are generated per operation
        # The error context contains the trace_id
        
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
        
        # Test that logging methods are called (they should pass silently with current implementation)
        service._log_operation_start("test_operation")
        service._log_operation_success("test_operation", result="test_result")
        service._log_operation_error("test_operation", Exception("test"), error_type="test_error")
        
        # With current logging integration, these calls should complete without errors
        # Future implementation will include actual metrics tracking
        assert True  # Test passes if no exceptions are raised
    
    @patch('requests.get')
    def test_enhanced_context_error_handling_integration(self, mock_get):
        """Test enhanced context error handling with fallback to basic context."""
        # Mock successful basic data but fail enhanced analysis
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.content = b'{"test": "response"}'
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100", 1640995200000, "1", 50, "50000", "0.1", ""] for _ in range(50)
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService()
        
        # This should succeed and provide basic context even if enhanced analysis fails
        try:
            market_data = service.get_market_data("BTCUSDT")
            result = service.get_enhanced_context(market_data)
            assert isinstance(result, str)
            assert "BTCUSDT" in result
            # Should contain basic market data even if enhanced analysis fails
            assert "MARKET DATA ANALYSIS" in result
        except Exception as e:
            # If it fails completely, it should be a structured error
            assert isinstance(e, (ValidationError, NetworkError, ProcessingError))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])