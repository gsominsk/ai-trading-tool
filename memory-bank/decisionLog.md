# Decision Log

## Archive Reference
Complete decision history with full details (approx. 522 lines before this optimization) is archived in [`memory-bank/archive/decisionLog.md`](memory-bank/archive/decisionLog.md). The full, unabridged history is preserved there.

## Recent Decisions (Last 10 Entries)
### [2025-08-11 22:24:00] - **Decision: Remove Obsolete Test from Test Suite**
**Problem**: The test suite contained a skipped test, `test_logging_integration_handles_logger_failure`, in `tests/unit/logging/test_logging_components.py`. This test was marked as obsolete because the underlying logic it was designed to validate (logger initialization within a service) was removed during a previous architectural refactoring that introduced dependency injection.
**Solution**: The obsolete test was permanently deleted from the test file.
**Rationale**: Leaving skipped, obsolete tests in the codebase creates "noise" and can lead to confusion for developers. It is better to remove them entirely to maintain a clean and relevant test suite. The functionality it once tested is now covered by other, more appropriate exception handling tests.
**Result**: The test suite is cleaner and more maintainable. The removal was validated by a full test run, which confirmed that no regressions were introduced.
### [2025-08-11 22:27:00] - **Decision: Modernize Datetime Calls to Eliminate Deprecation Warnings**
**Problem**: The test suite was generating multiple `DeprecationWarning`s because `tests/unit/trading/test_oms_repository_sqlite.py` used the `datetime.utcnow()` method, which is deprecated. These warnings cluttered the test output and signaled the use of outdated practices.
**Solution**: All instances of `datetime.utcnow()` were replaced with the modern, timezone-aware equivalent: `datetime.now(timezone.utc)`. The necessary `timezone` object was imported from the `datetime` module.
**Rationale**: Using up-to-date, non-deprecated methods is crucial for long-term code health and maintainability. This change ensures the codebase is aligned with current Python best practices and will be compatible with future versions.
**Result**: The test suite now runs cleanly without any `DeprecationWarning`s, improving readability and confidence in the test results.
### [2025-08-11 22:08:00] - **Architectural Decision: Refactor `BinanceApiClient` to Use `StructuredLogger`**
**Problem**: The `BinanceApiClient` was using Python's standard `logging.Logger`. This resulted in logs that lacked critical context, appearing with `"service": "default_service"` and `"operation": "unknown"`. This broke the unified logging schema and made it difficult to trace the origin and purpose of API-related log entries.
**Solution**: The `BinanceApiClient` will be refactored to accept and use the project's custom `StructuredLogger`.
1.  The `__init__` method will be updated to require a `StructuredLogger` instance.
2.  All logging calls (`.info()`, `.error()`, etc.) will be replaced with the structured equivalents, passing key information like `operation`, `context`, and `trace_id` as explicit parameters.
**Result**: This change will ensure that all logs originating from the `BinanceApiClient` are fully structured and conform to the project's logging standards. It will provide complete context, including the service name and operation, making the entire system's behavior more transparent and easier to debug.

### [2025-08-11 14:23:00] - **Architectural Decision: Complete Test Suite Refactoring for `MarketDataService`**
**Problem**: A major architectural refactoring to introduce a `BinanceApiClient` and a dedicated infrastructure layer had broken the entire unit test suite for `MarketDataService`. The tests were using an outdated strategy of mocking the low-level `requests` library, which was no longer directly used by the service. This resulted in a cascade of `DataInsufficientError` and `AttributeError` failures, rendering the tests useless.
**Solution**: A systematic, multi-wave refactoring of all affected unit tests (`test_market_data_api.py`, `test_market_data_core.py`, `test_market_data_edge_cases.py`) was executed.
1.  **Standardized Mocking**: All tests were updated to mock the `api_client.get_klines` method, which is the correct point of interaction after the refactoring.
2.  **Correct Exception Handling**: Tests were updated to assert for the correct, high-level exceptions (`ProcessingError`, `NetworkError`, etc.) that are now raised by the service, instead of low-level `requests` exceptions.
3.  **Removal of Private Method Tests**: Tests that directly targeted private methods were removed in favor of testing the same logic through the public `get_market_data` interface, making the tests more robust and less brittle.
**Result**: The entire unit test suite for `MarketDataService` is now fully aligned with the new, decoupled architecture. The tests are more reliable, easier to maintain, and correctly validate the service's contract. All 239 tests in the project now pass, confirming the stability of the system after the major architectural overhaul.

