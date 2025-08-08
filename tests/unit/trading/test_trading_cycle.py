import pytest
from unittest.mock import MagicMock, call
from src.trading.trading_cycle import TradingCycle
from src.trading.log_repository import TradeLogRepository
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
    # Mock a basic MarketDataSet for the service to return
    mock_market_data = MagicMock()
    mock_market_data.h1_candles = MagicMock()
    mock_market_data.h1_candles.empty = False
    # Correctly mock the return value for the chained call `...['close'].iloc[-1]`
    mock_market_data.h1_candles.__getitem__.return_value.iloc.__getitem__.return_value = 52000.0
    mock.get_market_data.return_value = mock_market_data
    return mock

@pytest.fixture
def mock_log_repository():
    """Fixture for a mocked TradeLogRepository."""
    return MagicMock(spec=TradeLogRepository)

@pytest.fixture
def trading_cycle(mock_oms, mock_market_data_service, mock_log_repository):
    """Fixture to create a TradingCycle instance with mocked dependencies."""
    return TradingCycle(
        oms=mock_oms,
        market_data_service=mock_market_data_service,
        log_repository=mock_log_repository
    )

def test_run_cycle_no_pending_order_buy_decision(trading_cycle, mock_oms, mock_log_repository):
    """
    Тест 1: Проверяет стандартный цикл покупки при отсутствии PENDING ордеров.
    """
    # Подготовка: нет PENDING ордеров
    mock_log_repository.get_last_record.return_value = None
    mock_oms.place_order.return_value = 'new-order-123'

    # Действие
    trading_cycle.run_cycle()

    # Проверка
    # 1. Проверить, что был запрошен последний лог
    mock_log_repository.get_last_record.assert_called_once()
    
    # 2. Проверить, что был размещен ордер
    mock_oms.place_order.assert_called_once_with(
        symbol="BTCUSDT",
        order_type='BUY',
        quantity=0.01,
        price=52000.0
    )

    # 3. Проверить, что новый ордер был залогирован как PENDING
    mock_log_repository.add_record.assert_called_once_with({
        'order_id': 'new-order-123',
        'symbol': 'BTCUSDT',
        'order_type': 'BUY',
        'price': 52000.0,
        'quantity': 0.01,
        'status': 'PENDING'
    })

def test_run_cycle_with_pending_order_syncs_to_filled(trading_cycle, mock_oms, mock_log_repository):
    """
    Тест 2: Проверяет синхронизацию, если в логе есть PENDING ордер, который стал FILLED.
    """
    # Подготовка: в логе есть PENDING ордер
    pending_order = {
        'order_id': 'pending-order-456',
        'symbol': 'ETHUSDT',
        'order_type': 'BUY',
        'price': '3000.0',
        'quantity': '0.5',
        'status': 'PENDING'
    }
    mock_log_repository.get_last_record.return_value = pending_order
    # OMS сообщает, что ордер теперь FILLED
    mock_oms.get_order_status.return_value = 'FILLED'

    # Действие
    trading_cycle.run_cycle()

    # Проверка
    # 1. Проверить, что был запрошен статус ордера
    mock_oms.get_order_status.assert_called_once_with('pending-order-456')

    # 2. Проверить, что лог был обновлен новым статусом
    mock_log_repository.add_record.assert_called_once_with({
        'order_id': 'pending-order-456',
        'symbol': 'ETHUSDT',
        'order_type': 'BUY',
        'price': '3000.0',
        'quantity': '0.5',
        'status': 'FILLED'
    })

    # 3. Проверить, что новый ордер НЕ размещался, так как цикл завершился после синхронизации
    mock_oms.place_order.assert_not_called()

def test_run_cycle_with_pending_order_remains_pending(trading_cycle, mock_oms, mock_log_repository):
    """
    Тест 3: Проверяет, что ничего не происходит, если PENDING ордер все еще PENDING.
    """
    # Подготовка: PENDING ордер все еще PENDING
    pending_order = {'order_id': 'pending-order-789', 'status': 'PENDING'}
    mock_log_repository.get_last_record.return_value = pending_order
    mock_oms.get_order_status.return_value = 'PENDING'

    # Действие
    trading_cycle.run_cycle()

    # Проверка
    # 1. Проверить, что был запрошен статус ордера
    mock_oms.get_order_status.assert_called_once_with('pending-order-789')

    # 2. Проверить, что лог НЕ обновлялся
    mock_log_repository.add_record.assert_not_called()

    # 3. Проверить, что новый ордер НЕ размещался
    mock_oms.place_order.assert_not_called()