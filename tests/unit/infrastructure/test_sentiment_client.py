import pytest
import requests
from unittest.mock import MagicMock, patch
from src.infrastructure.sentiment_client import SentimentApiClient
from src.infrastructure.exceptions import ApiClientError
from src.logging_system import MarketDataLogger

@pytest.fixture
def mock_logger():
    """Fixture for a mocked MarketDataLogger."""
    return MagicMock(spec=MarketDataLogger)

@pytest.fixture
def sentiment_api_client(mock_logger):
    """Fixture to create a SentimentApiClient instance with a mocked logger."""
    return SentimentApiClient(logger=mock_logger)

@patch('requests.get')
def test_get_fear_and_greed_index_success(mock_get, sentiment_api_client, mock_logger):
    """
    Тест успешного получения индекса страха и жадности.
    """
    # Подготовка
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "Fear and Greed Index",
        "data": [{"value": "50", "value_classification": "Neutral"}]
    }
    mock_get.return_value = mock_response

    # Действие
    result = sentiment_api_client.get_fear_and_greed_index(trace_id="test-trace-id")

    # Проверка
    mock_get.assert_called_once_with("https://api.alternative.me/fng/", timeout=10)
    mock_logger.log_operation_start.assert_called_once()
    mock_logger.log_operation_complete.assert_called_once()
    assert result["name"] == "Fear and Greed Index"
    assert result["data"][0]["value"] == "50"

@patch('requests.get')
def test_get_fear_and_greed_index_network_error(mock_get, sentiment_api_client, mock_logger):
    """
    Тест обработки сетевой ошибки (e.g., timeout).
    """
    # Подготовка
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    # Действие и Проверка
    with pytest.raises(ApiClientError, match="Network error"):
        sentiment_api_client.get_fear_and_greed_index(trace_id="test-trace-id")
    
    mock_logger.log_operation_start.assert_called_once()
    mock_logger.log_operation_error.assert_called_once()

@patch('requests.get')
def test_get_fear_and_greed_index_http_error(mock_get, sentiment_api_client, mock_logger):
    """
    Тест обработки ошибки HTTP (e.g., 500 Internal Server Error).
    """
    # Подготовка
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server Error")
    mock_get.return_value = mock_response

    # Действие и Проверка
    with pytest.raises(ApiClientError, match="Network error"):
        sentiment_api_client.get_fear_and_greed_index(trace_id="test-trace-id")

    mock_logger.log_operation_start.assert_called_once()
    mock_logger.log_operation_error.assert_called_once()