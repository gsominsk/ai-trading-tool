#!/usr/bin/env python3
"""
AI Trading System - Phase 9: End-to-End Tracing Demonstration
==============================================================

This script demonstrates the complete, end-to-end logging and tracing
capabilities of the AI Trading System, starting from the TradingCycle.

IT SHOWCASES:
- Master Trace ID Generation: A single `master_trace_id` is created at the start of `run_cycle`.
- Trace ID Propagation: The `master_trace_id` is passed through all system layers:
    - TradingCycle -> MarketDataService
    - TradingCycle -> OrderManagementSystem
    - OrderManagementSystem -> OmsRepository
- Comprehensive Logging: All logs, from high-level business logic to low-level
  database operations and API calls, are tagged with the same `master_trace_id`.
- Real-world Scenario: Simulates a full trading cycle, including:
    1. Checking for existing orders.
    2. Fetching market data from the REAL Binance API.
    3. Making a mock AI decision.
    4. Placing a new order.

Usage:
    python3 examples/phase9_full_cycle_demo.py

Expected Output:
    - Structured JSON logs in `logs/ai_trading_...log` and on the console.
    - All logs related to a single `run_cycle` will share the same `master_trace_id`.
    - You can `grep` the log file for a specific `trace_id` to see the entire
      operation lifecycle across all system components.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logging_system import configure_ai_logging, MarketDataLogger
from src.market_data.market_data_service import MarketDataService
from src.trading.oms import OrderManagementSystem
from src.trading.oms_repository import OmsRepository
from src.trading.trading_cycle import TradingCycle


def setup_logging():
    """Configure AI-optimized DEBUG logging for the demonstration."""
    print("🔧 AI Trading System - Phase 9 End-to-End Tracing Demo")
    print("=" * 60)
    print("🚀 Setting up enhanced DEBUG logging architecture...")
    
    log_date = datetime.now().strftime('%Y%m%d')
    log_file = f"logs/ai_trading_{log_date}.log"
    
    configure_ai_logging(
        log_level="DEBUG",
        console_output=True,
        log_file=log_file,
        max_bytes=10*1024*1024,
        backup_count=3
    )
    
    print(f"✅ AI-optimized DEBUG logging configured. Log file: {log_file}")
    print("=" * 60)


def main():
    """
    Initializes all system components and runs a single, complete trading cycle
    to demonstrate end-to-end tracing.
    """
    setup_logging()

    print("\n🏭 Initializing System Components...")
    
    # 1. Initialize the Repository (using in-memory SQLite for this demo)
    # In a real scenario, this would be a file path like 'data/oms.db'
    repo_logger = MarketDataLogger("oms_repository", service_name="oms_repository")
    oms_repository = OmsRepository(db_path=":memory:", logger=repo_logger)
    print("   - OmsRepository (in-memory) initialized.")

    # 2. Initialize the Order Management System
    oms_logger = MarketDataLogger("oms", service_name="oms")
    oms = OrderManagementSystem(repository=oms_repository, logger=oms_logger)
    print("   - OrderManagementSystem initialized.")

    # 3. Initialize the Market Data Service
    market_data_service = MarketDataService(enable_logging=True, log_level="DEBUG")
    print("   - MarketDataService initialized.")

    # 4. Initialize the main Trading Cycle
    trading_cycle = TradingCycle(oms=oms, market_data_service=market_data_service)
    print("   - TradingCycle initialized.")
    print("✅ All components are ready.")

    print("\n\n▶️  Running a Single Trading Cycle...")
    print("-" * 40)
    
    try:
        trading_cycle.run_cycle()
        print("\n🏁 Trading cycle finished.")
        print("🔍 Review the logs above or in the log file to see the complete trace.")
        print("   Look for the 'master_trace_id' to follow the entire operation.")

    except Exception as e:
        print(f"\n❌ An error occurred during the trading cycle: {e}")
        print("   This is an opportunity to check the error logs for the correct trace_id.")

    finally:
        # Clean up the in-memory database connection
        oms_repository.close()
        print("\n🔒 In-memory database connection closed.")


if __name__ == "__main__":
    main()