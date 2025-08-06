class OrderManagementSystem:
    """
    Управляет ордерами: создание, отмена, получение статуса.
    На Фазе 1 используется как заглушка с контрактом.
    """
    def place_order(self, symbol: str, order_type: str, quantity: float, price: float = None):
        """Размещает ордер."""
        raise NotImplementedError

    def cancel_order(self, order_id: str):
        """Отменяет ордер."""
        raise NotImplementedError

    def get_order_status(self, order_id: str):
        """Получает статус ордера."""
        raise NotImplementedError