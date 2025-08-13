import unittest
from unittest.mock import MagicMock, patch, call
import pandas as pd
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.market_data.market_data_service import MarketDataService
from src.infrastructure.binance_client import BinanceApiClient
from src.logging_system.logger_config import MarketDataLogger

def create_mock_klines(rows=100):
    """Helper to create a realistic-looking klines DataFrame."""
    base_time = datetime.now(timezone.utc)
    data = []
    for i in range(rows):
        ts = base_time - timedelta(hours=i)
        data.append([
            int(ts.timestamp() * 1000),  # timestamp
            100.0 + i,  # open
            105.0 + i,  # high
            95.0 + i,   # low
            102.0 + i,  # close
            1000.0      # volume
        ])
    # Reverse to have ascending time
    data.reverse()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
    return df

class TestMarketDataCaching(unittest.TestCase):

    def setUp(self):
        """Set up a mock environment for each test."""
        self.mock_api_client = MagicMock(spec=BinanceApiClient)
        self.mock_logger = MagicMock()
        self.market_data_service = MarketDataService(
            api_client=self.mock_api_client,
            logger=self.mock_logger
        )
        # Mock the internal DataFrame creation to simplify testing
        self.market_data_service._create_dataframe_from_klines = lambda x: create_mock_klines(len(x))

    def test_btc_correlation_caching_logic(self):
        """
        Verify that BTC data is fetched once, cached, and logging events are correct.
        """
        # 1. Setup Mock Responses
        mock_btc_klines_raw = [[i] for i in range(100)]
        self.mock_api_client.get_klines.return_value = mock_btc_klines_raw

        # 2. First Call (Cache Miss)
        altcoin_df = create_mock_klines(100)
        correlation1 = self.market_data_service._calculate_btc_correlation("ETHUSDT", altcoin_df, trace_id="test1")

        # 3. Assertions for the First Call
        self.mock_api_client.get_klines.assert_called_once_with("BTCUSDT", "1h", 100, trace_id="test1")
        self.assertIsNotNone(correlation1)
        
        # Verify logging for miss and update
        expected_log_calls = [
            call(cache_name="btc_data", event_type="miss", trace_id="test1"),
            call(cache_name="btc_data", event_type="update", trace_id="test1")
        ]
        self.mock_logger.log_cache_event.assert_has_calls(expected_log_calls)
        self.assertEqual(self.mock_logger.log_cache_event.call_count, 2)

        # 4. Second Call (Cache Hit)
        correlation2 = self.market_data_service._calculate_btc_correlation("ETHUSDT", altcoin_df, trace_id="test2")

        # 5. Assertions for the Second Call
        # The call count for get_klines should STILL BE 1.
        self.mock_api_client.get_klines.assert_called_once()
        self.assertEqual(correlation1, correlation2)

        # Verify logging for hit
        self.mock_logger.log_cache_event.assert_called_with(
            cache_name="btc_data",
            event_type="hit",
            context={'cache_age_seconds': unittest.mock.ANY},
            trace_id="test2"
        )
        self.assertEqual(self.mock_logger.log_cache_event.call_count, 3) # 2 from miss, 1 from hit

    @patch('src.market_data.market_data_service.datetime')
    def test_btc_correlation_cache_expiration(self, mock_datetime):
        """
        Verify that stale cache is ignored, data is re-fetched, and logging is correct.
        """
        # 1. Setup Mock Time and Responses
        initial_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = initial_time
        
        mock_btc_klines_raw_1 = [[i] for i in range(100)]
        mock_btc_klines_raw_2 = [[i + 1] for i in range(100)]
        self.mock_api_client.get_klines.side_effect = [
            mock_btc_klines_raw_1,
            mock_btc_klines_raw_2,
        ]

        # 2. First Call (Cache Miss)
        altcoin_df = create_mock_klines(100)
        self.market_data_service._calculate_btc_correlation("ETHUSDT", altcoin_df, trace_id="test1")
        
        # Assert API call and logging for miss/update
        self.mock_api_client.get_klines.assert_called_once_with("BTCUSDT", "1h", 100, trace_id="test1")
        self.mock_logger.log_cache_event.assert_any_call(cache_name="btc_data", event_type="miss", trace_id="test1")
        self.mock_logger.log_cache_event.assert_any_call(cache_name="btc_data", event_type="update", trace_id="test1")
        self.assertEqual(self.mock_logger.log_cache_event.call_count, 2)

        # 3. Advance Time to make cache stale
        stale_time = initial_time + timedelta(minutes=10)
        mock_datetime.now.return_value = stale_time

        # 4. Second Call (Stale Cache, should re-fetch)
        self.market_data_service._calculate_btc_correlation("ETHUSDT", altcoin_df, trace_id="test2")

        # 5. Assertions for the Second Call
        # Check that get_klines was called a SECOND time.
        self.assertEqual(self.mock_api_client.get_klines.call_count, 2)
        self.mock_api_client.get_klines.assert_called_with("BTCUSDT", "1h", 100, trace_id="test2")

        # Verify logging for the second miss/update
        expected_log_calls = [
            call(cache_name="btc_data", event_type="miss", trace_id="test1"),
            call(cache_name="btc_data", event_type="update", trace_id="test1"),
            call(cache_name="btc_data", event_type="miss", trace_id="test2"),
            call(cache_name="btc_data", event_type="update", trace_id="test2")
        ]
        self.mock_logger.log_cache_event.assert_has_calls(expected_log_calls)
        self.assertEqual(self.mock_logger.log_cache_event.call_count, 4)

if __name__ == '__main__':
    unittest.main()