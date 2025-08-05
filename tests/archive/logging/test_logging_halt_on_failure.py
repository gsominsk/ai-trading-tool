"""
Тест простой системы остановки сервиса при сбоях логирования
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

def test_logging_system_halts_service_on_failure():
    """
    Тест: если логи сломались, система останавливает сервис
    """
    
    # Создаем тестовый скрипт который сломает логи
    test_script = '''
import sys
import os
sys.path.insert(0, "src")

from logging_system.json_formatter import get_logger

# Получаем логгер
logger = get_logger("test_service", "TestService")

# Эмулируем сломанное логирование
# Заменяем sys.stderr на readonly файл
import io
sys.stderr = io.StringIO()
sys.stderr.close()  # Закрываем чтобы вызвать ошибку

try:
    # Попытка записать лог должна завершить процесс
    logger.info("This should crash and halt service")
    print("ERROR: Service should have halted but didn't!")
    sys.exit(1)
except SystemExit:
    # os._exit() не перехватывается как SystemExit
    print("Service halted as expected")
'''
    
    # Записываем тестовый скрипт
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        script_path = f.name
    
    try:
        # Запускаем тестовый скрипт
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, timeout=5)
        
        # Процесс должен завершиться с кодом 1 (от os._exit(1))
        assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"
        
        # В stderr должно быть сообщение о критической ошибке
        assert "CRITICAL: Logging system failed" in result.stderr, \
               f"Expected critical error message in stderr: {result.stderr}"
        
        print("✅ Тест пройден: система корректно останавливает сервис при сбоях логирования")
        
    except subprocess.TimeoutExpired:
        print("❌ Тест провален: процесс завис и не остановился")
        raise
    finally:
        # Удаляем временный файл
        os.unlink(script_path)


def test_normal_logging_works():
    """
    Тест: при нормальной работе логирование функционирует
    """
    
    test_script = '''
import sys
sys.path.insert(0, "src")

from logging_system.json_formatter import get_logger

# Получаем логгер
logger = get_logger("test_service", "TestService")

# Нормальное логирование должно работать
logger.info("Normal logging works")
logger.debug("Debug message")
logger.warning("Warning message")

print("SUCCESS: Normal logging completed")
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        script_path = f.name
    
    try:
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, timeout=5)
        
        # Процесс должен завершиться успешно
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        
        # Должно быть сообщение об успехе
        assert "SUCCESS: Normal logging completed" in result.stdout, \
               f"Expected success message: {result.stdout}"
        
        print("✅ Тест пройден: нормальное логирование работает корректно")
        
    finally:
        os.unlink(script_path)


if __name__ == "__main__":
    print("🧪 Тестирование системы остановки сервиса при сбоях логирования")
    print()
    
    test_normal_logging_works()
    print()
    test_logging_system_halts_service_on_failure()
    print()
    print("🎉 Все тесты пройдены!")