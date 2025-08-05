#!/usr/bin/env python3
"""
Test operation context - verify all operations have proper identification.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.logging_system.logger_config import configure_ai_logging
from src.logging_system.json_formatter import get_logger
import logging

def test_operation_context():
    """Test that operations have proper context identification."""
    
    print("🔧 Testing operation context identification...")
    
    # Configure AI logging 
    configure_ai_logging(
        log_level="DEBUG",
        log_file="logs/operation_context_test.log", 
        console_output=True,
        filter_http_noise=True
    )
    
    # Get structured logger
    logger = get_logger("operation_context_test")
    
    # Test 1: AI operation with proper context
    logger.info(
        message="Test operation with context",
        operation="test_operation", 
        context={"test": "value"},
        trace_id="test_trace_001"
    )
    
    # Test 2: Direct logging without operation (should get 'unknown')
    raw_logger = logging.getLogger("test_raw")
    raw_logger.info("Direct log without operation context")
    
    print("✅ Operation context test completed!")
    print("📝 Check logs/operation_context_test.log for results")

if __name__ == "__main__":
    test_operation_context()