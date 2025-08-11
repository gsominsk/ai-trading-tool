# План Задачи: Рефакторинг API Клиента и Системы Ошибок

На основе нашего обсуждения, мы создадим выделенный инфраструктурный слой для взаимодействия с API Binance. Это повысит тестируемость, гибкость и отделит бизнес-логику от деталей взаимодействия с API.

--- ФАЗА 1: Подготовка Инфраструктуры и Файловой Структуры ---
[x] 1.1: Создать директорию `src/infrastructure`.
[x] 1.2: Создать пустой файл `src/infrastructure/__init__.py`.
[x] 1.3: Создать пустой файл `src/infrastructure/exceptions.py`.
[x] 1.4: Создать пустой файл `src/infrastructure/binance_client.py`.
[x] 1.5: Обновить Memory Bank (`decisionLog.md`), зафиксировав решение о создании инфраструктурного слоя и его файловой структуры.
[x] 1.6: Сделать коммит с сообщением 'feat: scaffold infrastructure layer directories and files'.

--- ФАЗА 2: Миграция и Адаптация Системы Ошибок ---
[x] 2.1: Скопировать содержимое из `src/market_data/exceptions.py` в `src/infrastructure/exceptions.py`.
[x] 2.2: Переименовать базовый класс `MarketDataError` на `ApiClientError` в `src/infrastructure/exceptions.py`.
[x] 2.3: Удалить старый файл `src/market_data/exceptions.py`.
[x] 2.4: Обновить Memory Bank (`progress.md`), отметив завершение миграции системы ошибок.
[x] 2.5: Сделать коммит с сообщением 'refactor: migrate and adapt exception classes to infrastructure layer'.

--- ФАЗА 3: Реализация Каркаса BinanceApiClient ---
[x] 3.1: Реализовать в `BinanceApiClient` базовую структуру с `__init__`, принимающим `logger`.
[x] 3.2: Реализовать в `BinanceApiClient` приватный метод `_handle_response` для централизованной обработки ошибок API.
[x] 3.3: Создать заглушки (`NotImplementedError`) для приватных методов: `create_order`, `cancel_order`, `get_order_status`.
[x] 3.4: Обновить Memory Bank (`progress.md`), отметив создание каркаса клиента.
[x] 3.5: Сделать коммит с сообщением 'feat: implement skeleton for BinanceApiClient'.

--- ФАЗА 4: Реализация Публичных Методов Клиента ---
[x] 4.1: Реализовать публичный метод `get_server_time` в `BinanceApiClient` для проверки связи.
[x] 4.2: Реализовать публичный метод `get_klines` в `BinanceApiClient`, включая логирование и проброс `trace_id`.
[x] 4.3: Обновить Memory Bank (`progress.md`), отметив реализацию публичных методов.
[x] 4.4: Сделать коммит с сообщением 'feat: implement public methods in BinanceApiClient'.

--- ФАЗА 5: Интеграция и Финальное Тестирование ---
[x] 5.1: Провести рефакторинг `MarketDataService` для использования нового `BinanceApiClient` через Dependency Injection.
[x] 5.2: Адаптировать тесты для `MarketDataService` (`tests/unit/test_market_data_service.py`) для работы с моком `BinanceApiClient`.
[x] 5.3: (Волна 1) Исправить простые ошибки рефакторинга в тестах. (Объединено и завершено)
[x] 5.4: (Волна 2) Исправить первоначальные ошибки логирования. (Объединено и завершено)
[-] 5.5: **(Волна 3) Устранение регрессий и блокеров:**
    - [ ] 5.5.1: Исправить `StopIteration` в `tests/integration/refactoring/test_api_call_efficiency.py`, предоставив 4 мок-ответа для `get_klines`.
    - [ ] 5.5.2: Глубоко проанализировать и исправить `AttributeError` в `tests/unit/logging/test_logging_components.py`, изучив исходный код логгера для правильного мокирования.
    - [ ] 5.5.3: Запустить тесты для подтверждения исправления регрессий.
[ ] 5.6: **(Волна 4) Исправление сложных интеграционных ошибок:**
    - [ ] 5.6.1: Исправить 7 ошибок в `tests/integration/error_architecture/test_error_integration.py` (RateLimitError, Timestamp, и др.).
    - [ ] 5.6.2: Исправить ошибки захвата логов (`caplog`) в `tests/integration/logging/test_logging_integration.py`.
    - [ ] 5.6.3: Запустить тесты для подтверждения исправления.
[ ] 5.7: **(Волна 5) Системное исправление `DataInsufficientError`:**
    - [ ] 5.7.1: Проанализировать все оставшиеся падения тестов, связанные с `DataInsufficientError` и `DataFrameValidationError`.
    - [ ] 5.7.2: Систематически исправить моки во всех затронутых тестах, предоставляя достаточное количество данных (например, >50 свечей).
[ ] 5.8: **(Волна 6) Финальная проверка и завершение:**
    - [ ] 5.8.1: Запустить `tests/run_all_tests.py` и убедиться, что все тесты проходят.
    - [ ] 5.8.2: Обновить Memory Bank (`decisionLog.md`), зафиксировав успешное завершение рефакторинга и тестирования.
    - [ ] 5.8.3: Сделать коммит с сообщением 'refactor: integrate BinanceApiClient into MarketDataService and adapt tests'.