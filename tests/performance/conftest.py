"""
Shared fixtures for performance tests.

This file provides fixtures specific to performance testing, benchmarking,
and load testing scenarios.
"""

import pytest
import time
import psutil
import threading
from decimal import Decimal
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class PerformanceMetrics:
    """Container for performance measurement data."""
    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    operations_per_second: float
    peak_memory_mb: float
    
    
@pytest.fixture
def performance_monitor():
    """Monitor system performance during test execution."""
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_memory = None
            self.peak_memory = 0
            self.operation_count = 0
            self.monitoring = False
            self._monitor_thread = None
            
        def start(self):
            """Start performance monitoring."""
            self.start_time = time.time()
            self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            self.peak_memory = self.start_memory
            self.operation_count = 0
            self.monitoring = True
            
            # Start memory monitoring thread
            self._monitor_thread = threading.Thread(target=self._monitor_memory)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
            
        def record_operation(self):
            """Record completion of one operation."""
            self.operation_count += 1
            
        def _monitor_memory(self):
            """Monitor memory usage in background thread."""
            while self.monitoring:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                if current_memory > self.peak_memory:
                    self.peak_memory = current_memory
                time.sleep(0.1)
                
        def stop(self) -> PerformanceMetrics:
            """Stop monitoring and return metrics."""
            self.monitoring = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=1.0)
                
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            execution_time = end_time - self.start_time
            
            ops_per_second = self.operation_count / execution_time if execution_time > 0 else 0
            cpu_percent = psutil.cpu_percent()
            
            return PerformanceMetrics(
                execution_time=execution_time,
                memory_usage_mb=end_memory - self.start_memory,
                cpu_percent=cpu_percent,
                operations_per_second=ops_per_second,
                peak_memory_mb=self.peak_memory
            )
    
    return PerformanceMonitor()


@pytest.fixture
def load_generator():
    """Generate load for stress testing."""
    
    def generate_market_data_load(count: int = 1000) -> List[Dict[str, Any]]:
        """Generate sample market data for load testing."""
        data = []
        base_price = Decimal('50000.00')
        
        for i in range(count):
            price_change = Decimal(str((i % 200) - 100)) * Decimal('0.01')
            data.append({
                'symbol': f'SYMBOL{i % 100}USDT',
                'price': base_price + price_change,
                'volume': Decimal('1000.00') + Decimal(str(i % 1000)),
                'timestamp': time.time() + i
            })
        
        return data
    
    def generate_log_load(count: int = 10000) -> List[Dict[str, Any]]:
        """Generate sample log entries for load testing."""
        logs = []
        
        for i in range(count):
            logs.append({
                'timestamp': time.time() + i,
                'level': ['DEBUG', 'INFO', 'WARNING', 'ERROR'][i % 4],
                'service': f'Service{i % 10}',
                'operation': f'operation_{i}',
                'message': f'Test message {i}',
                'context': {'test_id': i, 'batch': i // 100}
            })
        
        return logs
    
    return {
        'market_data': generate_market_data_load,
        'logs': generate_log_load
    }


@pytest.fixture
def benchmark_comparison():
    """Compare performance across different implementations."""
    
    class BenchmarkComparison:
        def __init__(self):
            self.results = defaultdict(list)
            
        def benchmark(self, name: str, func, *args, **kwargs):
            """Benchmark a function and store results."""
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            result = func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            metrics = {
                'execution_time': end_time - start_time,
                'memory_delta': end_memory - start_memory,
                'result': result
            }
            
            self.results[name].append(metrics)
            return result
            
        def get_average_metrics(self, name: str) -> Dict[str, float]:
            """Get average metrics for a benchmark."""
            if name not in self.results or not self.results[name]:
                return {}
                
            results = self.results[name]
            return {
                'avg_execution_time': sum(r['execution_time'] for r in results) / len(results),
                'avg_memory_delta': sum(r['memory_delta'] for r in results) / len(results),
                'min_execution_time': min(r['execution_time'] for r in results),
                'max_execution_time': max(r['execution_time'] for r in results),
                'sample_count': len(results)
            }
    
    return BenchmarkComparison()


@pytest.fixture
def stress_test_config():
    """Configuration for stress testing scenarios."""
    return {
        'light_load': {
            'concurrent_threads': 5,
            'operations_per_thread': 100,
            'duration_seconds': 10
        },
        'medium_load': {
            'concurrent_threads': 20,
            'operations_per_thread': 500,
            'duration_seconds': 30
        },
        'heavy_load': {
            'concurrent_threads': 50,
            'operations_per_thread': 1000,
            'duration_seconds': 60
        }
    }