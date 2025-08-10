import pytest
import sqlite3
from src.trading.oms_repository import OmsRepository
from src.market_data.exceptions import RepositoryError
from datetime import datetime

@pytest.fixture
def db_path(tmp_path):
    """Fixture to provide a temporary database path."""
    return tmp_path / "test_oms.db"

@pytest.fixture
def sample_order():
    """Fixture for a single sample order."""
    now = datetime.utcnow().isoformat()
    return {
        "order_id": "order1",
        "symbol": "BTCUSDT",
        "status": "PENDING",
        "order_type": "BUY",
        "margin": 100.50,
        "leverage": 10,
        "entry_price": 50000.0,
        "exit_price": None,
        "stop_loss": 49500.0,
        "take_profit": 51000.0,
        "created_at": now,
        "updated_at": now,
    }

def test_init_creates_table(db_path):
    """Test that the database and table are created on initialization."""
    assert not db_path.exists()
    OmsRepository(str(db_path))
    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders';")
    assert cursor.fetchone() is not None, "Table 'orders' was not created."
    conn.close()

def test_save_and_load_single_order(db_path, sample_order):
    """Test saving a single order and loading it back."""
    repo = OmsRepository(str(db_path))
    
    # Save the order
    repo.save(sample_order)
    
    # Load all orders
    loaded_orders = repo.load()
    
    assert len(loaded_orders) == 1
    assert "order1" in loaded_orders
    
    # Verify data types and values
    loaded_order = loaded_orders["order1"]
    assert loaded_order["order_id"] == sample_order["order_id"]
    assert isinstance(loaded_order["margin"], float)
    assert loaded_order["margin"] == 100.50
    assert isinstance(loaded_order["leverage"], int)
    assert loaded_order["leverage"] == 10
    assert loaded_order["exit_price"] is None

def test_load_empty_db(db_path):
    """Test loading from an empty database returns an empty dict."""
    repo = OmsRepository(str(db_path))
    loaded_orders = repo.load()
    assert loaded_orders == {}

def test_overwrite_order(db_path, sample_order):
    """Test that saving an order with an existing ID overwrites it."""
    repo = OmsRepository(str(db_path))
    
    # Save initial order
    repo.save(sample_order)
    
    # Modify and save again
    sample_order["status"] = "FILLED"
    sample_order["exit_price"] = 51000.0
    repo.save(sample_order)
    
    loaded_orders = repo.load()
    assert len(loaded_orders) == 1
    
    updated_order = loaded_orders["order1"]
    assert updated_order["status"] == "FILLED"
    assert updated_order["exit_price"] == 51000.0

def test_delete_order(db_path, sample_order):
    """Test deleting an order from the database."""
    repo = OmsRepository(str(db_path))
    
    # Save an order, then delete it
    repo.save(sample_order)
    assert len(repo.load()) == 1
    
    repo.delete("order1")
    assert len(repo.load()) == 0

def test_multiple_orders(db_path, sample_order):
    """Test saving and loading multiple distinct orders."""
    repo = OmsRepository(str(db_path))
    
    order2 = sample_order.copy()
    order2["order_id"] = "order2"
    order2["symbol"] = "ETHUSDT"

    repo.save(sample_order)
    repo.save(order2)
    
    loaded_orders = repo.load()
    assert len(loaded_orders) == 2
    assert "order1" in loaded_orders
    assert "order2" in loaded_orders
    assert loaded_orders["order2"]["symbol"] == "ETHUSDT"

def test_save_raises_exception_on_db_error(db_path, sample_order, mocker):
    """
    Test that save method raises an exception when a database error occurs.
    This test will currently fail because the exception is not caught and re-raised.
    """
    repo = OmsRepository(str(db_path))
    
    # Mock the connect method to raise an OperationalError
    mocker.patch('sqlite3.connect', side_effect=sqlite3.OperationalError("disk I/O error"))
    
    with pytest.raises(RepositoryError) as excinfo:
        repo.save(sample_order)
    
    assert "disk I/O error" in str(excinfo.value)
    assert excinfo.value.db_operation == "save"

def test_save_raises_integrity_error_on_missing_not_null_field(db_path, sample_order):
    """
    Test that saving an order with a missing NOT NULL field raises IntegrityError.
    """
    repo = OmsRepository(str(db_path))
    
    # Remove a field that has a NOT NULL constraint in the database
    del sample_order["symbol"]
    
    with pytest.raises(RepositoryError) as excinfo:
        repo.save(sample_order)
        
    assert "NOT NULL constraint failed" in str(excinfo.value)
    assert excinfo.value.db_operation == "save"

def test_load_returns_empty_dict_on_corrupt_db_file(db_path):
    """
    Test that load() returns an empty dictionary if the database file is corrupt.
    """
    # Create a corrupted database file
    with open(db_path, "w") as f:
        f.write("this is not a database file")
        
    repo = OmsRepository(str(db_path))
    with pytest.raises(RepositoryError) as excinfo:
        repo.load()

    assert "file is not a database" in str(excinfo.value)