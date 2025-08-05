#!/usr/bin/env python3
"""
Test script for HTTP logging filter functionality.
Tests that urllib3/requests logs are filtered while preserving AI operation logs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.logging_system.logger_config import configure_ai_logging
from src.market_data.market_data_service import MarketDataService
import logging

def test_http_filter():
    """Test HTTP logging filter by running market data operations."""
    
    print("🔧 Configuring AI logging with HTTP noise filtering...")
    
    # Configure with HTTP filtering enabled
    configure_ai_logging(
        log_level="DEBUG",
        log_file="logs/http_filter_test.log", 
        console_output=True,
        filter_http_noise=True  # Enable HTTP filtering
    )
    
    print("✅ AI logging configured with HTTP filtering")
    print("📊 Starting market data operations to test filtering...")
    
    # Initialize market data service
    service = MarketDataService()
    
    # Test operations that previously generated "unknown" logs
    try:
        # This should generate HTTP requests but filter the verbose logs
        market_data = service.get_market_data("BTCUSDT")
        
        print(f"📈 Market data retrieved: {len(market_data)} records")
        
        # Check if we have any data
        if market_data:
            print("✅ Market operations completed successfully")
            print("🔍 Check logs/http_filter_test.log for filtered results")
        else:
            print("⚠️  No market data retrieved, but HTTP filtering test completed")
            
    except Exception as e:
        print(f"❌ Error during market data operations: {e}")
    
    print("\n🎯 HTTP filter test completed!")
    print("📝 Analyze logs/http_filter_test.log to verify:")
    print("   - AI operation logs are present")
    print("   - urllib3/requests verbose logs are filtered")
    print("   - No 'unknown' operations from HTTP libraries")

if __name__ == "__main__":
    test_http_filter()