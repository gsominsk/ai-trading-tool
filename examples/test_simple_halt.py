"""
Простой тест остановки сервиса при сбоях логирования
"""

import sys
import os
sys.path.insert(0, "src")

from logging_system.json_formatter import get_logger
import tempfile

print("🧪 Тестируем систему остановки при сбоях логирования...")

# Получаем логгер
logger = get_logger("test_service", "TestService")

# Тест 1: Нормальное логирование
print("1. Тест нормального логирования:")
try:
    logger.info("Это обычное сообщение")
    logger.debug("Это debug сообщение")
    print("✅ Нормальное логирование работает")
except Exception as e:
    print(f"❌ Ошибка в нормальном логировании: {e}")

# Тест 2: Попробуем сломать файловое логирование
print("\n2. Тест с поломкой файлового логирования:")

from logging_system.logger_config import configure_ai_logging

try:
    # Попробуем настроить логирование в недоступную директорию
    configure_ai_logging(
        log_level="DEBUG",
        log_file="/root/readonly/test.log",  # Недоступная директория
        console_output=True
    )
    
    # Создаем новый логгер с файловым выводом
    file_logger = get_logger("file_test", "TestService")
    
    print("Попытка записи в недоступный файл...")
    file_logger.info("Это должно вызвать сбой")
    print("❌ Система не остановилась как ожидалось")
    
except Exception as e:
    print(f"✅ Ошибка перехвачена: {e}")

print("\n3. Тест завершен")