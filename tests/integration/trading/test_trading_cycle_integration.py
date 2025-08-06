import pytest
import os
import pandas as pd
from src.trading.trading_cycle import TradingCycle
from src.trading.oms import OrderManagementSystem
from src.trading.repository import OrderRepository
from src.market_data.market_data_service import MarketDataService

@pytest.fixture(scope="function")
def persistent_storage_cleanup(tmp_path):
    """
    Fixture to clean up trade log and OMS state, and provide a clean environment.
    """
    # Define file paths
    log_file = "data/trade_log.csv"
    oms_state_file = tmp_path / "test_oms_state.json"

    # Setup: Ensure files are clean before the test
    for f in [log_file, oms_state_file]:
        if os.path.exists(f):
            os.remove(f)
    
    # Create the log file with a header
    pd.DataFrame(columns=["timestamp", "order_id", "symbol", "order_type", "price", "quantity", "status"]).to_csv(log_file, index=False)

    yield str(oms_state_file) # Pass the state file path to the test

    # Teardown: Clean up files after the test
    if os.path.exists(log_file):
        os.remove(log_file)
    if os.path.exists(oms_state_file):
        os.remove(oms_state_file)

def test_trading_cycle_full_integration_with_oms(persistent_storage_cleanup):
    """
    Tests the full integration of TradingCycle with a persistent OMS.
    Verifies that a trade is executed and the log is updated correctly.
    """
    # 1. Setup
    oms_state_file = persistent_storage_cleanup
    repository = OrderRepository(file_path=oms_state_file)
    oms = OrderManagementSystem(repository=repository)
    market_data_service = MarketDataService()
    trading_cycle = TradingCycle(oms=oms, market_data_service=market_data_service)

    # 2. Execute the first trading cycle to place the order
    trading_cycle.run_cycle()

    # 3. Verification after the first run
    log_df_after_first_run = pd.read_csv("data/trade_log.csv")
    assert len(log_df_after_first_run) == 1, "A new trade should have been logged"
    first_record = log_df_after_first_run.iloc[0]
    assert first_record["status"] == "PENDING", "Order should be PENDING after the first cycle"

    # 4. Execute the second trading cycle to update the order status
    print("\n--- Running second cycle to update status ---")
    trading_cycle.run_cycle()
    
    # 5. Verification after the second run
    log_df_after_second_run = pd.read_csv("data/trade_log.csv")
    
    # The log should now have two entries: the initial PENDING and the final FILLED
    assert len(log_df_after_second_run) == 2, "Log should have two records after status update"
    
    last_record = log_df_after_second_run.iloc[-1]
    assert last_record["symbol"] == "BTCUSDT"
    assert last_record["order_type"] == "BUY"
    assert last_record["quantity"] == 0.01
    assert last_record["status"] == "FILLED", "Order status should be updated to FILLED in the second cycle"
    assert pd.notna(last_record["order_id"])
    assert pd.notna(last_record["timestamp"])
    assert last_record["order_id"] == first_record["order_id"], "The order ID should be the same"