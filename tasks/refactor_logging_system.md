--- ФАЗА 1: Рефакторинг логирования в BinanceApiClient ---
[ ] 1.1: Модифицировать `src/infrastructure/binance_client.py`, чтобы он принимал `StructuredLogger` вместо стандартного логгера.
[ ] 1.2: Заменить все вызовы `self.logger.info`, `self.logger.error` и т.д. на соответствующие методы `StructuredLogger` с передачей контекста (`operation`, `context`, `trace_id`).
[ ] 1.3: Обновить `main.py` для корректной инициализации `BinanceApiClient` с новым логгером.
[ ] 1.4: Запустить `main.py` для проверки, что логи от `BinanceApiClient` теперь имеют правильную структуру (`service`, `operation`).

--- ФАЗА 2: Улучшение структуры логов в main.py ---
[ ] 2.1: В `main.py`, в функции `test_market_data_service`, изменить логирование вывода LLM-контекста. Вместо прямого вывода текста в `message`, поместить его в поле `context.llm_context_preview`.
[ ] 2.2: Запустить `main.py` и убедиться, что лог с предпросмотром контекста имеет валидную JSON-структуру.

--- ФАЗА 3: Финальная проверка и очистка ---
[ ] 3.1: Запустить `tests/run_all_tests.py` и убедиться, что все тесты проходят после изменений в логировании.
[ ] 3.2: Очистить файл `logs/trading_system.log`.
[ ] 3.3: Обновить Memory Bank (`decisionLog.md`, `progress.md`), зафиксировав улучшения в системе логирования.
[ ] 3.4: Сделать коммит с сообщением 'refactor(logging): improve logging structure and context'.