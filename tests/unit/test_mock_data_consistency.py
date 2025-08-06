#!/usr/bin/env python3
"""
Unit tests to validate mock data consistency across symbols
"""

import unittest
import json
from unittest.mock import patch, Mock
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from examples.phase6_final_demo import Phase6DemoRunner


class TestMockDataConsistency(unittest.TestCase):
    """Test that mock data is consistent and appropriate for each symbol."""
    
    def setUp(self):
        """Set up test environment."""
        self.demo_runner = Phase6DemoRunner()
        
        # Expected price ranges for validation
        self.expected_price_ranges = {
            'BTCUSDT': (60000, 75000),    # BTC typical range
            'ETHUSDT': (3000, 4500),      # ETH typical range
            'ADAUSDT': (0.3, 0.7),        # ADA typical range
            'BNBUSDT': (500, 800),        # BNB typical range
            'SOLUSDT': (100, 200)         # SOL typical range
        }
        
        # Expected volume ranges (relative to typical trading volumes)
        self.expected_volume_ranges = {
            'BTCUSDT': (1000, 2000),      # BTC lower volume, higher value
            'ETHUSDT': (7000, 10000),     # ETH medium volume
            'ADAUSDT': (100000, 150000),  # ADA high volume, low price
            'BNBUSDT': (4000, 6000),      # BNB medium volume
            'SOLUSDT': (4000, 6000)       # SOL medium volume
        }
    
    def test_symbol_specific_price_consistency(self):
        """Test that generated prices are appropriate for each symbol."""
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT']
        
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                mock_response = self.demo_runner.create_realistic_binance_response(symbol)
                candle_data = mock_response.json()
                
                # Extract OHLC prices from first candle
                candle = candle_data[0]
                open_price = float(candle[1])
                high_price = float(candle[2])
                low_price = float(candle[3])
                close_price = float(candle[4])
                
                # Check prices are in expected range for symbol
                expected_min, expected_max = self.expected_price_ranges[symbol]
                
                self.assertGreaterEqual(open_price, expected_min,
                    f"{symbol} open price {open_price} should be >= {expected_min}")
                self.assertLessEqual(open_price, expected_max,
                    f"{symbol} open price {open_price} should be <= {expected_max}")
                
                self.assertGreaterEqual(high_price, expected_min,
                    f"{symbol} high price {high_price} should be >= {expected_min}")
                self.assertLessEqual(high_price, expected_max,
                    f"{symbol} high price {high_price} should be <= {expected_max}")
                
                self.assertGreaterEqual(low_price, expected_min,
                    f"{symbol} low price {low_price} should be >= {expected_min}")
                self.assertLessEqual(low_price, expected_max,
                    f"{symbol} low price {low_price} should be <= {expected_max}")
                
                self.assertGreaterEqual(close_price, expected_min,
                    f"{symbol} close price {close_price} should be >= {expected_min}")
                self.assertLessEqual(close_price, expected_max,
                    f"{symbol} close price {close_price} should be <= {expected_max}")
    
    def test_symbol_specific_volume_consistency(self):
        """Test that generated volumes are appropriate for each symbol."""
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT']
        
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                mock_response = self.demo_runner.create_realistic_binance_response(symbol)
                candle_data = mock_response.json()
                
                # Extract volume from first candle
                candle = candle_data[0]
                volume = float(candle[5])
                
                # Check volume is in expected range for symbol
                if symbol in self.expected_volume_ranges:
                    expected_min, expected_max = self.expected_volume_ranges[symbol]
                    
                    self.assertGreaterEqual(volume, expected_min,
                        f"{symbol} volume {volume} should be >= {expected_min}")
                    self.assertLessEqual(volume, expected_max,
                        f"{symbol} volume {volume} should be <= {expected_max}")
    
    def test_ohlc_price_relationships(self):
        """Test that OHLC prices follow logical relationships."""
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                mock_response = self.demo_runner.create_realistic_binance_response(symbol)
                candle_data = mock_response.json()
                
                # Extract OHLC prices from first candle
                candle = candle_data[0]
                open_price = float(candle[1])
                high_price = float(candle[2])
                low_price = float(candle[3])
                close_price = float(candle[4])
                
                # High should be >= Open, Close, Low
                self.assertGreaterEqual(high_price, open_price,
                    f"{symbol}: High {high_price} should be >= Open {open_price}")
                self.assertGreaterEqual(high_price, close_price,
                    f"{symbol}: High {high_price} should be >= Close {close_price}")
                self.assertGreaterEqual(high_price, low_price,
                    f"{symbol}: High {high_price} should be >= Low {low_price}")
                
                # Low should be <= Open, Close, High
                self.assertLessEqual(low_price, open_price,
                    f"{symbol}: Low {low_price} should be <= Open {open_price}")
                self.assertLessEqual(low_price, close_price,
                    f"{symbol}: Low {low_price} should be <= Close {close_price}")
                self.assertLessEqual(low_price, high_price,
                    f"{symbol}: Low {low_price} should be <= High {high_price}")
    
    def test_data_format_consistency(self):
        """Test that data format is consistent across symbols."""
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                mock_response = self.demo_runner.create_realistic_binance_response(symbol)
                candle_data = mock_response.json()
                
                # Should have exactly one candle
                self.assertEqual(len(candle_data), 1,
                    f"{symbol}: Should have exactly 1 candle")
                
                candle = candle_data[0]
                
                # Should have exactly 12 fields
                self.assertEqual(len(candle), 12,
                    f"{symbol}: Candle should have 12 fields")
                
                # Check field types and ranges
                open_time = int(candle[0])
                close_time = int(candle[6])
                count = int(candle[8])
                
                # Timestamps should be reasonable
                self.assertGreater(open_time, 1600000000000,  # After 2020
                    f"{symbol}: Open time should be recent")
                self.assertGreater(close_time, open_time,
                    f"{symbol}: Close time should be after open time")
                
                # Count should be reasonable
                self.assertGreater(count, 1000,
                    f"{symbol}: Trade count should be realistic")
                self.assertLess(count, 10000,
                    f"{symbol}: Trade count should not be excessive")
    
    def test_no_cross_symbol_data_contamination(self):
        """Test that each symbol generates its own distinct data."""
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        symbol_data = {}
        
        # Generate data for each symbol
        for symbol in symbols:
            mock_response = self.demo_runner.create_realistic_binance_response(symbol)
            candle_data = mock_response.json()
            symbol_data[symbol] = candle_data[0]
        
        # Compare data between symbols - should be different
        btc_data = symbol_data['BTCUSDT']
        eth_data = symbol_data['ETHUSDT']
        ada_data = symbol_data['ADAUSDT']
        
        # Prices should be significantly different
        btc_price = float(btc_data[1])  # BTC open price
        eth_price = float(eth_data[1])  # ETH open price
        ada_price = float(ada_data[1])  # ADA open price
        
        # BTC price should be much higher than ETH
        self.assertGreater(btc_price, eth_price * 10,
            f"BTC price {btc_price} should be much higher than ETH price {eth_price}")
        
        # ETH price should be much higher than ADA
        self.assertGreater(eth_price, ada_price * 1000,
            f"ETH price {eth_price} should be much higher than ADA price {ada_price}")
        
        # Volumes should be different patterns
        btc_volume = float(btc_data[5])
        eth_volume = float(eth_data[5])
        ada_volume = float(ada_data[5])
        
        # ADA should have highest volume (typical altcoin pattern)
        self.assertGreater(ada_volume, eth_volume,
            f"ADA volume {ada_volume} should be higher than ETH volume {eth_volume}")
        self.assertGreater(ada_volume, btc_volume,
            f"ADA volume {ada_volume} should be higher than BTC volume {btc_volume}")
    
    def test_multiple_calls_generate_consistent_symbol_data(self):
        """Test that multiple calls for same symbol generate consistent data patterns."""
        symbol = "BTCUSDT"
        prices = []
        volumes = []
        
        # Generate multiple data points for same symbol
        for i in range(5):
            mock_response = self.demo_runner.create_realistic_binance_response(symbol)
            candle_data = mock_response.json()
            candle = candle_data[0]
            
            price = float(candle[1])  # open price
            volume = float(candle[5])  # volume
            
            prices.append(price)
            volumes.append(volume)
        
        # All prices should be within reasonable BTC range
        btc_min, btc_max = self.expected_price_ranges[symbol]
        for price in prices:
            self.assertGreaterEqual(price, btc_min,
                f"BTC price {price} should be >= {btc_min}")
            self.assertLessEqual(price, btc_max,
                f"BTC price {price} should be <= {btc_max}")
        
        # All volumes should be within reasonable BTC range
        btc_vol_min, btc_vol_max = self.expected_volume_ranges[symbol]
        for volume in volumes:
            self.assertGreaterEqual(volume, btc_vol_min,
                f"BTC volume {volume} should be >= {btc_vol_min}")
            self.assertLessEqual(volume, btc_vol_max,
                f"BTC volume {volume} should be <= {btc_vol_max}")


if __name__ == '__main__':
    unittest.main()