### [2025-08-11 01:29:00] - **Test Refactoring Strategy: Adapt Tests to Mock `BinanceApiClient`**
**Problem**: A significant number of tests were failing with `DataInsufficientError`. The root cause was identified as an outdated testing strategy. Tests were written to mock the low-level `requests.get` library, but the `MarketDataService` was refactored to use a high-level, injected `BinanceApiClient`. The existing mocks were therefore completely ignored, causing the service to receive no data.
**Solution**: A systematic refactoring of all affected test files will be performed.
1.  **Remove `patch('requests.get')`**: All tests that use this pattern will be updated.
2.  **Configure Mock API Client**: The tests will now correctly configure the `side_effect` or `return_value` of the `mock_api_client.get_klines` method, which is injected into the service during test setup.
**Result**: This aligns the entire test suite with the current dependency injection architecture. It makes the tests more robust, easier to understand, and correctly isolates the `MarketDataService` from the underlying transport layer, which is the purpose of the `BinanceApiClient`.
### [2025-08-11 01:16:00] - **Architectural Correction: Revert Graceful Degradation in Favor of Fail-Fast**
**Problem**: During test fixing, I incorrectly implemented a "graceful degradation" feature in `MarketDataService`'s `_calculate_btc_correlation_with_fallback` method. This feature suppressed `DataInsufficientError` exceptions, which contradicted the established "fail-fast" design principle and broke existing tests that correctly expected an exception to be raised.
**Solution**: Based on direct user feedback, the incorrect implementation will be reverted.
1.  The `_calculate_btc_correlation_with_fallback` method will be removed.
2.  The `get_market_data` method will call `_calculate_btc_correlation` directly.
3.  The corresponding unit test (`test_btc_correlation_processing_error`) will be restored to assert that a `DataInsufficientError` is raised.
**Result**: The system's error handling strategy is restored to the intended "fail-fast" behavior. This ensures that data processing does not silently continue with incomplete or missing data, which is critical for financial safety. The codebase is now correctly aligned with the test suite's expectations.

### [2025-08-10 23:44:00] - **Architectural Decision: Decouple API Logic into a Dedicated Infrastructure Layer**
**Problem**: The current implementation has API interaction logic (URLs, request/response handling) tightly coupled within the `MarketDataService`. This violates the Single Responsibility Principle, makes the service difficult to test without real network calls, and hinders flexibility for supporting other exchanges or data sources in the future.
**Solution**: A dedicated infrastructure layer will be created to abstract all external API interactions.
1.  **New Directory**: A new directory, `src/infrastructure`, will be created to house all external service clients.
2.  **`BinanceApiClient`**: A new `BinanceApiClient` class will be created in this layer. Its sole responsibility will be to handle the specifics of communicating with the Binance API (endpoints, error codes, rate limits).
3.  **Shared Exceptions**: A new, more generic exception hierarchy will be created in `src/infrastructure/exceptions.py`, evolving from the existing `market_data` exceptions. This allows any client in the infrastructure layer to use a common set of errors (`ApiClientError`, `RateLimitError`, etc.).
4.  **Dependency Injection**: The `MarketDataService` will be refactored to receive the `BinanceApiClient` via dependency injection, making it completely unaware of the underlying API details.
**Result**: This architectural refactoring will lead to a cleaner, more modular, and highly testable system. It promotes separation of concerns, simplifies the `MarketDataService`, and establishes a clear pattern for adding new external data sources in the future.

