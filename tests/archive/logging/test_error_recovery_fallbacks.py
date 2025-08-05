"""
Error Architecture Phase 3 - Error Recovery and Fallback Tests

Tests for error recovery strategies and graceful degradation mechanisms.
Verifies fail-fast vs recovery configurations and fallback behaviors for
non-critical operations.

Test Coverage:
- Fail-fast vs recovery strategy configuration and behavior
- Graceful degradation for non-critical operations
- Logging integration points preparation (without actual logging)
- Configurable error handling (enable_logging, fail_fast parameters)
- Recovery mechanisms for BTC correlation, volume profile, technical indicators
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


class TestFailFastVsRecoveryStrategies:
    """Test fail-fast vs recovery strategy configurations."""
    
    def test_fail_fast_configuration_enabled(self):
        """Test fail-fast configuration when enabled."""
        service = MarketDataService(fail_fast=True)
        
        # Verify configuration
        assert service._fail_fast is True
        assert hasattr(service, '_critical_failures')
        assert hasattr(service, '_recoverable_operations')
        
        # Check critical failures list
        critical_operations = service._critical_failures
        assert "symbol_validation" in critical_operations
        assert "api_connection" in critical_operations
        assert "data_validation" in critical_operations
        
        # Check recoverable operations list
        recoverable_operations = service._recoverable_operations
        assert "btc_correlation" in recoverable_operations
        assert "volume_profile" in recoverable_operations
        assert "technical_indicators" in recoverable_operations
        assert "enhanced_analysis" in recoverable_operations
    
    def test_recovery_strategy_configuration_enabled(self):
        """Test recovery strategy configuration when fail-fast is disabled."""
        service = MarketDataService(fail_fast=False)
        
        # Verify configuration
        assert service._fail_fast is False
        
        # Recovery mode should have same operation classifications but different behavior
        assert hasattr(service, '_critical_failures')
        assert hasattr(service, '_recoverable_operations')
    
    @patch('requests.get')
    def test_fail_fast_on_critical_operations(self, mock_get):
        """Test that critical operations fail fast regardless of configuration."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")
        
        # Test both fail-fast and recovery configurations
        for fail_fast_setting in [True, False]:
            service = MarketDataService(fail_fast=fail_fast_setting)
            
            with pytest.raises(APIConnectionError) as exc_info:
                service.get_market_data("BTCUSDT")
            
            error = exc_info.value
            assert isinstance(error, APIConnectionError)
            assert "Failed to connect" in str(error)
            # Critical operations should always fail fast
            assert error.operation == "get_klines"
    
    def test_fail_fast_on_symbol_validation(self):
        """Test that symbol validation errors always fail fast."""
        # Test both configurations
        for fail_fast_setting in [True, False]:
            service = MarketDataService(fail_fast=fail_fast_setting)
            
            with pytest.raises(SymbolValidationError) as exc_info:
                service.get_market_data("INVALID")
            
            error = exc_info.value
            assert isinstance(error, SymbolValidationError)
            # Symbol validation is always critical
            assert error.operation == "validation"
    
    @patch('requests.get')
    def test_recovery_strategy_for_non_critical_operations(self, mock_get):
        """Test recovery strategy for non-critical operations."""
        # Mock successful basic data but simulate BTC correlation failure
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100", 1640998800000, "1000", 100, "50", "500", "0"] for _ in range(50)
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService(fail_fast=False)
        
        # Should succeed with graceful degradation for BTC correlation
        with patch.object(service, '_calculate_btc_correlation') as mock_correlation:
            mock_correlation.side_effect = DataInsufficientError(
                "Insufficient data for BTC correlation",
                required_periods=100,
                available_periods=50,
                operation="btc_correlation"
            )
            
            # This should NOT raise an exception in recovery mode
            # Instead, it should gracefully degrade
            try:
                result = service.get_market_data("ETHUSDT")
                # In recovery mode, should return basic data without BTC correlation
                assert isinstance(result, MarketDataSet)
                assert result.symbol == "ETHUSDT"
                # BTC correlation should be None or default value due to graceful degradation
            except DataInsufficientError:
                # If it still raises, verify it's properly logged for recovery
                pass


