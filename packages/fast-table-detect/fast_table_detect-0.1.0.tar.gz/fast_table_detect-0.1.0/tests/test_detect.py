import pytest
import numpy as np
import cv2 as cv
from fast_table_detect.detect import detect_tables


class TestDetectTables:
    """Test cases for the main table detection function."""
    
    def test_detect_tables_with_sample_image(self, sample_image):
        """Test table detection with a well-formed table image."""
        results = detect_tables(sample_image)
        
        assert isinstance(results, list)
        assert len(results) >= 1, "Should detect at least one table"
        
        # Check result format: (x, y, w, h, area)
        for result in results:
            assert isinstance(result, tuple)
            assert len(result) == 5
            x, y, w, h, area = result
            assert isinstance(x, (int, np.integer))
            assert isinstance(y, (int, np.integer))
            assert isinstance(w, (int, np.integer))
            assert isinstance(h, (int, np.integer))
            assert isinstance(area, (int, np.integer))
            assert x >= 0 and y >= 0
            assert w > 0 and h > 0
            assert area > 0
            assert area == w * h
    
    def test_detect_tables_with_empty_image(self, empty_image):
        """Test table detection with an empty image."""
        results = detect_tables(empty_image)
        
        assert isinstance(results, list)
        # Empty image might return empty results or small noise detections
        # We just verify the function doesn't crash and returns valid format
    
    def test_detect_tables_with_grayscale_input(self, grayscale_image):
        """Test that the function works with grayscale input."""
        # Convert grayscale to RGB for input
        rgb_image = cv.cvtColor(grayscale_image, cv.COLOR_GRAY2RGB)
        results = detect_tables(rgb_image)
        
        assert isinstance(results, list)
        # Should be able to process grayscale-converted images
    
    def test_detect_tables_output_format(self, sample_image):
        """Test that all output tuples have the correct format."""
        results = detect_tables(sample_image)
        
        for result in results:
            x, y, w, h, area = result
            
            # Check types
            assert all(isinstance(val, (int, np.integer)) for val in result)
            
            # Check logical constraints
            assert x >= 0, f"x coordinate should be non-negative, got {x}"
            assert y >= 0, f"y coordinate should be non-negative, got {y}"
            assert w > 0, f"width should be positive, got {w}"
            assert h > 0, f"height should be positive, got {h}"
            assert area > 0, f"area should be positive, got {area}"
            assert area == w * h, f"area {area} should equal w*h {w*h}"
    
    def test_detect_tables_with_noisy_image(self, noisy_image):
        """Test table detection with a noisy image."""
        results = detect_tables(noisy_image)
        
        assert isinstance(results, list)
        # Function should handle noisy images without crashing
    
    def test_detect_tables_bounding_box_constraints(self, sample_image):
        """Test that detected bounding boxes are within image bounds."""
        h, w = sample_image.shape[:2]
        results = detect_tables(sample_image)
        
        for x, y, box_w, box_h, area in results:
            assert x + box_w <= w, f"Bounding box extends beyond image width"
            assert y + box_h <= h, f"Bounding box extends beyond image height"
    
    def test_detect_tables_minimum_area_filtering(self, sample_image):
        """Test that results respect minimum area constraints."""
        results = detect_tables(sample_image)
        h, w = sample_image.shape[:2]
        page_area = h * w
        min_area_threshold = 0.005 * page_area
        
        for x, y, box_w, box_h, area in results:
            # The function should filter out very small areas
            assert area >= min_area_threshold * 0.1, "Area should not be too small"
    
    def test_detect_tables_reproducibility(self, sample_image):
        """Test that the function produces consistent results."""
        results1 = detect_tables(sample_image)
        results2 = detect_tables(sample_image)
        
        assert len(results1) == len(results2), "Function should be deterministic"
        
        # Sort results for comparison (since order might vary)
        def sort_key(result):
            return (result[0], result[1], result[2], result[3])
        
        sorted_results1 = sorted(results1, key=sort_key)
        sorted_results2 = sorted(results2, key=sort_key)
        
        assert sorted_results1 == sorted_results2, "Results should be identical"
    
    def test_detect_tables_with_different_image_sizes(self):
        """Test table detection with various image sizes."""
        sizes = [(100, 100), (200, 300), (400, 600), (50, 200)]
        
        for h, w in sizes:
            # Create a simple table image
            img = np.ones((h, w, 3), dtype=np.uint8) * 255
            
            # Add a simple rectangular structure
            if h > 20 and w > 20:
                cv.rectangle(img, (10, 10), (w-10, h-10), (0, 0, 0), 2)
                if h > 40:
                    cv.line(img, (10, h//2), (w-10, h//2), (0, 0, 0), 2)
                if w > 40:
                    cv.line(img, (w//2, 10), (w//2, h-10), (0, 0, 0), 2)
            
            results = detect_tables(img)
            assert isinstance(results, list), f"Failed for size {h}x{w}"
    
    def test_detect_tables_edge_cases(self):
        """Test edge cases for table detection."""
        # Very small image
        small_img = np.ones((10, 10, 3), dtype=np.uint8) * 255
        results = detect_tables(small_img)
        assert isinstance(results, list)
        
        # Single pixel wide/tall image
        narrow_img = np.ones((100, 1, 3), dtype=np.uint8) * 255
        results = detect_tables(narrow_img)
        assert isinstance(results, list)
        
        tall_img = np.ones((1, 100, 3), dtype=np.uint8) * 255
        results = detect_tables(tall_img)
        assert isinstance(results, list)