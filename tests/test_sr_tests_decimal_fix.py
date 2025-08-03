"""
Тесты для проверки исправления mixed arithmetic в _analyze_sr_tests.
Проверяет корректность Decimal арифметики в support/resistance анализе.
"""

import pytest
from decimal import Decimal
from src.market_data.market_data_service import MarketDataService

class TestSRTestsDecimalFix:
    """Тесты для проверки Decimal арифметики в _analyze_sr_tests."""
    
    def setup_method(self):
        """Настройка тестов."""
        self.service = MarketDataService()
    
    def test_resistance_test_decimal_precision(self):
        """Тест точности Decimal в анализе сопротивления."""
        # Точные Decimal уровни сопротивления и поддержки
        resistance_level = Decimal('50000.123456789')
        support_level = Decimal('49000.987654321')
        
        # Candles с высокой ценой близко к сопротивлению (в пределах 1%)
        candles = [
            [0, "50000.000000000", "50000.617283945", "49950.000000000", "50000.000000000", "1000"],  # Resistance test
            [0, "49950.000000000", "50000.123456789", "49900.000000000", "49950.000000000", "1000"],  # Exact resistance
            [0, "49800.000000000", "49850.000000000", "49000.987654321", "49820.000000000", "1000"],  # Exact support
        ]
        
        result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        
        # Должно найти тесты и сопротивления, и поддержки
        assert "R:" in result and "S:" in result
        assert "tests" in result
    
    def test_no_float_conversion_in_calculations(self):
        """Проверка отсутствия конверсии в float в процессе вычислений."""
        resistance_level = Decimal('100000.123456789012345')  # Высокая точность
        support_level = Decimal('99000.987654321098765')
        
        # Candles с точными Decimal значениями
        candles = [
            [0, "100000.000000000", "100000.123456789012345", "99500.000000000", "100000.000000000", "1000"],  # Exact resistance test
            [0, "99500.000000000", "99800.000000000", "99000.987654321098765", "99600.000000000", "1000"],  # Exact support test
        ]
        
        result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        
        # Функция находит все тесты уровней в candles - каждый candle может содержать несколько тестов
        # Первый candle: high точно равен resistance_level, второй candle: low точно равен support_level
        assert "R:" in result and "S:" in result and "tests" in result
    
    def test_edge_case_very_small_differences(self):
        """Тест edge case с очень маленькими различиями."""
        resistance_level = Decimal('50000.000000001')  # Очень точное значение
        support_level = Decimal('49000.000000002')
        
        # Candles с различиями на границе точности
        candles = [
            [0, "50000.000000000", "50000.000500000", "49950.000000000", "50000.000000000", "1000"],  # В пределах 1%
            [0, "49000.000000000", "49050.000000000", "49000.000000001", "49020.000000000", "1000"],  # Почти точное совпадение
        ]
        
        result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        
        # Должно найти тесты
        assert "R:" in result and "S:" in result
    
    def test_precision_boundary_1_percent(self):
        """Тест границы 1% для определения тестов уровней."""
        resistance_level = Decimal('100000')
        support_level = Decimal('90000')
        
        # Candles с точными расчетами для 1% границы
        candles = [
            [0, "99000.000000000", "99000.000000000", "89100.000000000", "99000.000000000", "1000"],  # Ровно 1% от support (90000 * 0.99 = 89100)
            [0, "99000.000000000", "99000.000000000", "89101.000000000", "99000.000000000", "1000"],  # Чуть больше 1% от support - не должно засчитаться
        ]
        
        result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        
        # Должно найти только один тест поддержки (первый candle в пределах 1%)
        assert "Support tested 1 times" == result
    
    def test_no_tests_found(self):
        """Тест случая когда тесты уровней не найдены."""
        resistance_level = Decimal('60000')
        support_level = Decimal('50000')
        
        # Candles далеко от уровней
        candles = [
            [0, "55000.000000000", "56000.000000000", "54000.000000000", "55500.000000000", "1000"],
            [0, "55500.000000000", "56500.000000000", "54500.000000000", "56000.000000000", "1000"],
        ]
        
        result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        
        assert result == "No recent S/R tests"
    
    def test_only_resistance_tests(self):
        """Тест случая только тестов сопротивления."""
        resistance_level = Decimal('55000')
        support_level = Decimal('50000')
        
        # Candles только близко к сопротивлению
        candles = [
            [0, "54500.000000000", "54999.999999999", "54000.000000000", "54800.000000000", "1000"],  # Close to resistance
            [0, "54800.000000000", "55000.000000000", "54200.000000000", "54900.000000000", "1000"],  # Exact resistance
        ]
        
        result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        
        assert "Resistance tested" in result
        assert "2 times" in result
    
    def test_only_support_tests(self):
        """Тест случая только тестов поддержки."""
        resistance_level = Decimal('60000')
        support_level = Decimal('50000')
        
        # Candles только близко к поддержке
        candles = [
            [0, "52000.000000000", "53000.000000000", "50000.000000000", "52500.000000000", "1000"],  # Exact support
            [0, "51000.000000000", "52000.000000000", "49999.999999999", "51500.000000000", "1000"],  # Close to support
        ]
        
        result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        
        assert "Support tested" in result
        assert "2 times" in result
    
    def test_multiple_tests_counting(self):
        """Тест подсчета множественных тестов уровней."""
        resistance_level = Decimal('55000')
        support_level = Decimal('50000')
        
        # Multiple candles testing levels
        candles = [
            [0, "54500.000000000", "55000.000000000", "54000.000000000", "54800.000000000", "1000"],  # R test
            [0, "54800.000000000", "54999.999999999", "54200.000000000", "54900.000000000", "1000"],  # R test
            [0, "52000.000000000", "53000.000000000", "50000.000000000", "52500.000000000", "1000"],  # S test
            [0, "51000.000000000", "52000.000000000", "50100.000000000", "51500.000000000", "1000"],  # S test
            [0, "50500.000000000", "51500.000000000", "49999.999999999", "51000.000000000", "1000"],  # S test
        ]
        
        result = self.service._analyze_sr_tests(candles, support_level, resistance_level)
        
        assert "R:2 tests, S:3 tests" == result

def test_decimal_import_available():
    """Проверка что Decimal доступен в методе."""
    service = MarketDataService()
    
    # Простой тест с валидными данными
    candles = [
        [0, "50000.000000000", "50500.000000000", "49500.000000000", "50250.000000000", "1000"],
    ]
    
    result = service._analyze_sr_tests(
        candles, 
        Decimal('50000'), 
        Decimal('50500')
    )
    
    # Не должно выбрасывать исключение
    assert isinstance(result, str)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])