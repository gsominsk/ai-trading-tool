import unittest
import json
import io
import logging
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

from src.trading.trading_cycle import TradingCycle
from src.trading.oms import OrderManagementSystem
from src.trading.oms_repository import OmsRepository
from src.market_data.market_data_service import MarketDataService
from src.logging_system import MarketDataLogger
from src.logging_system.logger_config import configure_ai_logging

class TestEndToEndTracing(unittest.TestCase):

    def setUp(self):
        """Set up a complete trading cycle with mocked external dependencies."""
        # 1. Setup logging to capture to a string buffer
        self.log_stream = io.StringIO()
        # Make sure to use a handler that writes to the stream
        handler = logging.StreamHandler(self.log_stream)
        # Use a flexible formatter that doesn't fail on missing keys
        formatter = logging.Formatter('{"trace_id": "%(trace_id)s", "operation": "%(operation)s", "message": "%(message)s"}', defaults={"trace_id": None, "operation": "unknown"})
        handler.setFormatter(formatter)
        
        # We need a clean logger for each test
        configure_ai_logging(log_level="INFO", console_output=False) # Disable console output to avoid clutter
        self.logger_instance = MarketDataLogger("E2E_Test")
        # Remove all handlers and add our custom one
        # Get the root logger to which handlers are attached by configure_ai_logging
        root_logger = logging.getLogger()
        for h in root_logger.handlers[:]: # Iterate over a copy
            root_logger.removeHandler(h)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

        # 2. Mock external dependencies
        self.mock_ai_analyst = MagicMock()
        self.mock_exchange = MagicMock()

        # 3. Setup real components with an in-memory SQLite DB
        db_path = ":memory:"
        self.repository = OmsRepository(db_path=db_path, logger=self.logger_instance)
        self.oms = OrderManagementSystem(repository=self.repository, logger=self.logger_instance)
        self.market_data_service = MarketDataService(enable_logging=False)
        self.market_data_service.logger = self.logger_instance

        # 4. Create the TradingCycle instance
        self.trading_cycle = TradingCycle(
            oms=self.oms,
            market_data_service=self.market_data_service
        )
        # Manually inject mocks and logger
        self.trading_cycle.ai_analyst = self.mock_ai_analyst
        self.trading_cycle.logger = self.logger_instance

    def test_trace_id_propagates_through_all_layers(self):
        """
        Verify that a single master trace_id from TradingCycle.run_cycle is propagated
        to MarketDataService, OMS, and OmsRepository.
        """
        # --- ARRANGE ---
        # Clear the log stream to only capture logs from this specific test run
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        
        # Mock the AI to suggest placing an order
        self.mock_ai_analyst.analyze.return_value = {
            "decision": "BUY",
            "symbol": "BTC/USDT",
            "confidence": 0.95,
            "amount_usd": 100,
            "price_target": 70000
        }
        # Mock the underlying klines method to allow get_market_data to run and log.
        # This is better than mocking get_market_data itself for an end-to-end tracing test.
        # We need to return a valid DataFrame with enough data for calculations.
        def mock_get_klines(symbol, interval, limit, trace_id=None):
            # Ensure we have enough data for MA calculations (e.g., 50 periods)
            if limit < 50:
                limit = 50
            return pd.DataFrame({
                'timestamp': pd.to_datetime(pd.date_range(end=pd.Timestamp.now(tz='UTC'), periods=limit, freq='H')),
                'open': np.random.uniform(64000, 66000, size=limit),
                'high': np.random.uniform(66000, 67000, size=limit),
                'low': np.random.uniform(63000, 64000, size=limit),
                'close': np.random.uniform(65000, 65500, size=limit),
                'volume': np.random.uniform(100, 500, size=limit)
            })
        self.market_data_service._get_klines = MagicMock(side_effect=mock_get_klines)
        
        # --- ACT ---
        self.trading_cycle.run_cycle()

        # --- ASSERT ---
        # Retrieve and parse logs
        log_contents = self.log_stream.getvalue()
        log_lines = [line for line in log_contents.strip().split('\n') if line]
        parsed_logs = [json.loads(line) for line in log_lines]

        # Find the master trace_id from the 'run_cycle' start log entry
        master_trace_id = None
        for log in parsed_logs:
            if log.get("operation") == "run_cycle" and "initiated" in log.get("message", ""):
                master_trace_id = log.get("trace_id")
                break
        
        self.assertIsNotNone(master_trace_id, "Master trace_id from 'run_cycle' was not found in logs.")

        # Verify that the master trace_id is present in logs from all key components
        expected_operations = {"run_cycle", "get_market_data", "repo_save"}
        found_operations = set()

        for log in parsed_logs:
            # We are checking that the master trace_id is in every relevant log.
            # The old logic checked for parent_trace_id, which is now removed.
            if log.get("trace_id") == master_trace_id:
                op_name = log.get("operation")
                if op_name in expected_operations:
                    found_operations.add(op_name)

        self.assertEqual(expected_operations, found_operations,
                         f"Not all expected operations were logged with the master trace_id. "
                         f"Expected: {expected_operations}, Found: {found_operations}")

if __name__ == "__main__":
    unittest.main()