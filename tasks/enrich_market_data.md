# Задача: Обогащение рыночного контекста (Корреляция и Индекс страха)

**ID Задачи:** T-008
**Приоритет:** Высокий
**Статус:** К выполнению

## Описание:
Текущая реализация `MarketDataService` не предоставляет полные данные для LLM, в частности, `btc_correlation` и `fear_greed_index` всегда `null`. Эта задача направлена на реализацию двух ключевых улучшений:
1.  **Эффективный расчет корреляции с BTC:** Добавить механизм кеширования для данных BTC, чтобы избежать повторных API-запросов при анализе нескольких активов.
2.  **Интеграция "Индекса страха и жадности":** Создать новый API-клиент для получения данных о настроениях рынка с внешнего источника (`api.alternative.me`) и интегрировать его в `MarketDataService`.

## План Реализации:

--- ФАЗА 1: Реализация кеширования для корреляции с BTC ---
- [ ] 1.1: В `src/market_data/market_data_service.py`, в классе `MarketDataService`, добавить в `__init__` атрибуты для кеширования: `_btc_cache` и `_btc_cache_timestamp`.
- [ ] 1.2: В методе `_calculate_btc_correlation` добавить логику проверки кеша. Если кеш свежий (например, < 5 минут), использовать его. Иначе, выполнить API-запрос и обновить кеш.
- [ ] 1.3: Создать новый юнит-тест в `tests/unit/market_data/` (например, `test_market_data_caching.py`) для проверки логики кеширования. Тест должен убедиться, что `api_client.get_klines` для BTC вызывается только один раз при повторных вызовах.
- [ ] 1.4: Запустить все тесты (`tests/run_all_tests.py`) и убедиться, что они проходят успешно.
- [ ] 1.5: Обновить Memory Bank (`progress.md`, `decisionLog.md`), зафиксировав реализацию кеширования.
- [ ] 1.6: Сделать коммит с сообщением 'feat(market_data): Implement caching for BTC correlation'.

--- ФАЗА 2: Создание клиента для "Индекса страха и жадности" ---
- [ ] 2.1: Создать новый файл `src/infrastructure/sentiment_client.py`.
- [ ] 2.2: В `sentiment_client.py` реализовать класс `SentimentApiClient` с методом `get_fear_and_greed_index()`, который делает GET-запрос к `https://api.alternative.me/fng/`.
- [ ] 2.3: Добавить обработку ошибок (сетевые, ошибки API) и логирование в `SentimentApiClient`.
- [ ] 2.4: Создать юнит-тест для `SentimentApiClient` в `tests/unit/infrastructure/test_sentiment_client.py`, используя моки для `requests`.
- [ ] 2.5: Запустить тесты для Фазы 2 и убедиться, что они проходят.
- [ ] 2.6: Обновить Memory Bank, зафиксировав создание нового клиента.
- [ ] 2.7: Сделать коммит с сообщением 'feat(infrastructure): Create SentimentApiClient for Fear & Greed Index'.

--- ФАЗА 3: Интеграция SentimentApiClient в MarketDataService ---
- [ ] 3.1: В `src/market_data/market_data_service.py` импортировать `SentimentApiClient` и добавить его в `__init__`.
- [ ] 3.2: В `main.py` обновить создание `MarketDataService`, передавая ему инстанс `SentimentApiClient`.
- [ ] 3.3: В `MarketDataService` создать новый приватный метод, например, `_get_fear_and_greed_index()`, который вызывает клиент и обрабатывает результат.
- [ ] 3.4: В `get_market_data` вызывать `_get_fear_and_greed_index()` и передавать результат в `MarketDataSet`.
- [ ] 3.5: Обновить юнит-тесты для `MarketDataService`, чтобы проверить интеграцию и передачу данных.
- [ ] 3.6: Запустить все тесты (`tests/run_all_tests.py`) и убедиться, что они проходят успешно.
- [ ] 3.7: Обновить Memory Bank, зафиксировав завершение интеграции.
- [ ] 3.8: Сделать коммит с сообщением 'feat(market_data): Integrate Fear & Greed Index into MarketDataService'.