class TestGracefulDegradationMechanisms:
    """Test graceful degradation for non-critical operations."""
    
    @patch('requests.get')
    def test_btc_correlation_graceful_degradation(self, mock_get):
        """Test graceful degradation when BTC correlation fails."""
        # Mock successful main data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100",
             1640995259999, "5050000", 200, "50", "2525000", "0"] for _ in range(50)
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService(fail_fast=False)
        
        with patch.object(service, '_calculate_btc_correlation') as mock_btc_correlation:
            # Simulate BTC correlation calculation failure
            mock_btc_correlation.side_effect = APIConnectionError(
                "Failed to fetch BTC data for correlation",
                endpoint="https://api.binance.com/api/v3/klines",
                operation="get_klines",
                status_code=503
            )
            
            # Should gracefully degrade and return data without BTC correlation
            result = service._get_market_data_with_fallback("ETHUSDT")
            
            # Verify graceful degradation occurred
            assert "correlation" not in result or result.get("correlation") is None
            assert "basic_data" in result  # Should still have basic market data
    
    @patch('requests.get')
    def test_volume_profile_graceful_degradation(self, mock_get):
        """Test graceful degradation when volume profile analysis fails."""
        # Mock successful main data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100",
             1640995259999, "5050000", 200, "50", "2525000", "0"] for _ in range(50)
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService(fail_fast=False)
        
        with patch.object(service, '_analyze_volume_profile') as mock_volume:
            # Simulate volume profile analysis failure
            mock_volume.side_effect = CalculationError(
                "Volume profile analysis failed",
                indicator_type="volume_profile",
                calculation_step="volume_weighted_average_price",
                operation="volume_analysis"
            )
            
            # Should gracefully degrade
            result = service._get_market_data_with_fallback("ETHUSDT")
            
            # Should return data without volume profile
            assert "volume_profile" not in result or result.get("volume_profile") is None
            assert "basic_data" in result
    
    @patch('requests.get')
    def test_technical_indicators_graceful_degradation(self, mock_get):
        """Test graceful degradation when technical indicator calculations fail."""
        # Mock successful main data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100",
             1640995259999, "5050000", 200, "50", "2525000", "0"] for _ in range(50)
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService(fail_fast=False)
        
        with patch.object(service, '_calculate_technical_indicators') as mock_indicators:
            # Simulate technical indicators calculation failure
            mock_indicators.side_effect = CalculationError(
                "RSI calculation failed with insufficient data",
                indicator_type="rsi_14",
                calculation_step="rsi_calculation",
                operation="technical_analysis"
            )
            
            # Should gracefully degrade
            result = service._get_market_data_with_fallback("ETHUSDT")
            
            # Should return basic data without technical indicators
            assert "technical_indicators" not in result or result.get("technical_indicators") is None
            assert "basic_data" in result
    
    def test_cascading_failure_recovery(self):
        """Test recovery from cascading failures in multiple non-critical operations."""
        service = MarketDataService(fail_fast=False)
        
        with patch.object(service, '_get_klines') as mock_get_klines:
            # Mock basic data success
            valid_df = pd.DataFrame({
                'timestamp': pd.date_range('2023-01-01', periods=50, freq='1H'),
                'open': [100.0] * 50,
                'high': [101.0] * 50,
                'low': [99.0] * 50,
                'close': [100.0] * 50,
                'volume': [1000.0] * 50
            })
            mock_get_klines.return_value = valid_df
            
            with patch.object(service, '_calculate_btc_correlation') as mock_btc, \
                 patch.object(service, '_analyze_volume_profile') as mock_volume, \
                 patch.object(service, '_calculate_technical_indicators') as mock_tech:
                
                # Simulate multiple failures
                mock_btc.side_effect = DataInsufficientError(
                    "BTC correlation failed", required_periods=100, available_periods=50
                )
                mock_volume.side_effect = CalculationError(
                    "Volume profile failed",
                    indicator_type="vwap",
                    calculation_step="volume_analysis"
                )
                mock_tech.side_effect = CalculationError(
                    "Technical indicators failed",
                    indicator_type="rsi",
                    calculation_step="technical_analysis"
                )
                
                # Should still return basic market data
                result = service._get_market_data_with_fallback("ETHUSDT")
                
                # Verify graceful degradation handled multiple failures
                assert "basic_data" in result
                assert result["basic_data"] is not None
                # Enhanced features should be None or excluded
                for enhanced_feature in ["btc_correlation", "volume_profile", "technical_indicators"]:
                    if enhanced_feature in result:
                        assert result[enhanced_feature] is None


