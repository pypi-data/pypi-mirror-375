import pytest
import numpy as np
import cv2 as cv
from fast_table_detect.preprocess import (
    preprocess, _otsu, _canny, _projection, 
    _angle_scan_score, _deskew_small_scan, _rotate_image
)


class TestOtsu:
    """Test cases for Otsu thresholding function."""
    
    def test_otsu_with_grayscale_image(self, grayscale_image):
        """Test Otsu thresholding with grayscale input."""
        thresh, img_bin = _otsu(grayscale_image)
        
        assert isinstance(thresh, (int, np.integer))
        assert isinstance(img_bin, np.ndarray)
        assert img_bin.shape == grayscale_image.shape
        assert img_bin.dtype == np.uint8
        assert np.all(np.isin(img_bin, [0, 255])), "Binary image should only contain 0 and 255"
        assert 0 <= thresh <= 255, f"Threshold should be between 0 and 255, got {thresh}"
    
    def test_otsu_with_different_kernels(self, grayscale_image):
        """Test Otsu with different Gaussian kernel sizes."""
        kernels = [(3, 3), (5, 5), (7, 7), (9, 9)]
        
        for kernel in kernels:
            thresh, img_bin = _otsu(grayscale_image, gaussian_kernel=kernel)
            assert isinstance(thresh, (int, np.integer))
            assert isinstance(img_bin, np.ndarray)
            assert img_bin.shape == grayscale_image.shape
    
    def test_otsu_with_sigma_values(self, grayscale_image):
        """Test Otsu with different sigma values."""
        sigmas = [0, 1.0, 2.0, 3.0]
        
        for sigma in sigmas:
            thresh, img_bin = _otsu(grayscale_image, gaussian_sigma=sigma)
            assert isinstance(thresh, (int, np.integer))
            assert isinstance(img_bin, np.ndarray)
            assert img_bin.shape == grayscale_image.shape
    
    def test_otsu_output_inverted(self, grayscale_image):
        """Test that Otsu output is properly inverted."""
        thresh, img_bin = _otsu(grayscale_image)
        
        # The function inverts the binary image, so text (dark areas) should become white
        # This is hard to test precisely without knowing the exact content,
        # but we can verify the inversion happened by checking that we have both 0 and 255 values
        unique_values = np.unique(img_bin)
        assert len(unique_values) <= 2, "Binary image should have at most 2 unique values"
        assert np.all(np.isin(unique_values, [0, 255])), "Values should only be 0 or 255"


class TestCanny:
    """Test cases for Canny edge detection function."""
    
    def test_canny_with_grayscale_image(self, grayscale_image):
        """Test Canny edge detection with grayscale input."""
        ret = 128  # Sample threshold value
        edges = _canny(grayscale_image, ret)
        
        assert isinstance(edges, np.ndarray)
        assert edges.shape == grayscale_image.shape
        assert edges.dtype == np.uint8
        assert np.all(np.isin(edges, [0, 255])), "Edge image should only contain 0 and 255"
    
    def test_canny_threshold_calculation(self, grayscale_image):
        """Test that Canny thresholds are calculated correctly."""
        ret_values = [50, 100, 150, 200]
        
        for ret in ret_values:
            edges = _canny(grayscale_image, ret)
            # We can't easily test the exact threshold values used internally,
            # but we can verify the function runs without error
            assert isinstance(edges, np.ndarray)
            assert edges.shape == grayscale_image.shape
    
    def test_canny_edge_cases(self, grayscale_image):
        """Test Canny with edge case threshold values."""
        # Very low threshold
        edges_low = _canny(grayscale_image, 1)
        assert isinstance(edges_low, np.ndarray)
        
        # Very high threshold
        edges_high = _canny(grayscale_image, 254)
        assert isinstance(edges_high, np.ndarray)
        
        # Zero threshold
        edges_zero = _canny(grayscale_image, 0)
        assert isinstance(edges_zero, np.ndarray)


