"""
MarketDataService Exception Hierarchy

This module provides a structured exception system for the MarketDataService
with rich context for debugging and logging integration. Designed to maintain
backward compatibility with existing ValueError tests while providing
foundation for upcoming logging system implementation.

Design Principles:
- Financial safety through comprehensive error context
- Backward compatibility with existing tests
- Rich debugging information for production environments
- Integration-ready for logging tasks 24-36
"""

import sys
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal


class ErrorContext:
    """
    Error context class providing trace ID support and system information
    for debugging and logging integration.
    
    This class collects system information and maintains trace IDs
    to support the logging architecture defined in tasks 24-36.
    """
    
    def __init__(self, trace_id: Optional[str] = None, operation: Optional[str] = None):
        """
        Initialize error context with trace ID and system information.
        
        Args:
            trace_id: Optional trace ID for logging correlation
            operation: The operation being performed when error occurred
        """
        self.trace_id = trace_id or f"err_{uuid.uuid4().hex[:8]}"
        self.operation = operation
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.system_info = self._collect_system_info()
        self.stack_trace = self._get_stack_trace()
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for debugging context."""
        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp
        }
    
    def _get_stack_trace(self) -> List[str]:
        """Get current stack trace for debugging context."""
        return traceback.format_stack()[:-1]  # Exclude current frame
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary for logging."""
        return {
            "trace_id": self.trace_id,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "system_info": self.system_info,
            "stack_depth": len(self.stack_trace)
        }


