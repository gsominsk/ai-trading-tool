"""
Простая демонстрация системы "No Logs = No Trading"
"""

import sys
sys.path.insert(0, "src")

from logging_system.logger_config import configure_ai_logging
from logging_system.json_formatter import get_logger

def simulate_trading_service():
    """
    Симуляция торгового сервиса
    """
    print("🚀 Запуск торгового сервиса...")
    
    # Настройка логирования (работает)
    configure_ai_logging(
        log_level="INFO",
        log_file="logs/trading.log",
        console_output=True
    )
    
    # Получение логгера
    logger = get_logger("trading_service", "TradingBot")
    
    print("📊 Начинаем торговые операции...")
    
    # Симуляция торговых операций
    for i in range(3):
        logger.info(f"Trading operation {i+1}", 
                   operation="place_order",
                   context={"symbol": "BTCUSDT", "amount": 100})
        print(f"✅ Торговая операция {i+1} выполнена")
    
    print("🎉 Торговый сервис работает нормально!")

def simulate_broken_logging():
    """
    Симуляция сломанного логирования
    """
    print("💥 Попытка запуска с поломанным логированием...")
    
    # Попытка настроить логирование в недоступное место
    configure_ai_logging(
        log_level="INFO", 
        log_file="/root/impossible/trading.log",  # Недоступная директория
        console_output=True
    )
    
    print("❌ Этот код никогда не выполнится")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "break":
        print("🧪 Тестируем поломку логирования...")
        simulate_broken_logging()
    else:
        print("🧪 Тестируем нормальную работу...")
        simulate_trading_service()