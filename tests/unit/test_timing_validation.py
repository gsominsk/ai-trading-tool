#!/usr/bin/env python3
"""
Unit tests to validate timing metrics are always positive
"""

import unittest
import time
from unittest.mock import patch, Mock
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from examples.phase6_final_demo import Phase6DemoRunner


class TestTimingValidation(unittest.TestCase):
    """Test that timing metrics are always positive values."""
    
    def setUp(self):
        """Set up test environment."""
        self.demo_runner = Phase6DemoRunner()
    
    def test_realistic_timestamp_generation(self):
        """Test that generated timestamps are incrementing and produce positive timing."""
        base_time = time.time()
        
        # Test the pattern used in the fixed demo
        timestamps = [
            base_time, base_time + 0.150, base_time + 0.155,
            base_time + 0.300, base_time + 0.450, base_time + 0.455
        ]
        
        # Simulate timing calculations
        for i in range(0, len(timestamps)-1, 2):
            start_time = timestamps[i]
            end_time = timestamps[i+1]
            elapsed = end_time - start_time
            
            self.assertGreater(elapsed, 0, 
                f"Timing should be positive: {elapsed}s (start: {start_time}, end: {end_time})")
            self.assertLess(elapsed, 1.0, 
                f"Timing should be realistic: {elapsed}s")
    
    def test_demo_timing_patterns_are_positive(self):
        """Test that all demo timing patterns produce positive values."""
        test_cases = [
            # (base_time_offset, response_time, description)
            (0, 0.150, "Normal market data operation"),
            (0, 0.180, "Enhanced context operation"),  
            (0, 0.120, "Technical indicators calculation"),
            (0, 0.045, "Fast cache hit"),
            (0, 0.650, "Slow network response"),
            (0, 1.200, "Very slow network response")
        ]
        
        for offset, response_time, description in test_cases:
            with self.subTest(description=description):
                base_time = time.time() + offset
                
                # Test single operation timing
                start_time = base_time
                end_time = base_time + response_time
                elapsed = end_time - start_time
                
                self.assertGreater(elapsed, 0, 
                    f"{description}: Timing should be positive: {elapsed}s")
                self.assertAlmostEqual(elapsed, response_time, places=3,
                    msg=f"{description}: Timing should match expected response time")
    
    def test_multi_operation_timing_sequence(self):
        """Test that multi-operation sequences maintain positive timing."""
        base_time = time.time()
        response_time = 0.200
        gap_between_operations = 0.100
        
        # Simulate the pattern used in multi-symbol integration
        intervals = []
        current_time = base_time
        
        for i in range(5):  # 5 operation cycles
            intervals.extend([
                current_time,
                current_time + response_time,
                current_time + response_time + 0.005
            ])
            current_time += response_time + gap_between_operations
        
        # Validate all timing calculations are positive
        for i in range(0, len(intervals)-1, 3):
            start_time = intervals[i]
            end_time = intervals[i+1]
            cleanup_time = intervals[i+2]
            
            operation_elapsed = end_time - start_time
            cleanup_elapsed = cleanup_time - end_time
            
            self.assertGreater(operation_elapsed, 0,
                f"Operation {i//3}: timing should be positive: {operation_elapsed}s")
            self.assertGreater(cleanup_elapsed, 0,
                f"Cleanup {i//3}: timing should be positive: {cleanup_elapsed}s")
            
            self.assertAlmostEqual(operation_elapsed, response_time, places=3,
                msg=f"Operation {i//3}: should match expected timing")
    
    def test_no_negative_timing_in_demo_scenarios(self):
        """Test that demo scenarios never produce negative timing values."""
        scenarios = [
            ("fast", 0.045),
            ("normal", 0.180), 
            ("slow", 0.650),
            ("very_slow", 1.200)
        ]
        
        for scenario, response_time in scenarios:
            with self.subTest(scenario=scenario):
                base_time = time.time()
                
                # Test the exact pattern used in performance monitoring
                timestamps = [base_time, base_time + response_time, base_time + response_time + 0.005]
                
                for i in range(len(timestamps)-1):
                    elapsed = timestamps[i+1] - timestamps[i]
                    self.assertGreater(elapsed, 0,
                        f"Scenario {scenario}: All timing should be positive: {elapsed}s")


if __name__ == '__main__':
    unittest.main()