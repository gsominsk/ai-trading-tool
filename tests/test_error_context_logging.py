"""
Error Architecture Phase 3 - Error Context and Logging Preparation Tests

Comprehensive tests for error context functionality and logging integration
preparation. Tests trace ID generation, error context preservation, and
logging hooks without implementing actual logging.

Test Coverage:
- Trace ID generation and propagation across operations
- Error context preservation across multiple operation calls
- Logging hooks functionality without actual logging implementation
- Operation metrics tracking for future logging integration
- ErrorContext serialization and deserialization
- System information collection and validation
"""

import pytest
import requests
import json
import re
from unittest.mock import patch, Mock, MagicMock
from decimal import Decimal
import pandas as pd
from datetime import datetime, timedelta
import platform
import sys
import traceback

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


class TestTraceIDGenerationAndPropagation:
    """Test trace ID generation and propagation across operations."""
    
    def test_trace_id_generation_format(self):
        """Test trace ID generation format and uniqueness."""
        service = MarketDataService()
        
        # Test different operation prefixes
        test_operations = ["validation", "api_call", "processing", "analysis"]
        
        generated_ids = []
        for operation in test_operations:
            trace_id = service._generate_trace_id(operation)
            generated_ids.append(trace_id)
            
            # Check format: operation_XXXXXXXX (8 hex chars)
            assert trace_id.startswith(f"{operation}_")
            suffix = trace_id[len(operation) + 1:]
            assert len(suffix) == 8
            assert re.match(r'^[0-9a-f]{8}$', suffix), f"Invalid hex format: {suffix}"
        
        # All trace IDs should be unique
        assert len(set(generated_ids)) == len(generated_ids)
    
    def test_trace_id_storage_and_retrieval(self):
        """Test trace ID storage and retrieval in service."""
        service = MarketDataService()
        
        # Generate and store trace ID
        trace_id = service._generate_trace_id("test_operation")
        assert service._current_trace_id == trace_id
        
        # Generate another trace ID - should update current
        new_trace_id = service._generate_trace_id("another_operation")
        assert service._current_trace_id == new_trace_id
        assert new_trace_id != trace_id
    
    def test_error_context_trace_id_auto_generation(self):
        """Test automatic trace ID generation in ErrorContext."""
        context = ErrorContext(operation="test_operation")
        
        # Should auto-generate trace ID
        assert hasattr(context, 'trace_id')
        assert context.trace_id.startswith("err_")
        assert len(context.trace_id) == 12  # "err_" + 8 hex chars
        
        # Should be valid hex
        suffix = context.trace_id[4:]
        assert re.match(r'^[0-9a-f]{8}$', suffix)
    
    def test_error_context_custom_trace_id(self):
        """Test ErrorContext with custom trace ID."""
        custom_trace_id = "custom_12345678"
        context = ErrorContext(trace_id=custom_trace_id, operation="test_operation")
        
        assert context.trace_id == custom_trace_id
    
    @patch('requests.get')
    def test_trace_id_propagation_through_error_chain(self, mock_get):
        """Test trace ID propagation through the entire error chain."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        service = MarketDataService()
        
        with pytest.raises(APIConnectionError) as exc_info:
            service.get_market_data("BTCUSDT")
        
        error = exc_info.value
        
        # Check trace ID exists and follows format
        assert hasattr(error, 'context')
        assert hasattr(error.context, 'trace_id')
        trace_id = error.context.trace_id
        
        # Should be operation-specific trace ID
        assert "_" in trace_id
        operation_prefix = trace_id.split("_")[0]
        assert operation_prefix in ["get", "klines", "api", "fetch"]  # Likely operation prefixes
        
        # Service should store the same trace ID
        assert service._current_trace_id == trace_id
    
    def test_trace_id_consistency_across_operations(self):
        """Test trace ID consistency across multiple operations in same context."""
        service = MarketDataService()
        
        # Generate initial trace ID
        initial_trace_id = service._generate_trace_id("main_operation")
        
        # Simulate sub-operations using the same trace ID
        sub_operations = ["validate_symbol", "fetch_data", "process_data"]
        
        for sub_op in sub_operations:
            # In real implementation, sub-operations would use current trace ID
            current_trace_id = service._current_trace_id
            assert current_trace_id == initial_trace_id
            
            # Can generate new trace IDs for new operations
            new_trace_id = service._generate_trace_id(f"sub_{sub_op}")
            assert new_trace_id != initial_trace_id
            assert service._current_trace_id == new_trace_id


class TestErrorContextPreservation:
    """Test error context preservation across multiple operation calls."""
    
    def test_error_context_creation_completeness(self):
        """Test that ErrorContext contains all required information."""
        context = ErrorContext(operation="test_operation")
        
        # Required fields
        assert hasattr(context, 'trace_id')
        assert hasattr(context, 'operation')
        assert hasattr(context, 'timestamp')
        assert hasattr(context, 'system_info')
        assert hasattr(context, 'stack_trace')
        
        # Check field types and values
        assert isinstance(context.trace_id, str)
        assert isinstance(context.operation, str)
        assert isinstance(context.timestamp, str)
        assert isinstance(context.system_info, dict)
        assert isinstance(context.stack_trace, list)
        
        # Operation should be preserved
        assert context.operation == "test_operation"
        
        # Timestamp should be ISO format with Z
        assert context.timestamp.endswith("Z")
        datetime.fromisoformat(context.timestamp.replace("Z", "+00:00"))  # Should parse
    
    def test_error_context_system_info_collection(self):
        """Test system information collection in ErrorContext."""
        context = ErrorContext(operation="test_operation")
        system_info = context.system_info
        
        # Required system info fields
        required_fields = ['python_version', 'platform', 'trace_id', 'timestamp']
        for field in required_fields:
            assert field in system_info, f"Missing system info field: {field}"
        
        # Verify system info values
        assert system_info['python_version'] == sys.version
        assert system_info['platform'] == platform.platform()
        assert system_info['trace_id'] == context.trace_id
        assert system_info['timestamp'] == context.timestamp
    
    def test_error_context_stack_trace_collection(self):
        """Test stack trace collection in ErrorContext."""
        def nested_function():
            return ErrorContext(operation="nested_operation")
        
        def wrapper_function():
            return nested_function()
        
        context = wrapper_function()
        
        # Should have stack trace
        assert len(context.stack_trace) > 0
        
        # Stack trace should contain function names
        stack_trace_str = '\n'.join(context.stack_trace)
        assert 'nested_function' in stack_trace_str
        assert 'wrapper_function' in stack_trace_str
    
    def test_error_context_to_dict_serialization(self):
        """Test ErrorContext to_dict method for logging serialization."""
        context = ErrorContext(
            trace_id="test_trace_123",
            operation="test_operation"
        )
        
        context_dict = context.to_dict()
        
        # Required keys for logging
        required_keys = [
            'trace_id', 'operation', 'timestamp', 'system_info', 'stack_depth'
        ]
        for key in required_keys:
            assert key in context_dict
        
        # Verify values
        assert context_dict['trace_id'] == "test_trace_123"
        assert context_dict['operation'] == "test_operation"
        assert isinstance(context_dict['stack_depth'], int)
        assert context_dict['stack_depth'] > 0
        
        # Should be JSON serializable
        json_str = json.dumps(context_dict)
        assert isinstance(json_str, str)
        
        # Should be deserializable
        deserialized = json.loads(json_str)
        assert deserialized['trace_id'] == "test_trace_123"
    
    def test_market_data_error_context_preservation(self):
        """Test context preservation in MarketDataError hierarchy."""
        context = ErrorContext(
            trace_id="preserve_test_456",
            operation="preservation_test"
        )
        
        error = MarketDataError(
            message="Test preservation error",
            context=context,
            operation="preservation_test",
            symbol="TESTUSDT",
            custom_field="custom_value"
        )
        
        # Context should be preserved
        assert error.context == context
        assert error.context.trace_id == "preserve_test_456"
        assert error.context.operation == "preservation_test"
        
        # Error-specific context should be preserved
        assert error.operation == "preservation_test"
        assert error.symbol == "TESTUSDT"
        assert error.additional_context['custom_field'] == "custom_value"
        
        # Full context should be accessible
        full_context = error.get_context()
        assert full_context['trace_id'] == "preserve_test_456"
        assert full_context['operation'] == "preservation_test"
        assert full_context['symbol'] == "TESTUSDT"
        assert full_context['custom_field'] == "custom_value"
    
    def test_context_preservation_across_exception_inheritance(self):
        """Test context preservation across the exception inheritance chain."""
        context = ErrorContext(
            trace_id="inherit_test_789",
            operation="inheritance_test"
        )
        
        # Test with SymbolValidationError (inherits from ValidationError and ValueError)
        symbol_error = SymbolValidationError(
            "Invalid symbol test",
            symbol="INVALID",
            field_name="symbol",
            expected_format="XXXUSDT",
            context=context
        )
        
        # Context should be preserved at all inheritance levels
        assert symbol_error.context == context
        assert symbol_error.context.trace_id == "inherit_test_789"
        
        # Should work when caught as different types
        try:
            raise symbol_error
        except ValueError as e:
            assert hasattr(e, 'context')
            assert e.context.trace_id == "inherit_test_789"
        
        try:
            raise symbol_error
        except ValidationError as e:
            assert hasattr(e, 'context')
            assert e.context.trace_id == "inherit_test_789"
        
        try:
            raise symbol_error
        except MarketDataError as e:
            assert hasattr(e, 'context')
            assert e.context.trace_id == "inherit_test_789"


class TestLoggingHooksFunctionality:
    """Test logging hooks functionality without actual logging implementation."""
    
    def test_logging_methods_exist_and_callable(self):
        """Test that all required logging methods exist and are callable."""
        service = MarketDataService(enable_logging=True)
        
        # Required logging methods
        logging_methods = [
            '_log_operation_start',
            '_log_operation_success',
            '_log_operation_error',
            '_log_graceful_degradation'
        ]
        
        for method_name in logging_methods:
            assert hasattr(service, method_name)
            assert callable(getattr(service, method_name))
    
    def test_log_operation_start_functionality(self):
        """Test _log_operation_start method functionality."""
        service = MarketDataService(enable_logging=True)
        
        # Should execute without errors
        service._log_operation_start("test_operation")
        service._log_operation_start("test_operation", symbol="BTCUSDT")
        service._log_operation_start("test_operation", trace_id="test_123", symbol="ETHUSDT")
        
        # Should update operation metrics
        assert "test_operation" in service._operation_metrics
        assert service._operation_metrics["test_operation"]["count"] >= 1
    
    def test_log_operation_success_functionality(self):
        """Test _log_operation_success method functionality."""
        service = MarketDataService(enable_logging=True)
        
        # Initialize operation first
        service._log_operation_start("success_test")
        
        # Should execute without errors
        service._log_operation_success("success_test")
        service._log_operation_success("success_test", result_type="MarketDataSet")
        service._log_operation_success("success_test", trace_id="test_456", duration=1.5)
    
    def test_log_operation_error_functionality(self):
        """Test _log_operation_error method functionality."""
        service = MarketDataService(enable_logging=True)
        
        # Initialize operation first
        service._log_operation_start("error_test")
        
        test_error = ValueError("Test error message")
        
        # Should execute without errors
        service._log_operation_error("error_test", test_error)
        service._log_operation_error("error_test", test_error, error_type="ValueError")
        service._log_operation_error("error_test", test_error, trace_id="test_789")
        
        # Should update error metrics
        assert "error_test" in service._operation_metrics
        assert service._operation_metrics["error_test"]["errors"] >= 1
    
    def test_log_graceful_degradation_functionality(self):
        """Test _log_graceful_degradation method functionality."""
        service = MarketDataService(enable_logging=True)
        
        # Should execute without errors
        service._log_graceful_degradation("degradation_test")
        service._log_graceful_degradation(
            "degradation_test",
            failed_component="btc_correlation",
            fallback_used="basic_data_only"
        )
        service._log_graceful_degradation(
            "degradation_test",
            failed_component="volume_profile",
            fallback_used="no_volume_analysis",
            trace_id="degrade_123"
        )
    
    def test_logging_disabled_functionality(self):
        """Test that logging methods work when logging is disabled."""
        service = MarketDataService(enable_logging=False)
        
        # All logging methods should still be callable and not raise errors
        service._log_operation_start("disabled_test")
        service._log_operation_success("disabled_test")
        service._log_operation_error("disabled_test", Exception("test"))
        service._log_graceful_degradation("disabled_test")
        
        # Operation metrics should still be tracked
        assert hasattr(service, '_operation_metrics')
    
    def test_logging_parameter_validation(self):
        """Test logging method parameter validation and handling."""
        service = MarketDataService(enable_logging=True)
        
        # Test with various parameter combinations
        test_cases = [
            {"operation": "param_test"},
            {"operation": "param_test", "symbol": "BTCUSDT"},
            {"operation": "param_test", "trace_id": "trace_123"},
            {"operation": "param_test", "symbol": "ETHUSDT", "trace_id": "trace_456"},
            {"operation": "param_test", "extra_param": "extra_value"},
        ]
        
        for params in test_cases:
            # Should handle all parameter combinations gracefully
            service._log_operation_start(**params)
            service._log_operation_success(**params)


class TestOperationMetricsTracking:
    """Test operation metrics tracking for future logging integration."""
    
    def test_operation_metrics_initialization(self):
        """Test operation metrics initialization."""
        service = MarketDataService()
        
        # Should have operation metrics dictionary
        assert hasattr(service, '_operation_metrics')
        assert isinstance(service._operation_metrics, dict)
        
        # Should be empty initially
        assert len(service._operation_metrics) == 0
    
    def test_operation_metrics_tracking(self):
        """Test operation metrics tracking functionality."""
        service = MarketDataService()
        
        # Track some operations
        operations = ["op1", "op2", "op1", "op3", "op1"]
        
        for op in operations:
            service._log_operation_start(op)
        
        # Check metrics
        assert "op1" in service._operation_metrics
        assert "op2" in service._operation_metrics
        assert "op3" in service._operation_metrics
        
        # Check counts
        assert service._operation_metrics["op1"]["count"] == 3
        assert service._operation_metrics["op2"]["count"] == 1
        assert service._operation_metrics["op3"]["count"] == 1
        
        # Initial error counts should be 0
        assert service._operation_metrics["op1"]["errors"] == 0
        assert service._operation_metrics["op2"]["errors"] == 0
        assert service._operation_metrics["op3"]["errors"] == 0
    
    def test_error_metrics_tracking(self):
        """Test error metrics tracking functionality."""
        service = MarketDataService()
        
        # Initialize operations
        service._log_operation_start("error_op")
        service._log_operation_start("error_op")
        service._log_operation_start("success_op")
        
        # Log some errors
        service._log_operation_error("error_op", Exception("Error 1"))
        service._log_operation_error("error_op", Exception("Error 2"))
        
        # Check error counts
        assert service._operation_metrics["error_op"]["count"] == 2
        assert service._operation_metrics["error_op"]["errors"] == 2
        assert service._operation_metrics["success_op"]["count"] == 1
        assert service._operation_metrics["success_op"]["errors"] == 0
    
    def test_metrics_with_multiple_services(self):
        """Test that metrics are isolated between service instances."""
        service1 = MarketDataService()
        service2 = MarketDataService()
        
        # Log operations to different services
        service1._log_operation_start("service1_op")
        service2._log_operation_start("service2_op")
        
        # Metrics should be isolated
        assert "service1_op" in service1._operation_metrics
        assert "service1_op" not in service2._operation_metrics
        assert "service2_op" in service2._operation_metrics
        assert "service2_op" not in service1._operation_metrics
    
    def test_metrics_persistence_across_operations(self):
        """Test that metrics persist across multiple operations."""
        service = MarketDataService()
        
        # Perform multiple operations over time
        for i in range(5):
            service._log_operation_start("persistent_op")
            if i % 2 == 0:
                service._log_operation_error("persistent_op", Exception(f"Error {i}"))
            else:
                service._log_operation_success("persistent_op")
        
        # Metrics should accumulate
        metrics = service._operation_metrics["persistent_op"]
        assert metrics["count"] == 5
        assert metrics["errors"] == 3  # Errors at i=0, 2, 4
    
    @patch('requests.get')
    def test_real_operation_metrics_integration(self, mock_get):
        """Test metrics tracking with real operation calls."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        service = MarketDataService(enable_logging=True)
        
        # Perform operations that will fail
        for _ in range(3):
            try:
                service.get_market_data("BTCUSDT")
            except:
                pass  # Expected to fail
        
        # Should have tracked operations
        operation_names = list(service._operation_metrics.keys())
        assert len(operation_names) > 0
        
        # At least one operation should have been tracked
        total_count = sum(metrics["count"] for metrics in service._operation_metrics.values())
        total_errors = sum(metrics["errors"] for metrics in service._operation_metrics.values())
        
        assert total_count >= 3  # At least 3 attempts
        assert total_errors >= 3  # All should have failed