class MarketDataError(Exception):
    """
    Base exception class for all MarketDataService errors.
    
    Provides rich context for debugging and logging integration while
    maintaining backward compatibility. All MarketDataService exceptions
    should inherit from this base class.
    
    Features:
    - Rich error context with trace IDs
    - System information collection
    - Integration-ready for logging system
    - Financial safety emphasis
    """
    
    def __init__(
        self, 
        message: str, 
        context: Optional[ErrorContext] = None,
        operation: Optional[str] = None,
        symbol: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize MarketDataError with rich context.
        
        Args:
            message: Human-readable error message
            context: ErrorContext instance for debugging
            operation: The operation being performed
            symbol: The trading symbol involved (if applicable)
            **kwargs: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.context = context or ErrorContext(operation=operation)
        self.operation = operation
        self.symbol = symbol
        self.additional_context = kwargs
        
    def get_context(self) -> Dict[str, Any]:
        """Get complete error context for logging and debugging."""
        context_dict = self.context.to_dict()
        context_dict.update({
            "error_type": self.__class__.__name__,
            "message": self.message,
            "operation": self.operation,
            "symbol": self.symbol,
            **self.additional_context
        })
        return context_dict
    
    def __str__(self) -> str:
        """String representation with trace ID for debugging."""
        base_msg = self.message
        if self.context.trace_id:
            base_msg += f" [trace_id: {self.context.trace_id}]"
        if self.symbol:
            base_msg += f" [symbol: {self.symbol}]"
        return base_msg


class ValidationError(MarketDataError, ValueError):
    """
    Validation error with backward compatibility for existing tests.
    
    This class inherits from both MarketDataError (for rich context)
    and ValueError (for backward compatibility with existing tests).
    
    Used for:
    - Input validation failures
    - Data format validation errors
    - Parameter validation issues
    """
    
    def __init__(
        self, 
        message: str, 
        field_name: Optional[str] = None,
        field_value: Any = None,
        expected_format: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize ValidationError with field-specific context.
        
        Args:
            message: Error message
            field_name: Name of the field that failed validation
            field_value: The invalid value
            expected_format: Description of expected format
            **kwargs: Additional context
        """
        super().__init__(
            message, 
            operation="validation",
            field_name=field_name,
            field_value=str(field_value) if field_value is not None else None,
            expected_format=expected_format,
            **kwargs
        )
        self.field_name = field_name
        self.field_value = field_value
        self.expected_format = expected_format


class NetworkError(MarketDataError):
    """
    Network-related errors for API connection issues.
    
    Used for:
    - API connection failures
    - Timeout errors
    - HTTP response errors
    - Rate limiting issues
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[str] = None,
        endpoint: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize NetworkError with network-specific context.

        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
            response_data: Response data from API
            endpoint: API endpoint that failed
            **kwargs: Additional context
        """
        # Set default operation if not provided
        if 'operation' not in kwargs:
            kwargs['operation'] = "network_request"
        
        super().__init__(
            message,
            status_code=status_code,
            response_data=response_data,
            endpoint=endpoint,
            **kwargs
        )
        self.status_code = status_code
        self.response_data = response_data
        self.endpoint = endpoint


class ProcessingError(MarketDataError):
    """
    Data processing and calculation errors.
    
    Used for:
    - Mathematical calculation failures
    - Data processing errors
    - Algorithm execution issues
    - Financial calculation problems
    """
    
    def __init__(
        self,
        message: str,
        calculation_type: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize ProcessingError with calculation-specific context.

        Args:
            message: Error message
            calculation_type: Type of calculation that failed
            input_data: Input data that caused the error
            **kwargs: Additional context
        """
        # Sanitize input_data for logging (convert Decimal to string)
        sanitized_input = {}
        if input_data:
            for key, value in input_data.items():
                if isinstance(value, Decimal):
                    sanitized_input[key] = str(value)
                elif hasattr(value, '__len__') and len(value) > 10:
                    # Truncate large data structures for logging
                    sanitized_input[key] = f"<{type(value).__name__} length={len(value)}>"
                else:
                    sanitized_input[key] = str(value)

        # Set default operation if not provided
        if 'operation' not in kwargs:
            kwargs['operation'] = "data_processing"

        super().__init__(
            message,
            calculation_type=calculation_type,
            input_data=sanitized_input,
            **kwargs
        )
        self.calculation_type = calculation_type
        self.input_data = input_data


# Specific Validation Exceptions

class SymbolValidationError(ValidationError):
    """
    Symbol validation specific error.
    
    Raised when trading symbol format or content is invalid.
    Maintains backward compatibility with existing symbol validation tests.
    """
    
    def __init__(self, message: str, symbol: str, **kwargs):
        # Remove conflicting parameters from kwargs to avoid conflicts
        kwargs.pop('field_name', None)
        kwargs.pop('field_value', None)
        kwargs.pop('operation', None)  # Remove operation conflict
        expected_format = kwargs.pop('expected_format', "Valid trading pair format (e.g., BTCUSDT)")
        
        super().__init__(
            message,
            field_name="symbol",
            field_value=symbol,
            expected_format=expected_format,
            symbol=symbol,
            **kwargs
        )


class DataFrameValidationError(ValidationError):
    """
    DataFrame validation specific error.
    
    Raised when DataFrame structure, content, or OHLC logic is invalid.
    Used for comprehensive validation failures in MarketDataSet.
    """
    
    def __init__(
        self,
        message: str,
        dataframe_type: str,
        validation_type: str,
        **kwargs
    ):
        self.dataframe_type = dataframe_type
        self.validation_type = validation_type
        super().__init__(
            message,
            field_name="dataframe",
            field_value=f"{dataframe_type} DataFrame",
            expected_format=f"Valid {dataframe_type} DataFrame structure",
            dataframe_type=dataframe_type,
            validation_type=validation_type,
            **kwargs
        )


# Specific Network Exceptions

class APIConnectionError(NetworkError):
    """
    API connection failure error.
    
    Raised when unable to establish connection to Binance API
    or other external data sources.
    """
    
    def __init__(self, message: str, api_name: str = "Binance", **kwargs):
        # Extract endpoint if provided, otherwise set default
        endpoint = kwargs.pop('endpoint', f"{api_name} API")
        super().__init__(
            message,
            endpoint=endpoint,
            api_name=api_name,
            **kwargs
        )


class RateLimitError(NetworkError):
    """
    API rate limiting error.
    
    Raised when API rate limits are exceeded.
    Provides context for retry logic and backoff strategies.
    """
    
    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None,
        limit_type: str = "requests",
        **kwargs
    ):
        super().__init__(
            message,
            status_code=429,
            retry_after=retry_after,
            limit_type=limit_type,
            **kwargs
        )
        self.retry_after = retry_after
        self.limit_type = limit_type


class APIResponseError(NetworkError):
    """
    API response parsing or content error.
    
    Raised when API responds successfully but with invalid or unexpected data.
    """
    
    def __init__(
        self, 
        message: str, 
        response_format: str = "JSON",
        expected_fields: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            response_format=response_format,
            expected_fields=expected_fields,
            **kwargs
        )


# Specific Processing Exceptions

class CalculationError(ProcessingError):
    """
    Mathematical calculation error.
    
    Raised when financial calculations fail due to invalid data,
    mathematical constraints, or algorithm limitations.
    """
    
    def __init__(
        self, 
        message: str, 
        indicator_type: str,
        calculation_step: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            calculation_type=f"{indicator_type}_calculation",
            indicator_type=indicator_type,
            calculation_step=calculation_step,
            **kwargs
        )


class DataInsufficientError(ProcessingError):
    """
    Insufficient data for processing error.
    
    Raised when there's not enough data to perform required calculations
    or analysis. Common in technical indicator calculations.
    """
    
    def __init__(
        self, 
        message: str, 
        required_periods: int,
        available_periods: int,
        data_type: str = "candlestick",
        **kwargs
    ):
        super().__init__(
            message,
            calculation_type=f"{data_type}_analysis",
            required_periods=required_periods,
            available_periods=available_periods,
            data_type=data_type,
            **kwargs
        )
        self.required_periods = required_periods
        self.available_periods = available_periods
        self.data_type = data_type