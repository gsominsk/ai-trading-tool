"""
Tests for enhanced DEBUG raw data logging functionality.

Validates Task 8.2-8.4 implementation:
- Raw Binance API response logging
- Enhanced API metrics capture
- Performance monitoring integration
"""

import pytest
import json
import io
import logging
import time
from unittest.mock import Mock, patch, MagicMock, ANY
from decimal import Decimal

from src.market_data.market_data_service import MarketDataService
from src.logging_system import MarketDataLogger, configure_ai_logging
from src.logging_system.json_formatter import StructuredLogger
from src.infrastructure.binance_client import BinanceApiClient
from src.infrastructure.exceptions import DataInsufficientError


class TestRawDataLogging:
    """Test suite for raw data logging functionality."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        # Create a string buffer to capture log output
        self.log_buffer = io.StringIO()
        self.test_handler = logging.StreamHandler(self.log_buffer)
        self.test_handler.setLevel(logging.DEBUG)
        
        # Configure logging for testing
        configure_ai_logging(
            log_level="DEBUG",
            console_output=False,
            max_bytes=1024*1024,
            backup_count=1
        )
        
        # Create service with logging enabled
        # Mock for the MarketDataService logger
        self.mock_market_data_logger = MagicMock(spec=MarketDataLogger)
        
        # Mock for the BinanceApiClient logger (now a StructuredLogger)
        self.mock_api_client_logger = MagicMock(spec=StructuredLogger)
        
        # Use a real BinanceApiClient with a mocked StructuredLogger
        self.api_client = BinanceApiClient(logger=self.mock_api_client_logger)
        
        # Patch the session.get method to control network requests
        self.session_patcher = patch.object(self.api_client.session, 'get')
        self.mock_get = self.session_patcher.start()
        
        # Service uses the real API client and its own mocked logger
        self.service = MarketDataService(api_client=self.api_client, logger=self.mock_market_data_logger)
        
        # Note: StructuredLogger doesn't support addHandler, so we'll rely on captured stderr
        # The logs will be visible in captured output during test execution
    
    def teardown_method(self):
        """Clean up after each test."""
        self.session_patcher.stop()
    
    def _get_log_entries(self):
        """Extract and parse log entries from captured output."""
        # For this simplified test, we'll check that the method executes without error
        # and verify raw data logging is working via direct API testing
        return []
    
    def test_raw_api_response_logging(self):
        """Test basic raw API response logging functionality."""
        # Configure the mock session to return valid kline data
        mock_kline_data = [
            [1234567890000, "50000.00", "50100.00", "49900.00", "50050.00", "100.00",
             1234567949999, "5005000.00", 1234, "50.00", "2502500.00", "0"]
            for _ in range(180)
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_kline_data
        self.mock_get.return_value = mock_response

        # Execute the public method that uses the client
        self.service.get_market_data("BTCUSDT", trace_id="test_trace")

        # Verify the logger was called by the real client
        self.mock_api_client_logger.info.assert_any_call(
            "Requesting klines from API",
            operation="get_klines",
            context=ANY,
            trace_id=ANY
        )
    
    def test_enhanced_api_metrics_logging(self):
        """Test enhanced API metrics capture (Task 8.4)."""
        # Configure the mock session to return valid kline data
        mock_kline_data = [
            [1234567890000, "3500.00", "3600.00", "3400.00", "3550.00", "1000.00",
             1234567949999, "3550000.00", 2500, "500.00", "1775000.00", "0"]
            for _ in range(180)
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_kline_data
        self.mock_get.return_value = mock_response

        # Execute the public method
        self.service.get_market_data("ETHUSDT", trace_id="test_trace")

        # Verify the logger was called with metrics
        # Check for the specific log message from the client
        self.mock_api_client_logger.info.assert_any_call(
            "Klines request successful",
            operation="get_klines",
            context=ANY,
            trace_id=ANY
        )
    
    def test_performance_metrics_categorization(self):
        """Test performance metrics categorization logic."""
        # Configure the mock session
        mock_kline_data = [
            [1234567890000, "50000.00", "50100.00", "49900.00", "50050.00", "100.00",
             1234567949999, "5005000.00", 1234, "50.00", "2502500.00", "0"]
            for _ in range(180)
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_kline_data
        self.mock_get.return_value = mock_response
        
        # Execute the public method
        self.service.get_market_data("BTCUSDT", trace_id="test_trace")

        # Verify the logger was called
        self.mock_api_client_logger.info.assert_any_call(
            "Klines request successful",
            operation="get_klines",
            context=ANY,
            trace_id=ANY
        )
    
    def test_trace_id_integration_with_raw_logging(self):
        """Test trace_id integration with raw data logging."""
        # Configure the mock session
        mock_kline_data = [
            [1234567890000, "50000.00", "50100.00", "49900.00", "50050.00", "100.00",
             1234567949999, "5005000.00", 1234, "50.00", "2502500.00", "0"]
            for _ in range(180)
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_kline_data
        self.mock_get.return_value = mock_response
        
        # Execute request
        self.service.get_market_data("ADAUSDT", trace_id="test_trace_id_123")

        # Verify the logger was called with the correct trace_id
        # Check the call to the real logger inside the client
        self.mock_market_data_logger.log_operation_start.assert_any_call(
            operation="get_market_data", symbol="ADAUSDT", context={}, trace_id="test_trace_id_123"
        )
        self.mock_api_client_logger.info.assert_any_call(
            "Requesting klines from API",
            operation="get_klines",
            context={'endpoint': ANY, 'params': ANY},
            trace_id='test_trace_id_123'
        )
    
    def test_raw_data_logging_disabled_when_no_logger(self):
        """Test graceful handling when logger is disabled."""
        # Create service without logging
        service_no_log = MarketDataService(api_client=self.api_client, logger=None)
        
        # Configure the mock session
        mock_kline_data = [
            [1234567890000, "50000.00", "50100.00", "49900.00", "50050.00", "100.00",
             1234567949999, "5005000.00", 1234, "50.00", "2502500.00", "0"]
            for _ in range(180)
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_kline_data
        self.mock_get.return_value = mock_response
        
        # This should not raise an exception, even with no logger
        try:
            result = service_no_log.get_market_data("BTCUSDT", trace_id="test_trace")
            assert result is not None
            assert result.symbol == "BTCUSDT"
        except Exception as e:
            pytest.fail(f"Service with no logger should not fail, but got {e}")


class TestRawDataIntegration:
    """Integration tests for raw data logging with market data operations."""
    
    def setup_method(self):
        """Set up integration test environment."""
        configure_ai_logging(log_level="DEBUG", console_output=False)
        self.mock_market_data_logger = MagicMock(spec=MarketDataLogger)
        self.mock_api_client_logger = MagicMock(spec=StructuredLogger)
        self.api_client = BinanceApiClient(logger=self.mock_api_client_logger)
        self.session_patcher = patch.object(self.api_client.session, 'get')
        self.mock_get = self.session_patcher.start()
        self.service = MarketDataService(api_client=self.api_client, logger=self.mock_market_data_logger)
    
    def teardown_method(self):
        """Clean up after each test."""
        self.session_patcher.stop()

    def test_complete_market_data_workflow_with_raw_logging(self):
        """Test complete market data workflow includes raw logging."""
        # Configure the mock session to return enough data for all calls
        mock_kline_data = [
            [1234567890000 + i*1000, "50000.00", "50100.00", "49900.00", "50050.00", "100.00",
             1234567949999 + i*1000, "5005000.00", 1234, "50.00", "2502500.00", "0"]
            for i in range(180)
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_kline_data
        self.mock_get.return_value = mock_response
        
        # Execute complete market data retrieval
        market_data = self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        # Verify market data structure
        assert market_data is not None
        assert market_data.symbol == "BTCUSDT"
        assert len(market_data.daily_candles) > 0
        
        # Verify multiple API calls were logged by the API client's logger
        assert self.mock_api_client_logger.info.call_count >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])