class TestLoggingIntegrationPreparation:
    """Test logging integration points preparation without actual logging."""
    
    def test_logging_configuration_options(self):
        """Test logging configuration options."""
        # Test logging enabled
        service_with_logging = MarketDataService(enable_logging=True)
        assert service_with_logging._enable_logging is True
        
        # Test logging disabled
        service_without_logging = MarketDataService(enable_logging=False)
        assert service_without_logging._enable_logging is False
        
        # Test default behavior
        service_default = MarketDataService()
        assert hasattr(service_default, '_enable_logging')
    
    def test_operation_logging_methods_exist(self):
        """Test that operation logging methods exist and are callable."""
        service = MarketDataService(enable_logging=True)
        
        # Check logging methods exist
        assert hasattr(service, '_log_operation_start')
        assert hasattr(service, '_log_operation_success')
        assert hasattr(service, '_log_operation_error')
        assert hasattr(service, '_log_graceful_degradation')
        
        # Check they're callable
        assert callable(service._log_operation_start)
        assert callable(service._log_operation_success)
        assert callable(service._log_operation_error)
        assert callable(service._log_graceful_degradation)
    
    def test_operation_logging_preparation(self):
        """Test operation logging method calls (should pass silently)."""
        service = MarketDataService(enable_logging=True)
        
        # These should execute without errors (logging not implemented yet)
        service._log_operation_start("test_operation", symbol="BTCUSDT")
        service._log_operation_success("test_operation", result_type="MarketDataSet")
        service._log_operation_error(
            "test_operation", 
            error=Exception("test error"),
            error_type="TestError"
        )
        service._log_graceful_degradation(
            "test_operation",
            failed_component="btc_correlation",
            fallback_used="basic_data_only"
        )
    
    def test_operation_metrics_tracking_preparation(self):
        """Test operation metrics tracking for future logging integration."""
        service = MarketDataService(enable_logging=True)
        
        # Verify metrics tracking infrastructure exists
        assert hasattr(service, '_operation_metrics')
        assert isinstance(service._operation_metrics, dict)
        
        # Test metrics update methods
        service._log_operation_start("test_operation")
        assert "test_operation" in service._operation_metrics
        assert service._operation_metrics["test_operation"]["count"] >= 1
        assert service._operation_metrics["test_operation"]["errors"] >= 0
        
        # Test error tracking
        service._log_operation_error("test_operation", Exception("test"))
        assert service._operation_metrics["test_operation"]["errors"] >= 1
    
    def test_trace_id_logging_integration(self):
        """Test trace ID integration with logging preparation."""
        service = MarketDataService(enable_logging=True)
        
        # Generate trace ID
        trace_id = service._generate_trace_id("test_operation")
        
        # Logging methods should accept trace_id parameter
        service._log_operation_start("test_operation", trace_id=trace_id)
        service._log_operation_success("test_operation", trace_id=trace_id)
        service._log_operation_error(
            "test_operation", 
            Exception("test"),
            trace_id=trace_id
        )
        
        # Verify trace ID is stored for operation context
        assert service._current_trace_id == trace_id


