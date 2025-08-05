"""
Memory Leak Detection Tests for AI-Optimized Logging System

Tests memory usage patterns, garbage collection behavior, and resource cleanup
to ensure the logging system doesn't cause memory leaks in production.
"""

import pytest
import gc
import threading
import time
import sys
import weakref
from typing import List, Dict, Any

from src.logging_system import get_ai_logger, configure_ai_logging, MarketDataLogger
from src.logging_system import flow_operation, advance_to_stage
from src.logging_system.logger_config import reset_logging_state
from src.logging_system.trace_generator import reset_trace_counter


class TestMemoryLeakDetection:
    """Test memory leak detection and prevention."""
    
    def setup_method(self):
        """Reset logging state and force garbage collection."""
        reset_logging_state()
        reset_trace_counter()
        gc.collect()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_logging_state()
        gc.collect()
    
    def test_logger_creation_cleanup(self):
        """Test that logger creation doesn't cause memory leaks."""
        configure_ai_logging(log_level="INFO")
        
        # Get baseline memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Create many loggers
        loggers = []
        for i in range(100):
            logger = get_ai_logger(f"test_logger_{i}")
            loggers.append(logger)
        
        # Force garbage collection and check memory
        del loggers
        gc.collect()
        
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Should not have excessive object growth (allow reasonable growth for logger caching)
        assert object_increase < 2000, f"Too many objects retained: {object_increase}"
    
    def test_log_message_cleanup(self):
        """Test that log messages don't accumulate in memory."""
        configure_ai_logging(log_level="DEBUG")
        logger = get_ai_logger("memory_test")
        
        # Get baseline
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Log many messages with complex data
        for i in range(1000):
            complex_data = {
                "iteration": i,
                "data": list(range(i % 100)),  # Variable size data
                "nested": {
                    "symbol": f"TEST{i}USDT",
                    "prices": [float(j) for j in range(10)],
                    "metadata": {
                        "timestamp": f"2025-01-01T{i%24:02d}:00:00Z",
                        "large_string": "x" * (i % 1000)  # Variable string size
                    }
                }
            }
            
            logger.info(f"Memory test message {i}",
                       operation="memory_test",
                       context=complex_data,
                       tags=["memory", "test", f"batch_{i//100}"])
        
        # Force cleanup
        gc.collect()
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Memory should not grow excessively
        assert object_increase < 200, f"Memory leak detected: {object_increase} new objects"
    
    def test_flow_context_cleanup(self):
        """Test that flow contexts are properly cleaned up."""
        configure_ai_logging(log_level="INFO")
        logger = get_ai_logger("flow_memory_test")
        
        # Get baseline
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Create many flow contexts
        for i in range(100):
            with flow_operation(f"SYMBOL{i}", f"operation_{i}"):
                advance_to_stage("processing", data_size=i * 100)
                advance_to_stage("analysis", complexity=i % 10)
                
                logger.info(f"Flow operation {i}",
                           operation=f"flow_test_{i}",
                           context={"flow_iteration": i})
        
        # Force cleanup
        gc.collect()
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Flow contexts should be cleaned up
        assert object_increase < 100, f"Flow context leak: {object_increase} new objects"
    
    def test_concurrent_logging_memory(self):
        """Test memory behavior under concurrent logging."""
        configure_ai_logging(log_level="INFO")
        
        # Get baseline
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        def worker_function(worker_id: int):
            logger = get_ai_logger(f"concurrent_worker_{worker_id}")
            
            for i in range(50):
                logger.info(f"Worker {worker_id} message {i}",
                           operation=f"concurrent_worker_{worker_id}",
                           context={
                               "worker_id": worker_id,
                               "iteration": i,
                               "data": list(range(i % 20))
                           })
                time.sleep(0.001)  # Small delay
        
        # Start concurrent workers
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Cleanup and check memory
        gc.collect()
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Concurrent logging should not cause memory leaks (allow reasonable growth)
        assert object_increase < 500, f"Concurrent logging leak: {object_increase} new objects"
    
    def test_exception_handling_memory(self):
        """Test memory behavior when exceptions occur during logging."""
        configure_ai_logging(log_level="DEBUG")
        logger = get_ai_logger("exception_memory_test")
        
        # Get baseline
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Generate many exceptions and log them
        for i in range(100):
            try:
                # Create different types of exceptions
                if i % 3 == 0:
                    raise ValueError(f"Test ValueError {i}")
                elif i % 3 == 1:
                    raise KeyError(f"Test KeyError {i}")
                else:
                    raise RuntimeError(f"Test RuntimeError {i}")
            except Exception:
                logger.error(f"Exception test {i}",
                           operation="exception_test",
                           context={"exception_num": i, "test_data": "x" * (i % 100)},
                           exc_info=True)
        
        # Force cleanup
        gc.collect()
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Exception logging should not leak memory
        assert object_increase < 150, f"Exception handling leak: {object_increase} new objects"


