import unittest
import json
import io
import logging
from unittest.mock import patch
from src.market_data.market_data_service import MarketDataService
from src.logging_system.logger_config import reset_logging_state

class TestHierarchicalTracingIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a clean logging environment for each test."""
        # Reset logging state to ensure no handlers are carried over
        reset_logging_state()
        
        # Patch sys.stderr to capture log output directly
        self.mock_stderr = patch('sys.stderr', new_callable=io.StringIO).start()
        self.addCleanup(patch.stopall)

    def tearDown(self):
        """Clean up is handled by addCleanup."""
        pass

    def get_log_entries(self):
        """Retrieve and parse log entries from the mocked stderr."""
        log_contents = self.mock_stderr.getvalue()
        if not log_contents:
            return []
        
        # Split logs by newline and parse each JSON entry
        # Filter lines to only include those that are valid JSON objects
        json_lines = []
        for line in log_contents.strip().split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    json_lines.append(json.loads(line))
                except json.JSONDecodeError:
                    # Ignore lines that look like JSON but fail to parse
                    pass
        return json_lines

    def test_get_market_data_establishes_trace_hierarchy(self):
        """
        Verify that get_market_data creates a root trace and all sub-operations are correctly parented.
        """
        service = MarketDataService(enable_logging=True, log_level="DEBUG")
        
        try:
            market_data = service.get_market_data("BTCUSDT")
        except Exception as e:
            self.fail(f"get_market_data failed unexpectedly: {e}")

        logs = self.get_log_entries()
        
        # Find the root operation log for get_market_data
        root_log = next((log for log in logs if log.get("operation") == "get_market_data" and "flow_start" in log.get("tags", [])), None)
        self.assertIsNotNone(root_log, "Root 'get_market_data' start log not found.")
        
        root_trace_id = root_log.get("trace_id")
        self.assertIsNone(root_log.get("parent_trace_id"), "Root operation should not have a parent_trace_id.")

        # Check child operations
        child_operations = ["get_klines", "rsi_calculation", "macd_calculation", "ma_calculation", "volume_analysis"]
        for op_name in child_operations:
            child_log = next((log for log in logs if log.get("operation") == op_name and "flow_start" in log.get("tags", [])), None)
            self.assertIsNotNone(child_log, f"Child operation '{op_name}' log not found.")
            self.assertEqual(child_log.get("parent_trace_id"), root_trace_id, f"'{op_name}' should be a child of 'get_market_data'.")
            self.assertNotEqual(child_log.get("trace_id"), root_trace_id, f"'{op_name}' should have its own unique trace_id.")

    def test_get_enhanced_context_continues_trace_hierarchy(self):
        """
        Verify that get_enhanced_context correctly uses the trace_id from MarketDataSet as its parent.
        """
        service = MarketDataService(enable_logging=True, log_level="DEBUG")
        
        try:
            market_data = service.get_market_data("ETHUSDT")
            # Reset the stream to only capture the next operation's logs
            self.mock_stderr.truncate(0)
            self.mock_stderr.seek(0)
            
            service.get_enhanced_context(market_data)
            
        except Exception as e:
            self.fail(f"Test failed unexpectedly: {e}")

        logs = self.get_log_entries()
        
        parent_trace_id = market_data.trace_id
        self.assertIsNotNone(parent_trace_id, "MarketDataSet should have a trace_id from the initial call.")

        # Find the log for get_enhanced_context
        enhanced_context_log = next((log for log in logs if log.get("operation") == "get_enhanced_context" and "flow_start" in log.get("tags", [])), None)
        self.assertIsNotNone(enhanced_context_log, "'get_enhanced_context' start log not found.")
        
        self.assertEqual(enhanced_context_log.get("parent_trace_id"), parent_trace_id, "'get_enhanced_context' should be a child of the 'get_market_data' call.")
        self.assertNotEqual(enhanced_context_log.get("trace_id"), parent_trace_id, "'get_enhanced_context' should have its own unique trace_id.")

if __name__ == "__main__":
    unittest.main()