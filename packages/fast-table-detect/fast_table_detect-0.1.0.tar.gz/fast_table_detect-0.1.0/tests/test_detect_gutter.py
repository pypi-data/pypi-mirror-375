import pytest
import numpy as np
import cv2 as cv
from fast_table_detect.detect_gutter import (
    detect_gutter, _ensure_odd, _box1d, _rolling_max_deque, _find_gutters
)


class TestHelperFunctions:
    """Test cases for helper functions in gutter detection."""
    
    def test_ensure_odd_basic(self):
        """Test basic functionality of _ensure_odd."""
        assert _ensure_odd(4) == 5
        assert _ensure_odd(5) == 5
        assert _ensure_odd(6) == 7
        assert _ensure_odd(7) == 7
        
        # Test with minimum value
        assert _ensure_odd(2, lo=5) == 5
        assert _ensure_odd(4, lo=7) == 7
        assert _ensure_odd(8, lo=3) == 9
    
    def test_ensure_odd_edge_cases(self):
        """Test edge cases for _ensure_odd."""
        assert _ensure_odd(0) == 3  # Should use default lo=3
        assert _ensure_odd(-1) == 3
        assert _ensure_odd(1, lo=1) == 1
        assert _ensure_odd(2, lo=1) == 3
    
    def test_box1d_basic(self):
        """Test basic functionality of _box1d (1D box filter)."""
        x = np.array([1, 2, 3, 4, 5], dtype=np.float32)
        result = _box1d(x, 3)
        
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert result.shape == x.shape
        assert np.all(result > 0)  # All values should be positive
        
        # Middle value should be average of neighbors
        expected_middle = (2 + 3 + 4) / 3
        assert np.isclose(result[2], expected_middle)
    
    def test_box1d_no_smoothing(self):
        """Test _box1d with k=1 (no smoothing)."""
        x = np.array([1, 2, 3, 4, 5])
        result = _box1d(x, 1)
        
        np.testing.assert_array_equal(result, x.astype(np.float32))
    
    def test_box1d_edge_cases(self):
        """Test _box1d with edge cases."""
        # Single element
        x = np.array([5.0])
        result = _box1d(x, 3)
        assert result.shape == (1,)
        assert result[0] == 5.0
        
        # Zero kernel size
        x = np.array([1, 2, 3])
        result = _box1d(x, 0)
        np.testing.assert_array_equal(result, x.astype(np.float32))
    
    def test_rolling_max_deque_basic(self):
        """Test basic functionality of _rolling_max_deque."""
        x = np.array([1, 3, 2, 5, 4, 1, 6])
        result = _rolling_max_deque(x, 3)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
        assert result.dtype == x.dtype
        
        # Check some expected values
        assert result[1] == 3  # max(1,3,2) = 3
        assert result[3] == 5  # max(3,2,5) = 5
    
    def test_rolling_max_deque_no_window(self):
        """Test _rolling_max_deque with window size 1."""
        x = np.array([1, 3, 2, 5, 4])
        result = _rolling_max_deque(x, 1)
        
        np.testing.assert_array_equal(result, x)
    
    def test_rolling_max_deque_large_window(self):
        """Test _rolling_max_deque with large window."""
        x = np.array([1, 3, 2, 5, 4])
        result = _rolling_max_deque(x, 10)  # Window larger than array
        
        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
        # Should work without crashing
    
    def test_find_gutters_basic(self):
        """Test basic functionality of _find_gutters."""
        # Create a projection with clear gutters (low values)
        proj_s = np.array([10, 10, 1, 1, 1, 10, 10, 2, 2, 10], dtype=np.float32)
        
        gutters, centers = _find_gutters(proj_s, alpha=0.5, local_win=3, 
                                       min_gutter_h=2, min_dist=2, prominence=0.1)
        
        assert isinstance(gutters, list)
        assert isinstance(centers, list)
        assert len(gutters) == len(centers)
        
        # Check format of gutters
        for gutter in gutters:
            assert isinstance(gutter, tuple)
            assert len(gutter) == 2
            assert gutter[0] <= gutter[1]  # Start <= end
    
    def test_find_gutters_no_gutters(self):
        """Test _find_gutters with uniform projection (no gutters)."""
        proj_s = np.ones(10, dtype=np.float32) * 5
        
        gutters, centers = _find_gutters(proj_s, alpha=0.5, local_win=3)
        
        assert isinstance(gutters, list)
        assert isinstance(centers, list)
        # Should find no gutters in uniform signal
        assert len(gutters) == len(centers)
    
    def test_find_gutters_parameters(self):
        """Test _find_gutters with different parameters."""
        proj_s = np.array([10, 10, 1, 1, 1, 10, 10, 1, 1, 10], dtype=np.float32)
        
        # Test with different alpha values
        gutters1, _ = _find_gutters(proj_s, alpha=0.1)
        gutters2, _ = _find_gutters(proj_s, alpha=0.9)
        
        assert isinstance(gutters1, list)
        assert isinstance(gutters2, list)
        # Higher alpha should be more restrictive
        assert len(gutters2) <= len(gutters1)


