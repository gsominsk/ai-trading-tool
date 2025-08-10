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
        # 1. Setup logging to use the actual AIOptimizedJSONFormatter
        self.log_stream = io.StringIO()
        handler = logging.StreamHandler(self.log_stream)
        
        # Use the real formatter to ensure 'service' field is handled correctly
        from src.logging_system.json_formatter import AIOptimizedJSONFormatter
        formatter = AIOptimizedJSONFormatter()
        handler.setFormatter(formatter)
        
        # Configure logging without console output and get the root logger
        configure_ai_logging(log_level="INFO", console_output=False)
        root_logger = logging.getLogger()
        
        # Clean up any existing handlers and add our stream handler
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

        # 2. Mock external dependencies
        self.mock_ai_analyst = MagicMock()
        self.mock_exchange = MagicMock()

        # 3. Setup real components with correct service names
        db_path = ":memory:"
        # Each component gets a logger with its specific service name
        self.repo_logger = MarketDataLogger("E2E_Test_Repo", service_name="oms_repository")
        self.oms_logger = MarketDataLogger("E2E_Test_OMS", service_name="oms")
        self.mds_logger = MarketDataLogger("E2E_Test_MDS", service_name="market_data_service")
        self.tc_logger = MarketDataLogger("E2E_Test_TC", service_name="trading_cycle")

        self.repository = OmsRepository(db_path=db_path, logger=self.repo_logger)
        self.oms = OrderManagementSystem(repository=self.repository, logger=self.oms_logger)
        self.market_data_service = MarketDataService(enable_logging=True) # Enable logging
        self.market_data_service.logger = self.mds_logger

        # 4. Create the TradingCycle instance
        self.trading_cycle = TradingCycle(
            oms=self.oms,
            market_data_service=self.market_data_service
        )
        # Manually inject mocks and the specific logger
        self.trading_cycle.ai_analyst = self.mock_ai_analyst
        self.trading_cycle.logger = self.tc_logger

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

        # Verify that the master trace_id and correct service name are in logs from all key components
        expected_services = {
            "trading_cycle": False,
            "market_data_service": False,
            "oms": False,
            "oms_repository": False
        }

        for log in parsed_logs:
            if log.get("trace_id") == master_trace_id:
                service = log.get("service")
                if service in expected_services:
                    expected_services[service] = True
        
        for service, found in expected_services.items():
            self.assertTrue(found, f"Did not find log with master trace_id for service: {service}")

if __name__ == "__main__":
    unittest.main()