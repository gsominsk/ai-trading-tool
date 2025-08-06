import csv
from datetime import datetime
from src.trading.oms import OrderManagementSystem
from src.market_data.market_data_service import MarketDataService


class TradingCycle:
    """
    Основной цикл торговой логики.
    """
    def __init__(self, oms: OrderManagementSystem, market_data_service: MarketDataService, trade_log_path: str = 'data/trade_log.csv'):
        self.oms = oms
        self.market_data_service = market_data_service
        self.trade_log_path = trade_log_path
        self.header = ['timestamp', 'order_id', 'symbol', 'type', 'price', 'quantity', 'status']

    def _get_current_position(self):
        """Читает последнюю запись из лога для определения текущей позиции."""
        try:
            with open(self.trade_log_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                records = list(reader)
                if not records:
                    return None  # Нет позиции
                return records[-1]
        except FileNotFoundError:
            return None

    def _update_log(self, order_id, symbol, order_type, price, quantity, status):
        """Добавляет новую запись в лог."""
        with open(self.trade_log_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.header)
            writer.writerow({
                'timestamp': datetime.utcnow().isoformat(),
                'order_id': order_id,
                'symbol': symbol,
                'type': order_type,
                'price': price,
                'quantity': quantity,
                'status': status
            })

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
        print("--- Промпт для ИИ ---")
        print(prompt)
        
        # Заглушка для решения ИИ
        decision = "BUY"
        print(f"--- Решение ИИ: {decision} ---")
        return decision

    def run_cycle(self):
        """Запускает один полный торговый цикл."""
        print("--- Запуск нового торгового цикла ---")
        
        current_position = self._get_current_position()
        
        # Шаг 1: Синхронизация статуса "зависших" ордеров
        if current_position and current_position['status'] == 'PENDING':
            order_id = current_position['order_id']
            print(f"Обнаружен ордер в статусе PENDING: {order_id}. Проверяю статус...")
            
            try:
                actual_status = self.oms.get_order_status(order_id)
                print(f"Актуальный статус ордера {order_id}: {actual_status}")
                
                if actual_status != current_position['status']:
                    self._update_log(
                        order_id=order_id,
                        symbol=current_position['symbol'],
                        order_type=current_position['type'],
                        price=current_position['price'],
                        quantity=current_position['quantity'],
                        status=actual_status
                    )
                    print(f"Статус ордера {order_id} обновлен в логе на {actual_status}.")
                    current_position = self._get_current_position()
                
            except Exception as e:
                print(f"Ошибка при получении статуса ордера {order_id}: {e}")
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
            price = market_data.get('price', 52000) # Пример
            
            print(f"ИИ принял решение BUY. Размещаю ордер: {symbol} {quantity} @ {price}")
            
            try:
                # Размещаем ордер через OMS
                new_order_id = self.oms.place_order(
                    symbol=symbol,
                    order_type='BUY',
                    quantity=quantity,
                    price=price
                )
                print(f"Ордер размещен. ID: {new_order_id}")
                
                # Сразу же логируем новый ордер как PENDING
                self._update_log(
                    order_id=new_order_id,
                    symbol=symbol,
                    order_type='BUY',
                    price=price,
                    quantity=quantity,
                    status='PENDING'
                )
                print(f"Новый ордер {new_order_id} залогирован со статусом PENDING.")

            except Exception as e:
                print(f"Ошибка при размещении ордера: {e}")
                # Обработка ошибок размещения

        elif ai_decision == "SELL":
            # Логика для продажи (пока заглушка)
            print("ИИ принял решение SELL. Логика продажи будет реализована позже.")
            pass
        
        elif ai_decision == "HOLD":
            print("ИИ принял решение HOLD. Никаких действий не требуется.")
            pass

        print("--- Торговый цикл завершен ---")