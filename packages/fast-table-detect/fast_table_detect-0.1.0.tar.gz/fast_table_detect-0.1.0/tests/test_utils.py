import pytest
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
from fast_table_detect.utils import (
    plot_table_candidates, display_detection_results, save_detection_results,
    filter_candidates_by_area, get_candidate_info
)


class TestPlotTableCandidates:
    """Test cases for plot_table_candidates function."""
    
    def test_plot_table_candidates_basic(self, sample_image):
        """Test basic functionality of plot_table_candidates."""
        candidates = [(50, 50, 100, 80, 8000), (200, 100, 120, 90, 10800)]
        
        result_img = plot_table_candidates(sample_image, candidates)
        
        assert isinstance(result_img, np.ndarray)
        assert result_img.shape == sample_image.shape
        assert result_img.dtype == sample_image.dtype
        
        # Should not be identical to original (rectangles added)
        assert not np.array_equal(result_img, sample_image)
    
    def test_plot_table_candidates_empty_list(self, sample_image):
        """Test plot_table_candidates with empty candidates list."""
        candidates = []
        
        result_img = plot_table_candidates(sample_image, candidates)
        
        assert isinstance(result_img, np.ndarray)
        assert result_img.shape == sample_image.shape
        # Should be identical to original (no rectangles added)
        np.testing.assert_array_equal(result_img, sample_image)
    
    def test_plot_table_candidates_with_area_display(self, sample_image):
        """Test plot_table_candidates with area text display."""
        candidates = [(50, 50, 100, 80, 8000)]
        
        result_img = plot_table_candidates(sample_image, candidates, show_area=True)
        
        assert isinstance(result_img, np.ndarray)
        assert result_img.shape == sample_image.shape
        assert not np.array_equal(result_img, sample_image)
    
    def test_plot_table_candidates_different_colors(self, sample_image):
        """Test plot_table_candidates with different colors."""
        candidates = [(50, 50, 100, 80, 8000)]
        
        # Test with red color
        result_red = plot_table_candidates(sample_image, candidates, color=(0, 0, 255))
        
        # Test with blue color
        result_blue = plot_table_candidates(sample_image, candidates, color=(255, 0, 0))
        
        assert isinstance(result_red, np.ndarray)
        assert isinstance(result_blue, np.ndarray)
        assert not np.array_equal(result_red, result_blue)
    
    def test_plot_table_candidates_different_thickness(self, sample_image):
        """Test plot_table_candidates with different line thickness."""
        candidates = [(50, 50, 100, 80, 8000)]
        
        result_thin = plot_table_candidates(sample_image, candidates, thickness=1)
        result_thick = plot_table_candidates(sample_image, candidates, thickness=5)
        
        assert isinstance(result_thin, np.ndarray)
        assert isinstance(result_thick, np.ndarray)
        # Different thickness should produce different results
        assert not np.array_equal(result_thin, result_thick)
    
    def test_plot_table_candidates_bounds_check(self, sample_image):
        """Test plot_table_candidates with candidates at image boundaries."""
        h, w = sample_image.shape[:2]
        
        # Candidates at boundaries
        candidates = [
            (0, 0, 50, 50, 2500),          # Top-left corner
            (w-50, h-50, 50, 50, 2500),    # Bottom-right corner
            (0, h//2, w, 50, w*50)         # Full width
        ]
        
        result_img = plot_table_candidates(sample_image, candidates)
        
        assert isinstance(result_img, np.ndarray)
        assert result_img.shape == sample_image.shape
    
    def test_plot_table_candidates_large_area_values(self, sample_image):
        """Test plot_table_candidates with large area values."""
        candidates = [(50, 50, 100, 80, 123456789)]  # Very large area
        
        result_img = plot_table_candidates(sample_image, candidates, show_area=True)
        
        assert isinstance(result_img, np.ndarray)
        assert result_img.shape == sample_image.shape


class TestDisplayDetectionResults:
    """Test cases for display_detection_results function."""
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.imshow')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.axis')
    @patch('matplotlib.pyplot.tight_layout')
    def test_display_detection_results_basic(self, mock_tight_layout, mock_axis, 
                                          mock_title, mock_imshow, mock_figure, mock_show,
                                          sample_image):
        """Test basic functionality of display_detection_results."""
        candidates = [(50, 50, 100, 80, 8000)]
        
        display_detection_results(sample_image, candidates)
        
        # Verify matplotlib functions were called
        mock_figure.assert_called_once()
        mock_imshow.assert_called_once()
        mock_title.assert_called_once()
        mock_axis.assert_called_once_with('off')
        mock_tight_layout.assert_called_once()
        mock_show.assert_called_once()
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.imshow')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.axis')
    @patch('matplotlib.pyplot.tight_layout')
    def test_display_detection_results_custom_title(self, mock_tight_layout, mock_axis,
                                                  mock_title, mock_imshow, mock_figure, mock_show,
                                                  sample_image):
        """Test display_detection_results with custom title."""
        candidates = [(50, 50, 100, 80, 8000)]
        custom_title = "Custom Table Detection"
        
        display_detection_results(sample_image, candidates, title=custom_title)
        
        # Check that title was called with expected string
        mock_title.assert_called_once()
        title_arg = mock_title.call_args[0][0]
        assert custom_title in title_arg
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.imshow')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.axis')
    @patch('matplotlib.pyplot.tight_layout')
    def test_display_detection_results_grayscale(self, mock_tight_layout, mock_axis,
                                               mock_title, mock_imshow, mock_figure, mock_show,
                                               grayscale_image):
        """Test display_detection_results with grayscale image."""
        candidates = [(25, 25, 50, 50, 2500)]
        
        display_detection_results(grayscale_image, candidates)
        
        # Should handle grayscale images
        mock_imshow.assert_called_once()


