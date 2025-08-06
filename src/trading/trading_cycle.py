from src.trading.oms import OrderManagementSystem
from src.market_data.market_data_service import MarketDataService


class TradingCycle:
    """
    Основной цикл торговой логики.
    На Фазе 1 определяется только контракт.
    """
    def __init__(self, oms: OrderManagementSystem, market_data_service: MarketDataService):
        self.oms = oms
        self.market_data_service = market_data_service

    def run_cycle(self):
        """Запускает один полный торговый цикл."""
        raise NotImplementedError