# Memory Bank Guidelines

## Что должен содержать Memory Bank:

### ✅ **ВКЛЮЧАТЬ:**
- **Архитектурные принципы** - Flow Context, Error Architecture
- **Паттерны проектирования** - Graceful Degradation, Singleton patterns
- **Ключевые решения** - Decimal vs Float, JSON vs Text logging
- **Системные концепции** - Multi-timeframe strategy, AI-optimized patterns
- **"Почему" и "Зачем"** - Обоснование архитектурных решений

### ❌ **НЕ ВКЛЮЧАТЬ:**
- **Технические детали реализации** - конкретные методы и классы
- **Конкретный код** - примеры кода должны быть в документации
- **Временные решения** - багфиксы и хотфиксы
- **Низкоуровневые детали** - параметры методов, конфигурации

### 🎯 **Цель Memory Bank:**
Обеспечить понимание **архитектурных концепций** для будущих разработчиков, объяснить **почему система спроектирована именно так**.


## ИСТИНЫ
Читай Memory Bank первым → Останавливайся после задач → Обновляй MB → Коммить → Уточняй вместо додумывания → Контекст активирован

---

---

# System Patterns

## Archive Reference
Complete architectural patterns (1,085 lines) archived in [`memory-bank/archive/systemPatterns.md`](memory-bank/archive/systemPatterns.md).

## Core Architectural Patterns

### **Memory Bank First Pattern**
- **Rule**: All sessions MUST start by reading ALL Memory Bank files
- **Rationale**: Ensures context continuity and prevents workflow violations
- **Implementation**: Automated blocking until Memory Bank status = ACTIVE

### **Financial Safety Pattern**
- **Rule**: Use Decimal arithmetic for all financial calculations
- **Rationale**: Prevent floating-point precision errors in trading operations
- **Implementation**: Strict Decimal validation throughout MarketDataService

### **Fail-Fast Validation Pattern**
- **Rule**: Validate inputs immediately at service boundaries
- **Rationale**: Early detection prevents cascading failures in financial data
- **Implementation**: 6-level validation system in MarketDataSet

### **Graceful Degradation Pattern**
- **Rule**: Non-critical operations have fallback mechanisms
- **Rationale**: System continues operating when possible during errors
- **Implementation**: Enhanced context methods with error recovery

### **Structured Error Handling Pattern**
- **Rule**: All exceptions include rich context and trace IDs
- **Rationale**: Enable efficient debugging of complex trading scenarios
- **Implementation**: Comprehensive exception hierarchy with ErrorContext

## AI Trading System Architecture

### **Core Components (Stable Foundation)**
- **DataPreparer**: Market data ingestion and preparation
- **PortfolioManager**: Position tracking and portfolio operations
- **RiskManager**: Risk assessment and safety mechanisms
- **OrderExecutor**: Trade execution and order management

### **Modular LLM Layer**
- **Abstract Interfaces**: Provider-agnostic decision-making
- **Concrete Implementations**: Claude, GPT, Gemini providers
- **Configuration-Driven**: YAML-based mode switching
- **Combinatorial Support**: Single, ensemble, specialized modes

### **Data Flow Architecture**
```
Scheduler → Trading Script → MarketDataService → LLM Provider → OrderExecutor
```

### **Testing Patterns**
- **Real TDD**: Tests verify actual working code, not mocks
- **Financial Precision**: All money-related operations tested with Decimal
- **Edge Case Coverage**: Network failures, extreme values, malformed data
- **Comprehensive Validation**: Automated + manual testing for production readiness

## Development Patterns

### **Git Workflow Pattern**
- **Rule**: Commit after each completed task
- **Implementation**: Task completion → Memory Bank update → Git commit
- **Rationale**: Preserve incremental progress and enable rollback

### **Documentation-Code Alignment Pattern**
- **Rule**: All documentation must reflect actual implementation
- **Implementation**: Remove fictional operations, use real method names
- **Rationale**: Prevent confusion between planned and implemented features

### **Memory Bank Update Pattern**
- **Rule**: Update Memory Bank files when significant changes occur
- **Implementation**: Automated triggers for decisions, progress, context changes
- **Rationale**: Maintain project context continuity across sessions

### **Quality Gates Pattern**
- **Rule**: Systematic verification before task completion
- **Implementation**: Code quality, testing, documentation checks
- **Rationale**: Ensure production-ready deliverables

## Logging Patterns

