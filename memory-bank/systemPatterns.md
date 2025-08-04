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
*Optimized 2025-01-04: Reduced from 1,085 lines to core patterns + archive reference*