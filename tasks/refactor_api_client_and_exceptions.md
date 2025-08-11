# План Задачи: Рефакторинг API Клиента и Системы Ошибок

На основе нашего обсуждения, мы создадим выделенный инфраструктурный слой для взаимодействия с API Binance. Это повысит тестируемость, гибкость и отделит бизнес-логику от деталей взаимодействия с API.

--- ФАЗА 1: Подготовка Инфраструктуры и Файловой Структуры ---
[ ] 1.1: Создать директорию `src/infrastructure`.
[ ] 1.2: Создать пустой файл `src/infrastructure/__init__.py`.
[ ] 1.3: Создать пустой файл `src/infrastructure/exceptions.py`.
[ ] 1.4: Создать пустой файл `src/infrastructure/binance_client.py`.
[ ] 1.5: Обновить Memory Bank (`decisionLog.md`), зафиксировав решение о создании инфраструктурного слоя и его файловой структуры.
[ ] 1.6: Сделать коммит с сообщением 'feat: scaffold infrastructure layer directories and files'.

--- ФАЗА 2: Миграция и Адаптация Системы Ошибок ---
[ ] 2.1: Скопировать содержимое из `src/market_data/exceptions.py` в `src/infrastructure/exceptions.py`.
[ ] 2.2: Переименовать базовый класс `MarketDataError` на `ApiClientError` в `src/infrastructure/exceptions.py`.
[ ] 2.3: Удалить старый файл `src/market_data/exceptions.py`.
[ ] 2.4: Обновить Memory Bank (`progress.md`), отметив завершение миграции системы ошибок.
[ ] 2.5: Сделать коммит с сообщением 'refactor: migrate and adapt exception classes to infrastructure layer'.

--- ФАЗА 3: Реализация Каркаса BinanceApiClient ---
[ ] 3.1: Реализовать в `BinanceApiClient` базовую структуру с `__init__`, принимающим `logger`.
[ ] 3.2: Реализовать в `BinanceApiClient` приватный метод `_handle_response` для централизованной обработки ошибок API.
[ ] 3.3: Создать заглушки (`NotImplementedError`) для приватных методов: `create_order`, `cancel_order`, `get_order_status`.
[ ] 3.4: Обновить Memory Bank (`progress.md`), отметив создание каркаса клиента.
[ ] 3.5: Сделать коммит с сообщением 'feat: implement skeleton for BinanceApiClient'.

--- ФАЗА 4: Реализация Публичных Методов Клиента ---
[ ] 4.1: Реализовать публичный метод `get_server_time` в `BinanceApiClient` для проверки связи.
[ ] 4.2: Реализовать публичный метод `get_klines` в `BinanceApiClient`, включая логирование и проброс `trace_id`.
[ ] 4.3: Обновить Memory Bank (`progress.md`), отметив реализацию публичных методов.
[ ] 4.4: Сделать коммит с сообщением 'feat: implement public methods in BinanceApiClient'.

--- ФАЗА 5: Интеграция и Финальное Тестирование ---
[ ] 5.1: Провести рефакторинг `MarketDataService` для использования нового `BinanceApiClient` через Dependency Injection.
[ ] 5.2: Адаптировать тесты для `MarketDataService` (`tests/unit/test_market_data_service.py`) для работы с моком `BinanceApiClient`.
[ ] 5.3: Запустить все тесты (`tests/run_all_tests.py`) и убедиться, что они проходят успешно.
[ ] 5.4: Обновить Memory Bank (`decisionLog.md`), зафиксировав успешное завершение рефакторинга и тестирования.
[ ] 5.5: Сделать коммит с сообщением 'refactor: integrate BinanceApiClient into MarketDataService and adapt tests'.