"""
Test backward compatibility of new exception hierarchy with existing ValueError tests.

This test ensures that the new MarketDataService exception hierarchy maintains
backward compatibility with existing tests that expect ValueError to be raised.
"""

import pytest
from unittest.mock import Mock
from decimal import Decimal
from datetime import datetime

# Import our new exceptions
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

# Import existing service to test integration
from src.market_data.market_data_service import MarketDataService


class TestExceptionHierarchyBackwardCompatibility:
    """Test backward compatibility with existing ValueError expectations."""
    
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
            assert str(e) == "Test validation error [trace_id: " + error.context.trace_id + "]"
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


if __name__ == "__main__":
    # Run basic compatibility check
    print("Testing exception hierarchy backward compatibility...")
    
    # Test that ValidationError can be caught as ValueError
    try:
        raise ValidationError("Test error")
    except ValueError as e:
        print(f"✅ ValidationError caught as ValueError: {e}")
    
    # Test SymbolValidationError compatibility
    try:
        raise SymbolValidationError("Invalid symbol", "INVALID")
    except ValueError as e:
        print(f"✅ SymbolValidationError caught as ValueError: {e}")
    
    print("All backward compatibility tests passed!")