### [2025-08-09 23:22:00] - **Architectural Decision: Final Documentation and Diagram Enhancement**
**Problem**: The architectural diagram, while functionally correct, lacked explicit textual descriptions of each component's role, leading to potential ambiguity (e.g., the exact responsibility of the OMS vs. the Exchange Interface).
**Solution**: The main architectural document, `docs/architecture/project_structure.txt`, was significantly enhanced.
1.  **Detailed Component Descriptions**: A new section, "Component Responsibilities," was added to explicitly define the role of each major part of the system, from the `Scheduler` to the `Concrete Exchange Wrapper`.
2.  **Enhanced Block Diagram**: The system diagram was updated to be more explicit. It now visually distinguishes between component types (e.g., "Orchestrator", "State Logic", "Contract", "Worker") and clearly shows the full, decoupled data flow from the `OMS` to the `ExchangeInterface` and finally to the `Concrete Exchange Wrapper`, which makes the actual API call.
**Result**: The project now has a comprehensive, unambiguous, and self-contained architectural document that serves as a clear blueprint for development and onboarding, fully clarifying the separation of concerns within the system.

### [2025-08-09 23:15:00] - **Architectural Decision: Persistence Simplification & Finalization**
**Problem**: The existing architectural diagram and persistence strategy were overly complex and contained contradictions. The `TradeLogRepository` duplicated the function of the main logging system, and the `OMSRepository`'s data format (JSON) was not aligned with the final requirements.
**Solution**: A definitive simplification of the persistence layer was implemented, based on direct user feedback.
1.  **`TradeLogRepository` Abolished**: The concept of a separate repository for historical trade logs has been completely removed. The primary, hierarchical logging system is now the sole source of truth for the historical audit trail of all trading cycle events. This eliminates redundancy and simplifies the architecture, aligning with the decision made on [2025-08-06 18:41:00].
2.  **`OMSRepository` Format Changed to CSV**: The `OMSRepository`, which is responsible for managing the **current state** of orders, will now use a CSV file (`oms_state.csv`) as its persistence mechanism. This decision supersedes the previous decision ([2025-08-06 23:16:00]) to use JSON. The repository will overwrite the CSV file to reflect the latest state.
**Result**: The architecture is now cleaner, more logical, and free of contradictions. The roles of each component are clearly defined: `OMSRepository` handles the current state, and the global `Logging System` handles the historical record. The master architectural document, `docs/architecture/project_structure.txt`, has been updated to reflect this final design.

[2025-08-06 23:16:41] - Принято решение реализовать персистентность OMS через паттерн "Репозиторий". Создается отдельный класс `OrderRepository` для инкапсуляции логики сохранения/загрузки состояния ордеров. Это разделяет ответственности и повышает гибкость системы по сравнению с хранением логики персистентности внутри `OMS`.

### [2025-08-06 23:16:00] - **Architectural Decision: OMS Persistence via Repository Pattern**
**Problem**: The `OrderManagementSystem (OMS)` was stateless, losing all order information between script runs. This made it impossible to test the full order lifecycle (e.g., from `PENDING` to `FILLED`) and rendered manual testing ineffective. A simple file-based persistence within the `OMS` itself would violate the Single Responsibility Principle and tightly couple the `OMS` to a specific storage mechanism (e.g., JSON).
**Solution**: The Repository Pattern was implemented to decouple the persistence logic from the core business logic of the `OMS`.
1.  **`OrderRepository` Created**: A new class, `OrderRepository`, was created in `src/trading/repository.py` with the sole responsibility of handling the serialization (`save`) and deserialization (`load`) of the OMS state to and from a JSON file.
2.  **Dependency Injection**: The `OMS` was refactored to accept an `OrderRepository` instance via its constructor. It no longer has any knowledge of how or where the data is stored.
3.  **State Synchronization**: The `OMS` now calls `repository.load()` on initialization to restore its state and `repository.save()` after any state-mutating operation (e.g., `place_order`, `cancel_order`).
**Result**: This architecture provides a clean separation of concerns, making the `OMS` more modular, easier to test (by injecting a mock repository), and more flexible for future changes (e.g., switching to a database by simply creating a new repository implementation). It solves the state persistence problem without polluting the core business logic.

