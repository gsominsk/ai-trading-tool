import csv
from datetime import datetime
from src.trading.oms import OrderManagementSystem
from src.market_data.market_data_service import MarketDataService, MarketDataError
from src.trading.log_repository import TradeLogRepository
from src.logging_system import MarketDataLogger


class TradingCycle:
    """
    Основной цикл торговой логики.
    """
    def __init__(self, oms: OrderManagementSystem, market_data_service: MarketDataService, log_repository: TradeLogRepository):
        self.oms = oms
        self.market_data_service = market_data_service
        self.log_repository = log_repository
        self.logger = MarketDataLogger("trading_cycle")

    def _get_current_position(self):
        """Получает последнюю запись из лога через репозиторий."""
        return self.log_repository.get_last_record()

    def _update_log(self, order_id, symbol, order_type, price, quantity, status):
        """Добавляет новую запись в лог через репозиторий."""
        record_data = {
            'order_id': order_id,
            'symbol': symbol,
            'order_type': order_type,
            'price': price,
            'quantity': quantity,
            'status': status
        }
        self.log_repository.add_record(record_data)

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
        
        current_position = self._get_current_position()
        
        # Шаг 1: Синхронизация статуса "зависших" ордеров
        if current_position and current_position['status'] == 'PENDING':
            order_id = current_position['order_id']
            self.logger.log_operation_start("sync_pending_order", context={"order_id": order_id})
            
            try:
                actual_status = self.oms.get_order_status(order_id)
                self.logger.log_operation_complete("get_order_status", context={"order_id": order_id, "status": actual_status})
                
                if actual_status != current_position['status']:
                    self._update_log(
                        order_id=order_id,
                        symbol=current_position['symbol'],
                        order_type=current_position['order_type'],
                        price=current_position['price'],
                        quantity=current_position['quantity'],
                        status=actual_status
                    )
                    self.logger.log_operation_complete("update_log", context={"order_id": order_id, "new_status": actual_status})
                    current_position = self._get_current_position()
                    # Завершаем цикл, так как основное действие - синхронизация - выполнено
                    return
                else:
                    # Если статус не изменился, просто завершаем цикл
                    self.logger.log_operation_complete("sync_pending_order", context={"order_id": order_id, "status": "unchanged"})
                    return
               
            except Exception as e:
                self.logger.log_operation_error("get_order_status", error=str(e), context={"order_id": order_id})
                return

        # Шаг 2: Получение рыночных данных (пока заглушка)
        market_data = self.market_data_service.get_market_data("BTCUSDT")
        
        # Шаг 3: Взаимодействие с ИИ
        ai_decision = self._get_ai_decision(market_data, current_position)

        # Шаг 4: Оркестрация и исполнение решения
        if ai_decision == "BUY":
            # В реальной системе параметры будут браться из market_data и решения ИИ
            symbol = "BTCUSDT"
            quantity = 0.01
            price = market_data.h1_candles['close'].iloc[-1] if not market_data.h1_candles.empty else 52000
            
            self.logger.log_operation_start("place_buy_order", context={"symbol": symbol, "quantity": quantity, "price": price})
            
            try:
                # Размещаем ордер через OMS
                new_order_id = self.oms.place_order(
                    symbol=symbol,
                    order_type='BUY',
                    quantity=quantity,
                    price=price
                )
                self.logger.log_operation_complete("place_order", context={"order_id": new_order_id})
                
                # Сразу же логируем новый ордер как PENDING
                self._update_log(
                    order_id=new_order_id,
                    symbol=symbol,
                    order_type='BUY',
                    price=price,
                    quantity=quantity,
                    status='PENDING'
                )
                self.logger.log_operation_complete("log_pending_order", context={"order_id": new_order_id})

            except MarketDataError as e:
                self.logger.log_operation_error("place_buy_order", error=str(e), context={"error_type": "MarketDataError"})
            except Exception as e:
                self.logger.log_operation_error("place_buy_order", error=str(e), context={"error_type": "Unexpected"})
                # Обработка ошибок размещения

        elif ai_decision == "SELL":
            # Логика для продажи (пока заглушка)
            self.logger.log_operation_start("sell_logic", context={"decision": "SELL"})
            pass
        
        elif ai_decision == "HOLD":
            self.logger.log_operation_start("hold_logic", context={"decision": "HOLD"})
            pass

        self.logger.log_operation_complete("run_cycle")