import pytest
from unittest.mock import MagicMock, call
from src.trading.trading_cycle import TradingCycle
from src.trading.oms import OrderManagementSystem
from src.market_data.market_data_service import MarketDataService

@pytest.fixture
def mock_oms():
    """Fixture for a mocked OrderManagementSystem."""
    return MagicMock(spec=OrderManagementSystem)

@pytest.fixture
def mock_market_data_service():
    """Fixture for a mocked MarketDataService."""
    mock = MagicMock(spec=MarketDataService)
    mock_market_data = MagicMock()
    mock_market_data.h1_candles = MagicMock()
    mock_market_data.h1_candles.empty = False
    mock_market_data.h1_candles.__getitem__.return_value.iloc.__getitem__.return_value = 52000.0
    mock.get_market_data.return_value = mock_market_data
    return mock

@pytest.fixture
def trading_cycle(mock_oms, mock_market_data_service):
    """Fixture to create a TradingCycle instance with mocked dependencies."""
    return TradingCycle(
        oms=mock_oms,
        market_data_service=mock_market_data_service
    )

def test_run_cycle_no_active_order_buy_decision(trading_cycle, mock_oms):
    """
    Тест 1: Проверяет стандартный цикл покупки при отсутствии активных ордеров.
    """
    # Подготовка: OMS не возвращает активных ордеров для символа
    mock_oms.get_order_by_symbol.return_value = None

    # Действие
    trading_cycle.run_cycle()

    # Проверка
    # 1. Проверить, что был запрошен ордер по символу
    mock_oms.get_order_by_symbol.assert_called_once_with("BTCUSDT")
    
    # 2. Проверить, что был размещен новый ордер
    mock_oms.place_order.assert_called_once_with(
        symbol="BTCUSDT",
        order_type='BUY',
        quantity=0.01,
        price=52000.0
    )

def test_run_cycle_with_pending_order_syncs_it(trading_cycle, mock_oms):
    """
    Тест 2: Проверяет, что цикл синхронизирует PENDING ордер и завершается.
    """
    # Подготовка: OMS возвращает PENDING ордер
    pending_order = {'order_id': 'pending-order-456', 'status': 'PENDING'}
    mock_oms.get_order_by_symbol.return_value = pending_order

    # Действие
    trading_cycle.run_cycle()

    # Проверка
    # 1. Проверить, что был запрошен статус ордера для синхронизации
    mock_oms.get_order_status.assert_called_once_with('pending-order-456')

    # 2. Проверить, что новый ордер НЕ размещался, так как цикл был занят синхронизацией
    mock_oms.place_order.assert_not_called()

def test_run_cycle_with_filled_order_does_nothing(trading_cycle, mock_oms):
    """
    Тест 3: Проверяет, что цикл ничего не делает, если уже есть исполненный ордер.
    (В будущем здесь может быть логика продажи).
    """
    # Подготовка: OMS возвращает FILLED ордер
    filled_order = {'order_id': 'filled-order-789', 'status': 'FILLED'}
    mock_oms.get_order_by_symbol.return_value = filled_order

    # Действие
    trading_cycle.run_cycle()

    # Проверка
    # 1. Проверить, что статус PENDING ордера НЕ запрашивался
    mock_oms.get_order_status.assert_not_called()

    # 2. Проверить, что новый ордер НЕ размещался
    mock_oms.place_order.assert_not_called()