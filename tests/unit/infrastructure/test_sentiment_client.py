import pytest
from unittest.mock import MagicMock, patch
import requests
from requests.exceptions import JSONDecodeError

from src.infrastructure.sentiment_client import SentimentApiClient
from src.infrastructure.exceptions import ApiClientError
from src.logging_system import MarketDataLogger

class TestSentimentApiClient:
    """Unit tests for the SentimentApiClient."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        self.mock_logger = MagicMock(spec=MarketDataLogger)
        self.client = SentimentApiClient(logger=self.mock_logger)

    @patch('requests.get')
    def test_get_fear_and_greed_index_success(self, mock_get):
        """Test successful retrieval of the Fear & Greed Index."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_data = {"name": "Fear and Greed Index", "data": [{"value": "50"}]}
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        # Act
        result = self.client.get_fear_and_greed_index(trace_id="test_success")

        # Assert
        assert result == expected_data
        self.mock_logger.log_operation_start.assert_called_once()
        self.mock_logger.log_operation_complete.assert_called_once()
        mock_get.assert_called_once_with("https://api.alternative.me/fng/", timeout=10)

    @patch('requests.get')
    def test_get_fear_and_greed_index_network_error(self, mock_get):
        """Test that ApiClientError is raised on a network error."""
        # Arrange
        mock_get.side_effect = requests.exceptions.RequestException("Connection timed out")

        # Act & Assert
        with pytest.raises(ApiClientError, match="Network error"):
            self.client.get_fear_and_greed_index(trace_id="test_network_error")
        
        self.mock_logger.log_operation_start.assert_called_once()
        self.mock_logger.log_operation_error.assert_called_once()

    @patch('requests.get')
    def test_get_fear_and_greed_index_http_error(self, mock_get):
        """Test that ApiClientError is raised on an HTTP 4xx/5xx error."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server Error")
        mock_get.return_value = mock_response

        # Act & Assert
        with pytest.raises(ApiClientError, match="Network error"):
            self.client.get_fear_and_greed_index(trace_id="test_http_error")

        self.mock_logger.log_operation_error.assert_called_once()

    @patch('requests.get')
    def test_get_fear_and_greed_index_json_decode_error(self, mock_get):
        """Test that ApiClientError is raised on a JSON decoding error."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Invalid JSON</body></html>"
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "<html>", 0)
        mock_get.return_value = mock_response

        # Act & Assert
        with pytest.raises(ApiClientError, match="Failed to decode JSON"):
            self.client.get_fear_and_greed_index(trace_id="test_json_error")

        self.mock_logger.log_operation_start.assert_called_once()
        self.mock_logger.log_operation_error.assert_called_once()
        # Check that the error log for json decode was called
        call_args = self.mock_logger.log_operation_error.call_args
        assert call_args.args[0] == 'get_fear_and_greed_index_json_decode'