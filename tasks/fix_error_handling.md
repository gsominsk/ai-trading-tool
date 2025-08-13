# Задача: Улучшение обработки ошибок и логирования

## Цель
Устранить критические уязвимости в обработке ошибок и закрыть пробелы в логировании для повышения надежности и упрощения диагностики системы.

--- ФАЗА 1: Исправление критической ошибки парсинга JSON в SentimentApiClient ---
[ ] 1.1: В `src/infrastructure/sentiment_client.py` обернуть вызов `response.json()` в блок `try...except JSONDecodeError` и генерировать `ApiClientError` при сбое.
[ ] 1.2: Создать новый файл с тестами `tests/unit/infrastructure/test_sentiment_client.py` и добавить тест, который проверяет, что при невалидном JSON от API генерируется `ApiClientError`.
[ ] 1.3: Запустить все тесты (`tests/run_all_tests.py`) и убедиться, что они проходят успешно.

--- ФАЗА 2: Корректировка логирования операционных ошибок ---
[ ] 2.1: В `src/logging_system/logger_config.py` (или соответствующем файле логгера) создать новый метод `log_operation_failure` для логирования общих операционных ошибок.
[ ] 2.2: В `src/market_data/market_data_service.py`, в методе `_get_fear_and_greed_index`, заменить вызов `log_operation_error` на новый `log_operation_failure` при перехвате `ApiClientError`.
[ ] 2.3: Обновить юнит-тест `test_get_fear_and_greed_index_handles_api_error` в `tests/unit/test_market_data_service.py`, чтобы он проверял вызов нового метода `log_operation_failure`.
[ ] 2.4: Запустить все тесты (`tests/run_all_tests.py`) и убедиться, что они проходят успешно.

--- ФАЗА 3: Улучшение логирования при неожиданной структуре данных ---
[ ] 3.1: В `src/market_data/market_data_service.py`, в методе `_get_fear_and_greed_index`, добавить логирование (уровень WARNING) в случаях, когда структура ответа API не соответствует ожидаемой (например, отсутствует ключ 'data' или 'value').
[ ] 3.2: В `tests/unit/test_market_data_service.py` добавить новый тест для проверки этого нового логирования.
[ ] 3.3: Запустить все тесты (`tests/run_all_tests.py`) и убедиться, что они проходят успешно.

--- ФАЗА 4: Завершение ---
[ ] 4.1: Обновить Memory Bank (`progress.md`, `activeContext.md`), зафиксировав все внесенные улучшения.
[ ] 4.2: Сделать коммит с сообщением 'fix(error_handling): Improve error handling and logging for sentiment client'.