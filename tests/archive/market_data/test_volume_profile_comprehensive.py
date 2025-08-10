"""
Comprehensive Volume Profile Testing for MarketDataService
Tests the critical _analyze_volume_profile() method that has NO current test coverage.
"""

import pytest
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from src.market_data.market_data_service import MarketDataService


class TestVolumeProfileComprehensive:
    """Comprehensive test suite for volume profile analysis."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MarketDataService()
    
    def _create_volume_dataframe(self, volumes: List[float], hours_back: int = None) -> pd.DataFrame:
        """Create DataFrame with specific volume pattern."""
        if hours_back is None:
            hours_back = len(volumes)
        
        base_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        data = []
        for i, volume in enumerate(volumes):
            data.append({
                'timestamp': base_time + timedelta(hours=i),
                'open': 50000.0 + i,
                'high': 50100.0 + i,
                'low': 49900.0 + i,
                'close': 50000.0 + i,
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    @pytest.mark.unit
    def test_volume_profile_high_volume(self):
        """Test detection of high volume profile (ratio > 1.5)."""
        # Create pattern: recent volume significantly higher than historical
        volumes = [1000.0] * 20 + [2000.0] * 24  # Historical low, recent high
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "high", f"Expected 'high' volume profile, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_low_volume(self):
        """Test detection of low volume profile (ratio < 0.5)."""
        # Create pattern: recent volume significantly lower than historical
        volumes = [2000.0] * 20 + [800.0] * 24  # Historical high, recent low
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "low", f"Expected 'low' volume profile, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_normal_volume(self):
        """Test detection of normal volume profile (0.5 <= ratio <= 1.5)."""
        # Create pattern: recent volume similar to historical
        volumes = [1000.0] * 44  # Consistent volume
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "normal", f"Expected 'normal' volume profile, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_normal_slight_increase(self):
        """Test normal classification with slight volume increase."""
        # Create pattern: slight increase within normal range
        volumes = [1000.0] * 20 + [1300.0] * 24  # 30% increase - still normal
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "normal", f"Expected 'normal' volume profile, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_normal_slight_decrease(self):
        """Test normal classification with slight volume decrease."""
        # Create pattern: slight decrease within normal range
        volumes = [1000.0] * 20 + [700.0] * 24  # 30% decrease - still normal
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "normal", f"Expected 'normal' volume profile, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_insufficient_data(self):
        """Test behavior with insufficient data (< 24 hours)."""
        # Create DataFrame with insufficient data
        volumes = [1000.0] * 10  # Only 10 hours of data
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "normal", f"Expected 'normal' for insufficient data, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_edge_case_exactly_24_hours(self):
        """Test with exactly 24 hours of data."""
        # Create DataFrame with exactly 24 hours
        volumes = [1000.0] * 24
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "normal", f"Expected 'normal' for 24 hours data, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_extreme_high_volume(self):
        """Test with extreme volume spike (10x increase)."""
        # Create extreme volume pattern
        volumes = [1000.0] * 20 + [10000.0] * 24  # 10x increase
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "high", f"Expected 'high' for extreme volume, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_extreme_low_volume(self):
        """Test with extreme volume drop (10x decrease)."""
        # Create extreme volume drop pattern
        volumes = [10000.0] * 20 + [1000.0] * 24  # 10x decrease
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "low", f"Expected 'low' for extreme volume drop, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_zero_historical_volume(self):
        """Test handling of zero historical volume."""
        # Create pattern with zero historical volume
        volumes = [0.0] * 20 + [1000.0] * 24
        df = self._create_volume_dataframe(volumes)
        
        # This should not crash - service should handle division by zero
        result = self.service._analyze_volume_profile(df)
        
        # With zero historical volume, any recent volume should be "high"
        assert result in ["high", "normal"], f"Should handle zero volume gracefully, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_zero_recent_volume(self):
        """Test handling of zero recent volume."""
        # Create pattern with zero recent volume
        volumes = [1000.0] * 20 + [0.0] * 24
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        # Zero recent volume should be classified as "low"
        assert result == "low", f"Expected 'low' for zero recent volume, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_all_zero_volume(self):
        """Test handling of all zero volume."""
        # Create pattern with all zero volume
        volumes = [0.0] * 44
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        # All zero should default to "normal" (no meaningful comparison)
        assert result == "normal", f"Expected 'normal' for all zero volume, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_boundary_high_threshold(self):
        """Test exact boundary at high threshold (ratio = 1.5)."""
        # Create pattern exactly at high threshold
        volumes = [1000.0] * 20 + [1500.0] * 24  # Ratio = 1.5
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        # At boundary, should be "normal" (ratio > 1.5 for "high")
        assert result == "normal", f"Expected 'normal' at boundary, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_boundary_low_threshold(self):
        """Test exact boundary at low threshold (ratio = 0.5)."""
        # Create pattern exactly at low threshold
        volumes = [1000.0] * 20 + [500.0] * 24  # Ratio = 0.5
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        # At boundary, should be "normal" (ratio < 0.5 for "low")
        assert result == "normal", f"Expected 'normal' at boundary, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_just_above_high_threshold(self):
        """Test just above high threshold (ratio = 1.51)."""
        # Create pattern just above high threshold
        volumes = [1000.0] * 20 + [1510.0] * 24  # Ratio = 1.51
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "high", f"Expected 'high' just above threshold, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_just_below_low_threshold(self):
        """Test just below low threshold (ratio = 0.49)."""
        # Create pattern just below low threshold
        volumes = [1000.0] * 20 + [490.0] * 24  # Ratio = 0.49
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "low", f"Expected 'low' just below threshold, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_decimal_precision(self):
        """Test with high precision decimal volumes."""
        # Create pattern with high precision volumes
        volumes = [1000.123456789] * 20 + [2000.987654321] * 24
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        # Should handle decimal precision correctly
        assert result == "high", f"Expected 'high' with decimal precision, got '{result}'"
    
    @pytest.mark.unit 
    def test_volume_profile_large_numbers(self):
        """Test with very large volume numbers."""
        # Create pattern with large volumes
        volumes = [1_000_000.0] * 20 + [2_500_000.0] * 24  # 2.5x increase
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "high", f"Expected 'high' with large numbers, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_small_numbers(self):
        """Test with very small volume numbers."""
        # Create pattern with small volumes
        volumes = [0.001] * 20 + [0.0005] * 24  # 50% decrease
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "low", f"Expected 'low' with small numbers, got '{result}'"
    
    @pytest.mark.unit
    def test_volume_profile_mixed_pattern(self):
        """Test with mixed volume pattern (varying historical and recent)."""
        # Create mixed pattern: varying historical, consistent recent
        historical = [500.0, 1500.0, 800.0, 2000.0] * 5  # Average = 1200
        recent = [1000.0] * 24  # Recent average = 1000, ratio = 0.83 (normal)
        volumes = historical + recent
        df = self._create_volume_dataframe(volumes)
        
        result = self.service._analyze_volume_profile(df)
        
        assert result == "normal", f"Expected 'normal' for mixed pattern, got '{result}'"


def test_volume_profile_integration():
    """Integration test for volume profile in real service usage."""
    service = MarketDataService()
    
    # Test that function exists and is callable
    assert hasattr(service, '_analyze_volume_profile'), "Service should have _analyze_volume_profile method"
    assert callable(getattr(service, '_analyze_volume_profile')), "Method should be callable"
    
    # Create realistic test data
    test_df = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=50, freq='1H'),
        'open': [50000.0] * 50,
        'high': [50100.0] * 50,
        'low': [49900.0] * 50,
        'close': [50000.0] * 50,
        'volume': [1000.0 + i * 10 for i in range(50)]  # Increasing volume
    })
    
    # Test that it returns valid result
    result = service._analyze_volume_profile(test_df)
    assert result in ["high", "normal", "low"], f"Should return valid volume profile, got '{result}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])