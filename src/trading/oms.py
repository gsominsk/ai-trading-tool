import uuid
from datetime import datetime, timezone
from .oms_repository import OmsRepository
from typing import Optional

class OrderManagementSystem:
    """
    Управляет ордерами: создание, отмена, получение статуса.
    Делегирует сохранение и загрузку состояния классу OmsRepository.
    """
    def __init__(self, repository: OmsRepository):
        self.repository = repository
        self._orders = self.repository.load()

    def place_order(self, symbol: str, order_type: str, margin: float, leverage: int, entry_price: float, stop_loss: Optional[float] = None, take_profit: Optional[float] = None):
        """
        Размещает ордер, сохраняет состояние и возвращает его ID.
        """
        order_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        new_order = {
            "order_id": order_id,
            "symbol": symbol,
            "status": "PENDING",
            "order_type": order_type,
            "margin": margin,
            "leverage": leverage,
            "entry_price": entry_price,
            "exit_price": None,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "created_at": now,
            "updated_at": now,
        }
        
        self._orders[order_id] = new_order
        self.repository.save(new_order)
        return order_id

    def cancel_order(self, order_id: str):
        """Отменяет ордер и сохраняет состояние."""
        if order_id in self._orders:
            order = self._orders[order_id]
            order["status"] = "CANCELLED"
            order["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.repository.save(order)
            return True
        return False

    def get_order_status(self, order_id: str):
        """
        Получает актуальный статус ордера из внутреннего состояния.
        """
        if order_id in self._orders:
            order = self._orders[order_id]
            # Для симуляции ручного тестирования, мы можем имитировать
            # исполнение ордера при его проверке.
            if order["status"] == "PENDING":
                order["status"] = "FILLED"
                order["exit_price"] = order["entry_price"] * 1.02 # Simulate 2% profit
                order["updated_at"] = datetime.now(timezone.utc).isoformat()
                self.repository.save(order)
            return order["status"]
        return "UNKNOWN"

    def get_order_by_symbol(self, symbol: str):
        """
        Находит первый активный (не CANCELLED или FILLED) ордер по символу.
        """
        for order in self._orders.values():
            if order['symbol'] == symbol and order['status'] not in ['CANCELLED', 'FILLED']:
                return order
        return None