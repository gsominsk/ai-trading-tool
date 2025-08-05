"""
Shared fixtures for integration tests.

This file provides fixtures specific to testing component interactions
and cross-system functionality.
"""

import pytest
import tempfile
import threading
import time
from unittest.mock import Mock, patch
from pathlib import Path


@pytest.fixture
def real_file_system():
    """Fixture providing real filesystem for integration testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create subdirectories for different test scenarios
        (tmpdir_path / "logs").mkdir()
        (tmpdir_path / "data").mkdir() 
        (tmpdir_path / "config").mkdir()
        
        yield tmpdir_path


@pytest.fixture
def threaded_execution():
    """Fixture for testing concurrent operations."""
    threads = []
    results = {}
    errors = []
    
    def run_threaded(target, *args, **kwargs):
        def wrapper():
            try:
                thread_id = threading.get_ident()
                result = target(*args, **kwargs)
                results[thread_id] = result
            except Exception as e:
                errors.append(e)
        
        thread = threading.Thread(target=wrapper)
        threads.append(thread)
        return thread
    
    yield run_threaded
    
    # Wait for all threads to complete
    for thread in threads:
        if thread.is_alive():
            thread.join(timeout=5.0)
    
    # Return results and errors for analysis
    return results, errors


@pytest.fixture
def mock_network_conditions():
    """Simulate various network conditions for integration testing."""
    conditions = {
        'normal': {'delay': 0, 'fail_rate': 0},
        'slow': {'delay': 2.0, 'fail_rate': 0},
        'unstable': {'delay': 0.5, 'fail_rate': 0.2},
        'offline': {'delay': 0, 'fail_rate': 1.0}
    }
    
    def apply_condition(condition_name='normal'):
        condition = conditions.get(condition_name, conditions['normal'])
        
        with patch('requests.get') as mock_get:
            def slow_response(*args, **kwargs):
                if condition['delay']:
                    time.sleep(condition['delay'])
                if condition['fail_rate'] and hash(str(args)) % 10 < condition['fail_rate'] * 10:
                    raise Exception("Network error")
                
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "success"}
                return mock_response
            
            mock_get.side_effect = slow_response
            yield mock_get
    
    return apply_condition


@pytest.fixture
def component_registry():
    """Registry for managing component instances in integration tests."""
    registry = {}
    
    def register(name, component):
        registry[name] = component
        return component
    
    def get(name):
        return registry.get(name)
    
    def cleanup():
        for component in registry.values():
            if hasattr(component, 'cleanup'):
                component.cleanup()
        registry.clear()
    
    yield {'register': register, 'get': get}
    
    # Cleanup all registered components
    cleanup()