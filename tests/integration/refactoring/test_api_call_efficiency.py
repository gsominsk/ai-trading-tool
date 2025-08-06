import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.market_data.market_data_service import MarketDataService

@pytest.mark.integration
def test_get_enhanced_context_avoids_redundant_api_calls():
    """
    Verifies that get_enhanced_context uses the provided MarketDataSet
    and does not trigger new API calls.
    """
    service = MarketDataService()

    # Mock the internal method that makes the actual API calls
    with patch.object(service, '_get_klines', autospec=True) as mock_get_klines:
        # Create a mock DataFrame with enough data to pass validation (30 rows for daily)
        mock_data = {
            'timestamp': pd.to_datetime(pd.date_range(start='2023-01-01', periods=30)),
            'open': [100 + i for i in range(30)],
            'high': [105 + i for i in range(30)],
            'low': [99 + i for i in range(30)],
            'close': [102 + i for i in range(30)],
            'volume': [1000 + i * 10 for i in range(30)]
        }
        mock_df = pd.DataFrame(mock_data)
        mock_get_klines.return_value = mock_df

        # 1. First, get the market data. This is expected to make API calls.
        market_data_set = service.get_market_data("BTCUSDT")
        
        # Assert that API calls were made to get the initial data
        assert mock_get_klines.call_count > 0, "API calls should be made for get_market_data"
        
        # Reset the mock to monitor calls for the next step
        mock_get_klines.reset_mock()
        
        # 2. Now, get the enhanced context. This should NOT make new API calls.
        enhanced_context = service.get_enhanced_context(market_data_set)
        
        # Assert that no new API calls were made
        assert mock_get_klines.call_count == 0, "get_enhanced_context should not make new API calls"
        
        # Verify that we still get a valid context
        assert "MARKET DATA ANALYSIS" in enhanced_context
        assert "BTCUSDT" in enhanced_context