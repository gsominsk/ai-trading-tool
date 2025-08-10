# План Работ: Фаза 7 - Миграция на SQLite

**Цель:** Заменить текущую реализацию `OmsRepository`, основанную на CSV, на новую, использующую базу данных SQLite для повышения надежности, производительности и гибкости.

---
### --- ФАЗА 7: Миграция OmsRepository на SQLite ---

- [x] 7.1: Создать и заполнить файл `docs/architecture/database_schema.md`, описав схему таблицы `orders`.
- [x] 7.2: Реализовать в `src/trading/oms_repository.py` полную поддержку SQLite, включая методы `__init__`, `save` и `load`.
- [x] 7.3: Создать новый файл юнит-тестов `tests/unit/trading/test_oms_repository_sqlite.py` для проверки новой реализации.
- [x] 7.4: Добавить `tests/unit/trading/test_oms_repository_sqlite.py` в список `unit` тестов в `tests/run_all_tests.py`.
- [x] 7.5: Запустить полный набор тестов (`unit` и `integration`) для проверки отсутствия регрессий.
- [x] 7.6: Удалить старый файл состояния `data/oms_state.csv`.
- [x] 7.7: Удалить старый файл тестов `tests/unit/trading/test_oms_repository.py`, который проверял работу с CSV.
- [x] 7.8: Обновить `decisionLog.md`, зафиксировав решение о переходе на SQLite и завершение миграции.
- [ ] 7.9: Сделать коммит с сообщением `feat(oms): Migrate OmsRepository from CSV to SQLite (Phase 7)`.