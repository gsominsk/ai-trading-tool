# Project Backlog - AI Trading System

This file tracks medium and low priority tasks that should be addressed in future development cycles.

## Medium Priority Tasks - Reliability Improvements

### 4. **Caching Implementation Enhancement**
- **Status**: Future development  
- **Description**: Implement actual caching mechanism for MarketDataService
- **Current State**: Only mock cache tests exist
- **Requirements**:
  - Real cache implementation (Redis/Memory cache)
  - Cache invalidation logic
  - TTL management testing
  - Performance impact measurement
- **Estimated Effort**: 1-2 weeks
- **Dependencies**: Core MarketDataService completion

### 5. **Extreme Market Conditions Testing**
- **Status**: Future development
- **Description**: Handle edge cases in volatile crypto markets
- **Requirements**:
  - Flash crash scenarios (>10% price drops in minutes)
  - Zero volume periods handling
  - Market gaps and missing data recovery
  - Weekend/holiday data gaps
- **Estimated Effort**: 1 week
- **Dependencies**: Real API integration tests completion

### 6. **Enhanced Error Recovery Systems**
- **Status**: Future development
- **Description**: Robust error handling for production environment
- **Requirements**:
  - API timeout scenarios (>30 seconds)
  - Fallback mechanism implementation
  - Graceful degradation validation
  - Circuit breaker pattern for API failures
  - Automatic retry with exponential backoff
- **Estimated Effort**: 2 weeks
- **Dependencies**: Real API integration completion

## Low Priority Tasks - Future Enhancements

### 7. **Additional Edge Cases Coverage**
- Very old timestamps (>1 year)
- Future timestamp validation edge cases
- Currency precision boundary testing
- Multi-timezone handling

### 8. **Performance Optimization**
- Memory usage optimization for large datasets
- Calculation speed improvements
- Parallel processing for multiple symbols

### 9. **Advanced Analytics Features**
- Additional technical indicators (Bollinger Bands, Stochastic)
- Multi-timeframe correlation analysis
- Market sentiment integration

## Backlog Management

**Review Frequency**: Monthly
**Priority Reevaluation**: After each major release
**Dependencies Tracking**: Update when core features change

---
Last Updated: [2025-08-03 21:43:34]

--- Appended on Thu Aug  7 00:03:19 EEST 2025 ---


### Задача: Рефакторинг Тестов с Использованием Централизованной Mock Factory

**ID Задачи:** T-003
**Приоритет:** Высокий (Технический долг)
**Оценка:** 2-3 дня (инкрементально)
**Статус:** К выполнению

**1. Проблема:**
Текущая тестовая база (>25 тестов, >260 использований моков) страдает от хаотичного и неконсистентного создания моков. Логика мокирования API-ответов Binance, логгеров и других зависимостей дублируется в десятках файлов. Это приводит к:
- **Замедлению разработки:** Написание новых тестов требует копирования и адаптации громоздких конструкций.
- **Хрупкости тестов:** Изменение в API требует правок во многих местах, что увеличивает риск ошибок.
- **Плохой читаемости:** Тесты загромождены кодом для настройки моков, что скрывает их основную цель.

**2. Решение:**
Создать централизованную **Mock Factory** (`tests/fixtures/mock_factory.py`), которая станет единым источником для генерации всех тестовых моков и данных. Это позволит инкапсулировать логику создания моков и предоставлять консистентные, готовые к использованию мок-объекты для тестов.

**3. План Реализации:**

**Этап 1: Создание Фабрики (2-3 часа)**
- [ ] Создать файл `tests/fixtures/mock_factory.py`.
- [ ] Реализовать класс `MockFactory`.
- [ ] Добавить статические методы для генерации наиболее частых моков:
    - `create_successful_klines_response(data, symbol)`
    - `create_rate_limit_response()`
    - `create_api_error_response(status_code)`
    - `create_insufficient_data_response()`
    - `generate_realistic_klines(count, base_price)`

**Этап 2: Инкрементальный Рефакторинг Тестов (2-3 дня)**
- [ ] **Цель:** Заменить все инлайновые создания `Mock` и `MagicMock` на вызовы `MockFactory`.
- [ ] **Приоритетные файлы для рефакторинга:**
    - `tests/integration/error_architecture/test_error_integration.py`
    - `tests/unit/test_market_data_service.py`
    - `tests/integration/market_data/test_market_data_integration.py`
    - `tests/unit/market_data/test_market_data_api.py`
- [ ] Провести рефакторинг остальных тестов по мере возможности.

**4. Критерии Успеха:**
- Создан и используется `MockFactory`.
- >90% созданий моков в тестах заменены на вызовы фабрики.
- Тестовые файлы стали короче и чище.
- Запуск всех тестов (`pytest`) проходит успешно после рефакторинга.


--- Appended on Thu Aug  7 00:03:26 EEST 2025 ---


### Задача: Рефакторинг Тестов с Использованием Централизованной Mock Factory

**ID Задачи:** T-003
**Приоритет:** Высокий (Технический долг)
**Оценка:** 2-3 дня (инкрементально)
**Статус:** К выполнению

**1. Проблема:**
Текущая тестовая база (>25 тестов, >260 использований моков) страдает от хаотичного и неконсистентного создания моков. Логика мокирования API-ответов Binance, логгеров и других зависимостей дублируется в десятках файлов. Это приводит к:
- **Замедлению разработки:** Написание новых тестов требует копирования и адаптации громоздких конструкций.
- **Хрупкости тестов:** Изменение в API требует правок во многих местах, что увеличивает риск ошибок.
- **Плохой читаемости:** Тесты загромождены кодом для настройки моков, что скрывает их основную цель.

**2. Решение:**
Создать централизованную **Mock Factory** (`tests/fixtures/mock_factory.py`), которая станет единым источником для генерации всех тестовых моков и данных. Это позволит инкапсулировать логику создания моков и предоставлять консистентные, готовые к использованию мок-объекты для тестов.

**3. План Реализации:**

**Этап 1: Создание Фабрики (2-3 часа)**
- [ ] Создать файл `tests/fixtures/mock_factory.py`.
- [ ] Реализовать класс `MockFactory`.
- [ ] Добавить статические методы для генерации наиболее частых моков:
    - `create_successful_klines_response(data, symbol)`
    - `create_rate_limit_response()`
    - `create_api_error_response(status_code)`
    - `create_insufficient_data_response()`
    - `generate_realistic_klines(count, base_price)`

**Этап 2: Инкрементальный Рефакторинг Тестов (2-3 дня)**
- [ ] **Цель:** Заменить все инлайновые создания `Mock` и `MagicMock` на вызовы `MockFactory`.
- [ ] **Приоритетные файлы для рефакторинга:**
    - `tests/integration/error_architecture/test_error_integration.py`
    - `tests/unit/test_market_data_service.py`
    - `tests/integration/market_data/test_market_data_integration.py`
    - `tests/unit/market_data/test_market_data_api.py`
- [ ] Провести рефакторинг остальных тестов по мере возможности.

**4. Критерии Успеха:**
- Создан и используется `MockFactory`.
- >90% созданий моков в тестах заменены на вызовы фабрики.
- Тестовые файлы стали короче и чище.
- Запуск всех тестов (`pytest`) проходит успешно после рефакторинга.
