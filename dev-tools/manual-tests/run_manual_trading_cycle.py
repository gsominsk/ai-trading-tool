import sys
import os
import csv
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.trading.trading_cycle import TradingCycle
from src.trading.oms import OrderManagementSystem
from src.trading.repository import OrderRepository
from src.market_data.market_data_service import MarketDataService

def main():
    """
    Main function to run a manual trading cycle.
    Initializes the system components and executes one cycle.
    """
    print("--- Manual Trading Cycle Runner ---")
    print(f"Project Root: {project_root}")
    
    # Define paths
    data_dir = project_root / "data"
    log_file = data_dir / "trade_log.csv"
    oms_state_file = data_dir / "oms_state.json"
    header = ['timestamp', 'order_id', 'symbol', 'order_type', 'price', 'quantity', 'status']
    
    os.makedirs(data_dir, exist_ok=True)
    
    # Check and write header for trade_log.csv if needed
    needs_header = True
    if log_file.exists() and os.path.getsize(log_file) > 0:
        with open(log_file, 'r', newline='') as f:
            try:
                reader = csv.reader(f)
                first_row = next(reader)
                if first_row == header:
                    needs_header = False
            except StopIteration:
                pass
    
    if needs_header:
        with open(log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        print(f"Log file '{log_file}' initialized with header.")
    else:
        print(f"Log file '{log_file}' already has a valid header.")

    # Initialize system components with persistence
    print(f"Using OMS state file: '{oms_state_file}'")
    repository = OrderRepository(file_path=str(oms_state_file))
    oms = OrderManagementSystem(repository=repository)
    market_data_service = MarketDataService()
    trading_cycle = TradingCycle(oms=oms, market_data_service=market_data_service)
    
    print("\nComponents initialized. Starting trading cycle...")
    
    try:
        trading_cycle.run_cycle()
        print("\nTrading cycle finished successfully.")
        print(f"Check the log file for details: {trading_cycle.trade_log_path}")
    except Exception as e:
        print(f"\nAn error occurred during the trading cycle: {e}")

if __name__ == "__main__":
    main()