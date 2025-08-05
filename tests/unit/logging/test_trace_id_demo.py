"""
Demo test for Task 7.4: Successful trace_id uniqueness implementation

This test demonstrates that the trace_id uniqueness fix is working correctly.
"""

import pytest
from src.logging_system import get_flow_id, reset_trace_counter


def test_trace_id_uniqueness_demo():
    """Demonstration that trace_id uniqueness is working correctly."""
    # Reset counter for clean test
    reset_trace_counter()
    
    # Generate trace_ids for different symbols
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    trace_ids = []
    
    for symbol in symbols:
        trace_id = get_flow_id(symbol, "get_market_data")
        trace_ids.append(trace_id)
    
    # Verify all trace_ids are unique
    unique_trace_ids = set(trace_ids)
    assert len(unique_trace_ids) == len(trace_ids), f"Found duplicate trace_ids: {trace_ids}"
    
    # Verify proper format with counters
    for i, trace_id in enumerate(trace_ids, 1):
        assert trace_id.endswith(f"{i:03d}"), f"Trace_id {trace_id} should end with {i:03d}"
        assert "flow_" in trace_id, f"Trace_id {trace_id} should contain 'flow_'"
    
    print(f"✅ SUCCESS: All {len(symbols)} trace_ids are unique: {trace_ids}")


def test_rapid_generation_uniqueness():
    """Test that rapid trace_id generation produces unique results."""
    reset_trace_counter()
    
    # Generate multiple trace_ids rapidly
    trace_ids = []
    for i in range(10):
        trace_id = get_flow_id("BTCUSDT", "test_operation")
        trace_ids.append(trace_id)
    
    # All should be unique
    unique_trace_ids = set(trace_ids)
    assert len(unique_trace_ids) == len(trace_ids), f"Found duplicate trace_ids in rapid generation"
    
    # Should have incremental counters
    for i, trace_id in enumerate(trace_ids, 1):
        assert trace_id.endswith(f"{i:03d}"), f"Trace_id {trace_id} should end with {i:03d}"
    
    print(f"✅ SUCCESS: Rapid generation of {len(trace_ids)} unique trace_ids")


if __name__ == "__main__":
    test_trace_id_uniqueness_demo()
    test_rapid_generation_uniqueness()
    print("\n🎉 Task 7.4 COMPLETED: trace_id uniqueness successfully implemented!")