### [2025-08-06 18:41:00] - **Architectural Decision: Trading Engine Simplification**
**Problem**: The initial 8-module design for the Trading Engine was deemed too complex for the initial implementation ("слишком много модулей"). Key areas of concern were the necessity of a separate `AI_Strategist` and a real-time `PositionMonitor`.
**Solution**: The architecture was refactored and simplified into 4 core modules by merging responsibilities.
1.  **`TradingCycle`** now absorbs the logic of `AI_Strategist` (prompt engineering) and `TradeLogger` (CSV operations).
2.  The real-time `PositionMonitor` was replaced by a synchronous check at the beginning of each cycle, where `TradingCycle` queries the `OMS` for the actual status of any pending orders. This was deemed an acceptable trade-off as the user confirmed that a 15-minute reaction delay is not critical for the chosen trading strategy.
**Result**: A significantly simpler 4-module architecture (`Scheduler`, `MarketDataService`, `OMS`, `TradingCycle`) that is easier to implement and maintain for the MVP, while still addressing the core problem of state synchronization. This decision accelerates development by reducing initial complexity.

[2025-08-06 16:56:00] - Fixed a logging bug in `_analyze_volume_profile` where the `symbol` was not being logged. The method signature was updated to accept the symbol, and all related calls (including in unit tests) were modified accordingly to ensure log consistency.

[2025-08-06 16:56:00] - Refactored `examples/phase6_final_demo.py` to eliminate redundant API calls by fetching market data once and reusing the `MarketDataSet` object. This resolves a critical performance inefficiency.

### [2025-08-06 14:58:00] - **Architectural Decision: Defensive Data Validation in `get_market_data`**
**Problem**: The integration test `test_api_call_efficiency.py` revealed a critical production vulnerability. When the underlying `_get_klines` method returns an empty DataFrame (e.g., due to an API issue or for a new, low-liquidity symbol), the `get_market_data` method proceeds with calculations, attempting to call `.min()` on an empty Series. This raises a `decimal.InvalidOperation` error because `min()` on an empty sequence returns `NaN`, which cannot be converted to a `Decimal`.
**Solution**: Implement a defensive check at the beginning of the `get_market_data` method. Before any calculations are performed, the service will now validate that the `daily_data` and `h1_data` DataFrames are not empty. If either is empty, a `DataInsufficientError` will be raised immediately.
**Result**: This change prevents the `decimal.InvalidOperation` crash, making the service more robust. It provides a clear, specific error (`DataInsufficientError`) when core data is missing, improving diagnostics and preventing the system from operating on incomplete or invalid data. This ensures that all downstream calculations are only performed on valid, non-empty datasets.

### [2025-08-06 14:46:00] - **Architectural Decision: Hierarchical Tracing Implementation**
**Problem**: The existing logging system treated every operation as a flat, independent event. This made it impossible to understand the causal relationships between a primary operation (e.g., `get_market_data`) and the multiple sub-operations it triggers (e.g., `_get_klines`, `_calculate_rsi`). The lack of a parent-child link obscured the execution flow, making debugging and performance analysis difficult.
**Solution**: A hierarchical tracing pattern was implemented by introducing a `parent_trace_id` field into the logging schema.
1.  **Trace Inheritance**: Child operations now inherit the `trace_id` from their parent.
2.  **Parent ID**: The `parent_trace_id` field explicitly links a sub-operation to its initiator.
3.  **Logging System Update**: The `StructuredLogger` and `AIOptimizedJSONFormatter` were updated to include and correctly process the `parent_trace_id`.
4.  **Integration Test**: A dedicated integration test (`test_hierarchical_tracing.py`) was created to validate that parent-child relationships are correctly established and logged. The test captures `sys.stderr` to reliably verify the final log output.
**Result**: The system now produces logs that form a clear execution tree. This provides full observability into complex operations, simplifies debugging by showing the exact sequence of events, and enables more accurate performance analysis by allowing the aggregation of timings for a parent and all its children.

