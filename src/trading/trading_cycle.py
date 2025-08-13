import csv
from datetime import datetime
from src.trading.oms import OrderManagementSystem
from src.market_data.market_data_service import MarketDataService
from src.infrastructure.exceptions import ApiClientError as MarketDataError
from src.logging_system import MarketDataLogger
from src.logging_system.trace_generator import get_trace_id


class TradingCycle:
    """
    Основной цикл торговой логики.
    """
    def __init__(self, oms: OrderManagementSystem, market_data_service: MarketDataService):
        self.oms = oms
        self.market_data_service = market_data_service
        self.logger = MarketDataLogger("trading_cycle", service_name="trading_cycle")

    def _get_ai_decision(self, market_data, current_position, trace_id: str):
        """
        Формирует промпт для ИИ и возвращает решение.
        На Фазе 2 возвращает жестко закодированное решение.
        """
        # Get the context as a dictionary for logging.
        context_dict = market_data.to_context_dict()
        # Get the context as a compact JSON string for the LLM.
        json_context_str = market_data.to_json_context()

        prompt = f"""
        Market Analysis (JSON): {json_context_str}
        Current Position: {current_position}
        What is your next action (BUY, SELL, HOLD)?
        """
        # Log the context as a dictionary for proper structured logging.
        self.logger.log_operation_start("get_ai_decision", trace_id=trace_id, context={"json_context": context_dict})
        
        # Заглушка для решения ИИ
        decision = "BUY"
        self.logger.log_operation_complete("get_ai_decision", trace_id=trace_id, context={"decision": decision})
        return decision

    def run_cycle(self):
        """Запускает один полный торговый цикл."""
        master_trace_id = get_trace_id()
        self.logger.log_operation_start("run_cycle", trace_id=master_trace_id)
        
        # Теперь OMS - единственный источник правды о позициях.
        symbol = "BTCUSDT"
        current_position = self.oms.get_order_by_symbol(symbol, trace_id=master_trace_id)

        # Шаг 1: Синхронизация статуса, если есть активный ордер
        if current_position and current_position['status'] == 'PENDING':
            order_id = current_position['order_id']
            # Используем семантическое логирование для фиксации события
            self.logger.log_operation_start(
                operation="check_pending_order_status",
                context={"order_id": order_id},
                trace_id=master_trace_id
            )
            
            try:
                # get_order_status в OMS теперь сам обновляет состояние, если оно изменилось
                self.oms.get_order_status(order_id, trace_id=master_trace_id)
                # После проверки, получаем обновленное состояние
                current_position = self.oms.get_order_by_symbol(symbol, trace_id=master_trace_id)
                
                # Если ордер исполнен или отменен, завершаем цикл
                if current_position and current_position.get('status') != 'PENDING':
                    self.logger.info("Order status synced. Continuing cycle.", context={"order_id": order_id, "new_status": current_position.get('status')}, trace_id=master_trace_id)
                    # Цикл должен продолжаться, чтобы ИИ мог принять решение на основе закрытой позиции.
                    # Поэтому убираем return и log_operation_complete.
            except Exception as e:
                self.logger.log_operation_error("sync_order_status", error=str(e), context={"order_id": order_id}, trace_id=master_trace_id)
                self.logger.log_operation_error("run_cycle", error=str(e), context={"order_id": order_id}, trace_id=master_trace_id)
                return
 
        # Шаг 2: Получение рыночных данных
        try:
            market_data = self.market_data_service.get_market_data(symbol, trace_id=master_trace_id)
        except MarketDataError as e:
            self.logger.log_operation_error("get_market_data", error=str(e), trace_id=master_trace_id)
            self.logger.log_operation_error("run_cycle", error="Failed to get market data", trace_id=master_trace_id)
            return

        # Шаг 3: Взаимодействие с ИИ
        ai_decision = self._get_ai_decision(market_data, current_position, trace_id=master_trace_id)

        # Шаг 4: Оркестрация и исполнение решения
        if ai_decision == "BUY" and not current_position:
            quantity = 0.01
            price = market_data.h1_candles['close'].iloc[-1] if not market_data.h1_candles.empty else 52000
            
            self.logger.log_operation_start("place_buy_order", context={"symbol": symbol, "quantity": quantity, "price": price}, trace_id=master_trace_id)
            try:
                # В реальной системе здесь должны быть параметры stop_loss и take_profit
                self.oms.place_order(
                    symbol=symbol,
                    order_type='BUY',
                    margin=price * quantity,  # Примерный расчет
                    leverage=10,              # Пример
                    entry_price=price,
                    trace_id=master_trace_id
                )
            except Exception as e:
                self.logger.log_operation_error("place_buy_order", error=str(e), trace_id=master_trace_id)

        elif ai_decision == "SELL" and current_position:
            self.logger.log_operation_start("place_sell_order", context={"order_id": current_position.get('order_id')}, trace_id=master_trace_id)
            # Логика отмены или продажи
            self.oms.cancel_order(current_position.get('order_id'), trace_id=master_trace_id)
        
        elif ai_decision == "HOLD":
            self.logger.info("AI decision is HOLD. No action taken.", trace_id=master_trace_id)
            pass

        self.logger.log_operation_complete("run_cycle", trace_id=master_trace_id)