class TestSaveDetectionResults:
    """Test cases for save_detection_results function."""
    
    @patch('cv2.imwrite')
    @patch('builtins.print')
    def test_save_detection_results_basic(self, mock_print, mock_imwrite, sample_image, tmp_path):
        """Test basic functionality of save_detection_results."""
        candidates = [(50, 50, 100, 80, 8000)]
        output_path = str(tmp_path / "test_output.jpg")
        
        save_detection_results(sample_image, candidates, output_path)
        
        # Verify cv2.imwrite was called
        mock_imwrite.assert_called_once()
        call_args = mock_imwrite.call_args[0]
        assert call_args[0] == output_path
        assert isinstance(call_args[1], np.ndarray)
        
        # Verify print statement
        mock_print.assert_called_once()
    
    @patch('cv2.imwrite')
    @patch('builtins.print')
    def test_save_detection_results_no_area(self, mock_print, mock_imwrite, sample_image, tmp_path):
        """Test save_detection_results without showing area."""
        candidates = [(50, 50, 100, 80, 8000)]
        output_path = str(tmp_path / "test_output.jpg")
        
        save_detection_results(sample_image, candidates, output_path, show_area=False)
        
        mock_imwrite.assert_called_once()
        mock_print.assert_called_once()


class TestFilterCandidatesByArea:
    """Test cases for filter_candidates_by_area function."""
    
    def test_filter_candidates_by_area_basic(self):
        """Test basic area filtering functionality."""
        candidates = [
            (10, 10, 20, 30, 600),    # area = 600
            (50, 50, 100, 80, 8000),  # area = 8000
            (100, 100, 10, 10, 100),  # area = 100
            (200, 200, 50, 40, 2000)  # area = 2000
        ]
        
        filtered = filter_candidates_by_area(candidates, min_area=500, max_area=5000)
        
        assert isinstance(filtered, list)
        assert len(filtered) == 2  # Should keep 600 and 2000
        
        areas = [candidate[4] for candidate in filtered]
        assert all(500 <= area <= 5000 for area in areas)
    
    def test_filter_candidates_by_area_min_only(self):
        """Test filtering with minimum area only."""
        candidates = [
            (10, 10, 20, 30, 600),
            (50, 50, 100, 80, 8000),
            (100, 100, 10, 10, 100)
        ]
        
        filtered = filter_candidates_by_area(candidates, min_area=500)
        
        assert len(filtered) == 2  # Should exclude area = 100
        areas = [candidate[4] for candidate in filtered]
        assert all(area >= 500 for area in areas)
    
    def test_filter_candidates_by_area_max_only(self):
        """Test filtering with maximum area only."""
        candidates = [
            (10, 10, 20, 30, 600),
            (50, 50, 100, 80, 8000),
            (100, 100, 10, 10, 100)
        ]
        
        filtered = filter_candidates_by_area(candidates, max_area=1000)
        
        assert len(filtered) == 2  # Should exclude area = 8000
        areas = [candidate[4] for candidate in filtered]
        assert all(area <= 1000 for area in areas)
    
    def test_filter_candidates_by_area_no_filter(self):
        """Test filtering with no constraints."""
        candidates = [
            (10, 10, 20, 30, 600),
            (50, 50, 100, 80, 8000),
        ]
        
        filtered = filter_candidates_by_area(candidates)
        
        assert len(filtered) == len(candidates)
        assert filtered == candidates
    
    def test_filter_candidates_by_area_empty_input(self):
        """Test filtering with empty input."""
        candidates = []
        
        filtered = filter_candidates_by_area(candidates, min_area=100, max_area=1000)
        
        assert isinstance(filtered, list)
        assert len(filtered) == 0
    
    def test_filter_candidates_by_area_no_matches(self):
        """Test filtering where no candidates match criteria."""
        candidates = [
            (10, 10, 20, 30, 600),
            (50, 50, 100, 80, 8000),
        ]
        
        filtered = filter_candidates_by_area(candidates, min_area=1000, max_area=2000)
        
        assert isinstance(filtered, list)
        assert len(filtered) == 0


