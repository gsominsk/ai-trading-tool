"""
Тесты критических исправлений для production safety
"""

import pytest
import sys
import threading
import time
from unittest.mock import patch
from decimal import Decimal
from datetime import datetime

# Добавляем src в путь
sys.path.insert(0, "src")

from logging_system.json_formatter import AIOptimizedJSONFormatter, StructuredLogger
from logging_system.trace_generator import get_trace_id, get_flow_id, reset_trace_counter
from logging_system.logger_config import configure_ai_logging


class TestProductionSafetyFixes:
    """Тесты критических исправлений для production safety."""
    
    def test_systemexit_instead_of_os_exit(self):
        """Тест: SystemExit(1) вместо os._exit(1) должен быть перехватываемым."""
        logger = StructuredLogger("test_logger", "TestService")
        
        # Эмулируем сбой логирования
        with patch.object(logger.logger, 'log', side_effect=Exception("Mock logging failure")):
            with pytest.raises(SystemExit) as exc_info:
                logger.info("This should fail")
            
            # Проверяем что это SystemExit(1), а не os._exit(1)
            assert exc_info.value.code == 1
            assert exc_info.type == SystemExit
    
    def test_json_serialization_fallback(self):
        """Тест: JSON serialization должен иметь fallback при ошибках."""
        formatter = AIOptimizedJSONFormatter("TestService")
        
        # Создаем mock record с non-serializable объектами
        class MockRecord:
            def __init__(self):
                self.levelname = "INFO"
                self.getMessage = lambda: "Test message"
                self.exc_info = None
                # Добавляем non-serializable объект
                self.context = {"decimal_value": Decimal("123.45"), "datetime_value": datetime.now()}
                self.operation = "test_operation"
                self.tags = ["test"]
                self.flow = {}
                self.trace_id = "test_trace_123"
        
        record = MockRecord()
        
        # Форматирование должно работать с fallback
        result = formatter.format(record)
        
        # Проверяем что получили строку (не exception)
        assert isinstance(result, str)
        # Проверяем что это либо правильный JSON, либо fallback
        assert "Test message" in result
        assert ("INFO" in result or "FALLBACK_LOG" in result)
    
    def test_thread_safety_trace_generator(self):
        """Тест: trace generator должен быть thread-safe."""
        reset_trace_counter()
        
        trace_ids = []
        
        def generate_trace_ids():
            for _ in range(10):
                trace_ids.append(get_trace_id())
                time.sleep(0.001)  # Небольшая задержка
        
        # Запускаем несколько потоков одновременно
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=generate_trace_ids)
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()
        
        # Проверяем что все trace_id уникальны
        assert len(trace_ids) == 30  # 3 threads * 10 ids each
        assert len(set(trace_ids)) == 30  # Все должны быть уникальными
    
    def test_handler_accumulation_prevention(self):
        """Тест: handlers не должны накапливаться."""
        # Создаем несколько логгеров с одинаковым именем
        logger1 = StructuredLogger("same_logger", "TestService")
        initial_handlers_count = len(logger1.logger.handlers)
        
        logger2 = StructuredLogger("same_logger", "TestService")
        second_handlers_count = len(logger2.logger.handlers)
        
        logger3 = StructuredLogger("same_logger", "TestService")
        third_handlers_count = len(logger3.logger.handlers)
        
        # Количество handlers не должно расти неконтролируемо
        assert initial_handlers_count > 0  # Должен быть хотя бы один handler
        assert second_handlers_count <= initial_handlers_count + 1  # Не больше чем +1
        assert third_handlers_count <= initial_handlers_count + 1   # Не больше чем +1
    
    def test_flow_id_generation_thread_safety(self):
        """Тест: flow_id generation должен быть thread-safe."""
        flow_ids = []
        
        def generate_flow_ids():
            for _ in range(5):
                flow_ids.append(get_flow_id("BTCUSDT"))
                time.sleep(0.001)
        
        threads = []
        for _ in range(4):
            thread = threading.Thread(target=generate_flow_ids)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Проверяем что все flow_id имеют правильный формат
        assert len(flow_ids) == 20
        for flow_id in flow_ids:
            assert flow_id.startswith("flow_btc_")
            assert len(flow_id.split("_")) == 3
    
    def test_logging_configuration_graceful_failure(self):
        """Тест: конфигурация логирования должна gracefully fail."""
        # Пытаемся создать лог в недоступном месте
        with pytest.raises(SystemExit) as exc_info:
            configure_ai_logging(
                log_level="INFO",
                log_file="/root/impossible/path/test.log"  # Недоступный путь
            )
        
        # Должен быть SystemExit, а не os._exit
        assert exc_info.value.code == 1
        assert exc_info.type == SystemExit


if __name__ == "__main__":
    print("🧪 Тестирование production safety исправлений...")
    
    # Запускаем тесты
    test_suite = TestProductionSafetyFixes()
    
    try:
        test_suite.test_systemexit_instead_of_os_exit()
        print("✅ SystemExit test passed")
    except Exception as e:
        print(f"❌ SystemExit test failed: {e}")
    
    try:
        test_suite.test_json_serialization_fallback()
        print("✅ JSON serialization fallback test passed")
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
    
    try:
        test_suite.test_thread_safety_trace_generator()
        print("✅ Thread safety test passed")
    except Exception as e:
        print(f"❌ Thread safety test failed: {e}")
    
    try:
        test_suite.test_handler_accumulation_prevention()
        print("✅ Handler accumulation test passed")
    except Exception as e:
        print(f"❌ Handler accumulation test failed: {e}")
    
    try:
        test_suite.test_flow_id_generation_thread_safety()
        print("✅ Flow ID thread safety test passed")
    except Exception as e:
        print(f"❌ Flow ID thread safety test failed: {e}")
    
    print("🎉 Все production safety тесты завершены!")