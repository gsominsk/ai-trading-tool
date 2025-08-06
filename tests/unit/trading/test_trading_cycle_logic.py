import pytest
import csv
import os
from datetime import datetime
from unittest.mock import Mock
from src.trading.trading_cycle import TradingCycle

@pytest.fixture
def temp_trade_log(tmp_path):
    """Фикстура для создания временного файла trade_log.csv."""
    log_path = tmp_path / "trade_log.csv"
    header = ['timestamp', 'order_id', 'symbol', 'type', 'price', 'quantity', 'status']
    with open(log_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
    return str(log_path)

@pytest.fixture
def trading_cycle_instance(temp_trade_log):
    """Фикстура для создания экземпляра TradingCycle с mock-зависимостями."""
    mock_oms = Mock()
    mock_mds = Mock()
    return TradingCycle(oms=mock_oms, market_data_service=mock_mds, trade_log_path=temp_trade_log)

def test_get_current_position_no_records(trading_cycle_instance):
    """Тест: _get_current_position возвращает None, если в логе нет записей."""
    assert trading_cycle_instance._get_current_position() is None

def test_get_current_position_file_not_found():
    """Тест: _get_current_position возвращает None, если файл лога отсутствует."""
    mock_oms = Mock()
    mock_mds = Mock()
    cycle = TradingCycle(oms=mock_oms, market_data_service=mock_mds, trade_log_path='non_existent_file.csv')
    assert cycle._get_current_position() is None

def test_update_and_get_current_position(trading_cycle_instance):
    """Тест: _update_log корректно записывает данные, а _get_current_position их читает."""
    # Записываем первую позицию
    trading_cycle_instance._update_log('order1', 'BTCUSDT', 'BUY', 50000, 0.1, 'FILLED')
    
    # Проверяем, что последняя позиция корректна
    position1 = trading_cycle_instance._get_current_position()
    assert position1 is not None
    assert position1['order_id'] == 'order1'
    assert position1['symbol'] == 'BTCUSDT'

    # Записываем вторую позицию
    trading_cycle_instance._update_log('order2', 'ETHUSDT', 'SELL', 4000, 1.0, 'PENDING')

    # Проверяем, что последняя позиция - это вторая запись
    position2 = trading_cycle_instance._get_current_position()
    assert position2 is not None
    assert position2['order_id'] == 'order2'
    assert position2['symbol'] == 'ETHUSDT'
    assert float(position2['price']) == 4000.0
    assert position2['status'] == 'PENDING'

def test_update_log_appends_correctly(trading_cycle_instance, temp_trade_log):
    """Тест: _update_log добавляет записи в конец файла."""
    trading_cycle_instance._update_log('order1', 'BTCUSDT', 'BUY', 50000, 0.1, 'FILLED')
    trading_cycle_instance._update_log('order2', 'ETHUSDT', 'SELL', 4000, 1.0, 'PENDING')

    with open(temp_trade_log, 'r') as f:
        reader = csv.reader(f)
        lines = list(reader)
        # 1 строка заголовка + 2 строки данных
        assert len(lines) == 3
        assert lines[1][1] == 'order1'
        assert lines[2][1] == 'order2'

from unittest.mock import patch

def test_run_cycle_synchronization_logic(trading_cycle_instance):
    """
    Тест: run_cycle корректно синхронизирует статус PENDING ордера.
    """
    # Подготовка: создаем "зависший" ордер в логе
    pending_order_id = 'order_pending'
    trading_cycle_instance._update_log(
        pending_order_id, 'BTCUSDT', 'BUY', 51000, 0.1, 'PENDING'
    )

    # Настраиваем mock OMS, чтобы он вернул новый статус
    trading_cycle_instance.oms.get_order_status.return_value = 'FILLED'

    # Патчим _get_ai_decision, чтобы он не мешал тесту синхронизации
    with patch.object(trading_cycle_instance, '_get_ai_decision', return_value="HOLD") as mock_ai_decision:
        # Запускаем цикл
        trading_cycle_instance.run_cycle()

    # Проверка 1: Был вызван метод get_order_status с правильным ID
    trading_cycle_instance.oms.get_order_status.assert_called_once_with(pending_order_id)

    # Проверка 2: Лог был обновлен новым статусом
    last_position = trading_cycle_instance._get_current_position()
    assert last_position['order_id'] == pending_order_id
    assert last_position['status'] == 'FILLED'

def test_run_cycle_no_pending_order(trading_cycle_instance):
    """
    Тест: run_cycle не вызывает OMS, если нет PENDING ордеров.
    """
    # Подготовка: создаем исполненный ордер
    trading_cycle_instance._update_log(
        'order_filled', 'BTCUSDT', 'BUY', 51000, 0.1, 'FILLED'
    )

    # Запускаем цикл
    trading_cycle_instance.run_cycle()

    # Проверка: get_order_status не был вызван
    trading_cycle_instance.oms.get_order_status.assert_not_called()

def test_get_ai_decision_stub(trading_cycle_instance):
    """
    Тест: _get_ai_decision возвращает жестко закодированное решение.
    """
    # Настраиваем mock MarketDataService для полноты картины
    mock_market_data = {'price': 52000, 'volume': 1000}
    
    # Получаем текущую позицию (в данном случае None, так как лог пуст)
    current_position = trading_cycle_instance._get_current_position()
    
    # Вызываем тестируемый метод
    decision = trading_cycle_instance._get_ai_decision(
        market_data=mock_market_data,
        current_position=current_position
    )
    
    # Проверяем, что решение соответствует заглушке
    assert decision == "BUY"

def test_run_cycle_full_orchestration(trading_cycle_instance):
    """
    Тест: run_cycle корректно выполняет полный цикл оркестрации.
    """
    # Настройка mock-объектов
    trading_cycle_instance.market_data_service.get_market_data.return_value = {'price': 53000}
    trading_cycle_instance.oms.place_order.return_value = 'new_order_123'

    # Запускаем цикл (предполагаем, что лог пуст)
    trading_cycle_instance.run_cycle()

    # Проверка 1: Был вызван get_market_data
    trading_cycle_instance.market_data_service.get_market_data.assert_called_once_with("BTCUSDT")

    # Проверка 2: Был вызван place_order с правильными параметрами
    trading_cycle_instance.oms.place_order.assert_called_once_with(
        symbol='BTCUSDT',
        order_type='BUY',
        quantity=0.01,
        price=53000
    )

    # Проверка 3: В лог была добавлена новая PENDING запись
    last_position = trading_cycle_instance._get_current_position()
    assert last_position is not None
    assert last_position['order_id'] == 'new_order_123'
    assert last_position['status'] == 'PENDING'