### [2025-08-06 14:23:00] - **Refactoring `get_enhanced_context` for API Efficiency**
**Problem**: The `get_enhanced_context` method was inefficiently making a second, redundant API call to fetch market data that had already been retrieved by the calling context. This increased latency and API usage costs.
**Solution**: The method signature was changed from `get_enhanced_context(self, symbol: str)` to `get_enhanced_context(self, market_data: MarketDataSet)`. This enforces a cleaner data flow where the caller must first fetch the data via `get_market_data()` and then pass the resulting `MarketDataSet` object for enhancement.
**Result**: Complete elimination of redundant API calls, reduced latency, lower API costs, and a more logical and explicit data flow within the service. All call sites (tests, examples, manual scripts) were updated to conform to the new, more efficient pattern.

[2025-08-06 14:12:41] - Initialized `_operation_metrics` and `_degradation_history` attributes in the `MarketDataService.__init__` method. This prevents potential `AttributeError` exceptions when methods like `_log_graceful_degradation` are called on a fresh service instance before any metrics have been recorded. A unit test was added to verify the fix.

[2025-08-06 14:04:06] - Fix `NameError` in `get_enhanced_context` exception handling. Unified access to `trace_id` by consistently using `self._current_trace_id`. This prevents crashes when unexpected errors occur, ensuring the `trace_id` is always available for logging. A dedicated unit test was added to prevent regression.

## Historical Decision Index (Chronological)
- [2025-08-06 02:57:00] - Comprehensive MarketDataService Logging Demonstration
- [2025-08-05 23:39:00] - PHASE 5 ARCHITECTURAL DECISIONS: Data Tracing Issues Resolution
- [2025-08-05 23:31:00] - PHASE 6 COMPLETION: COMPREHENSIVE LOGGING ENHANCEMENT ARCHITECTURE
- [2025-08-05 22:59:18] - TRACE_ID UNIFICATION ARCHITECTURE DECISION
- [2025-08-05 22:21:15] - FINAL LOGGING SIMPLIFICATION PROJECT COMPLETION
- [2025-08-05 22:12:40] - PHASE 6 TRACE_ID UNIQUENESS ARCHITECTURAL DECISION
- [2025-08-05 21:26:30] - LOGGING SIMPLIFICATION ARCHITECTURAL DECISION COMPLETED
- [2025-08-05 21:09:29] - TEST INFRASTRUCTURE DECISION: Integration of Phase 5 validation tests
- [2025-08-05 20:32:00] - Стратегия упрощения системы логирования MarketDataService
- [2025-08-05 18:52:00] - Performance Tests Integration Strategy
- [2025-08-05 18:10:41] - ФАЗА 4 Test Reorganization Methodology Validation
- [2025-08-05 17:54:58] - Уточнение подхода к реорганизации тестов
- [2025-08-05 16:56:07] - Критические исправления безопасности логирования
- [2025-08-05 13:27:00] - Замена TradingGuard на "No Logs = No Trading"
- [2025-08-05 12:52:00] - Exception Handling in Logging System Complete
- [2025-08-05 03:43:23] - MarketDataService Logging Integration Complete
- [2025-08-05 03:23:11] - Phase 9 Critical Architecture Decisions
- [2025-08-05 02:44:16] - Comprehensive Logging System Test Coverage
- [2025-08-05 00:28:44] - Complete Test Suite Validation Achievement
- [2025-08-04 23:21:15] - Critical Timezone Standardization
- [2025-08-04 23:00:00] - Memory Bank Optimization Process Documentation
- [2025-08-04 20:54:00] - Error Architecture Phase 4 - Migration Complete
- [2025-08-04 03:09:01] - Removal of Obsolete roocode-modules Directory
- [2025-08-04 03:04:58] - Memory Bank File Consolidation
- [2025-08-04 00:46:00] - Cyclic Reinforcement + Priority Coding System
- [2025-08-03 23:47:00] - RooCode .roomodes Configuration Refinement
- [2025-08-03 23:22:00] - Corrected .roomodes Configuration
- [2025-08-03 21:38:52] - Complete Logging Architecture Ready
- [2025-08-03 21:31:40] - Restored Logging Chain Integrity
- [2025-08-03 21:26:02] - Raw API Data Logging Enhancement
- [2025-08-03 21:21:41] - Complete Logging Architecture Rewrite
- [2025-08-03 20:47:30] - Complete RooCode Module Suite Creation
- [2025-08-03 18:46:46] - Workflow Automation System Design
- [2025-08-03 18:16:45] - Logging Architecture Field Removal
- [2025-08-03 17:52:00] - Logging Architecture and Workflow Clarification
- [2025-08-03 15:38:30] - Network Failures and Extreme Edge Cases Testing
- [2025-08-03 04:26:00] - Comprehensive Testing Strategy Architecture
- [2025-08-02 23:51:00] - Enhanced Candlestick Analysis Implementation
- [2025-08-02 23:03:00] - MVP LLM Model Selection: Claude Sonnet 4
- [2025-08-02 22:40:47] - Финальное решение по технологическому стеку
- [2025-08-02 22:27:11] - Детальный анализ ChatGPT-Micro-Cap-Experiment
- [2025-08-02 18:59:53] - Уточнение роли архитектуры
- [2025-08-02 18:54:48] - Фундаментальная архитектура системы
- [2025-08-01 22:24:54] - MVP Component Reuse Strategy
- [2025-08-01 22:18:50] - Repository Analysis and Adaptation Strategy
- [2025-01-05 22:31:12] - Enhanced DEBUG Logging with Raw API Data Capture
- [2025-01-04 03:29:00] - XML Rules → Text-based Enforcement
- [2025-01-03 12:53:00] - MarketDataService Testing Critical Fix