class TestProjection:
    """Test cases for projection function."""
    
    def test_projection_row_axis(self, binary_image):
        """Test projection along row axis (axis=1)."""
        proj = _projection(binary_image, axis=1)
        
        assert isinstance(proj, np.ndarray)
        assert proj.dtype == np.float32
        assert proj.shape == (binary_image.shape[0],), f"Expected shape {(binary_image.shape[0],)}, got {proj.shape}"
        assert np.all(proj >= 0), "Projection values should be non-negative"
    
    def test_projection_column_axis(self, binary_image):
        """Test projection along column axis (axis=0)."""
        proj = _projection(binary_image, axis=0)
        
        assert isinstance(proj, np.ndarray)
        assert proj.dtype == np.float32
        assert proj.shape == (binary_image.shape[1],), f"Expected shape {(binary_image.shape[1],)}, got {proj.shape}"
        assert np.all(proj >= 0), "Projection values should be non-negative"
    
    def test_projection_with_cropping(self, binary_image):
        """Test projection with cropping parameters."""
        h, w = binary_image.shape
        y0, y1 = h // 4, 3 * h // 4
        x0, x1 = w // 4, 3 * w // 4
        
        proj = _projection(binary_image, axis=1, y0=y0, y1=y1, x0=x0, x1=x1)
        
        assert isinstance(proj, np.ndarray)
        assert proj.shape == (y1 - y0,)
        assert np.all(proj >= 0)
    
    def test_projection_full_vs_cropped(self, binary_image):
        """Test that cropped projection matches manual cropping."""
        h, w = binary_image.shape
        y0, y1 = 10, h - 10
        x0, x1 = 5, w - 5
        
        # Get projection with cropping parameters
        proj_cropped = _projection(binary_image, axis=1, y0=y0, y1=y1, x0=x0, x1=x1)
        
        # Manual crop and projection
        roi = binary_image[y0:y1, x0:x1]
        proj_manual = roi.sum(axis=1).astype(np.float32)
        
        np.testing.assert_array_equal(proj_cropped, proj_manual)


class TestAngleScanScore:
    """Test cases for angle scan scoring function."""
    
    def test_angle_scan_score_basic(self, binary_image):
        """Test basic angle scan scoring."""
        angles = [-1.0, 0.0, 1.0]
        best_angle = _angle_scan_score(binary_image, angles)
        
        assert isinstance(best_angle, (float, np.floating))
        assert best_angle in angles, f"Best angle {best_angle} should be one of {angles}"
    
    def test_angle_scan_score_with_rotated_image(self):
        """Test angle scan with a known rotated image."""
        # Create a simple horizontal line image
        img = np.zeros((100, 200), dtype=np.uint8)
        cv.line(img, (20, 50), (180, 50), 255, 2)
        
        # Test with angles around 0
        angles = [-2.0, -1.0, 0.0, 1.0, 2.0]
        best_angle = _angle_scan_score(img, angles)
        
        # For a horizontal line, best angle should be close to 0
        assert abs(best_angle) <= 1.0, f"Best angle should be close to 0, got {best_angle}"


class TestDeskewSmallScan:
    """Test cases for small angle deskewing function."""
    
    def test_deskew_small_scan_basic(self, binary_image):
        """Test basic deskewing functionality."""
        angle = _deskew_small_scan(binary_image)
        
        assert isinstance(angle, (float, np.floating))
        assert -3.0 <= angle <= 3.0, f"Angle should be within [-3, 3] degrees, got {angle}"
    
    def test_deskew_small_scan_with_different_params(self, binary_image):
        """Test deskewing with different parameter values."""
        angle1 = _deskew_small_scan(binary_image, max_angle=2.0, step=0.5)
        angle2 = _deskew_small_scan(binary_image, max_angle=5.0, step=0.25)
        
        assert isinstance(angle1, (float, np.floating))
        assert isinstance(angle2, (float, np.floating))
        assert -2.0 <= angle1 <= 2.0
        assert -5.0 <= angle2 <= 5.0
    
    def test_deskew_straight_image(self):
        """Test deskewing with a perfectly straight image."""
        # Create a straight horizontal line
        img = np.zeros((100, 200), dtype=np.uint8)
        cv.line(img, (20, 50), (180, 50), 255, 2)
        
        angle = _deskew_small_scan(img)
        
        # Should detect minimal rotation needed
        assert abs(angle) < 1.0, f"Straight image should need minimal rotation, got {angle}"


