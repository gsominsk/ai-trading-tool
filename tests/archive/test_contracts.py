def test_oms_contract():
    """
    Проверяет контракт класса OrderManagementSystem.
    """
    from src.trading.oms import OrderManagementSystem
    
    # Проверяем, что класс существует
    assert OrderManagementSystem is not None, "Класс OrderManagementSystem не найден."
    
    # Проверяем наличие методов
    assert hasattr(OrderManagementSystem, 'place_order'), "Метод place_order отсутствует."
    assert hasattr(OrderManagementSystem, 'cancel_order'), "Метод cancel_order отсутствует."
    assert hasattr(OrderManagementSystem, 'get_order_status'), "Метод get_order_status отсутствует."


def test_trading_cycle_contract():
    """
    Проверяет контракт класса TradingCycle.
    """
    from src.trading.trading_cycle import TradingCycle
    from src.trading.oms import OrderManagementSystem
    from src.market_data.market_data_service import MarketDataService
    from unittest.mock import Mock

    # Создаем mock-объекты для зависимостей
    mock_oms = Mock(spec=OrderManagementSystem)
    mock_mds = Mock(spec=MarketDataService)

    # Проверяем, что класс можно инстанциировать
    cycle = TradingCycle(oms=mock_oms, market_data_service=mock_mds)
    assert cycle is not None, "Не удалось создать экземпляр TradingCycle."

    # Проверяем наличие метода
    assert hasattr(cycle, 'run_cycle'), "Метод run_cycle отсутствует."