### **Structured Logging Pattern**
- **Format**: JSON with trace_id, timestamp, component, operation, context
- **Levels**: CRITICAL (financial) → DEBUG → TRACE (algorithm details)
- **Implementation**: Complete data flow traceability

### **Performance Monitoring Pattern**
- **Metrics**: API latency, calculation times, memory usage
- **Implementation**: Integration points for Prometheus/Grafana
- **Rationale**: Operational visibility for 24/7 trading system

### **Error Context Preservation Pattern**
- **Rule**: All errors include debugging context and system information
- **Implementation**: ErrorContext with trace IDs and stack traces
- **Rationale**: Efficient troubleshooting in production environment

## Token Optimization Patterns

### **Archive Strategy Pattern**
- **Rule**: Move historical content to archive/, keep recent entries active
- **Implementation**: Last 10 entries + archive reference
- **Rationale**: 75% token reduction while preserving 100% context

### **Hierarchical Information Pattern**
- **Active Files**: Current context and immediate decisions
- **Archive Files**: Complete historical information for deep analysis
- **Rationale**: Efficient daily operations with full history available

---

[2025-08-05 12:52:00] - Exception Isolation Pattern for Financial Safety

## Exception Isolation Pattern для защиты торговых операций

### Проблема:
В финансовых системах сбои вспомогательных компонентов (логирование, мониторинг) не должны прерывать критические торговые операции, что может привести к финансовым потерям.

### Решение: Three-Layer Exception Isolation
Многоуровневая изоляция исключений с graceful degradation:

**Layer 1: Primary Protection**
- Try-catch блоки вокруг всех non-critical операций
- Silent exception handling с preserved functionality
- Never propagate exceptions to trading logic

**Layer 2: Fallback Mechanisms**  
- Secondary systems при failure основных компонентов
- Structured fallback logging к alternative destinations
- Maintained operational capability with reduced features

**Layer 3: Complete Failure Tolerance**
- Silent continuation при complete auxiliary system failure
- Core business logic continues uninterrupted
- Status awareness через degraded operation modes

### Архитектурные принципы:
1. **Critical Path Protection** - торговые операции изолированы от auxiliary failures
2. **Graceful Degradation** - система работает с reduced capability но не останавливается
3. **Comprehensive Fallbacks** - multiple backup mechanisms для каждого failure scenario
4. **Silent Resilience** - failures обрабатываются transparently без user impact

### Применение в AI Trading System:
```python
# Logging operations never interrupt trading
try:
    log_trading_operation(data)
except Exception:
    # Silent continuation - trading continues normally
    pass

# Fallback preservation of critical data
try:
    primary_logging(data)
except Exception:
    fallback_logging(data)  # Secondary logging path
    except Exception:
        pass  # Silent continuation if all logging fails
```

### Преимущества:
- **Financial Safety**: критические операции никогда не прерываются
- **Production Resilience**: система продолжает работать при auxiliary failures  
- **Operational Confidence**: predictable behavior при любых failure scenarios
- **Maintenance Freedom**: auxiliary systems можно обновлять без trading downtime

### Архитектурный принцип:
**"Core business logic must never fail due to auxiliary system problems"** - fundamental rule для финансовых систем.

*Optimized 2025-01-04: Reduced from 1,085 lines to core patterns + archive reference*

[2025-01-05 00:54:07] - AI-Optimized Logging Architecture: Flow Context Pattern

## Flow Context Pattern для ИИ-анализа логов

### Проблема:
Традиционное логирование создает разрозненные записи без связи между ними. ИИ не может понять:
- Какие логи относятся к одному запросу
- Последовательность выполнения операций
- Где произошла ошибка в цепочке
- Причинно-следственные связи

### Решение: Flow Context
Система отслеживания "потока выполнения" с тремя ключевыми компонентами:

**1. Flow ID** - уникальный идентификатор запроса
```
flow_btc_20250804215200 = flow + symbol + timestamp
```

**2. Stage Tracking** - отслеживание этапов выполнения
```
initiation → symbol_validation → data_collection → technical_indicators → completion
```

**3. Context Preservation** - сохранение данных между этапами
```json
{
  "flow_id": "flow_btc_20250804215200",
  "stage": "technical_indicators", 
  "previous_stage": "data_collection",
  "stages_completed": ["initiation", "symbol_validation", "data_collection"],
  "context_data": {"symbol": "BTCUSDT", "api_calls": 3}
}
```

### Преимущества для ИИ:

**До Flow Context:**
```
LOG: "Symbol validation passed"     # Какой символ? Какой запрос?
LOG: "API call failed"              # Связано с предыдущим логом?
LOG: "RSI calculation started"      # Откуда RSI если API failed???
```

