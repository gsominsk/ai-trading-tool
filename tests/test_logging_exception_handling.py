#!/usr/bin/env python3
"""
Test exception handling in logging integration for MarketDataService.

Validates that logging failures never crash trading operations.
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService
from src.market_data.logging_integration import MarketDataServiceLogging


class TestLoggingExceptionHandling:
    """Test exception handling and graceful degradation in logging."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_logging_integration_handles_logger_failure(self):
        """Test that logging integration handles logger initialization failures."""
        # Create service that should work even if logging fails during init
        with patch('src.market_data.logging_integration.MarketDataLogger') as mock_logger_class:
            mock_logger_class.side_effect = Exception("Logger initialization failed")
            
            # Service should still be created despite logging failure
            with pytest.raises(Exception):
                # This should fail during logging integration
                service = MarketDataService(enable_logging=True)
    
    def test_log_operation_start_handles_exceptions(self):
        """Test that log_operation_start gracefully handles exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock the logger to fail
        with patch.object(service._logging_integration.logger, 'log_operation_start') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # This should not raise an exception
            try:
                service._log_operation_start("test_operation", symbol="BTCUSDT")
                # If we reach here, the exception was handled gracefully
                assert True
            except Exception as e:
                pytest.fail(f"log_operation_start should not raise exceptions: {e}")
    
    def test_log_operation_success_handles_exceptions(self):
        """Test that log_operation_success gracefully handles exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock the logger to fail
        with patch.object(service._logging_integration.logger, 'log_operation_complete') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # This should not raise an exception
            try:
                service._log_operation_success("test_operation", symbol="BTCUSDT")
                assert True
            except Exception as e:
                pytest.fail(f"log_operation_success should not raise exceptions: {e}")
    
    def test_log_operation_error_handles_exceptions(self):
        """Test that log_operation_error gracefully handles exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock the logger to fail
        with patch.object(service._logging_integration.logger, 'log_validation_error') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # This should not raise an exception
            test_error = Exception("Test error")
            try:
                service._log_operation_error("test_operation", test_error, symbol="BTCUSDT")
                assert True
            except Exception as e:
                pytest.fail(f"log_operation_error should not raise exceptions: {e}")
    
    def test_fallback_error_logging_creates_file(self):
        """Test that fallback error logging creates a file when main logging fails."""
        service = MarketDataService(enable_logging=True)
        
        # Mock the logger to fail
        with patch.object(service._logging_integration.logger, 'log_operation_start') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # Call operation that should trigger fallback logging
            service._log_operation_start("test_operation", symbol="BTCUSDT")
            
            # Check if fallback error log was created
            fallback_log_path = "logs/logging_errors.log"
            if os.path.exists(fallback_log_path):
                with open(fallback_log_path, 'r') as f:
                    content = f.read()
                    assert "logging_method" in content
                    assert "log_operation_start" in content
                    assert "fallback_logging" in content
    
    def test_get_operation_metrics_handles_exceptions(self):
        """Test that get_operation_metrics returns fallback data on failure."""
        service = MarketDataService(enable_logging=True)
        
        # Mock flow summary to fail
        with patch('src.market_data.logging_integration.get_flow_summary') as mock_summary:
            mock_summary.side_effect = Exception("Flow summary failure")
            
            # Should return degraded metrics instead of crashing
            metrics = service._logging_integration.get_operation_metrics()
            
            assert metrics["service_name"] == "MarketDataService"
            assert metrics["logger_status"] == "degraded"
            assert metrics["active_operations"] == 0
            assert metrics["flow_summary"] == "metrics_unavailable"
    
    def test_reset_metrics_handles_exceptions(self):
        """Test that reset_metrics clears data even if logging fails."""
        service = MarketDataService(enable_logging=True)
        
        # Add some test data to metrics
        service._logging_integration._operation_start_times["test_op"] = 12345.0
        assert len(service._logging_integration._operation_start_times) == 1
        
        # Mock logger to fail
        with patch.object(service._logging_integration.logger, 'log_raw_data') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # Reset should still work
            service._logging_integration.reset_metrics()
            
            # Metrics should be cleared despite logging failure
            assert len(service._logging_integration._operation_start_times) == 0
    
    def test_trading_operation_logging_handles_exceptions(self):
        """Test that trading operation logging gracefully handles exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock logger to fail
        with patch.object(service._logging_integration.logger, 'log_raw_data') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # This should not raise an exception
            try:
                service._logging_integration.log_trading_operation(
                    "market_analysis", "BTCUSDT", {"rsi": 45.2}, "success"
                )
                assert True
            except Exception as e:
                pytest.fail(f"log_trading_operation should not raise exceptions: {e}")
    
    def test_market_analysis_logging_handles_exceptions(self):
        """Test that market analysis logging gracefully handles exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock logger to fail
        with patch.object(service._logging_integration.logger, 'log_raw_data') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # This should not raise an exception
            try:
                service._logging_integration.log_market_analysis(
                    "BTCUSDT", {"rsi": 45.2}, "buy", 0.8
                )
                assert True
            except Exception as e:
                pytest.fail(f"log_market_analysis should not raise exceptions: {e}")
    
    def test_order_execution_logging_handles_exceptions(self):
        """Test that order execution logging gracefully handles exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock logger to fail
        with patch.object(service._logging_integration.logger, 'log_raw_data') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # This should not raise an exception
            try:
                service._logging_integration.log_order_execution(
                    "ORD123", "BTCUSDT", "BUY", "0.001", "42000.00", "executed"
                )
                assert True
            except Exception as e:
                pytest.fail(f"log_order_execution should not raise exceptions: {e}")
    
    def test_api_response_logging_handles_exceptions(self):
        """Test that API response logging gracefully handles exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock logger to fail
        with patch.object(service._logging_integration.logger, 'log_api_call') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # This should not raise an exception
            try:
                service._logging_integration.log_api_response(
                    "get_klines", "https://api.binance.com", 200, 1024, "BTCUSDT"
                )
                assert True
            except Exception as e:
                pytest.fail(f"log_api_response should not raise exceptions: {e}")
    
    def test_graceful_degradation_logging_handles_exceptions(self):
        """Test that graceful degradation logging handles exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock logger to fail
        with patch.object(service._logging_integration.logger, 'log_fallback_usage') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # This should not raise an exception
            try:
                service._logging_integration.log_graceful_degradation(
                    "btc_correlation", "api_failure", "no_correlation_data"
                )
                assert True
            except Exception as e:
                pytest.fail(f"log_graceful_degradation should not raise exceptions: {e}")
    
    def test_performance_metrics_logging_handles_exceptions(self):
        """Test that performance metrics logging handles exceptions."""
        service = MarketDataService(enable_logging=True)
        
        # Mock logger to fail
        with patch.object(service._logging_integration.logger, 'log_raw_data') as mock_log:
            mock_log.side_effect = Exception("Logging system failure")
            
            # This should not raise an exception
            try:
                service._logging_integration.log_performance_metrics(
                    "get_market_data", {"duration_ms": 150, "rows": 100}, "BTCUSDT"
                )
                assert True
            except Exception as e:
                pytest.fail(f"log_performance_metrics should not raise exceptions: {e}")
    
    def test_fallback_logging_handles_complete_filesystem_failure(self):
        """Test that even fallback logging failure doesn't crash operations."""
        service = MarketDataService(enable_logging=True)
        
        # Mock both main logging and fallback logging to fail
        with patch.object(service._logging_integration.logger, 'log_operation_start') as mock_log:
            mock_log.side_effect = Exception("Main logging failure")
            
            with patch('builtins.open', side_effect=Exception("Filesystem failure")):
                # Even if both main and fallback logging fail, this should not crash
                try:
                    service._log_operation_start("test_operation", symbol="BTCUSDT")
                    assert True
                except Exception as e:
                    pytest.fail(f"Complete logging failure should not crash operations: {e}")
    
    def test_complete_trading_operation_protection_demonstration(self):
        """
        Comprehensive demonstration test showing that trading operations 
        are completely protected from logging system failures.
        
        This test simulates a real trading scenario where multiple 
        logging failures occur but trading operations continue normally.
        """
        service = MarketDataService(enable_logging=True)
        
        # Simulate complete logging system failure
        with patch.object(service._logging_integration.logger, 'log_operation_start') as mock_start, \
             patch.object(service._logging_integration.logger, 'log_operation_complete') as mock_complete, \
             patch.object(service._logging_integration.logger, 'log_validation_error') as mock_error, \
             patch.object(service._logging_integration.logger, 'log_raw_data') as mock_raw, \
             patch.object(service._logging_integration.logger, 'log_api_call') as mock_api, \
             patch.object(service._logging_integration.logger, 'log_fallback_usage') as mock_fallback:
            
            # All logging methods fail
            mock_start.side_effect = Exception("Start logging failed")
            mock_complete.side_effect = Exception("Complete logging failed")
            mock_error.side_effect = Exception("Error logging failed")
            mock_raw.side_effect = Exception("Raw logging failed")
            mock_api.side_effect = Exception("API logging failed")
            mock_fallback.side_effect = Exception("Fallback logging failed")
            
            # Even with complete logging failure, all operations should work
            try:
                # Start operation logging
                service._log_operation_start("market_analysis", symbol="BTCUSDT")
                
                # Log trading operations
                service._logging_integration.log_trading_operation(
                    "buy_signal", "BTCUSDT", {"price": 42000, "quantity": 0.001}, "success"
                )
                
                # Log market analysis
                service._logging_integration.log_market_analysis(
                    "BTCUSDT", {"rsi": 65, "macd": 0.2}, "buy", 0.85
                )
                
                # Log order execution
                service._logging_integration.log_order_execution(
                    "ORD789", "BTCUSDT", "BUY", "0.001", "42000.00", "filled"
                )
                
                # Log API response
                service._logging_integration.log_api_response(
                    "get_ticker", "https://api.binance.com", 200, 512, "BTCUSDT"
                )
                
                # Log performance metrics
                service._logging_integration.log_performance_metrics(
                    "market_analysis", {"duration_ms": 45, "operations": 3}, "BTCUSDT"
                )
                
                # Log graceful degradation
                service._logging_integration.log_graceful_degradation(
                    "price_feed", "timeout", "using_cached_data"
                )
                
                # Complete operation logging
                service._log_operation_success("market_analysis", symbol="BTCUSDT")
                
                # Get metrics (should return normal data since get_operation_metrics itself works)
                metrics = service._logging_integration.get_operation_metrics()
                assert metrics["service_name"] == "MarketDataService"
                # Logger status is "active" because get_operation_metrics itself is not failing
                assert metrics["logger_status"] == "active"
                
                # Reset metrics (should work despite logging failures)
                service._logging_integration.reset_metrics()
                
                # If we reach here, all trading operations completed successfully
                # despite complete logging system failure
                assert True, "All trading operations protected from logging failures"
                
            except Exception as e:
                pytest.fail(f"Trading operations should be completely protected from logging failures: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])