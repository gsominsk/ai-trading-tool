"""
Pytest configuration and shared fixtures for AI Trading System tests.

This module provides common test fixtures and configuration for all test modules
in the reorganized test structure: unit/, integration/, and performance/.
"""

import pytest
import json
import tempfile
import os
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from unittest.mock import Mock, MagicMock
from pathlib import Path

# Test configuration
pytest_plugins = []


@pytest.fixture
def sample_market_data() -> Dict[str, Any]:
    """Sample market data for testing MarketDataService."""
    return {
        "symbol": "BTCUSDT",
        "price": Decimal("50000.12345678"),
        "volume": Decimal("1234.56789012"),
        "timestamp": datetime.now(),
        "daily_candles": [
            {
                "open": Decimal("49000.00"),
                "high": Decimal("51000.00"),
                "low": Decimal("48500.00"),
                "close": Decimal("50000.00"),
                "volume": Decimal("1000.00"),
                "timestamp": datetime.now() - timedelta(days=1)
            }
        ],
        "technical_indicators": {
            "rsi": 65.5,
            "macd": {
                "macd": 120.5,
                "signal": 110.2,
                "histogram": 10.3
            },
            "moving_averages": {
                "ma20": Decimal("49500.00"),
                "ma50": Decimal("48000.00")
            }
        }
    }


@pytest.fixture
def sample_trading_signal() -> Dict[str, Any]:
    """Sample trading signal for testing LLM providers."""
    return {
        "action": "BUY",
        "confidence": 0.85,
        "reasoning": "Strong bullish momentum with RSI indicating oversold conditions",
        "risk_level": "MEDIUM",
        "target_price": Decimal("52000.00"),
        "stop_loss": Decimal("47000.00"),
        "timestamp": datetime.now()
    }


@pytest.fixture
def mock_binance_api() -> Mock:
    """Mock Binance API for testing without external dependencies."""
    mock_api = Mock()
    
    # Mock market data response
    mock_api.get_ticker.return_value = {
        "symbol": "BTCUSDT",
        "price": "50000.12345678"
    }
    
    # Mock order placement response
    mock_api.create_order.return_value = {
        "orderId": 12345,
        "status": "FILLED",
        "executedQty": "0.01",
        "fills": [
            {
                "price": "50000.00",
                "qty": "0.01",
                "commission": "0.001"
            }
        ]
    }
    
    return mock_api


@pytest.fixture
def mock_llm_provider() -> Mock:
    """Mock LLM provider for testing AI decision making."""
    mock_provider = Mock()
    
    # Mock successful analysis response
    mock_provider.analyze_market.return_value = {
        "action": "HOLD",
        "confidence": 0.75,
        "reasoning": "Market consolidation, waiting for clearer signals",
        "risk_level": "LOW",
        "target_price": None,
        "stop_loss": None,
        "timestamp": datetime.now()
    }
    
    mock_provider.get_confidence_score.return_value = 0.75
    
    return mock_provider


@pytest.fixture
def sample_portfolio_data() -> Dict[str, Any]:
    """Sample portfolio data for testing PortfolioManager."""
    return {
        "cash": Decimal("10000.00"),
        "positions": {
            "BTCUSDT": {
                "quantity": Decimal("0.1"),
                "avg_price": Decimal("48000.00"),
                "current_price": Decimal("50000.00"),
                "pnl": Decimal("200.00")
            },
            "ETHUSDT": {
                "quantity": Decimal("2.0"),
                "avg_price": Decimal("3000.00"),
                "current_price": Decimal("3200.00"),
                "pnl": Decimal("400.00")
            }
        },
        "total_value": Decimal("16600.00"),
        "total_pnl": Decimal("600.00")
    }


@pytest.fixture
def historical_data_sample() -> List[Dict[str, Any]]:
    """Sample historical data for backtesting."""
    base_date = datetime(2023, 1, 1)
    data = []
    
    for i in range(30):  # 30 days of data
        date = base_date + timedelta(days=i)
        price = Decimal("50000") + Decimal(str(i * 100))  # Trending upward
        
        data.append({
            "timestamp": date,
            "open": price - Decimal("100"),
            "high": price + Decimal("200"),
            "low": price - Decimal("150"),
            "close": price,
            "volume": Decimal("1000") + Decimal(str(i * 10))
        })
    
    return data


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Test configuration for various testing scenarios."""
    return {
        "trading": {
            "max_position_size": Decimal("0.1"),
            "stop_loss_pct": Decimal("0.05"),
            "take_profit_pct": Decimal("0.10"),
            "risk_per_trade": Decimal("0.02")
        },
        "llm": {
            "providers": ["claude", "gemini", "gpt"],
            "timeout": 30,
            "max_retries": 3
        },
        "binance": {
            "testnet": True,
            "api_key": "test_key",
            "api_secret": "test_secret"
        }
    }


@pytest.fixture
def temp_log_dir():
    """Temporary directory for logging tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_logger():
    """Mock logger for testing logging components."""
    mock_logger = Mock()
    mock_logger.debug = Mock()
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_logger.error = Mock()
    mock_logger.critical = Mock()
    return mock_logger


@pytest.fixture
def sample_log_record():
    """Sample log record for testing formatters and handlers."""
    return {
        "timestamp": "2025-01-05T14:00:00.000Z",
        "level": "INFO",
        "service": "MarketDataService",
        "operation": "get_market_data",
        "message": "Test log message",
        "context": {"symbol": "BTCUSDT", "test": True},
        "flow": {"flow_id": "test_flow_123", "stage": "testing"},
        "tags": ["test", "unit"],
        "trace_id": "test_trace_456"
    }


@pytest.fixture
def mock_market_data_service():
    """Mock MarketDataService for integration tests."""
    mock_service = Mock()
    mock_service.get_market_data.return_value = {
        "symbol": "BTCUSDT",
        "current_price": Decimal("50000.00"),
        "daily_data": [],
        "technical_indicators": {}
    }
    return mock_service


@pytest.fixture
def sample_error_context():
    """Sample error context for testing error architecture."""
    return {
        "trace_id": "error_trace_789",
        "operation": "test_operation",
        "symbol": "BTCUSDT",
        "timestamp": datetime.now(timezone.utc),
        "system_info": {
            "python_version": "3.9.0",
            "platform": "test_platform"
        }
    }


# Test markers for categorizing tests
def pytest_configure(config):
    """Configure pytest markers for reorganized test structure."""
    # Primary test categories (by structure)
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for cross-component functionality"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    
    # Component-specific markers
    config.addinivalue_line(
        "markers", "logging: Tests for logging system components"
    )
    config.addinivalue_line(
        "markers", "market_data: Tests for market data service components"
    )
    config.addinivalue_line(
        "markers", "error_architecture: Tests for error handling system"
    )
    
    # Functional markers
    config.addinivalue_line(
        "markers", "financial: Tests involving financial calculations"
    )
    config.addinivalue_line(
        "markers", "llm: Tests involving LLM providers"
    )
    config.addinivalue_line(
        "markers", "slow: Slow-running tests (backtesting, performance)"
    )
    config.addinivalue_line(
        "markers", "external: Tests requiring external API calls"
    )
    
    # Infrastructure markers
    config.addinivalue_line(
        "markers", "memory_leak: Tests for memory leak detection"
    )
    config.addinivalue_line(
        "markers", "thread_safety: Tests for concurrent access patterns"
    )
    config.addinivalue_line(
        "markers", "production: Tests simulating production conditions"
    )