## Summary Statistics
- **Total Decisions**: ~58 entries
- **Archive Size**: ~522 lines of complete history (before this optimization)
- **Current Active**: Last 10 entries
- **Complete History**: Available in [`memory-bank/archive/decisionLog.md`](memory-bank/archive/decisionLog.md)

---
*Optimized on 2025-08-06: Reduced from 522 lines to an optimized version with a historical index. Full content is preserved in the archive.*

[2025-08-09 22:14:57] - [ARCHITECTURAL BLUEPRINT ESTABLISHED] - Decided to move from a simple component list to a full hierarchical architecture plan. A new file, `docs/architecture/project_structure.txt`, has been created to serve as the blueprint for all future development. It defines a clear, modular, and scalable structure, separating concerns into distinct layers: Core Services, Data Handling, Trading Logic, and Analysis. This plan introduces several key new modules to be developed: Configuration Service, Notification Service, Strategy Engine, Risk Management, Backtesting Engine, and Performance Analyzer.

[2025-08-09 22:17:39] - [ARCHITECTURAL REVISION] - Based on user feedback and a thorough review of the Memory Bank, the previously proposed architecture in `project_structure.txt` was revised. The initial plan was found to be overly complex and inconsistent with the key decision to simplify the trading engine for the MVP (Decision Log: 2025-08-06 18:41:00). The architecture has been corrected to a leaner, more focused structure that accurately reflects the project's established goals. Auxiliary modules like Backtesting and Performance Analysis have been explicitly separated from the core operational loop.

[2025-08-10 00:01:00] - **Decision**: The custom logging framework's `MarketDataLogger` should be used semantically. Instead of adding generic `.info()` methods or accessing the inner logger (`.logger.info()`), the correct approach for informational messages that represent a specific event is to use an existing high-level method like `log_operation_start`.
**Rationale**: This adheres to the framework's design of logging meaningful, structured events rather than simple text messages. It makes logs more valuable for AI analysis and avoids modifying the core logging system for one-off cases. This decision was reached after multiple incorrect attempts to fix a logging error in `trading_cycle.py`.

[2025-08-10 00:14:00] - **Decision**: The `OmsRepository` will be migrated from a CSV-based persistence mechanism to SQLite.
**Rationale**: Analysis of the CSV implementation revealed significant risks regarding data integrity, type safety, and fragility when handling schema changes. SQLite provides ACID guarantees, strong data typing, and efficient row-level updates (`INSERT OR REPLACE`), making it a vastly more robust and scalable solution for managing OMS state. This decision was made after a critical review of the CSV repository's readiness for production.

[2025-08-10 00:26:30] - **Status**: The migration of `OmsRepository` to SQLite (Phase 7) has been successfully completed. The new implementation passed all unit and integration tests.

