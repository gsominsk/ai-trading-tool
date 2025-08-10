# План работ: Фаза 9 - Улучшение сквозного логирования и трассировки (v2)

## Цель:
Обеспечить полную прослеживаемость операций, перенеся генерацию корневого `trace_id` в `TradingCycle` и обеспечив его сквозную передачу через все компоненты (`OMS`, `MarketDataService`, `OmsRepository`).

## Задачи:

--- ФАЗА 9: Улучшение сквозного логирования и трассировки ---
- [ ] 9.1: **Рефакторинг `MarketDataService`**: Изменить метод `get_market_data`, чтобы он принимал `parent_trace_id` и использовал его как корневой для своей внутренней трассировки, вместо генерации нового.
- [ ] 9.2: **Рефакторинг `TradingCycle`**: В методе `run_cycle` генерировать **один** мастер `trace_id` в самом начале.
- [ ] 9.3: **Интеграция `TradingCycle` и `MarketDataService`**: Передавать мастер `trace_id` из `TradingCycle` в `market_data_service.get_market_data` в качестве `parent_trace_id`.
- [ ] 9.4: Обновить `memory-bank/progress.md` и `decisionLog.md`, зафиксировав рефакторинг `MarketDataService` и `TradingCycle`.
- [ ] 9.5: В `OmsRepository` (`src/trading/oms_repository.py`), обновить методы `load`, `save`, `delete`, добавив в их сигнатуры `trace_id: Optional[str] = None`.
- [ ] 9.6: В `OmsRepository`, добавить вызовы `self.logger` для `log_operation_start` и `log_operation_complete` в методы `load`, `save` и `delete`, используя `trace_id`.
- [ ] 9.7: В `OMS` (`src/trading/oms.py`), обновить вызовы `self.repository` в методах `__init__`, `place_order`, `cancel_order`, `get_order_status`, чтобы передавать `trace_id`.
- [ ] 9.8: В `OMS`, обновить метод `get_order_by_symbol`, добавив параметр `trace_id` и соответствующее логирование.
- [ ] 9.9: **Интеграция `TradingCycle` и `OMS`**: Передавать мастер `trace_id` из `TradingCycle` во все вызовы методов `OMS`.
- [ ] 9.10: Обновить `memory-bank/progress.md` и `decisionLog.md`, зафиксировав изменения в `OMS` и `OmsRepository`.
- [ ] 9.11: Создать новый тест `tests/integration/logging/test_end_to_end_tracing.py` для проверки сквозной передачи `trace_id` от `TradingCycle` до `OmsRepository` и `MarketDataService`.
- [ ] 9.12: Запустить все тесты проекта (`run_all_tests.py`).
- [ ] 9.13: Финальное обновление `memory-bank/progress.md` и `decisionLog.md` по итогам Фазы 9.
- [ ] 9.14: Сделать коммит с сообщением "feat(logging): implement full end-to-end tracing".