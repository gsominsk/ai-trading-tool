#!/usr/bin/env python3
"""
Unit tests to validate UUID isolation between symbols and uniqueness per call
"""

import unittest
import time
from unittest.mock import patch, Mock
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from examples.phase6_final_demo import Phase6DemoRunner


class TestUUIDIsolation(unittest.TestCase):
    """Test that UUIDs are isolated by symbol and unique per call."""
    
    def setUp(self):
        """Set up test environment."""
        self.demo_runner = Phase6DemoRunner()
    
    def test_uuid_contains_correct_symbol(self):
        """Test that UUIDs contain the correct symbol identifier."""
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT']
        
        for symbol in test_symbols:
            with self.subTest(symbol=symbol):
                mock_response = self.demo_runner.create_realistic_binance_response(symbol)
                uuid = mock_response.headers['x-mbx-uuid']
                
                # UUID should contain the symbol in lowercase
                expected_symbol = symbol.lower()
                self.assertIn(expected_symbol, uuid,
                    f"UUID '{uuid}' should contain symbol '{expected_symbol}'")
                
                # UUID should not contain other symbols
                other_symbols = [s.lower() for s in test_symbols if s != symbol]
                for other_symbol in other_symbols:
                    self.assertNotIn(other_symbol, uuid,
                        f"UUID '{uuid}' should not contain other symbol '{other_symbol}'")
    
    def test_uuid_uniqueness_across_calls(self):
        """Test that UUIDs are unique across multiple calls for the same symbol."""
        symbol = "BTCUSDT"
        uuids = []
        
        # Generate multiple UUIDs for the same symbol
        for i in range(10):
            mock_response = self.demo_runner.create_realistic_binance_response(symbol)
            uuid = mock_response.headers['x-mbx-uuid']
            uuids.append(uuid)
            time.sleep(0.001)  # Small delay to ensure timestamp changes
        
        # All UUIDs should be unique
        unique_uuids = set(uuids)
        self.assertEqual(len(unique_uuids), len(uuids),
            f"Expected {len(uuids)} unique UUIDs, got {len(unique_uuids)}. Duplicates: {[uuid for uuid in uuids if uuids.count(uuid) > 1]}")
    
    def test_uuid_isolation_between_symbols(self):
        """Test that different symbols generate different UUIDs."""
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        symbol_uuids = {}
        
        # Generate UUIDs for different symbols
        for symbol in symbols:
            mock_response = self.demo_runner.create_realistic_binance_response(symbol)
            uuid = mock_response.headers['x-mbx-uuid']
            symbol_uuids[symbol] = uuid
        
        # All UUIDs should be different
        uuids = list(symbol_uuids.values())
        unique_uuids = set(uuids)
        self.assertEqual(len(unique_uuids), len(uuids),
            f"UUIDs should be unique between symbols. Got: {symbol_uuids}")
        
        # Each UUID should contain its corresponding symbol
        for symbol, uuid in symbol_uuids.items():
            self.assertIn(symbol.lower(), uuid,
                f"UUID '{uuid}' should contain symbol '{symbol.lower()}'")
    
    def test_uuid_format_consistency(self):
        """Test that UUIDs follow the expected format: demo-{symbol}-{timestamp}"""
        import re
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        uuid_pattern = re.compile(r'^demo-([a-z]+)-(\d+)$')
        
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                mock_response = self.demo_runner.create_realistic_binance_response(symbol)
                uuid = mock_response.headers['x-mbx-uuid']
                
                # Check format matches pattern
                match = uuid_pattern.match(uuid)
                self.assertIsNotNone(match, 
                    f"UUID '{uuid}' should match format 'demo-{{symbol}}-{{timestamp}}'")
                
                if match:
                    extracted_symbol = match.group(1)
                    timestamp_str = match.group(2)
                    
                    # Check symbol matches
                    self.assertEqual(extracted_symbol, symbol.lower(),
                        f"Extracted symbol '{extracted_symbol}' should match '{symbol.lower()}'")
                    
                    # Check timestamp is numeric and reasonable
                    timestamp = int(timestamp_str)
                    current_time_ms = int(time.time() * 1000)
                    self.assertGreater(timestamp, current_time_ms - 10000,  # Within last 10 seconds
                        f"Timestamp {timestamp} should be recent")
                    self.assertLess(timestamp, current_time_ms + 10000,  # Not too far in future
                        f"Timestamp {timestamp} should not be too far in future")
    
    def test_fresh_response_generation(self):
        """Test that fresh responses are generated with different UUIDs."""
        symbol = "BTCUSDT"
        
        # Simulate the pattern used in the fixed demo
        def create_fresh_response(*args, **kwargs):
            return self.demo_runner.create_realistic_binance_response(symbol)
        
        # Generate multiple responses
        responses = []
        for i in range(5):
            response = create_fresh_response()
            responses.append(response)
            time.sleep(0.001)
        
        # Extract UUIDs
        uuids = [response.headers['x-mbx-uuid'] for response in responses]
        
        # All should be unique
        unique_uuids = set(uuids)
        self.assertEqual(len(unique_uuids), len(uuids),
            f"Fresh responses should have unique UUIDs. Got: {uuids}")
        
        # All should contain correct symbol
        for uuid in uuids:
            self.assertIn(symbol.lower(), uuid,
                f"UUID '{uuid}' should contain symbol '{symbol.lower()}'")
    
    def test_concurrent_symbol_processing_isolation(self):
        """Test that concurrent processing of different symbols maintains isolation."""
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        all_uuids = []
        
        # Simulate concurrent processing
        for symbol in symbols:
            for call_num in range(3):  # 3 API calls per symbol
                mock_response = self.demo_runner.create_realistic_binance_response(symbol)
                uuid = mock_response.headers['x-mbx-uuid']
                all_uuids.append((symbol, uuid))
        
        # Verify each UUID belongs to correct symbol
        for symbol, uuid in all_uuids:
            self.assertIn(symbol.lower(), uuid,
                f"UUID '{uuid}' should contain symbol '{symbol.lower()}'")
        
        # Verify no cross-contamination
        btc_uuids = [uuid for symbol, uuid in all_uuids if symbol == 'BTCUSDT']
        eth_uuids = [uuid for symbol, uuid in all_uuids if symbol == 'ETHUSDT']
        ada_uuids = [uuid for symbol, uuid in all_uuids if symbol == 'ADAUSDT']
        
        # BTC UUIDs should not contain ETH or ADA
        for uuid in btc_uuids:
            self.assertNotIn('ethusdt', uuid, f"BTC UUID '{uuid}' should not contain 'ethusdt'")
            self.assertNotIn('adausdt', uuid, f"BTC UUID '{uuid}' should not contain 'adausdt'")
        
        # ETH UUIDs should not contain BTC or ADA  
        for uuid in eth_uuids:
            self.assertNotIn('btcusdt', uuid, f"ETH UUID '{uuid}' should not contain 'btcusdt'")
            self.assertNotIn('adausdt', uuid, f"ETH UUID '{uuid}' should not contain 'adausdt'")
        
        # ADA UUIDs should not contain BTC or ETH
        for uuid in ada_uuids:
            self.assertNotIn('btcusdt', uuid, f"ADA UUID '{uuid}' should not contain 'btcusdt'")
            self.assertNotIn('ethusdt', uuid, f"ADA UUID '{uuid}' should not contain 'ethusdt'")


if __name__ == '__main__':
    unittest.main()