[2025-08-10 00:33:12] - **Decision:** Corrected the trading cycle logic in `trading_cycle.py`.
**Rationale:** The cycle was incorrectly terminating after an order's status was synced (e.g., from PENDING to FILLED). This prevented the AI from receiving the updated state (a closed position) to make a new decision.
**Implication:** The trading loop will now correctly continue after a position is closed, allowing for continuous operation and decision-making based on the latest portfolio state.

[2025-08-10 16:11:35] - **Architectural Decision: OMS/Repository Hardening (Phase 8)**
**Problem**: The initial implementation of `OmsRepository` and `OrderManagementSystem` was not production-ready. It lacked proper error handling (did not convert specific DB errors into domain exceptions), had no logging, and was missing tests for critical failure scenarios (DB corruption, integrity errors).
**Solution**: A systematic, test-driven approach was used to harden the components.
1.  **TDD for Errors**: Specific tests were created to simulate `sqlite3.OperationalError`, `sqlite3.IntegrityError`, and database corruption *before* implementing the fixes.
2.  **Custom Domain Exception**: A new `RepositoryError` was created to abstract away database-specific exceptions, providing a consistent error-handling contract.
3.  **Refactoring**: `OmsRepository` was refactored to catch `sqlite3.Error` and wrap it in the new `RepositoryError`.
4.  **Graceful Handling**: `OrderManagementSystem` was updated to handle `RepositoryError` gracefully, preventing crashes and logging the persistence issue.
5.  **Logging & Tracing**: The `MarketDataLogger` was injected into both `OMS` and `OmsRepository`, and `trace_id` propagation was implemented to ensure full end-to-end observability of order operations.
**Result**: The OMS and its repository are now robust, production-ready components that align with the project's established architectural patterns for error handling and logging. The entire system remains stable, as confirmed by a full test suite run.

[2025-08-10 16:30:50] - **Архитектурное решение: Централизация генерации `trace_id`**. Принято решение перенести точку генерации корневого `trace_id` из `MarketDataService` в `TradingCycle`. `TradingCycle` теперь отвечает за создание "мастер" `trace_id` для каждого цикла, который затем передается во все дочерние компоненты (`MarketDataService`, `OMS`). Это обеспечивает настоящую сквозную трассировку операций.

[2025-08-10 16:34:35] - **Архитектурное решение: Сквозная передача `trace_id` в слой персистентности**. Реализована передача `trace_id` через `OrderManagementSystem` в `OmsRepository`.
**Проблема**: Логирование в `OmsRepository` было изолированным и не имело связи с инициирующей операцией в `TradingCycle`.
**Решение**: Все методы в `OMS`, вызывающие репозиторий, и все методы в `OmsRepository` (`load`, `save`, `delete`) были модифицированы для приема и использования `trace_id`.
**Результат**: Завершено создание полной цепочки трассировки. Теперь каждое действие, от старта торгового цикла до записи в базу данных, связано единым `trace_id`, что обеспечивает полную наблюдаемость и упрощает отладку.

[2025-08-10 17:13:33] - Refactoring `OmsRepository` to handle `:memory:` database connections correctly for testing purposes. The change introduces a persistent connection for in-memory databases to prevent tables from being destroyed between operations, while maintaining the existing connection-per-operation logic for file-based databases in production.


[2025-08-10 20:50:22] - **Architectural Decision: Simplification of Tracing in `MarketDataService`**
**Problem**: The existing hierarchical tracing in `MarketDataService`, where the service generated its own `trace_id`s for sub-operations, was overly complex. It contradicted the project's goal of simple end-to-end tracing and was a root cause of failures in the `test_end_to_end_tracing.py` integration test.
**Solution**: The tracing mechanism was refactored to use a single, externally provided `trace_id`.
1.  **Removed `_start_operation`**: The method responsible for generating new `trace_id`s was deleted.
2.  **Simplified Signatures**: All methods, including `get_market_data` and internal calculation methods, were updated to accept a single `trace_id` instead of a `parent_trace_id`.
3.  **Direct Propagation**: The `trace_id` is now passed down directly through the entire call stack within the service.
**Result**: This change significantly simplifies the logging logic, makes log analysis more straightforward, and directly addresses the instability in the integration test by allowing for simpler, more robust assertions based on a single `trace_id`.

