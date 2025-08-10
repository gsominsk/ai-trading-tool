# TASK: Refactor Logging System to Correct `service_name`

**Description:** The current logging system incorrectly labels all log entries with `"service":"MarketDataService"`. This plan refactors the logging architecture to ensure each component logs with its correct, dynamically assigned `service_name`.

---

**--- ФАЗА 1: Рефакторинг ядра системы логирования и обновление тестов ---**

1.1: В `src/logging_system/json_formatter.py`, изменить `AIOptimizedJSONFormatter` для извлечения `service_name` из `LogRecord`.
1.2: В `src/logging_system/logger_config.py`, обновить `configure_logging`, `get_ai_logger` и `MarketDataLogger` для поддержки динамического `service_name`.
1.3: В `tests/unit/logging/test_core_logging.py`, адаптировать тесты: обновить создание логгеров для передачи `service_name` и проверить корректность `service` в логах.
1.4: Запустить тесты для Фазы 1 (`tests/unit/logging/test_core_logging.py`) и убедиться, что они проходят.
1.5: Обновить Memory Bank (`progress.md`, `decisionLog.md`).
1.6: Сделать коммит с сообщением 'refactor(logging): Core logging system to support dynamic service names'.

---

**--- ФАЗА 2: Обновление компонентов и их тестов ---**

2.1: В `src/trading/trading_cycle.py`, обновить создание `MarketDataLogger`, передав `service_name='trading_cycle'`.
2.2: В `src/market_data/market_data_service.py`, обновить создание `MarketDataLogger`, передав `service_name='market_data_service'`.
2.3: В `src/trading/oms.py`, обновить создание `MarketDataLogger`, передав `service_name='oms'`.
2.4: В `src/trading/oms_repository.py`, обновить создание `MarketDataLogger`, передав `service_name='oms_repository'`.
2.5: В соответствующих файлах тестов (`tests/unit/trading/test_trading_cycle.py`, `tests/unit/test_market_data_service.py` и т.д.), обновить моки и ассерты для проверки нового `service_name`.
2.6: Запустить все тесты, затронутые в Фазе 2, и убедиться, что они проходят.
2.7: Обновить Memory Bank.
2.8: Сделать коммит с сообщением 'feat(logging): Update components to provide service_name to logger'.

---

**--- ФАЗА 3: Финальная валидация через интеграционные тесты ---**

3.1: Проанализировать и исправить интеграционные тесты, если они упали после изменений (например, `tests/integration/logging/test_end_to_end_tracing.py`).
3.2: Запустить все тесты проекта (`tests/run_all_tests.py`) и исправить оставшиеся ошибки.
3.3: Обновить Memory Bank по итогам исправления тестов.
3.4: Сделать коммит с сообщением 'fix(tests): Adapt all tests to new logging architecture'.

---

**--- ФАЗА 4: Валидация в реальном сценарии и завершение ---**

4.1: В `examples/run_full_trading_cycle.py`, убедиться, что все логгеры создаются с правильными `service_name`.
4.2: Запустить скрипт `examples/run_full_trading_cycle.py`.
4.3: Проанализировать сгенерированный `logs/trading_cycle.log` и убедиться, что поле `service` в каждой записи JSON соответствует источнику лога.
4.4: Сделать финальное обновление Memory Bank по итогам всех работ.
4.5: Сделать коммит с сообщением 'docs: Update memory bank after logging refactoring'.