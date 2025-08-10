# Phase 9.1: Tracing Logic Simplification Plan

--- ФАЗА 1: Рефакторинг MarketDataService ---
[ ] 1.1: В `src/market_data/market_data_service.py`, удалить метод `_start_operation`.
[ ] 1.2: В `src/market_data/market_data_service.py`, изменить сигнатуру `get_market_data` с `parent_trace_id` на `trace_id`.
[ ] 1.3: В `src/market_data/market_data_service.py`, обновить все внутренние вызовы (`_get_klines`, `_calculate_rsi` и т.д.) для приема `trace_id`.
[ ] 1.4: В `src/market_data/market_data_service.py`, обновить все вызовы логгера, чтобы они использовали `trace_id` и не использовали `parent_trace_id`.
[ ] 1.5: Обновить Memory Bank (`progress.md`, `decisionLog.md`), чтобы отразить завершение рефакторинга MarketDataService.

--- ФАЗА 2: Рефакторинг TradingCycle ---
[ ] 2.1: В `src/trading/trading_cycle.py`, обновить вызов `self.market_data_service.get_market_data` для передачи `master_trace_id` в аргумент `trace_id`.
[ ] 2.2: Обновить Memory Bank, чтобы отразить завершение рефакторинга TradingCycle.

--- ФАЗА 3: Рефакторинг Интеграционного Теста ---
[ ] 3.1: В `tests/integration/logging/test_end_to_end_tracing.py`, обновить мок для `_get_klines` в соответствии с новой сигнатурой.
[ ] 3.2: В `tests/integration/logging/test_end_to_end_tracing.py`, упростить ассерты для проверки единого `master_trace_id`.
[ ] 3.3: Обновить Memory Bank, чтобы отразить завершение рефакторинга теста.

--- ФАЗА 4: Валидация и Завершение ---
[ ] 4.1: Запустить тест `tests/integration/logging/test_end_to_end_tracing.py`.
[ ] 4.2: Запустить все тесты проекта (`run_all_tests.py`).
[ ] 4.3: Сделать финальное обновление Memory Bank по итогам всех работ.
[ ] 4.4: Сделать коммит с сообщением 'refactor: Simplify tracing logic in MarketDataService to use a single trace_id'.