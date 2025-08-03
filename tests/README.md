# AI Trading System Test Suite

This directory contains comprehensive tests for the AI Trading System following Test-Driven Development (TDD) principles.

## Test Structure

```
tests/
├── unit/                    # Unit tests (70% coverage target)
├── integration/             # Integration tests (20% coverage target)
├── backtesting/             # Historical performance tests (10% coverage target)
├── fixtures/                # Test data and mock responses
├── conftest.py              # Shared pytest fixtures
└── README.md               # This file
```

## Testing Philosophy

### TDD Approach
We follow **Test-Driven Development** for all new modules:
1. **Red**: Write failing tests first
2. **Green**: Write minimal code to pass tests
3. **Refactor**: Improve code while keeping tests green

### Financial Safety First
Since this system handles real money, we prioritize:
- **100% coverage** for financial calculations
- **Decimal precision** testing for crypto amounts
- **Edge case validation** for risk management
- **Mock all external APIs** for predictable testing

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Individual component testing
- Financial precision validation
- Pattern recognition algorithms
- Data structure validation

### Integration Tests (`@pytest.mark.integration`)
- LLM provider integration
- Binance API connectivity
- End-to-end trading workflows
- Configuration switching

### Backtesting Tests (`@pytest.mark.slow`)
- Historical performance validation
- Strategy comparison
- Long-term stability testing

### Financial Tests (`@pytest.mark.financial`)
- Decimal arithmetic precision
- PnL calculations
- Risk management validation
- Portfolio value calculations

### LLM Tests (`@pytest.mark.llm`)
- AI decision validation
- Response format checking
- Multi-model comparison
- Fallback scenarios

## Running Tests

### All Tests
```bash
pytest
```

### Specific Categories
```bash
pytest -m unit                    # Unit tests only
pytest -m "financial and unit"    # Financial unit tests
pytest -m "not slow"              # Skip slow backtesting tests
pytest -m llm                     # LLM-related tests only
```

### Coverage Report
```bash
pytest --cov=src --cov-report=html
```

### Parallel Execution
```bash
pytest -n auto                    # Use all CPU cores
```

## Test Data

### Fixtures (`tests/fixtures/`)
- **market_data_samples.json**: Sample market data for testing
- **llm_response_mocks.json**: Mock LLM responses for all scenarios

### Shared Fixtures (`conftest.py`)
- `sample_market_data`: Basic market data structure
- `sample_trading_signal`: Standard trading signal format
- `mock_binance_api`: Mocked Binance API responses
- `mock_llm_provider`: Mocked LLM provider responses
- `test_config`: Test configuration parameters

## TDD Workflow Example

### 1. Write Test First (Red)
```python
def test_calculate_position_size():
    """Test position sizing calculation."""
    portfolio_value = Decimal("10000.00")
    risk_per_trade = Decimal("0.02")  # 2%
    entry_price = Decimal("50000.00")
    stop_loss = Decimal("47500.00")
    
    # This will fail initially - no implementation yet
    position_size = calculate_position_size(
        portfolio_value, risk_per_trade, entry_price, stop_loss
    )
    
    expected_size = Decimal("0.08")  # 2% risk = $200, $2500 risk per coin = 0.08 BTC
    assert position_size == expected_size
```

### 2. Implement Minimal Code (Green)
```python
def calculate_position_size(portfolio_value, risk_per_trade, entry_price, stop_loss):
    """Calculate position size based on risk management."""
    risk_amount = portfolio_value * risk_per_trade
    price_diff = abs(entry_price - stop_loss)
    return risk_amount / price_diff
```

### 3. Refactor and Improve
- Add validation
- Handle edge cases
- Optimize performance
- Improve readability

## Current Test Status

### Implemented
- ✅ Test structure and configuration
- ✅ MarketDataService unit tests (ready for TDD)
- ✅ Shared fixtures and mock data
- ✅ pytest configuration

### Pending (TDD Ready)
- ⏳ PortfolioManager tests (write when implementing module)
- ⏳ RiskManager tests (write when implementing module)
- ⏳ OrderExecutor tests (write when implementing module)
- ⏳ LLM Provider tests (write when implementing providers)

## Best Practices

### Financial Precision
```python
# Always use Decimal for financial calculations
from decimal import Decimal

# Good
price = Decimal("50000.12345678")
quantity = Decimal("0.1")
value = price * quantity

# Bad
price = 50000.12345678  # Float precision issues
```

### Mock External Dependencies
```python
@patch('requests.get')
def test_binance_api_integration(mock_get):
    mock_get.return_value.json.return_value = {"price": "50000.00"}
    # Test implementation without hitting real API
```

### Test Naming Convention
```python
def test_[component]_[functionality]_[expected_outcome]():
    """Clear docstring explaining what is being tested."""
    pass

# Examples:
def test_portfolio_manager_calculates_pnl_accurately():
def test_risk_manager_validates_stop_loss_levels():
def test_llm_provider_handles_api_timeout_gracefully():
```

## Contributing

1. **Always write tests first** for new functionality
2. **Run tests before committing**: `pytest`
3. **Maintain high coverage** for financial operations
4. **Use descriptive test names** and docstrings
5. **Mock all external dependencies**
6. **Test edge cases** thoroughly

For questions about testing approach, refer to the Memory Bank documentation in `memory-bank/systemPatterns.md`.