[2025-08-10 17:53:57] - [Decision] Refactored the end-to-end tracing test (`test_end_to_end_tracing.py`) to align with the simplified single `trace_id` architecture. [Rationale] The previous test was designed to validate a complex parent-child trace ID hierarchy, which has been removed. The new test validates that the single `master_trace_id` is correctly propagated through all logged operations. [Implication] This simplifies test maintenance and more accurately reflects the current, cleaner tracing design.

[2025-08-10 18:46:08] - Refactor tracing logic to enforce a single `trace_id` throughout the `MarketDataService`. All methods now require a `trace_id`, and the service raises a `ValidationError` if it's missing. This simplifies debugging and ensures consistent end-to-end tracing.


[2025-08-10 22:10:00] - **Architectural Decision: Stricter Workflow for Refactoring**. Added a mandatory testing policy to `workflowChecks.md`. Any change to existing code (refactoring, bug fix) must be immediately followed by a full test suite run within the same phase to ensure no regressions are introduced. This enforces a higher standard of quality and prevents breaking changes from being committed.


[2025-08-10 22:20:00] - **Architectural Decision: Make `service_name` a Mandatory Parameter in Logging System**. To fix incorrect service attribution in logs, the `service_name` parameter was made mandatory across the entire logging chain (`AIOptimizedJSONFormatter`, `StructuredLogger`, `get_logger`, `MarketDataLogger`). This forces each component to explicitly declare its identity when creating a logger, eliminating the risk of incorrect, hardcoded default values. A subsequent test run confirmed this change by producing widespread `TypeError` failures, precisely identifying all call sites that require updates.

[2025-08-10 20:45:00] - Refactored core logging system to support dynamic `service_name`.
    - **Decision:** Modified `AIOptimizedJSONFormatter` to extract `service_name` from the `LogRecord` instead of being initialized with a hardcoded value. `StructuredLogger` now acts as an adapter to inject the `service_name` into each log record's `extra` dictionary. The logging configuration (`LoggerConfig`) was also updated to manage its handlers without interfering with `pytest`'s capture mechanism.
    - **Rationale:** The previous implementation hardcoded `"service":"MarketDataService"` in the formatter, causing all logs to be incorrectly attributed. The new architecture decouples the formatter from specific services, allowing each component to correctly identify itself. The fix for the test interference ensures a stable and isolated testing environment.
    - **Implication:** All logger instantiations throughout the codebase must now provide a `service_name`. Unit tests for logging required significant refactoring.

[2025-08-10 21:20:15] - [Test Refactoring] - Refactored `tests/integration/logging/test_end_to_end_tracing.py` to use the real `AIOptimizedJSONFormatter` and validate the `service` field in the JSON logs. This ensures the test correctly verifies the dynamic service name injection, which was the primary goal of the logging refactoring. The previous implementation used a custom formatter that completely ignored the `service` field, rendering the test ineffective for its intended purpose.

### [2025-08-10 21:51:37] - **Decision: Increase Kline Data Fetch Limit for MA50 Calculation**
**Problem**: Log analysis revealed that the `MarketDataService` was consistently using a fallback mechanism to calculate the 50-period Moving Average (MA50). The service was fetching only 48 hours of 1-hour kline data, which was insufficient for a 50-period calculation, leading to a less accurate technical indicator.
**Solution**: The `limit` parameter in the `_get_klines` call within `market_data_service.py` was increased from 48 to 100 for the 1-hour interval.
**Rationale**: This simple change ensures that the service always has more than enough data (100 points) to perform a standard 50-period MA calculation. It eliminates the reliance on the graceful degradation logic, thereby improving the quality and reliability of the technical analysis data used for AI decision-making. The change was determined to have no impact on existing tests.
**Result**: The system now produces a more accurate MA50 indicator. The fix was validated through a full test suite run and a real-world scenario execution, confirming the fallback is no longer triggered.
