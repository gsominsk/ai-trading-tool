# System Patterns

## Archive Reference
Complete architectural patterns (599 lines) archived in [`memory-bank/archive/systemPatterns.md`](memory-bank/archive/systemPatterns.md).

## Memory Bank Guidelines

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

**ИСТИНЫ:** Читай Memory Bank первым → Останавливайся после задач → Обновляй MB → Коммить → Уточняй вместо додумывания → Контекст активирован

---

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

### **ZERO-DEFECT INTEGRATION POLICY**
**ЗАПРЕЩЕНО интегрировать любой модуль пока:**
- ❌ Не все тесты проходят (требуется 100% success rate)
- ❌ Не покрыты все edge cases
- ❌ Есть неопределенности в поведении
- ❌ Производительность не протестирована
- ❌ Thread safety не подтвержден
- ❌ Есть любые известные баги или проблемы

**ОБЯЗАТЕЛЬНЫЕ КРИТЕРИИ:** 100% прохождение тестов, полное покрытие edge cases, стабильная производительность, thread safety, документация, код-ревью.

## Logging Patterns

### **Unified & Hierarchical Tracing Pattern**
- **Problem**: A simple list of log events is not enough. We need to understand both the entire lifecycle of a request and the specific parent-child relationships between operations within that request.
- **Solution**: A unified tracing model using `trace_id` and `parent_trace_id`.
    - **`trace_id` (Unified Lifecycle)**: A single, unique `trace_id` is generated for a top-level operation (e.g., `get_market_data`). This same `trace_id` is inherited by *all* subsequent sub-operations (API calls, calculations, etc.). This groups all related events into a single, traceable flow.
    - **`parent_trace_id` (Hierarchical Relationship)**: To create a clear execution tree, a sub-operation's log entry includes a `parent_trace_id` field, which contains the `trace_id` of the operation that initiated it.
- **Architectural Principle**: "Every log entry must tell you what it is, what flow it belongs to, and what caused it."
- **Result**: This creates a powerful, tree-like structure for logs that allows for easy debugging, performance analysis of entire operational flows, and advanced AI-based analysis of system behavior.

### **Exception Isolation Pattern для защиты торговых операций**
**Проблема**: Сбои вспомогательных компонентов не должны прерывать критические торговые операции.
**Решение**: Three-Layer Exception Isolation:
- **Layer 1**: Try-catch блоки, silent exception handling
- **Layer 2**: Fallback mechanisms при failure основных компонентов
- **Layer 3**: Complete failure tolerance с silent continuation

**Архитектурный принцип**: "Core business logic must never fail due to auxiliary system problems"

### **Trading Halt on Logging Failure Pattern**
**Проблема**: Торговля без логирования = "слепые" операции с неконтролируемыми рисками.
**Решение**: Simple "No Logs = No Trading" Rule - любая ошибка логирования = немедленная остановка торговли.
**Архитектурный принцип**: "No Logs = No Trading" - простое правило для максимальной безопасности.

### **Performance Monitoring Pattern**
- **Metrics**: API latency, calculation times, memory usage
- **Implementation**: Integration points for Prometheus/Grafana
- **Rationale**: Operational visibility for 24/7 trading system

### **Error Context Preservation Pattern**
- **Rule**: All errors include debugging context and system information
- **Implementation**: ErrorContext with trace IDs and stack traces
- **Rationale**: Efficient troubleshooting in production environment

## Financial System Patterns

### **Decimal Financial Precision Pattern**
**Проблема**: Стандартный `float` создает ошибки округления, критичные для финансовых расчетов.
**Решение**: Использование `Decimal` для всех финансовых операций:
- Цены, объемы, технические индикаторы, корреляции и расчеты
**Архитектурный принцип**: "Никогда не используй float для денег"

### **Multi-Timeframe Data Strategy**
**Решение**: Параллельная агрегация timeframes:
- **Daily (180 periods)** - долгосрочный тренд, основные уровни
- **4-Hour (84 periods)** - среднесрочная динамика
- **1-Hour (48 periods)** - краткосрочные движения, текущая цена
**Архитектурный принцип**: "Время - это измерение рынка"

### **7-Algorithm Enhanced Context Pattern**
**Проблема**: Анализ 180+ свечей неэффективен и создает информационный шум.
**Решение**: Smart Candle Selection через 7 алгоритмов:
Recent 5, Extremes, High Volume, Big Moves, Patterns, S/R Tests, Deduplication
**Результат**: 180 свечей → 15 ключевых свечей (91% оптимизация)
**Архитектурный принцип**: "Меньше данных, больше смысла"

