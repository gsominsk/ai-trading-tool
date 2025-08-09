import unittest
import re
from datetime import datetime, timezone

from src.logging_system.trace_generator import get_trace_id, reset_trace_counter

class TestTraceGenerator(unittest.TestCase):

    def setUp(self):
        """Reset the counter before each test."""
        reset_trace_counter()

    def test_generate_trace_id_format(self):
        """Test if the generated trace_id has the correct format."""
        trace_id = get_trace_id()
        # Example format: trd_001_20250808233800001
        pattern = r"^trd_\d{3}_\d{14}\d{5}$"
        self.assertIsNotNone(re.match(pattern, trace_id), f"Trace ID {trace_id} does not match pattern {pattern}")

    def test_generate_trace_id_uniqueness(self):
        """Test if sequential trace IDs are unique."""
        trace_id_1 = get_trace_id()
        trace_id_2 = get_trace_id()
        self.assertNotEqual(trace_id_1, trace_id_2)

    def test_reset_counter(self):
        """Test if the counter resets correctly."""
        trace_id_before_reset = get_trace_id()
        
        reset_trace_counter()
        
        trace_id_after_reset = get_trace_id()
        
        # Extract sequence numbers
        seq_before = int(trace_id_before_reset[-5:])
        seq_after = int(trace_id_after_reset[-5:])
        
        self.assertEqual(seq_before, 1)
        self.assertEqual(seq_after, 1)

    def test_parent_trace_id_argument(self):
        """Test that generate_trace_id accepts a parent_trace_id without errors."""
        parent_id = "parent_123"
        try:
            child_id = get_trace_id(parent_trace_id=parent_id)
            self.assertIsInstance(child_id, str)
        except Exception as e:
            self.fail(f"get_trace_id raised an exception with parent_trace_id: {e}")

if __name__ == '__main__':
    unittest.main()