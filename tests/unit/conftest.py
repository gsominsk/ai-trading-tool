"""
Shared fixtures for unit tests.

This file provides fixtures specific to unit testing individual components.
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime


@pytest.fixture
def isolated_component():
    """Fixture to ensure components are tested in isolation."""
    with patch.dict('sys.modules', {}, clear=False):
        yield


@pytest.fixture
def decimal_precision():
    """Fixture to test Decimal precision requirements."""
    test_decimals = {
        'price': Decimal('50000.12345678'),
        'volume': Decimal('1234.56789012'),
        'percentage': Decimal('0.05'),
        'tiny_amount': Decimal('0.00000001')
    }
    return test_decimals


@pytest.fixture
def mock_external_dependencies():
    """Mock all external dependencies for pure unit testing."""
    mocks = {}
    
    with patch('requests.get') as mock_requests, \
         patch('time.sleep') as mock_sleep:
        
        mocks['requests'] = mock_requests
        mocks['sleep'] = mock_sleep
        
        # Default successful responses
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {"success": True}
        
        yield mocks