import json
import os
import pytest
from src.trading.repository import OrderRepository

@pytest.fixture
def test_orders():
    """Fixture for sample order data."""
    return {
        "order1": {"symbol": "BTCUSDT", "status": "FILLED"},
        "order2": {"symbol": "ETHUSDT", "status": "PENDING"}
    }

def test_save_and_load(tmp_path, test_orders):
    """
    Test that saving orders to a file and loading them back works correctly.
    """
    file_path = tmp_path / "oms_state.json"
    repository = OrderRepository(str(file_path))

    # 1. Save orders
    repository.save(test_orders)

    # 2. Check if file was created and contains correct data
    assert file_path.exists()
    with open(file_path, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    assert loaded_data == test_orders

    # 3. Load orders using the repository
    loaded_orders = repository.load()
    assert loaded_orders == test_orders

def test_load_non_existent_file(tmp_path):
    """
    Test that loading from a non-existent file returns an empty dictionary.
    """
    file_path = tmp_path / "non_existent.json"
    repository = OrderRepository(str(file_path))

    loaded_orders = repository.load()
    assert loaded_orders == {}

def test_load_empty_file(tmp_path):
    """
    Test that loading from an empty or corrupted file returns an empty dictionary.
    """
    file_path = tmp_path / "empty.json"
    file_path.touch()  # Create an empty file

    repository = OrderRepository(str(file_path))
    loaded_orders = repository.load()
    assert loaded_orders == {}

    # Test with corrupted JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("{corrupted_json")
    
    loaded_orders = repository.load()
    assert loaded_orders == {}

def test_overwrite_existing_file(tmp_path, test_orders):
    """
    Test that saving new data correctly overwrites existing data.
    """
    file_path = tmp_path / "oms_state.json"
    repository = OrderRepository(str(file_path))

    # Save initial data
    initial_data = {"order0": {"status": "CANCELLED"}}
    repository.save(initial_data)

    # Save new data
    repository.save(test_orders)

    # Load and verify that the new data is present
    loaded_orders = repository.load()
    assert loaded_orders == test_orders
    assert loaded_orders != initial_data

def test_directory_creation(tmp_path):
    """
    Test that the repository creates the directory if it doesn't exist.
    """
    dir_path = tmp_path / "new_dir"
    file_path = dir_path / "state.json"
    
    assert not dir_path.exists()
    
    OrderRepository(str(file_path))
    
    assert dir_path.exists()
    assert dir_path.is_dir()