import csv
from datetime import datetime
from src.trading.oms import OrderManagementSystem
from src.market_data.market_data_service import MarketDataService, MarketDataError
from src.logging_system import MarketDataLogger


class TradingCycle:
    """
    Основной цикл торговой логики.
    """
    def __init__(self, oms: OrderManagementSystem, market_data_service: MarketDataService):
        self.oms = oms
        self.market_data_service = market_data_service
        self.logger = MarketDataLogger("trading_cycle")

    def _get_ai_decision(self, market_data, current_position):
        """
        Формирует промпт для ИИ и возвращает решение.
        На Фазе 2 возвращает жестко закодированное решение.
        """
        prompt = f"""
        Анализ Рынка: {market_data}
        Текущая Позиция: {current_position}
        Каково ваше следующее действие (BUY, SELL, HOLD)?
        """
        self.logger.log_operation_start("get_ai_decision", context={"prompt": prompt})
        
        # Заглушка для решения ИИ
        decision = "BUY"
        self.logger.log_operation_complete("get_ai_decision", context={"decision": decision})
        return decision

    def run_cycle(self):
        """Запускает один полный торговый цикл."""
        self.logger.log_operation_start("run_cycle")
        
        # Теперь OMS - единственный источник правды о позициях.
        symbol = "BTCUSDT"
        current_position = self.oms.get_order_by_symbol(symbol)

        # Шаг 1: Синхронизация статуса, если есть активный ордер
        if current_position and current_position['status'] == 'PENDING':
            order_id = current_position['order_id']
            # Используем семантическое логирование для фиксации события
            self.logger.log_operation_start(
                operation="check_pending_order_status",
                context={"order_id": order_id}
            )
            
            try:
                # get_order_status в OMS теперь сам обновляет состояние, если оно изменилось
                self.oms.get_order_status(order_id)
                # После проверки, получаем обновленное состояние
                current_position = self.oms.get_order_by_symbol(symbol)
                
                # Если ордер исполнен или отменен, завершаем цикл
                if current_position and current_position.get('status') != 'PENDING':
                    self.logger.info("Order status synced. Ending cycle.", context={"order_id": order_id, "new_status": current_position.get('status')})
                    self.logger.log_operation_complete("run_cycle")
                    return
            except Exception as e:
                self.logger.log_operation_error("sync_order_status", error=str(e), context={"order_id": order_id})
                self.logger.log_operation_complete("run_cycle", status="failed")
                return

        # Шаг 2: Получение рыночных данных
        try:
            market_data = self.market_data_service.get_market_data(symbol)
        except MarketDataError as e:
            self.logger.log_operation_error("get_market_data", error=str(e))
            self.logger.log_operation_complete("run_cycle", status="failed")
            return

        # Шаг 3: Взаимодействие с ИИ
        ai_decision = self._get_ai_decision(market_data, current_position)

        # Шаг 4: Оркестрация и исполнение решения
        if ai_decision == "BUY" and not current_position:
            quantity = 0.01
            price = market_data.h1_candles['close'].iloc[-1] if not market_data.h1_candles.empty else 52000
            
            self.logger.log_operation_start("place_buy_order", context={"symbol": symbol, "quantity": quantity, "price": price})
            try:
                self.oms.place_order(symbol=symbol, order_type='BUY', quantity=quantity, price=price)
            except Exception as e:
                self.logger.log_operation_error("place_buy_order", error=str(e))

        elif ai_decision == "SELL" and current_position:
            self.logger.log_operation_start("place_sell_order", context={"order_id": current_position.get('order_id')})
            # Логика отмены или продажи
            self.oms.cancel_order(current_position.get('order_id'))
        
        elif ai_decision == "HOLD":
            self.logger.info("AI decision is HOLD. No action taken.")
            pass

        self.logger.log_operation_complete("run_cycle")