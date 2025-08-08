import pytest
import os
import csv
from datetime import datetime
from src.trading.log_repository import TradeLogRepository

@pytest.fixture
def temp_csv_file(tmp_path):
    """Pytest fixture to create a temporary file path for tests."""
    return tmp_path / "test_trade_log.csv"

def test_repository_creation_and_header(temp_csv_file):
    """
    Тест 1: Проверяет, что репозиторий создает файл с правильным заголовком.
    """
    # Действие
    repo = TradeLogRepository(file_path=str(temp_csv_file))

    # Проверка
    assert os.path.exists(temp_csv_file)
    with open(temp_csv_file, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == repo.header

def test_add_and_get_last_record(temp_csv_file):
    """
    Тест 2: Проверяет добавление одной записи и ее последующее чтение.
    """
    # Подготовка
    repo = TradeLogRepository(file_path=str(temp_csv_file))
    record_to_add = {
        'timestamp': datetime(2025, 1, 1, 12, 0, 0).isoformat(),
        'order_id': 'order-123',
        'symbol': 'BTCUSDT',
        'order_type': 'BUY',
        'price': '50000.0',
        'quantity': '0.1',
        'status': 'FILLED'
    }

    # Действие
    repo.add_record(record_to_add)
    last_record = repo.get_last_record()

    # Проверка
    assert last_record is not None
    assert last_record['order_id'] == record_to_add['order_id']
    assert last_record['symbol'] == record_to_add['symbol']
    assert last_record['status'] == record_to_add['status']

def test_get_last_record_multiple_entries(temp_csv_file):
    """
    Тест 3: Проверяет, что возвращается именно последняя запись из нескольких.
    """
    # Подготовка
    repo = TradeLogRepository(file_path=str(temp_csv_file))
    first_record = {'order_id': 'order-001', 'symbol': 'ETHUSDT', 'status': 'PENDING'}
    second_record = {'order_id': 'order-002', 'symbol': 'BTCUSDT', 'status': 'FILLED'}

    # Действие
    repo.add_record(first_record)
    repo.add_record(second_record)
    last_record = repo.get_last_record()

    # Проверка
    assert last_record is not None
    assert last_record['order_id'] == 'order-002'
    assert last_record['status'] == 'FILLED'

def test_get_last_record_empty_file(temp_csv_file):
    """
    Тест 4: Проверяет, что возвращается None, если в файле только заголовок.
    """
    # Подготовка
    repo = TradeLogRepository(file_path=str(temp_csv_file))

    # Действие
    last_record = repo.get_last_record()

    # Проверка
    assert last_record is None

def test_get_last_record_with_empty_lines(temp_csv_file):
    """
    Тест 5: Проверяет, что пустые строки в файле корректно игнорируются.
    """
    # Подготовка
    repo = TradeLogRepository(file_path=str(temp_csv_file))
    valid_record = {'order_id': 'valid-order', 'status': 'ACTIVE'}
    repo.add_record(valid_record)

    # Искусственно добавляем пустые строки в файл
    with open(temp_csv_file, 'a', newline='') as f:
        f.write('\n')
        f.write('\n')

    # Действие
    last_record = repo.get_last_record()

    # Проверка
    assert last_record is not None
    assert last_record['order_id'] == 'valid-order'

def test_add_record_with_auto_timestamp(temp_csv_file):
    """
    Тест 6: Проверяет, что timestamp добавляется автоматически, если не указан.
    """
    # Подготовка
    repo = TradeLogRepository(file_path=str(temp_csv_file))
    record_without_ts = {'order_id': 'ts-test', 'status': 'NEW'}

    # Действие
    repo.add_record(record_without_ts)
    last_record = repo.get_last_record()

    # Проверка
    assert last_record is not None
    assert 'timestamp' in last_record
    assert last_record['timestamp'] is not None
    # Проверяем, что это валидная ISO дата
    try:
        datetime.fromisoformat(last_record['timestamp'].replace('Z', '+00:00'))
        assert True
    except (ValueError, TypeError):
        pytest.fail("Timestamp is not a valid ISO 8601 string")