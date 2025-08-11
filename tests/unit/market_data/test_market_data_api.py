"""
Market Data Service API & Network Tests

Consolidated from archived tests covering:
- API rate limiting and error handling
- Network failures and edge cases
- HTTP error responses (404, 500, 429)
- Malformed API responses
- Connection timeouts and errors
- BTC correlation fetch failures
"""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from src.market_data.market_data_service import MarketDataService
from src.infrastructure.binance_client import BinanceApiClient
from src.logging_system import MarketDataLogger
from src.infrastructure.exceptions import (
    NetworkError,
    RateLimitError,
    APIResponseError,
    DataInsufficientError,
    ProcessingError,
    DataFrameValidationError,
    SymbolValidationError
)


class TestMarketDataServiceAPI:
    """API and network related tests for MarketDataService."""
    
    def setup_method(self):
        """Setup test environment."""
        self.mock_api_client = MagicMock(spec=BinanceApiClient)
        self.mock_logger = MagicMock(spec=MarketDataLogger)
        self.service = MarketDataService(api_client=self.mock_api_client, logger=self.mock_logger)
    
    # =================
    # NETWORK FAILURES
    # =================
    
    def test_api_connection_timeout(self):
        """Test handling of API connection timeout."""
        self.mock_api_client.get_klines.side_effect = NetworkError("Connection timeout")
        
        with pytest.raises(NetworkError) as exc_info:
            self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        assert "Connection timeout" in str(exc_info.value)
    
    def test_api_connection_error(self):
        """Test handling of API connection errors."""
        self.mock_api_client.get_klines.side_effect = NetworkError("Network unreachable")
        
        with pytest.raises(NetworkError) as exc_info:
            self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
        assert "Network unreachable" in str(exc_info.value)
    
    def test_api_http_error_404(self):
        """Test handling of HTTP 404 errors."""
        self.mock_api_client.get_klines.side_effect = APIResponseError("404 Not Found", status_code=404)

        with pytest.raises(APIResponseError) as exc_info:
            self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
        assert "404 Not Found" in str(exc_info.value)
        assert exc_info.value.status_code == 404
    
    def test_api_http_error_500(self):
        """Test handling of HTTP 500 server errors."""
        self.mock_api_client.get_klines.side_effect = APIResponseError("500 Internal Server Error", status_code=500)

        with pytest.raises(APIResponseError) as exc_info:
            self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
        assert "500 Internal Server Error" in str(exc_info.value)
        assert exc_info.value.status_code == 500
    
    def test_api_rate_limiting(self):
        """Test handling of API rate limiting."""
        self.mock_api_client.get_klines.side_effect = RateLimitError("429 Too Many Requests")

        with pytest.raises(RateLimitError) as exc_info:
            self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
        assert "429 Too Many Requests" in str(exc_info.value)
    
    # =================
    # MALFORMED RESPONSES
    # =================
    
    def test_malformed_api_response(self):
        """Test handling of malformed API responses."""
        self.mock_api_client.get_klines.side_effect = ProcessingError("Invalid JSON")

        with pytest.raises(ProcessingError) as exc_info:
            self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        assert "Invalid JSON" in str(exc_info.value)
    
    def test_empty_api_response(self):
        """Test handling of empty API responses."""
        self.mock_api_client.get_klines.return_value = []

        with pytest.raises(DataInsufficientError) as exc_info:
            self.service.get_market_data("BTCUSDT", trace_id="test_trace")
        
        assert "One or more required DataFrames are empty" in str(exc_info.value)
    
    # =================
    # PARTIAL FAILURES
    # =================
    
    def test_partial_network_failure_btc_correlation(self):
        """Test handling when BTC correlation fetch fails but main data succeeds."""
        # Create valid main response
        valid_klines_data = [
            [1640995200000, "50000", "51000", "49000", "50500", "1000.0",
             1640995259999, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(180)
        ]
        
        # Configure side effects for get_klines
        self.mock_api_client.get_klines.side_effect = [
            valid_klines_data,  # daily
            valid_klines_data,  # h4
            valid_klines_data,  # h1
            NetworkError("BTC timeout") # BTC correlation
        ]
        
        with pytest.raises(NetworkError) as exc_info:
            self.service.get_market_data("ETHUSDT", trace_id="test_trace")

        assert "BTC timeout" in str(exc_info.value)

    # =================
    # API RATE LIMITING COMPREHENSIVE
    # =================
    
    def test_rate_limiting_consecutive_requests(self):
        """Test consecutive rate limiting responses."""
        # Multiple consecutive rate limit responses
        for _ in range(3):
            self.mock_api_client.get_klines.side_effect = RateLimitError("429 Too Many Requests")
            
            with pytest.raises(RateLimitError) as exc_info:
                self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
            assert "429 Too Many Requests" in str(exc_info.value)
    
    def test_mixed_error_scenarios(self):
        """Test various mixed error scenarios."""
        error_scenarios = [
            (APIResponseError("400 Bad Request", status_code=400), APIResponseError),
            (APIResponseError("401 Unauthorized", status_code=401), APIResponseError),
            (APIResponseError("403 Forbidden", status_code=403), APIResponseError),
            (NetworkError("408 Request Timeout"), NetworkError),
            (APIResponseError("502 Bad Gateway", status_code=502), APIResponseError),
            (APIResponseError("503 Service Unavailable", status_code=503), APIResponseError),
        ]
        
        for exception_to_raise, expected_exception in error_scenarios:
            self.mock_api_client.get_klines.side_effect = exception_to_raise
            
            with pytest.raises(expected_exception) as exc_info:
                self.service.get_market_data("BTCUSDT", trace_id="test_trace")
            
            assert str(exception_to_raise.message) in str(exc_info.value)
    
    # =================
    # EXTREME DATA CASES
    # =================
    
    def test_invalid_ohlc_data(self):
        """Test handling of invalid OHLC relationships."""
        # Create data where high < low (impossible)
        invalid_ohlc_data = [
            [1640995200000, "50000", "49000", "51000", "50500", "1000.0",  # high < low
             1640995259999, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(180)
        ]
        
        self.mock_api_client.get_klines.return_value = invalid_ohlc_data
        
        with pytest.raises(DataFrameValidationError) as exc_info:
            self.service.get_market_data("INVUSDT", trace_id="test_trace")
        
        assert "invalid OHLC data" in str(exc_info.value)
    
    def test_negative_prices(self):
        """Test handling of negative prices."""
        negative_price_data = [
            [1640995200000, "-1000", "1000", "-2000", "500", "1000.0",
             1640995259999, "500000.0", 100, "500.0", "250000.0", "0"]
            for i in range(180)
        ]
        
        self.mock_api_client.get_klines.return_value = negative_price_data
        
        with pytest.raises(ProcessingError) as exc_info:
            self.service.get_market_data("NEGUSDT", trace_id="test_trace")
        
        # Should fail validation in MarketDataSet and be wrapped in ProcessingError
        assert "support_level must be positive" in str(exc_info.value)
    
    def test_nan_and_inf_values(self):
        """Test handling of NaN and infinite values."""
        nan_inf_data = [
            [1640995200000, "NaN", "inf", "-inf", "50000", "1000.0",
             1640995259999, "50000000.0", 100, "500.0", "25000000.0", "0"]
            for i in range(180)
        ]
        
        self.mock_api_client.get_klines.return_value = nan_inf_data
        
        with pytest.raises(ProcessingError) as exc_info:
            self.service.get_market_data("NANUSDT", trace_id="test_trace")
        
        assert "Unexpected error during market data aggregation" in str(exc_info.value)
    
    def test_memory_pressure_large_dataset(self):
        """Test handling of very large datasets."""
        # Create a large dataset (1000 candles instead of 50)
        large_dataset = [
            [1640995200000 + i*3600000, "50000", "51000", "49000", "50500", "1000.0",
             1640995259999 + i*3600000, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(1000)
        ]
        
        self.mock_api_client.get_klines.return_value = large_dataset
        
        # Should handle large datasets gracefully
        result = self.service.get_market_data("LARGUSDT", trace_id="test_trace")
        assert result.symbol == "LARGUSDT"
        assert len(result.daily_candles) == 1000
        assert isinstance(result.ma_20, Decimal)
    
    def test_concurrent_access_simulation(self):
        """Test handling of concurrent access patterns."""
        # Simulate multiple concurrent requests
        valid_klines_data = [
            [1640995200000, "50000", "51000", "49000", "50500", "1000.0",
             1640995259999, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(180)
        ]
        
        self.mock_api_client.get_klines.return_value = valid_klines_data
        
        # Create multiple service instances and call simultaneously
        services = [MarketDataService(api_client=self.mock_api_client, logger=self.mock_logger) for _ in range(5)]
        results = []
        
        for service in services:
            result = service.get_market_data("BTCUSDT", trace_id="test_trace")
            results.append(result)
        
        # All should succeed
        assert len(results) == 5
        for result in results:
            assert result.symbol == "BTCUSDT"
            assert isinstance(result.ma_20, Decimal)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])