**После Flow Context:**
```json
{"flow_id": "flow_btc_123", "stage": "validation", "message": "Symbol validation passed"}
{"flow_id": "flow_btc_123", "stage": "api_call", "message": "API call failed"}  
{"flow_id": "flow_btc_123", "stage": "termination", "message": "Flow terminated: API failure"}
```

ИИ теперь понимает:
- ✅ Все логи с `flow_btc_123` = один запрос BTCUSDT
- ✅ Последовательность этапов и место сбоя
- ✅ Причину прерывания потока выполнения

### Техническая реализация:

**Thread-Local Storage** - каждый поток имеет свой Flow Context
**Context Manager** - автоматическое управление жизненным циклом
**Stage Advancement** - программное продвижение по этапам

```python
# Использование Flow Context
with flow_operation("BTCUSDT", "get_market_data"):
    advance_to_stage("symbol_validation")
    # валидация символа
    advance_to_stage("data_collection") 
    # API вызовы
    advance_to_stage("technical_indicators")
    # расчеты
    complete_current_flow()
```

### Интеграция с ИИ-поиском:

**Семантические теги:**
- `flow_start`, `flow_complete`, `flow_termination`
- `stage_advance`, `context_preservation`
- `error_recovery`, `graceful_degradation`

**Структурированные запросы:**
- "Найти все ошибки в flow_btc_* за последний час"
- "Показать stage progression для failed flows" 
- "Сравнить processing_time между successful/failed flows"

### Архитектурный принцип:
**Flow Context = GPS навигатор для ИИ по операционным логам**

Это превращает хаотичный поток логов в структурированную карту выполнения операций, которую ИИ может анализировать, понимать и использовать для диагностики проблем.


[2025-01-05 01:58:18] - Decimal Financial Precision Pattern

## Decimal Financial Precision Pattern для торговых систем

### Проблема:
Стандартный `float` в Python создает ошибки округления, критичные для финансовых расчетов:
```python
float(0.1 + 0.2) = 0.30000000000000004  # НЕДОПУСТИМО в торговле!
```

### Решение: Decimal везде
Использование `Decimal` для всех финансовых операций:
- Цены: `Decimal("42980.25")`
- Объемы: `Decimal("234.56789")`
- Технические индикаторы: RSI, MACD, MA
- Корреляции и расчеты

### Почему критично:
- **Точность расчетов**: RSI должен быть точно между 0-100
- **Валидация данных**: MarketDataSet проверяет границы значений
- **Воспроизводимость**: Одинаковые результаты на разных машинах
- **Соответствие стандартам**: Финансовая индустрия требует точности

### Архитектурный принцип:
**"Никогда не используй float для денег"** - fundamental rule торговых систем.

---

[2025-01-05 01:58:18] - Graceful Degradation Pattern

## Graceful Degradation Pattern для устойчивости системы

### Проблема:
Торговая система не должна останавливаться из-за одной ошибки. Но нельзя игнорировать проблемы.

### Решение: Стратегия fallback значений
При ошибках расчетов использовать безопасные значения:
- **RSI fallback = 50.0** (нейтральный)
- **MACD fallback = "neutral"** (нет сигнала)
- **Correlation fallback = None** (нет данных)
- **Volume profile fallback = "normal"** (базовый уровень)

### Принципы graceful degradation:
1. **Логировать ошибку** - полная диагностическая информация
2. **Использовать fallback** - система продолжает работать
3. **Информировать пользователя** - прозрачность о качестве данных
4. **Не маскировать проблемы** - WARNING/ERROR логи

### Примеры в коде:
```python
try:
    rsi = calculate_rsi(data)
except CalculationError:
    logger.warning("RSI calculation failed, using fallback")
    rsi = Decimal("50.0")  # Neutral fallback
```

### Архитектурный принцип:
**"Fail gracefully, never fail silently"** - система должна деградировать изящно, но не скрывать проблемы.

---

[2025-01-05 01:58:18] - 7-Algorithm Enhanced Context Pattern

## 7-Algorithm Enhanced Context Pattern для оптимизации анализа

### Проблема:
Анализ 180+ свечей полностью неэффективен и создает информационный шум. Нужны **только ключевые моменты**.

### Решение: Smart Candle Selection
7 алгоритмов отбора важных свечей из большого массива:

