"""
Comprehensive Caching System Tests for MarketDataService
Tests caching functionality that is critical for production performance and stability.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, call
from pathlib import Path
from src.market_data.market_data_service import MarketDataService


class TestCachingSystemComprehensive:
    """Comprehensive test suite for MarketDataService caching functionality."""
    
    def setup_method(self):
        """Set up test fixtures with temporary cache directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "test_cache")
        
    def teardown_method(self):
        """Clean up temporary directories after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.unit
    def test_cache_directory_creation_basic(self):
        """Test basic cache directory creation functionality."""
        # Test that cache directory is created during service initialization
        service = MarketDataService(cache_dir=self.cache_dir)
        
        # Verify cache directory was created
        assert os.path.exists(self.cache_dir), f"Cache directory should be created at {self.cache_dir}"
        assert os.path.isdir(self.cache_dir), "Cache path should be a directory"
        
        # Verify service has correct cache_dir attribute
        assert service.cache_dir == self.cache_dir, "Service should store correct cache directory path"
    
    @pytest.mark.unit
    def test_cache_directory_creation_nested_paths(self):
        """Test cache directory creation with nested paths."""
        nested_cache_dir = os.path.join(self.temp_dir, "level1", "level2", "cache")
        
        # Create service with nested cache path
        service = MarketDataService(cache_dir=nested_cache_dir)
        
        # Verify all nested directories were created
        assert os.path.exists(nested_cache_dir), "Nested cache directories should be created"
        assert os.path.isdir(nested_cache_dir), "Final cache path should be a directory"
        
        # Verify intermediate directories exist
        assert os.path.exists(os.path.join(self.temp_dir, "level1")), "Intermediate directory level1 should exist"
        assert os.path.exists(os.path.join(self.temp_dir, "level1", "level2")), "Intermediate directory level2 should exist"
    
    @pytest.mark.unit
    def test_cache_directory_already_exists(self):
        """Test behavior when cache directory already exists."""
        # Pre-create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Create service with existing cache directory
        service = MarketDataService(cache_dir=self.cache_dir)
        
        # Should work without errors
        assert os.path.exists(self.cache_dir), "Existing cache directory should remain"
        assert service.cache_dir == self.cache_dir, "Service should use existing cache directory"
    
    @pytest.mark.unit
    def test_cache_directory_with_files(self):
        """Test cache directory behavior with existing files."""
        # Pre-create cache directory with files
        os.makedirs(self.cache_dir, exist_ok=True)
        test_file = os.path.join(self.cache_dir, "existing_file.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Create service
        service = MarketDataService(cache_dir=self.cache_dir)
        
        # Existing files should be preserved
        assert os.path.exists(test_file), "Existing cache files should be preserved"
        
        # Read content to verify file integrity
        with open(test_file, 'r') as f:
            content = f.read()
        assert content == "test content", "Existing file content should be preserved"
    
    @pytest.mark.unit
    def test_cache_directory_permissions_error(self):
        """Test behavior when cache directory creation fails due to permissions."""
        # Create a read-only directory to simulate permission error
        readonly_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only permissions
        
        restricted_cache_dir = os.path.join(readonly_dir, "cache")
        
        try:
            # This should handle permission errors gracefully
            with pytest.raises(PermissionError):
                service = MarketDataService(cache_dir=restricted_cache_dir)
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)
    
    @pytest.mark.unit 
    def test_default_cache_directory(self):
        """Test default cache directory creation."""
        # Create service with default cache directory
        service = MarketDataService()
        
        # Verify default cache directory
        expected_cache_dir = "data/cache"
        assert service.cache_dir == expected_cache_dir, f"Default cache directory should be {expected_cache_dir}"
    
    @pytest.mark.unit
    def test_cache_directory_relative_paths(self):
        """Test cache directory creation with relative paths."""
        relative_cache_dir = "./test_relative_cache"
        
        try:
            service = MarketDataService(cache_dir=relative_cache_dir)
            
            # Verify relative cache directory was created
            assert os.path.exists(relative_cache_dir), "Relative cache directory should be created"
            assert service.cache_dir == relative_cache_dir, "Service should store relative path"
        finally:
            # Clean up relative directory
            if os.path.exists(relative_cache_dir):
                shutil.rmtree(relative_cache_dir)
    
    @pytest.mark.unit
    def test_cache_directory_absolute_paths(self):
        """Test cache directory creation with absolute paths."""
        absolute_cache_dir = os.path.abspath(os.path.join(self.temp_dir, "absolute_cache"))
        
        service = MarketDataService(cache_dir=absolute_cache_dir)
        
        # Verify absolute cache directory was created
        assert os.path.exists(absolute_cache_dir), "Absolute cache directory should be created"
        assert service.cache_dir == absolute_cache_dir, "Service should store absolute path"
    
    @pytest.mark.unit
    def test_cache_directory_special_characters(self):
        """Test cache directory creation with special characters in path."""
        special_cache_dir = os.path.join(self.temp_dir, "cache-with_special.chars")
        
        service = MarketDataService(cache_dir=special_cache_dir)
        
        # Verify cache directory with special characters was created
        assert os.path.exists(special_cache_dir), "Cache directory with special characters should be created"
        assert service.cache_dir == special_cache_dir, "Service should handle special characters in path"
    
    @pytest.mark.unit
    def test_cache_directory_unicode_characters(self):
        """Test cache directory creation with Unicode characters."""
        unicode_cache_dir = os.path.join(self.temp_dir, "кэш_директория")
        
        service = MarketDataService(cache_dir=unicode_cache_dir)
        
        # Verify Unicode cache directory was created
        assert os.path.exists(unicode_cache_dir), "Unicode cache directory should be created"
        assert service.cache_dir == unicode_cache_dir, "Service should handle Unicode characters in path"
    
    @pytest.mark.unit
    def test_multiple_service_instances_same_cache(self):
        """Test multiple service instances using the same cache directory."""
        # Create first service instance
        service1 = MarketDataService(cache_dir=self.cache_dir)
        assert os.path.exists(self.cache_dir), "Cache directory should be created by first instance"
        
        # Create second service instance with same cache directory
        service2 = MarketDataService(cache_dir=self.cache_dir)
        
        # Both instances should work correctly
        assert service1.cache_dir == service2.cache_dir, "Both instances should use same cache directory"
        assert os.path.exists(self.cache_dir), "Cache directory should remain accessible"
    
    @pytest.mark.unit
    def test_cache_directory_very_long_path(self):
        """Test cache directory creation with very long paths."""
        # Create a very long path (approaching system limits)
        long_path_components = ["very_long_directory_name_" + "x" * 50 for _ in range(3)]
        long_cache_dir = os.path.join(self.temp_dir, *long_path_components)
        
        try:
            service = MarketDataService(cache_dir=long_cache_dir)
            
            # Should either succeed or fail gracefully with clear error
            if os.path.exists(long_cache_dir):
                assert service.cache_dir == long_cache_dir, "Service should handle long paths"
        except OSError as e:
            # Long paths might fail on some systems - this is expected behavior
            assert "File name too long" in str(e) or "path too long" in str(e).lower()
    
    @pytest.mark.unit
    def test_cache_directory_with_file_conflict(self):
        """Test cache directory creation when path conflicts with existing file."""
        # Create a file at the cache directory path
        conflicting_file = self.cache_dir
        os.makedirs(os.path.dirname(conflicting_file), exist_ok=True)
        with open(conflicting_file, 'w') as f:
            f.write("conflicting file")
        
        # Attempt to create service with conflicting path
        with pytest.raises((OSError, FileExistsError)):
            service = MarketDataService(cache_dir=conflicting_file)
    
    @pytest.mark.unit
    @patch('os.makedirs')
    def test_ensure_cache_dir_called_during_init(self, mock_makedirs):
        """Test that _ensure_cache_dir is called during initialization."""
        service = MarketDataService(cache_dir=self.cache_dir)
        
        # Verify makedirs was called with correct parameters
        mock_makedirs.assert_called_once_with(self.cache_dir, exist_ok=True)
    
    @pytest.mark.unit
    def test_cache_directory_error_handling(self):
        """Test error handling for cache directory operations."""
        # Test with invalid path characters (if supported by OS)
        import platform
        if platform.system() == "Windows":
            invalid_cache_dir = os.path.join(self.temp_dir, "cache<>invalid")
            with pytest.raises(OSError):
                service = MarketDataService(cache_dir=invalid_cache_dir)
    
    @pytest.mark.unit
    def test_cache_performance_impact(self):
        """Test that cache directory creation doesn't significantly impact performance."""
        import time
        
        # Measure time for service creation
        start_time = time.time()
        service = MarketDataService(cache_dir=self.cache_dir)
        creation_time = time.time() - start_time
        
        # Cache directory creation should be very fast (< 100ms even on slow systems)
        assert creation_time < 0.1, f"Service creation with cache dir took {creation_time:.3f}s - too slow"
    
    @pytest.mark.unit
    def test_cache_directory_thread_safety(self):
        """Test thread safety of cache directory creation."""
        import threading
        import time
        
        results = []
        exceptions = []
        
        def create_service():
            try:
                service = MarketDataService(cache_dir=self.cache_dir)
                results.append(service.cache_dir)
            except Exception as e:
                exceptions.append(e)
        
        # Create multiple threads that create services simultaneously
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_service)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=1.0)
        
        # Verify results
        assert len(exceptions) == 0, f"No exceptions should occur during concurrent creation: {exceptions}"
        assert len(results) == 5, "All threads should successfully create services"
        assert all(cache_dir == self.cache_dir for cache_dir in results), "All services should use same cache directory"
        assert os.path.exists(self.cache_dir), "Cache directory should exist after concurrent creation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])