# План по устранению предупреждений и очистке тестового набора

Цель: Устранить все предупреждения (warnings), пропуски несуществующих файлов (skips) и устаревший код при запуске тестов для повышения чистоты и надежности тестовой среды.

--- ФАЗА 1: Удаление устаревшего теста ---
[ ] 1.1: Открыть файл `tests/unit/logging/test_logging_components.py`.
[ ] 1.2: Удалить устаревший тест `test_logging_integration_handles_logger_failure`.
[ ] 1.3: Запустить все тесты (`python tests/run_all_tests.py`) и убедиться в отсутствии регрессий.
[ ] 1.4: Обновить Memory Bank, зафиксировав удаление устаревшего теста.
[ ] 1.5: Сделать коммит с сообщением 'refactor(tests): remove obsolete logging test'.

--- ФАЗА 2: Исправление DeprecationWarning ---
[ ] 2.1: Открыть файл `tests/unit/trading/test_oms_repository_sqlite.py`.
[ ] 2.2: Заменить все вхождения `datetime.utcnow()` на `datetime.now(datetime.UTC)`.
[ ] 2.3: Убедиться, что импортирован `datetime` из модуля `datetime`.
[ ] 2.4: Запустить все тесты (`python tests/run_all_tests.py`) и убедиться, что предупреждения `DeprecationWarning` исчезли.
[ ] 2.5: Обновить Memory Bank, зафиксировав исправление.
[ ] 2.6: Сделать коммит с сообщением 'fix(tests): replace utcnow with timezone-aware now'.

--- ФАЗА 3: Очистка конфигурации тестового раннера ---
[ ] 3.1: Открыть файл `tests/run_all_tests.py`.
[ ] 3.2: Найти и удалить строки, которые пытаются запустить `tests/unit/test_timing_validation.py`.
[ ] 3.3: Найти и удалить строки, которые пытаются запустить `tests/integration/logging/test_hierarchical_tracing.py`.
[ ] 3.4: Запустить все тесты (`python tests/run_all_tests.py`) и убедиться, что в выводе отсутствуют предупреждения о пропущенных файлах.
[ ] 3.5: Обновить Memory Bank, зафиксировав очистку конфигурации.
[ ] 3.6: Сделать коммит с сообщением 'chore(tests): clean up test runner configuration'.