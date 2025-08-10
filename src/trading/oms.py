import uuid
from datetime import datetime, timezone
from .oms_repository import OmsRepository
from typing import Optional
from src.logging_system.logger_config import MarketDataLogger
from src.market_data.exceptions import RepositoryError

class OrderManagementSystem:
    """
    Управляет ордерами: создание, отмена, получение статуса.
    Делегирует сохранение и загрузку состояния классу OmsRepository.
    """
    def __init__(self, repository: OmsRepository, logger: Optional[MarketDataLogger] = None):
        self.repository = repository
        self.logger = logger
        try:
            self._orders = self.repository.load()
        except RepositoryError as e:
            if self.logger:
                self.logger.log_operation_error("oms_init_load", "Failed to load initial orders from repository", error_details=e.get_context())
            self._orders = {}

    def place_order(self, symbol: str, order_type: str, margin: float, leverage: int, entry_price: float, stop_loss: Optional[float] = None, take_profit: Optional[float] = None, trace_id: Optional[str] = None):
        """
        Размещает ордер, сохраняет состояние и возвращает его ID.
        """
        order_id = str(uuid.uuid4())
        if self.logger:
            self.logger.log_operation_start("place_order", trace_id=trace_id, order_details={"symbol": symbol, "type": order_type, "margin": margin})
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
        try:
            self.repository.save(new_order)
        except RepositoryError as e:
            if self.logger:
                self.logger.log_operation_error("place_order_save", "Failed to save new order", trace_id=trace_id, error_details=e.get_context())
            # In a real system, we might want to handle this more gracefully
            # For now, we'll re-raise to make the failure visible.
            raise
        return order_id

    def cancel_order(self, order_id: str, trace_id: Optional[str] = None):
        """Отменяет ордер и сохраняет состояние."""
        if self.logger:
            self.logger.log_operation_start("cancel_order", trace_id=trace_id, order_id=order_id)
        if order_id in self._orders:
            order = self._orders[order_id]
            order["status"] = "CANCELLED"
            order["updated_at"] = datetime.now(timezone.utc).isoformat()
            try:
                self.repository.save(order)
            except RepositoryError as e:
                if self.logger:
                    self.logger.log_operation_error("cancel_order_save", "Failed to save cancelled order", trace_id=trace_id, error_details=e.get_context())
                raise
            return True
        return False

    def get_order_status(self, order_id: str, trace_id: Optional[str] = None):
        """
        Получает актуальный статус ордера из внутреннего состояния.
        """
        if self.logger:
            self.logger.log_operation_start("get_order_status", trace_id=trace_id, order_id=order_id)
        if order_id in self._orders:
            order = self._orders[order_id]
            # Для симуляции ручного тестирования, мы можем имитировать
            # исполнение ордера при его проверке.
            if order["status"] == "PENDING":
                order["status"] = "FILLED"
                order["exit_price"] = order["entry_price"] * 1.02 # Simulate 2% profit
                order["updated_at"] = datetime.now(timezone.utc).isoformat()
                try:
                    self.repository.save(order)
                except RepositoryError as e:
                    if self.logger:
                        self.logger.log_operation_error("get_order_status_save", "Failed to save updated order status", trace_id=trace_id, error_details=e.get_context())
                    # Do not re-raise here, as getting status is non-critical
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