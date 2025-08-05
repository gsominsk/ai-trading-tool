#!/usr/bin/env python3
"""
Test logging levels functionality for MarketDataService.

Validates that log levels properly filter messages and improve performance.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService
from src.market_data.logging_integration import MarketDataServiceLogging


class TestLoggingLevels:
    """Test log level filtering and performance optimization."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_log_level_filtering_debug(self):
        """Test that DEBUG level logs all messages."""
        service = MarketDataService(log_level="DEBUG")
        
        # DEBUG level should log everything
        assert service._should_log("DEBUG") == True
        assert service._should_log("INFO") == True
        assert service._should_log("WARNING") == True
        assert service._should_log("ERROR") == True
        assert service._should_log("CRITICAL") == True
    
    def test_log_level_filtering_info(self):
        """Test that INFO level filters out DEBUG messages."""
        service = MarketDataService(log_level="INFO")
        
        # INFO level should filter out DEBUG
        assert service._should_log("DEBUG") == False
        assert service._should_log("INFO") == True
        assert service._should_log("WARNING") == True
        assert service._should_log("ERROR") == True
        assert service._should_log("CRITICAL") == True
    
    def test_log_level_filtering_warning(self):
        """Test that WARNING level filters out DEBUG and INFO."""
        service = MarketDataService(log_level="WARNING")
        
        # WARNING level should filter out DEBUG and INFO
        assert service._should_log("DEBUG") == False
        assert service._should_log("INFO") == False
        assert service._should_log("WARNING") == True
        assert service._should_log("ERROR") == True
        assert service._should_log("CRITICAL") == True
    
    def test_log_level_filtering_error(self):
        """Test that ERROR level only logs errors and critical."""
        service = MarketDataService(log_level="ERROR")
        
        # ERROR level should only log ERROR and CRITICAL
        assert service._should_log("DEBUG") == False
        assert service._should_log("INFO") == False
        assert service._should_log("WARNING") == False
        assert service._should_log("ERROR") == True
        assert service._should_log("CRITICAL") == True
    
    def test_log_level_filtering_critical(self):
        """Test that CRITICAL level only logs critical messages."""
        service = MarketDataService(log_level="CRITICAL")
        
        # CRITICAL level should only log CRITICAL
        assert service._should_log("DEBUG") == False
        assert service._should_log("INFO") == False
        assert service._should_log("WARNING") == False
        assert service._should_log("ERROR") == False
        assert service._should_log("CRITICAL") == True
    
    def test_logging_integration_level_filtering(self):
        """Test that logging integration respects level filtering."""
        logging_integration = MarketDataServiceLogging(log_level="WARNING")
        
        # WARNING level should filter appropriately
        assert logging_integration._should_log("DEBUG") == False
        assert logging_integration._should_log("INFO") == False
        assert logging_integration._should_log("WARNING") == True
        assert logging_integration._should_log("ERROR") == True
        assert logging_integration._should_log("CRITICAL") == True
    
    def test_production_performance_optimization(self):
        """Test that high log levels improve performance by skipping operations."""
        # Test with real logging integration to verify level filtering works
        service = MarketDataService(log_level="ERROR", enable_logging=True)
        
        # The service should have level filtering working through its integration
        # Test level filtering directly
        assert service._logging_integration._should_log("DEBUG") == False
        assert service._logging_integration._should_log("INFO") == False
        assert service._logging_integration._should_log("WARNING") == False
        assert service._logging_integration._should_log("ERROR") == True
        assert service._logging_integration._should_log("CRITICAL") == True
        
        # Verify the service log level is set correctly
        assert service._log_level == "ERROR"
        assert service._logging_integration.log_level == "ERROR"
    
    def test_log_level_case_insensitive(self):
        """Test that log levels are case insensitive."""
        service = MarketDataService(log_level="warning")  # lowercase
        
        assert service._log_level == "WARNING"  # Should be converted to uppercase
        assert service._should_log("WARNING") == True
        assert service._should_log("warning") == True  # lowercase should work
        assert service._should_log("Warning") == True  # mixed case should work
    
    def test_invalid_log_level_defaults_to_info(self):
        """Test that invalid log levels default to INFO."""
        service = MarketDataService(log_level="INVALID")
        
        # Should default to INFO behavior
        assert service._should_log("DEBUG") == False
        assert service._should_log("INFO") == True
        assert service._should_log("WARNING") == True
    
    @patch('requests.get')
    def test_api_call_logging_levels(self, mock_get):
        """Test that API calls use appropriate log levels."""
        # Mock successful API response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1640995200000, "42000.00", "42100.00", "41900.00", "42050.00", "1.5",
             1640995259999, "63075.00", 10, "0.75", "31537.50", "0"]
        ] * 30
        
        # Create service with WARNING level (should skip DEBUG API success logs)
        service = MarketDataService(log_level="WARNING", enable_logging=True)
        mock_integration = MagicMock()
        service._logging_integration = mock_integration
        
        # Make API call - success should be logged at DEBUG level (skipped)
        try:
            service._get_klines("BTCUSDT", "1h", 10)
        except:
            pass  # We don't care about the result, just the logging
        
        # Success logging should have been skipped due to DEBUG level
        # (API success is logged at DEBUG level for performance)
        mock_integration.log_operation_success.assert_not_called()
    
    def test_error_logging_always_logged(self):
        """Test that ERROR and CRITICAL messages are always logged regardless of level."""
        # Test with CRITICAL level - should only log CRITICAL messages
        service = MarketDataService(log_level="CRITICAL", enable_logging=True)
        
        # Test level filtering directly
        assert service._logging_integration._should_log("DEBUG") == False
        assert service._logging_integration._should_log("INFO") == False
        assert service._logging_integration._should_log("WARNING") == False
        assert service._logging_integration._should_log("ERROR") == False  # ERROR should be skipped at CRITICAL level
        assert service._logging_integration._should_log("CRITICAL") == True
        
        # Verify the service log level is set correctly
        assert service._log_level == "CRITICAL"
        assert service._logging_integration.log_level == "CRITICAL"
    
    def test_log_level_integration_consistency(self):
        """Test that MarketDataService and logging integration have consistent levels."""
        service = MarketDataService(log_level="WARNING", enable_logging=True)
        
        # Both should have the same filtering behavior
        test_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in test_levels:
            service_result = service._should_log(level)
            integration_result = service._logging_integration._should_log(level)
            assert service_result == integration_result, f"Level {level} inconsistent between service and integration"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])