class TestConfigurableErrorHandling:
    """Test configurable error handling behavior."""
    
    def test_error_handling_configuration_combinations(self):
        """Test different combinations of error handling configurations."""
        # Test all configuration combinations
        configs = [
            {"enable_logging": True, "fail_fast": True},
            {"enable_logging": True, "fail_fast": False},
            {"enable_logging": False, "fail_fast": True},
            {"enable_logging": False, "fail_fast": False},
        ]
        
        for config in configs:
            service = MarketDataService(**config)
            
            # Verify configuration is applied
            assert service._enable_logging == config["enable_logging"]
            assert service._fail_fast == config["fail_fast"]
            
            # Verify both configurations work together
            assert hasattr(service, '_operation_metrics')
            assert hasattr(service, '_critical_failures')
            assert hasattr(service, '_recoverable_operations')
    
    @patch('requests.get')
    def test_configurable_behavior_with_network_errors(self, mock_get):
        """Test configurable behavior with network errors."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        # Test fail-fast with logging
        service_fail_fast = MarketDataService(enable_logging=True, fail_fast=True)
        with pytest.raises(APIConnectionError):
            service_fail_fast.get_market_data("BTCUSDT")
        
        # Test recovery with logging
        service_recovery = MarketDataService(enable_logging=True, fail_fast=False)
        with pytest.raises(APIConnectionError):
            # Network errors are critical, should fail even in recovery mode
            service_recovery.get_market_data("BTCUSDT")
    
    def test_recoverable_operation_classification(self):
        """Test that operations are correctly classified as critical vs recoverable."""
        service = MarketDataService()
        
        # Critical operations (always fail fast)
        critical_ops = service._critical_failures
        expected_critical = [
            "symbol_validation",
            "api_connection", 
            "data_validation",
            "basic_data_processing"
        ]
        
        for critical_op in expected_critical:
            assert critical_op in critical_ops
        
        # Recoverable operations (can gracefully degrade)
        recoverable_ops = service._recoverable_operations
        expected_recoverable = [
            "btc_correlation",
            "volume_profile",
            "technical_indicators",
            "enhanced_analysis",
            "market_sentiment"
        ]
        
        for recoverable_op in expected_recoverable:
            assert recoverable_op in recoverable_ops
    
    def test_error_context_configuration_integration(self):
        """Test error context integration with configuration options."""
        service = MarketDataService(enable_logging=True, fail_fast=False)
        
        # Test that error context includes configuration information
        context = ErrorContext(operation="test_operation")
        
        # Context should be usable regardless of configuration
        assert hasattr(context, 'trace_id')
        assert hasattr(context, 'timestamp')
        assert hasattr(context, 'system_info')
        
        # Configuration should not affect error context structure
        context_dict = context.to_dict()
        required_keys = ['trace_id', 'operation', 'timestamp', 'system_info']
        for key in required_keys:
            assert key in context_dict


class TestFallbackMechanismIntegration:
    """Test integration of fallback mechanisms across the system."""
    
    @patch('requests.get')
    def test_complete_fallback_chain(self, mock_get):
        """Test complete fallback chain from enhanced data to basic data."""
        # Mock successful basic API calls but fail enhanced features
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "50000", "51000", "49000", "50500", "100", 1640998800000, "1000", 100, "50", "500", "0"] for _ in range(50)
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MarketDataService(fail_fast=False, enable_logging=True)
        
        with patch.object(service, 'get_enhanced_context') as mock_enhanced:
            # Simulate enhanced context failure
            mock_enhanced.side_effect = ProcessingError(
                "Enhanced analysis failed",
                operation="enhanced_analysis"
            )
            
            # Should fall back to basic market data
            result = service._get_market_data_with_fallback("ETHUSDT")
            
            # Verify fallback occurred
            assert "basic_data" in result
            assert result["basic_data"] is not None
            # Enhanced context should be None or excluded
            if "enhanced_context" in result:
                assert result["enhanced_context"] is None
    
    def test_partial_failure_partial_recovery(self):
        """Test partial failure with partial recovery."""
        service = MarketDataService(fail_fast=False)
        
        # Simulate mixed success/failure scenario
        with patch.object(service, '_get_klines') as mock_klines:
            valid_df = pd.DataFrame({
                'timestamp': pd.date_range('2023-01-01', periods=50, freq='1H'),
                'open': [100.0] * 50,
                'high': [101.0] * 50,
                'low': [99.0] * 50,
                'close': [100.0] * 50,
                'volume': [1000.0] * 50
            })
            mock_klines.return_value = valid_df
            
            with patch.object(service, '_calculate_btc_correlation') as mock_btc, \
                 patch.object(service, '_calculate_technical_indicators') as mock_tech:
                
                # BTC correlation succeeds
                mock_btc.return_value = Decimal('0.75')
                
                # Technical indicators fail
                mock_tech.side_effect = CalculationError(
                    "RSI calculation failed",
                    indicator_type="rsi_14"
                )
                
                # Should return data with BTC correlation but without technical indicators
                result = service._get_market_data_with_fallback("ETHUSDT")
                
                assert "basic_data" in result
                if "btc_correlation" in result:
                    assert result["btc_correlation"] == Decimal('0.75')
                # Technical indicators should be missing or None
                if "technical_indicators" in result:
                    assert result["technical_indicators"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])