1. **Recent 5** - последние свечи (актуальность)
2. **Extremes** - максимумы/минимумы (ключевые уровни)
3. **High Volume** - свечи с большим объемом (значимые движения)
4. **Big Moves** - свечи с большими изменениями (волатильность)
5. **Patterns** - свечи с паттернами (технические сигналы)
6. **S/R Tests** - тесты поддержки/сопротивления (важные уровни)
7. **Deduplication** - удаление дубликатов (оптимизация)

### Результат:
180 свечей → 15 ключевых свечей (91% оптимизация)

### Преимущества:
- **Фокус на важном** - только значимые моменты
- **Производительность** - меньше данных для анализа
- **Качество анализа** - убираем "шум", оставляем "сигнал"
- **LLM оптимизация** - укладываемся в токен лимиты

### Архитектурный принцип:
**"Меньше данных, больше смысла"** - интеллектуальная фильтрация вместо brute force анализа.

---

[2025-01-05 01:58:18] - Multi-Timeframe Data Strategy

## Multi-Timeframe Data Strategy для комплексного анализа

### Проблема:
Различные временные рамки дают разную перспективу рынка. Нужна синхронизированная работа с 1d/4h/1h данными.

### Решение: Параллельная агрегация timeframes
Одновременный сбор и анализ:
- **Daily (180 periods)** - долгосрочный тренд, основные уровни
- **4-Hour (84 periods)** - среднесрочная динамика
- **1-Hour (48 periods)** - краткосрочные движения, текущая цена

### Архитектурные особенности:
- **Параллельные API вызовы** - оптимизация времени
- **Синхронизация временных меток** - выравнивание данных
- **Иерархия важности** - daily > 4h > 1h для конфликтов
- **Кросс-timeframe валидация** - проверка консистентности

### Преимущества:
- **Полная картина рынка** - от краткосрочной до долгосрочной
- **Подтверждение сигналов** - согласованность между timeframes
- **Контекстуальный анализ** - понимание позиции в разных масштабах

### Архитектурный принцип:
**"Время - это измерение рынка"** - анализ должен учитывать временную перспективу.

---

[2025-01-05 01:58:18] - AI-Optimized JSON Logging Architecture

## AI-Optimized JSON Logging Architecture для машинного анализа

### Проблема:
Традиционные текстовые логи плохо подходят для ИИ-анализа. ИИ нужны структурированные данные.

### Решение: JSON-First Logging
Каждый лог - это JSON объект с фиксированной схемой:
```json
{
  "timestamp": "2025-01-05T01:58:18.000Z",
  "level": "INFO",
  "service": "MarketDataService", 
  "operation": "get_market_data",
  "message": "Market data request initiated",
  "context": {"symbol": "BTCUSDT"},
  "tags": ["flow_start", "market_data"],
  "trace_id": "trd_001_2025010501581800"
}
```

### Ключевые принципы:
- **Структурированность** - фиксированная схема JSON
- **Семантические теги** - метки для ИИ-поиска
- **Контекстные данные** - полная информация об операции
- **Корреляционные ID** - trace_id, flow_id для связывания событий

### Преимущества для ИИ:
- **Парсинг JSON** - простая обработка структурированных данных
- **Семантический поиск** - поиск по тегам и полям
- **Агрегация данных** - группировка по операциям, символам, времени
- **Паттерн детекция** - выявление закономерностей в поведении

### Архитектурный принцип:
**"Логи в первую очередь для ИИ, во вторую для людей"** - структура важнее читаемости.

## КРИТИЧЕСКОЕ ПРАВИЛО: ZERO-DEFECT INTEGRATION POLICY

**[2025-08-04T22:11:50Z] - КРИТИЧЕСКИ ВАЖНОЕ ПРАВИЛО КАЧЕСТВА КОДА**

### Правило нулевых дефектов перед интеграцией

**ЗАПРЕЩЕНО интегрировать любой модуль пока:**
- ❌ Не все тесты проходят (требуется 100% success rate)
- ❌ Не покрыты все edge cases
- ❌ Есть неопределенности в поведении
- ❌ Производительность не протестирована
- ❌ Thread safety не подтвержден
- ❌ Есть любые известные баги или проблемы

**ОБЯЗАТЕЛЬНЫЕ КРИТЕРИИ для интеграции:**
- ✅ 100% прохождение всех тестов
- ✅ Полное покрытие edge cases
- ✅ Стабильная производительность
- ✅ Thread safety подтвержден
- ✅ Документация актуальна
- ✅ Код-ревью пройдено

**ИСКЛЮЧЕНИЙ НЕТ** - это правило критично для качества всей системы.

---