class TestGetCandidateInfo:
    """Test cases for get_candidate_info function."""
    
    @patch('builtins.print')
    def test_get_candidate_info_basic(self, mock_print):
        """Test basic functionality of get_candidate_info."""
        candidates = [
            (10, 20, 30, 40, 1200),
            (50, 60, 70, 80, 5600),
            (100, 110, 120, 130, 15600)
        ]
        
        get_candidate_info(candidates)
        
        # Verify print was called multiple times (header, separator, data, stats)
        assert mock_print.call_count >= 5
        
        # Check some of the printed content
        printed_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        printed_text = ' '.join(printed_calls)
        
        assert 'Found 3 table candidates' in printed_text
        assert 'Min area: 1200' in printed_text
        assert 'Max area: 15600' in printed_text
    
    @patch('builtins.print')
    def test_get_candidate_info_empty_input(self, mock_print):
        """Test get_candidate_info with empty input."""
        candidates = []
        
        get_candidate_info(candidates)
        
        mock_print.assert_called_once_with("No candidates found.")
    
    @patch('builtins.print')
    def test_get_candidate_info_single_candidate(self, mock_print):
        """Test get_candidate_info with single candidate."""
        candidates = [(10, 20, 30, 40, 1200)]
        
        get_candidate_info(candidates)
        
        # Should print information for 1 candidate
        printed_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        printed_text = ' '.join(printed_calls)
        
        assert 'Found 1 table candidates' in printed_text
        assert 'Min area: 1200' in printed_text
        assert 'Max area: 1200' in printed_text
        assert 'Mean area: 1200' in printed_text
        assert 'Median area: 1200' in printed_text
    
    @patch('builtins.print')
    def test_get_candidate_info_statistics(self, mock_print):
        """Test that statistics are calculated correctly."""
        candidates = [
            (0, 0, 10, 10, 100),    # area = 100
            (0, 0, 20, 20, 400),    # area = 400
            (0, 0, 30, 30, 900),    # area = 900
        ]
        
        get_candidate_info(candidates)
        
        printed_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        printed_text = ' '.join(printed_calls)
        
        # Check statistics
        assert 'Min area: 100' in printed_text
        assert 'Max area: 900' in printed_text
        assert 'Mean area: 466.7' in printed_text  # (100+400+900)/3 = 466.67
        assert 'Median area: 400' in printed_text
    
    @patch('builtins.print')
    def test_get_candidate_info_formatting(self, mock_print):
        """Test that output formatting is correct."""
        candidates = [
            (123, 456, 789, 101, 79889),
        ]
        
        get_candidate_info(candidates)
        
        printed_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        
        # Check that table headers are printed
        header_found = any('#' in call and 'X' in call and 'Y' in call for call in printed_calls)
        assert header_found
        
        # Check that separators are printed
        separator_found = any('-' * 10 in call for call in printed_calls)
        assert separator_found
        
        # Check that candidate data is printed with correct values
        data_found = any('123' in call and '456' in call and '789' in call for call in printed_calls)
        assert data_found