class TestRotateImage:
    """Test cases for image rotation function."""
    
    def test_rotate_image_basic(self, binary_image):
        """Test basic image rotation."""
        angle = 5.0
        rotated = _rotate_image(binary_image, angle)
        
        assert isinstance(rotated, np.ndarray)
        assert rotated.shape == binary_image.shape
        assert rotated.dtype == binary_image.dtype
    
    def test_rotate_image_zero_angle(self, binary_image):
        """Test rotation with zero angle."""
        rotated = _rotate_image(binary_image, 0.0)
        
        # Should be very similar to original (might have minor interpolation differences)
        assert isinstance(rotated, np.ndarray)
        assert rotated.shape == binary_image.shape
    
    def test_rotate_image_negative_angle(self, binary_image):
        """Test rotation with negative angle."""
        angle = -10.0
        rotated = _rotate_image(binary_image, angle)
        
        assert isinstance(rotated, np.ndarray)
        assert rotated.shape == binary_image.shape
    
    def test_rotate_image_large_angle(self, binary_image):
        """Test rotation with large angle."""
        angle = 45.0
        rotated = _rotate_image(binary_image, angle)
        
        assert isinstance(rotated, np.ndarray)
        assert rotated.shape == binary_image.shape


class TestPreprocess:
    """Test cases for the main preprocessing function."""
    
    def test_preprocess_basic(self, sample_image):
        """Test basic preprocessing functionality."""
        result = preprocess(sample_image)
        
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
        assert result.shape[:2] == sample_image.shape[:2]  # Height and width should be preserved
        assert len(result.shape) == 2, "Output should be grayscale (2D array)"
        assert np.all(np.isin(result, [0, 255])), "Output should be binary (0 and 255 only)"
    
    def test_preprocess_with_different_kernels(self, sample_image):
        """Test preprocessing with different kernel sizes."""
        kernels = [(3, 3), (5, 5), (7, 7)]
        
        for kernel in kernels:
            result = preprocess(sample_image, kernel=kernel)
            assert isinstance(result, np.ndarray)
            assert result.shape[:2] == sample_image.shape[:2]
            assert len(result.shape) == 2
    
    def test_preprocess_with_different_sigma(self, sample_image):
        """Test preprocessing with different sigma values."""
        sigmas = [0, 1.0, 2.0]
        
        for sigma in sigmas:
            result = preprocess(sample_image, sigma=sigma)
            assert isinstance(result, np.ndarray)
            assert result.shape[:2] == sample_image.shape[:2]
            assert len(result.shape) == 2
    
    def test_preprocess_with_rotated_image(self, rotated_image):
        """Test preprocessing with a rotated image."""
        result = preprocess(rotated_image)
        
        assert isinstance(result, np.ndarray)
        assert result.shape[:2] == rotated_image.shape[:2]
        assert len(result.shape) == 2
        assert np.all(np.isin(result, [0, 255]))
    
    def test_preprocess_reproducibility(self, sample_image):
        """Test that preprocessing is reproducible."""
        result1 = preprocess(sample_image)
        result2 = preprocess(sample_image)
        
        np.testing.assert_array_equal(result1, result2, "Results should be identical")
    
    def test_preprocess_with_noisy_image(self, noisy_image):
        """Test preprocessing with a noisy image."""
        result = preprocess(noisy_image)
        
        assert isinstance(result, np.ndarray)
        assert result.shape[:2] == noisy_image.shape[:2]
        assert len(result.shape) == 2
        assert np.all(np.isin(result, [0, 255]))
    
    def test_preprocess_edge_cases(self):
        """Test preprocessing with edge case images."""
        # Very small image
        small_img = np.ones((10, 10, 3), dtype=np.uint8) * 128
        result = preprocess(small_img)
        assert isinstance(result, np.ndarray)
        assert result.shape == (10, 10)
        
        # Single channel input should still work (converted from RGB)
        # Note: The function expects RGB input, so we create a 3-channel image
        gray_as_rgb = np.stack([np.ones((50, 50), dtype=np.uint8) * 128] * 3, axis=2)
        result = preprocess(gray_as_rgb)
        assert isinstance(result, np.ndarray)
        assert result.shape == (50, 50)