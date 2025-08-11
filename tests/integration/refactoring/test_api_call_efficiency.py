import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService
from src.infrastructure.binance_client import BinanceApiClient
from src.logging_system import MarketDataLogger

@pytest.mark.integration
def test_get_enhanced_context_avoids_redundant_api_calls():
    """
    Verifies that get_enhanced_context uses the provided MarketDataSet
    and does not trigger new API calls.
    """
    mock_api_client = MagicMock(spec=BinanceApiClient)
    mock_logger = MagicMock(spec=MarketDataLogger)
    service = MarketDataService(api_client=mock_api_client, logger=mock_logger)

    # Configure the mock API client to return valid kline data (list of lists)
    # The service is responsible for converting this to a DataFrame
    mock_klines = [
        [pd.Timestamp(f'2023-01-{i+1}').value // 10**6, 100+i, 105+i, 99+i, 102+i, 1000+i*10, pd.Timestamp(f'2023-01-{i+1} 23:59:59').value // 10**6, '...', 10, '...', '...', '...']
        for i in range(30)
    ]
    # The service calls get_klines four times: 1d, 4h, 1h for the main symbol, and 1h for BTC correlation.
    mock_api_client.get_klines.side_effect = [mock_klines, mock_klines, mock_klines, mock_klines]

    # 1. First, get the market data. This is expected to make API calls.
    market_data_set = service.get_market_data("ETHUSDT", trace_id="test_trace")
    
    # Assert that API calls were made to get the initial data
    # It should be called for the main symbol and for BTC correlation
    assert mock_api_client.get_klines.call_count >= 1, "API calls should be made for get_market_data"
    
    # Reset the mock to monitor calls for the next step
    mock_api_client.get_klines.reset_mock()
    
    # 2. Now, get the enhanced context. This should NOT make new API calls.
    enhanced_context = service.get_enhanced_context(market_data_set)
    
    # Assert that no new API calls were made
    assert mock_api_client.get_klines.call_count == 0, "get_enhanced_context should not make new API calls"
    
    # Verify that we still get a valid context
    assert "MARKET DATA ANALYSIS" in enhanced_context
    assert "ETHUSDT" in enhanced_context