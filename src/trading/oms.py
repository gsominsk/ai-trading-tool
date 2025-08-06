import uuid
from .repository import OrderRepository

class OrderManagementSystem:
    """
    Управляет ордерами: создание, отмена, получение статуса.
    Делегирует сохранение и загрузку состояния классу OrderRepository.
    """
    def __init__(self, repository: OrderRepository):
        self.repository = repository
        self._orders = self.repository.load()

    def place_order(self, symbol: str, order_type: str, quantity: float, price: float = None):
        """
        Размещает ордер, сохраняет состояние и возвращает его ID.
        """
        order_id = str(uuid.uuid4())
        self._orders[order_id] = {
            "symbol": symbol,
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
            "status": "PENDING"
        }
        self.repository.save(self._orders)
        return order_id

    def cancel_order(self, order_id: str):
        """Отменяет ордер и сохраняет состояние."""
        if order_id in self._orders:
            self._orders[order_id]["status"] = "CANCELLED"
            self.repository.save(self._orders)
            return True
        return False

    def get_order_status(self, order_id: str):
        """
        Получает актуальный статус ордера из внутреннего состояния.
        """
        if order_id in self._orders:
            # Для симуляции ручного тестирования, мы можем имитировать
            # исполнение ордера при его проверке.
            if self._orders[order_id]["status"] == "PENDING":
                self._orders[order_id]["status"] = "FILLED"
                self.repository.save(self._orders)
            return self._orders[order_id]["status"]
        return "UNKNOWN"