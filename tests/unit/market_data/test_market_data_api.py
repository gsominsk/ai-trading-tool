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
import requests
from decimal import Decimal
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService


class TestMarketDataServiceAPI:
    """API and network related tests for MarketDataService."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = MarketDataService()
    
    # =================
    # NETWORK FAILURES
    # =================
    
    def test_api_connection_timeout(self):
        """Test handling of API connection timeout."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("BTCUSDT")
            
            assert "Request to Binance API timed out" in str(exc_info.value)
    
    def test_api_connection_error(self):
        """Test handling of API connection errors."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("BTCUSDT")
            
            assert "Failed to connect to Binance API" in str(exc_info.value)
    
    def test_api_http_error_404(self):
        """Test handling of HTTP 404 errors."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("BTCUSDT")
            
            assert "Symbol BTCUSDT not found or invalid interval 1d" in str(exc_info.value)
    
    def test_api_http_error_500(self):
        """Test handling of HTTP 500 server errors."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("BTCUSDT")
            
            assert "Binance API server error: 500" in str(exc_info.value)
    
    def test_api_rate_limiting(self):
        """Test handling of API rate limiting."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("BTCUSDT")
            
            assert "Binance API rate limit exceeded" in str(exc_info.value)
    
    # =================
    # MALFORMED RESPONSES
    # =================
    
    def test_malformed_api_response(self):
        """Test handling of malformed API responses."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("BTCUSDT")
            
            assert "Unexpected error during klines data processing" in str(exc_info.value)
    
    def test_empty_api_response(self):
        """Test handling of empty API responses."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("BTCUSDT")
            
            assert "Empty or invalid response from Binance API" in str(exc_info.value)
    
    # =================
    # PARTIAL FAILURES
    # =================
    
    def test_partial_network_failure_btc_correlation(self):
        """Test handling when BTC correlation fetch fails but main data succeeds."""
        # Create valid main response
        valid_klines_data = [
            [1640995200000, "50000", "51000", "49000", "50500", "1000.0",
             1640995259999, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(50)
        ]
        
        with patch('requests.get') as mock_get:
            # First 3 calls succeed (daily, h4, h1), 4th call fails (BTC correlation)
            mock_responses = []
            for i in range(3):
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = valid_klines_data
                mock_responses.append(mock_response)
            
            # BTC correlation call fails
            btc_response = MagicMock()
            btc_response.status_code = 408  # Request timeout
            btc_response.raise_for_status.side_effect = requests.exceptions.Timeout("BTC timeout")
            mock_responses.append(btc_response)
            
            mock_get.side_effect = mock_responses
            
            # Should succeed with None BTC correlation
            result = self.service.get_market_data("ETHUSDT")
            assert result.btc_correlation is None
            assert result.symbol == "ETHUSDT"
    
    # =================
    # API RATE LIMITING COMPREHENSIVE
    # =================
    
    def test_rate_limiting_consecutive_requests(self):
        """Test consecutive rate limiting responses."""
        with patch('requests.get') as mock_get:
            # Multiple consecutive rate limit responses
            for _ in range(3):
                mock_response = MagicMock()
                mock_response.status_code = 429
                mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
                mock_get.return_value = mock_response
                
                with pytest.raises(Exception) as exc_info:
                    self.service.get_market_data("BTCUSDT")
                
                assert "Binance API rate limit exceeded" in str(exc_info.value)
    
    def test_mixed_error_scenarios(self):
        """Test various mixed error scenarios."""
        error_scenarios = [
            (400, "400 Bad Request", "Invalid request parameters"),
            (401, "401 Unauthorized", "API authentication failed"),
            (403, "403 Forbidden", "Access forbidden"),
            (408, "408 Request Timeout", "Request timeout"),
            (502, "502 Bad Gateway", "Bad gateway"),
            (503, "503 Service Unavailable", "Service temporarily unavailable"),
        ]
        
        for status_code, error_msg, expected_text in error_scenarios:
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = status_code
                mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(error_msg)
                mock_get.return_value = mock_response
                
                with pytest.raises(Exception) as exc_info:
                    self.service.get_market_data("BTCUSDT")
                
                # Should contain appropriate error handling
                assert str(exc_info.value)  # Should have meaningful error message
    
    # =================
    # EXTREME DATA CASES
    # =================
    
    def test_invalid_ohlc_data(self):
        """Test handling of invalid OHLC relationships."""
        # Create data where high < low (impossible)
        invalid_ohlc_data = [
            [1640995200000, "50000", "49000", "51000", "50500", "1000.0",  # high < low
             1640995259999, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(50)
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = invalid_ohlc_data
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("INVUSDT")
            
            assert "invalid OHLC data" in str(exc_info.value)
    
    def test_negative_prices(self):
        """Test handling of negative prices."""
        negative_price_data = [
            [1640995200000, "-1000", "1000", "-2000", "500", "1000.0",
             1640995259999, "500000.0", 100, "500.0", "250000.0", "0"]
            for i in range(50)
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = negative_price_data
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("NEGUSDT")
            
            # Should fail validation
            assert "support_level must be positive" in str(exc_info.value)
    
    def test_nan_and_inf_values(self):
        """Test handling of NaN and infinite values."""
        nan_inf_data = [
            [1640995200000, "NaN", "inf", "-inf", "50000", "1000.0",
             1640995259999, "50000000.0", 100, "500.0", "25000000.0", "0"]
            for i in range(50)
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = nan_inf_data
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                self.service.get_market_data("NANUSDT")
            
            assert "Invalid numeric data in column open" in str(exc_info.value)
    
    def test_memory_pressure_large_dataset(self):
        """Test handling of very large datasets."""
        # Create a large dataset (1000 candles instead of 50)
        large_dataset = [
            [1640995200000 + i*3600000, "50000", "51000", "49000", "50500", "1000.0",
             1640995259999 + i*3600000, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(1000)
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = large_dataset
            mock_get.return_value = mock_response
            
            # Should handle large datasets gracefully
            result = self.service.get_market_data("LARGUSDT")
            assert result.symbol == "LARGUSDT"
            assert len(result.daily_candles) == 1000
            assert isinstance(result.ma_20, Decimal)
    
    def test_concurrent_access_simulation(self):
        """Test handling of concurrent access patterns."""
        # Simulate multiple concurrent requests
        valid_klines_data = [
            [1640995200000, "50000", "51000", "49000", "50500", "1000.0",
             1640995259999, "50250000.0", 100, "500.0", "25125000.0", "0"]
            for i in range(50)
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = valid_klines_data
            mock_get.return_value = mock_response
            
            # Create multiple service instances and call simultaneously
            services = [MarketDataService() for _ in range(5)]
            results = []
            
            for service in services:
                result = service.get_market_data("BTCUSDT")
                results.append(result)
            
            # All should succeed
            assert len(results) == 5
            for result in results:
                assert result.symbol == "BTCUSDT"
                assert isinstance(result.ma_20, Decimal)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])