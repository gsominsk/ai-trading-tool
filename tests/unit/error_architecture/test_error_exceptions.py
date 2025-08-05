"""
Error Architecture Unit Tests - Exception Classes

Tests for individual exception classes and their functionality:
- Exception hierarchy validation
- ErrorContext creation and functionality
- Backward compatibility with ValueError
- Exception-specific context fields
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal
from datetime import datetime

from src.market_data.exceptions import (
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
    DataInsufficientError,
    ErrorContext
)


class TestExceptionHierarchy:
    """Test exception hierarchy structure and inheritance."""
    
    def test_exception_hierarchy_structure(self):
        """Test that exception hierarchy is properly structured."""
        # Test inheritance hierarchy
        assert issubclass(ValidationError, MarketDataError)
        assert issubclass(ValidationError, ValueError)
        assert issubclass(NetworkError, MarketDataError)
        assert issubclass(ProcessingError, MarketDataError)
        
        # Test specific exceptions
        assert issubclass(SymbolValidationError, ValidationError)
        assert issubclass(DataFrameValidationError, ValidationError)
        assert issubclass(APIConnectionError, NetworkError)
        assert issubclass(RateLimitError, NetworkError)
        assert issubclass(APIResponseError, NetworkError)
        assert issubclass(CalculationError, ProcessingError)
        assert issubclass(DataInsufficientError, ProcessingError)
        
        # Test backward compatibility through inheritance
        assert issubclass(SymbolValidationError, ValueError)
        assert issubclass(DataFrameValidationError, ValueError)
    
    def test_validation_error_is_value_error(self):
        """Test that ValidationError maintains ValueError inheritance."""
        # Create ValidationError instance
        error = ValidationError("Test validation error")
        
        # Should be both types
        assert isinstance(error, ValueError)
        assert isinstance(error, MarketDataError)
        
        # Should pass isinstance checks that existing tests use
        assert isinstance(error, ValueError)
        
        # Should be catchable as ValueError (backward compatibility)
        try:
            raise error
        except ValueError as e:
            assert str(e).startswith("Test validation error [trace_id:")
        except Exception:
            pytest.fail("ValidationError should be catchable as ValueError")
    
    def test_symbol_validation_error_compatibility(self):
        """Test that SymbolValidationError works with existing symbol validation tests."""
        # Test the pattern from existing tests
        invalid_symbols = ["BTC", "ETH-USD", "bitcoin", "", "TOOLONGUSDT123", "123USDT"]
        
        for symbol in invalid_symbols:
            error = SymbolValidationError(
                f"Invalid symbol format: {symbol}",
                symbol=symbol
            )
            
            # Should maintain ValueError inheritance
            assert isinstance(error, ValueError)
            assert isinstance(error, ValidationError)
            assert isinstance(error, MarketDataError)
            
            # Should be catchable in existing test patterns
            try:
                raise error
            except ValueError:
                pass  # This should work (backward compatibility)
            except Exception:
                pytest.fail(f"SymbolValidationError for {symbol} should be catchable as ValueError")


class TestErrorContext:
    """Test ErrorContext functionality."""
    
    def test_error_context_functionality(self):
        """Test ErrorContext provides rich debugging information."""
        context = ErrorContext(operation="test_operation")
        
        # Should have required fields
        assert context.trace_id is not None
        assert context.operation == "test_operation"
        assert context.timestamp is not None
        assert isinstance(context.system_info, dict)
        assert isinstance(context.stack_trace, list)
        
        # Should convert to dict for logging
        context_dict = context.to_dict()
        assert "trace_id" in context_dict
        assert "operation" in context_dict
        assert "timestamp" in context_dict
        assert "system_info" in context_dict
        assert "stack_depth" in context_dict
    
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


class TestMarketDataError:
    """Test MarketDataError base functionality."""
    
    def test_market_data_error_rich_context(self):
        """Test MarketDataError provides rich context for debugging."""
        error = MarketDataError(
            "Test error message",
            operation="test_operation",
            symbol="BTCUSDT",
            additional_field="additional_value"
        )
        
        # Should have rich context
        context = error.get_context()
        assert context["error_type"] == "MarketDataError"
        assert context["message"] == "Test error message"
        assert context["operation"] == "test_operation"
        assert context["symbol"] == "BTCUSDT"
        assert context["additional_field"] == "additional_value"
        assert "trace_id" in context
        assert "timestamp" in context
    
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


class TestNetworkErrors:
    """Test NetworkError specific functionality."""
    
    def test_network_error_api_context(self):
        """Test NetworkError provides API-specific context."""
        error = APIConnectionError(
            "Failed to connect to Binance API",
            api_name="Binance",
            endpoint="/api/v3/klines",
            status_code=500
        )
        
        assert isinstance(error, NetworkError)
        assert isinstance(error, MarketDataError)
        assert error.endpoint == "/api/v3/klines"
        assert error.status_code == 500
        
        context = error.get_context()
        assert context["api_name"] == "Binance"
        assert context["endpoint"] == "/api/v3/klines"
        assert context["status_code"] == 500
    
    def test_rate_limit_error_retry_context(self):
        """Test RateLimitError provides retry information."""
        error = RateLimitError(
            "API rate limit exceeded",
            retry_after=60,
            limit_type="requests_per_minute"
        )
        
        assert isinstance(error, NetworkError)
        assert error.status_code == 429
        assert error.retry_after == 60
        assert error.limit_type == "requests_per_minute"
        
        context = error.get_context()
        assert context["status_code"] == 429
        assert context["retry_after"] == 60
        assert context["limit_type"] == "requests_per_minute"


class TestProcessingErrors:
    """Test ProcessingError specific functionality."""
    
    def test_processing_error_calculation_context(self):
        """Test ProcessingError provides calculation-specific context."""
        input_data = {
            "prices": [Decimal("50000.12345678"), Decimal("50100.98765432")],
            "periods": 14,
            "data_type": "RSI"
        }
        
        error = CalculationError(
            "RSI calculation failed due to insufficient data",
            indicator_type="RSI",
            calculation_step="gains_losses",
            input_data=input_data
        )
        
        assert isinstance(error, ProcessingError)
        assert isinstance(error, MarketDataError)
        assert error.calculation_type == "RSI_calculation"
        
        context = error.get_context()
        assert context["indicator_type"] == "RSI"
        assert context["calculation_step"] == "gains_losses"
        # Input data should be sanitized for logging
        assert "input_data" in context
        assert "prices" in context["input_data"]
    
    def test_data_insufficient_error_specific_context(self):
        """Test DataInsufficientError provides specific period information."""
        error = DataInsufficientError(
            "Need at least 20 periods for MA calculation, got 15",
            required_periods=20,
            available_periods=15,
            data_type="moving_average"
        )
        
        assert isinstance(error, ProcessingError)
        assert error.required_periods == 20
        assert error.available_periods == 15
        assert error.data_type == "moving_average"
        
        context = error.get_context()
        assert context["required_periods"] == 20
        assert context["available_periods"] == 15
        assert context["data_type"] == "moving_average"


class TestValidationErrors:
    """Test ValidationError specific functionality."""
    
    def test_dataframe_validation_error_structure(self):
        """Test DataFrameValidationError provides DataFrame-specific context."""
        error = DataFrameValidationError(
            "OHLC logic validation failed: High price lower than Low price",
            dataframe_type="daily_candles",
            validation_type="ohlc_logic"
        )
        
        assert isinstance(error, ValidationError)
        assert isinstance(error, ValueError)  # Backward compatibility
        assert error.field_name == "dataframe"
        
        context = error.get_context()
        assert context["dataframe_type"] == "daily_candles"
        assert context["validation_type"] == "ohlc_logic"
        assert context["expected_format"] == "Valid daily_candles DataFrame structure"


class TestExceptionStringRepresentation:
    """Test exception string representations."""
    
    def test_exception_string_representation(self):
        """Test that exceptions have useful string representations."""
        # Test base MarketDataError
        error1 = MarketDataError(
            "Base error message",
            operation="test_op",
            symbol="BTCUSDT"
        )
        error_str = str(error1)
        assert "Base error message" in error_str
        assert "[trace_id:" in error_str
        assert "[symbol: BTCUSDT]" in error_str
        
        # Test ValidationError
        error2 = ValidationError(
            "Validation failed",
            field_name="symbol",
            field_value="INVALID"
        )
        error_str2 = str(error2)
        assert "Validation failed" in error_str2
        assert "[trace_id:" in error_str2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])