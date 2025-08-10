import pytest
import os
from src.trading.trading_cycle import TradingCycle
from src.trading.oms import OrderManagementSystem
from src.trading.oms_repository import OmsRepository
from src.market_data.market_data_service import MarketDataService

@pytest.fixture(scope="function")
def oms_integration_setup(tmp_path):
    """
    Provides a clean OMS instance with a repository pointing to a temporary CSV file.
    """
    oms_state_file = tmp_path / "test_oms_state.db"
    
    # Setup
    repository = OmsRepository(db_path=str(oms_state_file))
    oms = OrderManagementSystem(repository=repository)
    
    yield oms, repository # Pass instances to the test

    # Teardown
    if os.path.exists(oms_state_file):
        os.remove(oms_state_file)

def test_trading_cycle_full_integration_with_oms(oms_integration_setup):
    """
    Tests the full integration of TradingCycle with a persistent OMS using SQLite.
    Verifies that an order is placed and its status is updated across cycles.
    """
    # 1. Setup
    oms, repository = oms_integration_setup
    market_data_service = MarketDataService()
    trading_cycle = TradingCycle(oms=oms, market_data_service=market_data_service)

    # 2. Manually place an order to test the state change
    order_id = oms.place_order(
        symbol="BTCUSDT",
        order_type="BUY",
        margin=100.0,
        leverage=10,
        entry_price=50000.0,
        stop_loss=49500.0
    )
    
    # 3. Verification after placing the order
    orders_after_first_run = repository.load()
    assert len(orders_after_first_run) == 1
    placed_order = orders_after_first_run[order_id]
    assert placed_order["status"] == "PENDING"
    assert placed_order["margin"] == 100.0
    assert isinstance(placed_order["margin"], float)

    # 4. Simulate the TradingCycle checking and updating the order status
    oms.get_order_status(order_id) # This will flip the status to FILLED in our mock OMS

    # 5. Verification after the update
    orders_after_second_run = repository.load()
    assert len(orders_after_second_run) == 1
    
    updated_order = orders_after_second_run[order_id]
    assert updated_order["symbol"] == "BTCUSDT"
    assert updated_order["order_type"] == "BUY"
    assert updated_order["status"] == "FILLED", "Order status should be updated to FILLED"
    assert isinstance(updated_order["exit_price"], float)