class TestErrorContextIntegrationWithLogging:
    """Test integration between error context and logging preparation."""
    
    def test_error_context_logging_serialization(self):
        """Test error context serialization for logging systems."""
        context = ErrorContext(
            trace_id="log_test_999",
            operation="logging_integration_test"
        )
        
        error = SymbolValidationError(
            "Logging integration test error",
            symbol="INVALID_LOG_TEST",
            field_name="symbol",
            expected_format="XXXUSDT",
            context=context
        )
        
        # Get full context for logging
        log_context = error.get_context()
        
        # Should be serializable to JSON
        json_str = json.dumps(log_context, default=str)  # Use default=str for Decimal serialization
        assert isinstance(json_str, str)
        
        # Should contain all necessary information for logging
        deserialized = json.loads(json_str)
        assert deserialized['trace_id'] == "log_test_999"
        assert deserialized['operation'] == "logging_integration_test"
        assert deserialized['error_type'] == "SymbolValidationError"
        assert deserialized['symbol'] == "INVALID_LOG_TEST"
    
    def test_structured_logging_preparation(self):
        """Test structured logging data preparation."""
        service = MarketDataService(enable_logging=True)
        
        # Generate trace ID
        trace_id = service._generate_trace_id("structured_log_test")
        
        # Create context with additional structured data
        context = ErrorContext(
            trace_id=trace_id,
            operation="structured_log_test"
        )
        
        # Create error with rich context
        error = APIConnectionError(
            "Structured logging test error",
            endpoint="https://api.example.com/test",
            status_code=503,
            timeout_duration=30,
            context=context
        )
        
        # Prepare structured log data
        log_data = error.get_context()
        
        # Should have structured fields suitable for logging systems
        assert 'trace_id' in log_data
        assert 'timestamp' in log_data
        assert 'error_type' in log_data
        assert 'operation' in log_data
        assert 'endpoint' in log_data
        assert 'status_code' in log_data
        assert 'timeout_duration' in log_data
        
        # Should be compatible with structured logging formats
        assert isinstance(log_data['status_code'], int)
        assert isinstance(log_data['timeout_duration'], int)
        assert isinstance(log_data['trace_id'], str)
    
    def test_log_correlation_with_trace_ids(self):
        """Test log correlation capabilities using trace IDs."""
        service = MarketDataService(enable_logging=True)
        
        # Start operation with trace ID
        trace_id = service._generate_trace_id("correlation_test")
        service._log_operation_start("correlation_test", trace_id=trace_id)
        
        # Create error with same trace ID
        context = ErrorContext(trace_id=trace_id, operation="correlation_test")
        error = ProcessingError(
            "Correlation test error",
            operation="correlation_test",
            context=context
        )
        
        # Log error with trace ID
        service._log_operation_error("correlation_test", error, trace_id=trace_id)
        
        # Both logs should be correlatable via trace ID
        assert service._current_trace_id == trace_id
        assert error.context.trace_id == trace_id
        
        # Error context should contain correlation information
        log_context = error.get_context()
        assert log_context['trace_id'] == trace_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])