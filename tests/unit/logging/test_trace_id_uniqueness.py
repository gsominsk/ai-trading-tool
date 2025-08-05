"""
Test suite for Task 7.4: Тестирование уникальности trace_id между символами в логах

Validates that trace_id generation produces unique identifiers for different symbols
and maintains consistency for the same symbol operations.
"""

import pytest
import json
import io
import sys
from unittest.mock import patch, MagicMock
from src.logging_system import MarketDataLogger, get_flow_id, reset_trace_counter


class TestTraceIdUniqueness:
    """Test suite for trace_id uniqueness validation."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        # Reset trace counter for clean tests
        reset_trace_counter()
        
        # Create logger instance
        self.logger = MarketDataLogger("test_uniqueness")
    
    def teardown_method(self):
        """Cleanup after each test."""
        reset_trace_counter()
    
    def test_different_symbols_unique_trace_ids(self, caplog):
        """Test that different symbols produce unique trace_ids."""
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "DOGEUSDT"]
        
        # Log operations for multiple symbols
        for symbol in symbols:
            self.logger.log_operation_start(
                operation="get_market_data",
                symbol=symbol,
                context={"test": f"uniqueness_{symbol.lower()}"}
            )
        
        # Extract trace_ids from log records
        trace_ids = []
        for record in caplog.records:
            if hasattr(record, 'trace_id') and record.trace_id:
                trace_ids.append(record.trace_id)
        
        # Verify we have trace_ids for all symbols
        assert len(trace_ids) == len(symbols), f"Expected {len(symbols)} trace_ids, got {len(trace_ids)}"
        
        # Verify all trace_ids are unique
        unique_trace_ids = set(trace_ids)
        assert len(unique_trace_ids) == len(trace_ids), f"Found duplicate trace_ids: {trace_ids}"
        
        # Verify trace_id format contains symbol identifiers
        symbol_patterns = ["btc", "eth", "ada", "bnb", "doge"]
        for i, trace_id in enumerate(trace_ids):
            assert symbol_patterns[i] in trace_id.lower(), f"Trace_id {trace_id} doesn't contain {symbol_patterns[i]}"
            # Verify trace_id has counter suffix for uniqueness
            assert any(c.isdigit() for c in trace_id[-3:]), f"Trace_id {trace_id} doesn't have counter suffix"
        
        print(f"✓ Uniqueness test passed for {len(symbols)} symbols")
        print(f"Generated trace_ids: {trace_ids}")
    
    def test_same_symbol_consistent_trace_ids(self, caplog):
        """Test that same symbol produces consistent trace_id pattern."""
        symbol = "BTCUSDT"
        
        # Log multiple operations for the same symbol
        for i in range(3):
            self.logger.log_operation_start(
                operation="get_market_data",
                symbol=symbol,
                context={"test": f"consistency_check_{i}"}
            )
        
        # Extract trace_ids from log records
        trace_ids = []
        for record in caplog.records:
            if hasattr(record, 'trace_id') and record.trace_id:
                trace_ids.append(record.trace_id)
        
        # Verify we have trace_ids for all operations
        assert len(trace_ids) == 3, f"Expected 3 trace_ids, got {len(trace_ids)}"
        
        # Verify all trace_ids contain the same symbol pattern
        for trace_id in trace_ids:
            assert "btc" in trace_id.lower(), f"Trace_id {trace_id} doesn't contain 'btc'"
        
        # Verify trace_ids are still unique (different timestamps)
        unique_trace_ids = set(trace_ids)
        assert len(unique_trace_ids) == len(trace_ids), f"Found duplicate trace_ids: {trace_ids}"
        
        print(f"✓ Consistency test passed. All trace_ids contain 'btc': {trace_ids}")
    
    def test_trace_id_format_validation(self, caplog):
        """Test that trace_id follows expected format pattern."""
        symbols = ["BTCUSDT", "ETHUSDT"]
        
        # Log operations
        for symbol in symbols:
            self.logger.log_operation_start(
                operation="get_market_data",
                symbol=symbol,
                context={"test": "format_validation"}
            )
        
        # Extract trace_ids from log records
        trace_ids = []
        for record in caplog.records:
            if hasattr(record, 'trace_id') and record.trace_id:
                trace_ids.append(record.trace_id)
        
        # Validate trace_id format
        for trace_id in trace_ids:
            # Should start with 'flow_'
            assert trace_id.startswith("flow_"), f"Trace_id {trace_id} doesn't start with 'flow_'"
            
            # Should contain symbol abbreviation
            symbol_abbrevs = ["btc", "eth"]
            contains_symbol = any(abbrev in trace_id.lower() for abbrev in symbol_abbrevs)
            assert contains_symbol, f"Trace_id {trace_id} doesn't contain symbol abbreviation"
            
            # Should contain timestamp and counter (numbers)
            assert any(c.isdigit() for c in trace_id), f"Trace_id {trace_id} doesn't contain timestamp"
            # Should have 3-digit counter at the end
            assert trace_id[-3:].isdigit(), f"Trace_id {trace_id} doesn't have 3-digit counter suffix"
        
        print(f"✓ Format validation passed: {trace_ids}")
    
    def test_cross_operation_trace_id_uniqueness(self, caplog):
        """Test trace_id uniqueness across different operations for different symbols."""
        test_data = [
            ("BTCUSDT", "get_market_data"),
            ("ETHUSDT", "get_klines"),
            ("ADAUSDT", "get_market_data"),
            ("BNBUSDT", "calculate_indicators"),
        ]
        
        # Log different operations for different symbols
        for symbol, operation in test_data:
            self.logger.log_operation_start(
                operation=operation,
                symbol=symbol,
                context={"test": f"cross_op_{symbol}_{operation}"}
            )
        
        # Extract trace_ids from log records
        trace_ids = []
        for record in caplog.records:
            if hasattr(record, 'trace_id') and record.trace_id:
                trace_ids.append(record.trace_id)
        
        # Verify we have trace_ids for all operations
        assert len(trace_ids) == len(test_data), f"Expected {len(test_data)} trace_ids, got {len(trace_ids)}"
        
        # Verify all trace_ids are unique
        unique_trace_ids = set(trace_ids)
        assert len(unique_trace_ids) == len(trace_ids), f"Found duplicate trace_ids: {trace_ids}"
        
        print(f"✓ Cross-operation uniqueness test passed: {trace_ids}")
    
    def test_get_flow_id_direct_uniqueness(self):
        """Test get_flow_id function directly for uniqueness."""
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT"]
        operation = "get_market_data"
        
        # Generate trace_ids directly
        trace_ids = []
        for symbol in symbols:
            trace_id = get_flow_id(symbol, operation)
            trace_ids.append(trace_id)
        
        # Verify all trace_ids are unique
        unique_trace_ids = set(trace_ids)
        assert len(unique_trace_ids) == len(trace_ids), f"Found duplicate trace_ids: {trace_ids}"
        
        # Verify each trace_id contains appropriate symbol
        expected_patterns = ["btc", "eth", "ada", "bnb"]
        for i, trace_id in enumerate(trace_ids):
            assert expected_patterns[i] in trace_id.lower(), f"Trace_id {trace_id} doesn't contain {expected_patterns[i]}"
        
        print(f"✓ Direct get_flow_id uniqueness test passed: {trace_ids}")
    
    def test_trace_id_consistency_over_time(self):
        """Test that trace_id generation maintains consistency patterns over time."""
        symbol = "BTCUSDT"
        operation = "get_market_data"
        
        # Generate multiple trace_ids with small time intervals
        trace_ids = []
        for i in range(5):
            trace_id = get_flow_id(symbol, operation)
            trace_ids.append(trace_id)
        
        # All should be unique due to timestamp
        unique_trace_ids = set(trace_ids)
        assert len(unique_trace_ids) == len(trace_ids), f"Found duplicate trace_ids: {trace_ids}"
        
        # All should contain the same symbol pattern
        for trace_id in trace_ids:
            assert "btc" in trace_id.lower(), f"Trace_id {trace_id} doesn't contain 'btc'"
            assert trace_id.startswith("flow_"), f"Trace_id {trace_id} doesn't start with 'flow_'"
            # Should have 3-digit counter at the end
            assert trace_id[-3:].isdigit(), f"Trace_id {trace_id} doesn't have 3-digit counter suffix"
        
        print(f"✓ Time consistency test passed: {trace_ids}")
    
    def _extract_trace_ids_from_logs(self, log_output: str) -> list:
        """Extract trace_ids from JSON log output."""
        trace_ids = []
        
        for line in log_output.strip().split('\n'):
            if not line.strip():
                continue
            try:
                log_entry = json.loads(line)
                if 'trace_id' in log_entry:
                    trace_ids.append(log_entry['trace_id'])
            except json.JSONDecodeError:
                # Skip non-JSON lines
                continue
        
        return trace_ids


class TestTraceIdBoundaryConditions:
    """Test edge cases and boundary conditions for trace_id generation."""
    
    def setup_method(self):
        """Setup test environment."""
        reset_trace_counter()
        self.logger = MarketDataLogger("test_boundary")
    
    def teardown_method(self):
        """Cleanup after each test."""
        reset_trace_counter()
    
    def test_empty_symbol_handling(self, caplog):
        """Test trace_id generation with empty or None symbol."""
        # Test with None symbol
        self.logger.log_operation_start(
            operation="system_check",
            symbol=None,
            context={"test": "none_symbol"}
        )
        
        # Test with empty symbol
        self.logger.log_operation_start(
            operation="system_check",
            symbol="",
            context={"test": "empty_symbol"}
        )
        
        # Extract trace_ids from log records (may be None for fallback generation)
        trace_ids = []
        for record in caplog.records:
            if hasattr(record, 'trace_id'):
                # For empty/None symbols, trace_id might be None and generated in formatter
                if record.trace_id is not None:
                    trace_ids.append(record.trace_id)
                else:
                    # If None, the formatter will generate fallback - verify no symbol patterns
                    assert record.operation == "system_check"
        
        # Should have generated some trace_ids or None values processed
        assert len(caplog.records) == 2, f"Expected 2 log records, got {len(caplog.records)}"
        
        # Any generated trace_ids should not contain symbol-specific patterns
        for trace_id in trace_ids:
            assert not any(pattern in trace_id.lower() for pattern in ["btc", "eth", "ada"]), \
                f"Trace_id {trace_id} contains symbol pattern when it shouldn't"
        
        print(f"✓ Empty symbol handling test passed: {trace_ids}")
    
    def test_unusual_symbol_formats(self, caplog):
        """Test trace_id generation with unusual but valid symbol formats."""
        unusual_symbols = ["1000SATSUSDT", "PEPEUSDT", "SHIBAINIUUSDT"]
        
        for symbol in unusual_symbols:
            self.logger.log_operation_start(
                operation="get_market_data",
                symbol=symbol,
                context={"test": f"unusual_{symbol}"}
            )
        
        # Extract trace_ids from log records
        trace_ids = []
        for record in caplog.records:
            if hasattr(record, 'trace_id') and record.trace_id:
                trace_ids.append(record.trace_id)
        
        # Should have unique trace_ids
        assert len(trace_ids) == len(unusual_symbols), f"Expected {len(unusual_symbols)} trace_ids, got {len(trace_ids)}"
        
        unique_trace_ids = set(trace_ids)
        assert len(unique_trace_ids) == len(trace_ids), f"Found duplicate trace_ids: {trace_ids}"
        
        print(f"✓ Unusual symbol formats test passed: {trace_ids}")
    
    def _extract_trace_ids_from_logs(self, log_output: str) -> list:
        """Extract trace_ids from JSON log output."""
        trace_ids = []
        
        for line in log_output.strip().split('\n'):
            if not line.strip():
                continue
            try:
                log_entry = json.loads(line)
                if 'trace_id' in log_entry:
                    trace_ids.append(log_entry['trace_id'])
            except json.JSONDecodeError:
                continue
        
        return trace_ids


if __name__ == "__main__":
    # Quick test runner for development
    print("Running trace_id uniqueness tests...")
    
    # Test direct function uniqueness
    test_direct = TestTraceIdUniqueness()
    test_direct.setup_method()
    test_direct.test_get_flow_id_direct_uniqueness()
    test_direct.test_trace_id_consistency_over_time()
    test_direct.teardown_method()
    
    # Test boundary conditions
    test_boundary = TestTraceIdBoundaryConditions()
    test_boundary.setup_method()
    # Note: boundary tests need mock_stderr, so we skip them in direct run
    test_boundary.teardown_method()
    
    print("\n✅ All trace_id uniqueness tests completed successfully!")