### **AI-Optimized JSON Logging Architecture**
**Проблема**: Традиционные текстовые логи плохо подходят для ИИ-анализа.
**Решение**: JSON-First Logging с фиксированной схемой, семантическими тегами, контекстными данными.
**Архитектурный принцип**: "Логи в первую очередь для ИИ, во вторую для людей"

## Testing Patterns

### **Modular Performance Testing Pattern**
**Проблема**: Отдельные performance директории становятся "сиротами".
**Решение**: Embedded Performance Testing - performance тесты живут рядом с функциональными тестами.
**Маркировка**: `@pytest.mark.performance` для selective execution
**Архитектурный принцип**: "Performance tests should live where they belong, not where it's convenient"

### **Archive & Extract Test Migration Pattern**
**Проблема**: Реорганизация тестов рискует потерей working test logic.
**Решение**: Archive-First Strategy:
1. Полное архивирование оригинальных тестов
2. Извлечение реальной логики из архивных тестов
3. Консолидация в organized structure
4. Backward compatibility verification
**Архитектурный принцип**: "Preserve what works, organize what's scattered"

## Token Optimization Patterns
### **Repository Pattern for Persistence**
- **Problem**: Business logic components (like an `OrderManagementSystem`) should not be responsible for how their state is saved or loaded. Tightly coupling business logic with persistence logic (e.g., writing to a JSON file directly within a business class) violates the Single Responsibility Principle, reduces testability, and makes future changes (like moving to a database) difficult.
- **Solution**: Abstract the persistence logic into a separate `Repository` class.
    - The `Repository`'s only job is to handle data storage and retrieval (e.g., `load()` and `save()` methods).
    - The business logic class receives the repository instance via **Dependency Injection**, usually in its constructor.
    - The business class calls the repository's methods to manage its state, without knowing the underlying storage mechanism.
- **Architectural Principle**: "Separate business logic from data access logic."
- **Result**: A clean, decoupled architecture that is more modular, flexible, and easier to test. The storage mechanism can be changed without altering the business logic simply by providing a different repository implementation.


### **Archive Strategy Pattern**
- **Rule**: Move historical content to archive/, keep recent entries active
- **Implementation**: Last 10 entries + archive reference
- **Rationale**: 75% token reduction while preserving 100% context

### **Hierarchical Information Pattern**
- **Active Files**: Current context and immediate decisions
- **Archive Files**: Complete historical information for deep analysis
- **Rationale**: Efficient daily operations with full history available

---

## Summary Statistics
- **Total Patterns**: 20+ core architectural patterns
- **Archive Size**: 599 lines of complete pattern documentation
- **Current Active**: Essential patterns optimized for daily operations
- **Complete History**: Available in [`memory-bank/archive/systemPatterns.md`](memory-bank/archive/systemPatterns.md)

---

### **Complete Operation Coverage Demonstration Pattern**
- **Rule**: Demo scripts must showcase ALL service operations, not just basic examples
- **Rationale**: Comprehensive demonstrations provide complete operational visibility for production deployment
- **Implementation**: Systematic mapping of all service methods with categorized demo modules

### **Dual Trace_ID Hierarchy Pattern**
- **Rule**: Separate trace_id namespaces for business operations vs raw data capture
- **Rationale**: Clean separation enables AI analysis while maintaining operational traceability
- **Implementation**: `flow_xxx` for main operations, `trd_001_xxx` for raw data logging

### **AI-Optimized Demonstration Logging Pattern**
- **Rule**: Demo logs must be structured for automated AI analysis, not just human readability
- **Rationale**: Demonstration infrastructure should validate real-world AI analysis capabilities
- **Implementation**: Complete JSON structure with semantic tags, lifecycle tracking, and multi-symbol validation

---

[2025-08-06 02:57:00] - Added Comprehensive MarketDataService Logging Demonstration patterns following successful Phase 6 completion

*Optimized 2025-08-05: Reduced from 599 lines to essential patterns + archive reference*

---
### [2025-08-09 19:21:54] - Preferred Diagramming Format (UPDATED)

**Pattern:** All new architectural or explanatory diagrams should be created using **ASCII art** inside a Markdown (`.md`) file.

**Rationale:** Previous attempts to use PlantUML (`.puml`) have consistently failed due to syntax errors and tool incompatibility. ASCII art is a simple, reliable, and tool-independent format that guarantees readability and avoids technical issues.

**Implementation:** When a request to "draw" or "visualize" a concept is made, create a new `.md` file and draw the diagram using ASCII characters.