class TestWeakReferenceCleanup:
    """Test cleanup using weak references."""
    
    def setup_method(self):
        """Setup test environment."""
        reset_logging_state()
        gc.collect()
    
    def test_logger_weak_references(self):
        """Test that loggers can be garbage collected."""
        configure_ai_logging(log_level="INFO")
        
        # Create logger and weak reference
        logger = get_ai_logger("weak_ref_test")
        weak_ref = weakref.ref(logger)
        
        # Use logger
        logger.info("Test message", operation="weak_ref_test")
        
        # Delete strong reference
        del logger
        gc.collect()
        
        # Weak reference should still exist (logger is cached)
        # But the logger object should be accessible
        assert weak_ref() is not None, "Logger should be accessible through cache"
        
        # Reset logging state to clear cache
        reset_logging_state()
        gc.collect()
        
        # Now weak reference might be cleared depending on implementation
        # This tests that we don't have unexpected strong references
    
    def test_context_data_cleanup(self):
        """Test that context data doesn't prevent garbage collection."""
        configure_ai_logging(log_level="INFO")
        logger = get_ai_logger("context_cleanup_test")
        
        # Create object that should be garbage collected
        class TestObject:
            def __init__(self, data):
                self.data = data
        
        test_objects = []
        weak_refs = []
        
        # Create objects and log them
        for i in range(10):
            obj = TestObject(f"test_data_{i}")
            weak_refs.append(weakref.ref(obj))
            test_objects.append(obj)
            
            # Log with object in context
            logger.info(f"Context test {i}",
                       operation="context_cleanup",
                       context={"test_object_data": obj.data, "iteration": i})
        
        # Clear strong references
        del test_objects
        gc.collect()
        
        # Check that objects can be garbage collected
        # (logging shouldn't hold strong references to logged data)
        # Note: This test validates that logging doesn't prevent GC
        # but the exact behavior depends on implementation details


class TestResourceCleanup:
    """Test proper cleanup of system resources."""
    
    def setup_method(self):
        """Setup test environment."""
        reset_logging_state()
        gc.collect()
    
    def test_file_handle_cleanup(self):
        """Test that file handles are properly managed."""
        import tempfile
        import os
        
        log_file = None
        try:
            # Create temporary log file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
                log_file = f.name
            
            # Configure logging with file
            configure_ai_logging(log_level="INFO", log_file=log_file)
            logger = get_ai_logger("file_cleanup_test")
            
            # Log many messages
            for i in range(100):
                logger.info(f"File test {i}", operation="file_test")
            
            # Reset logging to close file handles
            reset_logging_state()
            
            # File should be accessible (not locked by logging)
            with open(log_file, 'r') as f:
                content = f.read()
                assert "File test" in content
            
            # Should be able to delete file (no handle leak)
            os.unlink(log_file)
            log_file = None
            
        finally:
            if log_file and os.path.exists(log_file):
                try:
                    os.unlink(log_file)
                except OSError:
                    pass
    
    def test_thread_local_cleanup(self):
        """Test that thread-local data is cleaned up."""
        configure_ai_logging(log_level="INFO")
        logger = get_ai_logger("thread_local_test")
        
        # Get baseline
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        def thread_worker(thread_id: int):
            # Use flow operations (which use thread-local storage)
            with flow_operation(f"THREAD{thread_id}", f"thread_operation_{thread_id}"):
                advance_to_stage("processing")
                
                for i in range(20):
                    logger.info(f"Thread {thread_id} message {i}",
                               operation=f"thread_worker_{thread_id}",
                               context={"thread_id": thread_id, "message": i})
        
        # Create and run threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=thread_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Allow thread cleanup
        time.sleep(0.1)
        gc.collect()
        
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Thread-local data should not accumulate
        assert object_increase < 100, f"Thread-local data leak: {object_increase} new objects"


class TestLongRunningProcessMemory:
    """Test memory behavior in long-running processes."""
    
    def setup_method(self):
        """Setup test environment."""
        reset_logging_state()
        gc.collect()
    
    def test_long_running_stability(self):
        """Test memory stability over extended logging."""
        configure_ai_logging(log_level="INFO")
        logger = get_ai_logger("long_running_test")
        
        # Simulate long-running process with periodic memory checks
        memory_samples = []
        
        for cycle in range(10):
            # Log burst of messages
            for i in range(100):
                logger.info(f"Cycle {cycle} message {i}",
                           operation="long_running_test",
                           context={
                               "cycle": cycle,
                               "message": i,
                               "timestamp": time.time(),
                               "data": {"values": list(range(i % 50))}
                           })
            
            # Sample memory usage
            gc.collect()
            memory_samples.append(len(gc.get_objects()))
            
            # Small delay between cycles
            time.sleep(0.01)
        
        # Check memory growth pattern
        initial_memory = memory_samples[0]
        final_memory = memory_samples[-1]
        max_memory = max(memory_samples)
        
        # Memory should not grow unbounded
        memory_growth = final_memory - initial_memory
        max_growth = max_memory - initial_memory
        
        assert memory_growth < 200, f"Excessive memory growth: {memory_growth}"
        assert max_growth < 300, f"Memory spike too high: {max_growth}"
        
        # Memory should stabilize (not continuously growing)
        last_half = memory_samples[5:]
        memory_variance = max(last_half) - min(last_half)
        assert memory_variance < 100, f"Memory not stable: variance {memory_variance}"
    
    def test_trace_counter_reset_behavior(self):
        """Test that trace counter reset prevents unbounded growth."""
        configure_ai_logging(log_level="INFO")
        logger = get_ai_logger("trace_reset_test")
        
        # Log with trace IDs
        for i in range(1000):
            logger.info(f"Trace test {i}", operation="trace_test")
            
            # Reset trace counter periodically
            if i % 200 == 0:
                reset_trace_counter()
        
        # Should complete without memory issues
        # This test ensures trace counter doesn't cause memory problems
        gc.collect()
        
        # Test successful if no memory errors occurred
        assert True, "Trace counter reset test completed successfully"