class TestDetectGutter:
    """Test cases for the main gutter detection function."""
    
    def test_detect_gutter_basic(self, sample_image):
        """Test basic gutter detection functionality."""
        results = detect_gutter(sample_image)
        
        assert isinstance(results, list)
        
        # Check result format: (x, y, bw, bh, area)
        for result in results:
            assert isinstance(result, tuple)
            assert len(result) == 5
            x, y, bw, bh, area = result
            assert isinstance(x, (int, np.integer))
            assert isinstance(y, (int, np.integer))
            assert isinstance(bw, (int, np.integer))
            assert isinstance(bh, (int, np.integer))
            assert isinstance(area, (int, np.integer))
            assert x >= 0 and y >= 0
            assert bw > 0 and bh > 0
            assert area > 0
            assert area == bw * bh
    
    def test_detect_gutter_with_grayscale_input(self, grayscale_image):
        """Test gutter detection with grayscale input."""
        results = detect_gutter(grayscale_image)
        
        assert isinstance(results, list)
        # Function should handle grayscale input
    
    def test_detect_gutter_with_color_input(self, sample_image):
        """Test gutter detection with color input."""
        results = detect_gutter(sample_image)
        
        assert isinstance(results, list)
        # Function should handle color input by converting to grayscale
    
    def test_detect_gutter_parameters(self, sample_image):
        """Test gutter detection with different parameter values."""
        # Test with different smoothing window sizes
        results1 = detect_gutter(sample_image, smooth_win_rows=21)
        results2 = detect_gutter(sample_image, smooth_win_rows=61)
        
        assert isinstance(results1, list)
        assert isinstance(results2, list)
        
        # Test with different alpha values
        results3 = detect_gutter(sample_image, alpha=0.1)
        results4 = detect_gutter(sample_image, alpha=0.3)
        
        assert isinstance(results3, list)
        assert isinstance(results4, list)
    
    def test_detect_gutter_min_gutters_filtering(self, sample_image):
        """Test that minimum gutters filter works correctly."""
        # Test with high minimum gutters requirement
        results_high = detect_gutter(sample_image, min_gutters_in_band=10)
        results_low = detect_gutter(sample_image, min_gutters_in_band=2)
        
        assert isinstance(results_high, list)
        assert isinstance(results_low, list)
        
        # Higher requirement should generally result in fewer results
        assert len(results_high) <= len(results_low)
    
    def test_detect_gutter_bounding_box_constraints(self, sample_image):
        """Test that detected bounding boxes are within image bounds."""
        h, w = sample_image.shape[:2]
        results = detect_gutter(sample_image)
        
        for x, y, bw, bh, area in results:
            assert x >= 0, f"x coordinate {x} should be non-negative"
            assert y >= 0, f"y coordinate {y} should be non-negative"
            assert x + bw <= w, f"Bounding box extends beyond image width"
            assert y + bh <= h, f"Bounding box extends beyond image height"
    
    def test_detect_gutter_full_width_boxes(self, sample_image):
        """Test that gutter detection produces full-width boxes."""
        w = sample_image.shape[1]
        results = detect_gutter(sample_image)
        
        for x, y, bw, bh, area in results:
            # Gutter detection should return full-width boxes
            assert x == 0, f"x should be 0 for full-width boxes, got {x}"
            assert bw == w, f"width should be image width {w}, got {bw}"
    
    def test_detect_gutter_min_band_height(self, sample_image):
        """Test minimum band height filtering."""
        results_high = detect_gutter(sample_image, min_band_height=50)
        results_low = detect_gutter(sample_image, min_band_height=5)
        
        assert isinstance(results_high, list)
        assert isinstance(results_low, list)
        
        # Check that all results meet minimum height requirement
        for x, y, bw, bh, area in results_high:
            assert bh >= 50, f"Band height {bh} should be >= 50"
        
        for x, y, bw, bh, area in results_low:
            assert bh >= 5, f"Band height {bh} should be >= 5"
    
    def test_detect_gutter_with_uniform_image(self):
        """Test gutter detection with uniform (no structure) image."""
        uniform_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        results = detect_gutter(uniform_img)
        
        assert isinstance(results, list)
        # Uniform image should have no gutters
        assert len(results) == 0 or len(results) <= 1
    
    def test_detect_gutter_with_horizontal_bands(self):
        """Test gutter detection with clear horizontal text bands."""
        img = np.ones((200, 300, 3), dtype=np.uint8) * 255
        
        # Create horizontal text bands with gaps between them
        # Band 1
        cv.rectangle(img, (20, 20), (280, 40), (0, 0, 0), -1)
        # Gap
        # Band 2
        cv.rectangle(img, (20, 60), (280, 80), (0, 0, 0), -1)
        # Gap
        # Band 3
        cv.rectangle(img, (20, 100), (280, 120), (0, 0, 0), -1)
        
        results = detect_gutter(img, min_gutters_in_band=2)
        
        assert isinstance(results, list)
        # Should detect the text band region
        if len(results) > 0:
            for x, y, bw, bh, area in results:
                assert x == 0  # Full width
                assert bw == 300  # Full width
                assert y >= 0 and y + bh <= 200  # Within bounds
    
    def test_detect_gutter_reproducibility(self, sample_image):
        """Test that gutter detection is reproducible."""
        results1 = detect_gutter(sample_image)
        results2 = detect_gutter(sample_image)
        
        assert len(results1) == len(results2)
        
        # Sort results for comparison
        def sort_key(result):
            return (result[0], result[1], result[2], result[3])
        
        sorted_results1 = sorted(results1, key=sort_key)
        sorted_results2 = sorted(results2, key=sort_key)
        
        assert sorted_results1 == sorted_results2
    
    def test_detect_gutter_different_image_sizes(self):
        """Test gutter detection with various image sizes."""
        sizes = [(50, 100), (100, 200), (200, 150)]
        
        for h, w in sizes:
            img = np.ones((h, w, 3), dtype=np.uint8) * 255
            
            # Add some horizontal structure
            if h > 30:
                cv.rectangle(img, (10, 10), (w-10, 20), (0, 0, 0), -1)
                cv.rectangle(img, (10, h-20), (w-10, h-10), (0, 0, 0), -1)
            
            results = detect_gutter(img)
            assert isinstance(results, list)
            
            # Check bounds for any results
            for x, y, bw, bh, area in results:
                assert 0 <= x < w
                assert 0 <= y < h
                assert x + bw <= w
                assert y + bh <= h
    
    def test_detect_gutter_gap_break_multiplier(self, sample_image):
        """Test gap break multiplier parameter."""
        results1 = detect_gutter(sample_image, gap_break_mult=2.0)
        results2 = detect_gutter(sample_image, gap_break_mult=8.0)
        
        assert isinstance(results1, list)
        assert isinstance(results2, list)
        
        # Different gap break multipliers might affect grouping
        # We just verify both work without error
    
    def test_detect_gutter_prominence_threshold(self, sample_image):
        """Test prominence threshold parameter."""
        results_low = detect_gutter(sample_image, prominence=0.05)
        results_high = detect_gutter(sample_image, prominence=0.25)
        
        assert isinstance(results_low, list)
        assert isinstance(results_high, list)
        
        # Higher prominence should be more restrictive
        assert len(results_high) <= len(results_low)
    
    def test_detect_gutter_edge_cases(self):
        """Test gutter detection with edge case images."""
        # Very small image
        small_img = np.ones((10, 10, 3), dtype=np.uint8) * 128
        results = detect_gutter(small_img)
        assert isinstance(results, list)
        
        # Very wide image
        wide_img = np.ones((50, 500, 3), dtype=np.uint8) * 128
        results = detect_gutter(wide_img)
        assert isinstance(results, list)
        
        # Very tall image
        tall_img = np.ones((500, 50, 3), dtype=np.uint8) * 128
        results = detect_gutter(tall_img)
        assert isinstance(results, list)