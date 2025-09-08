from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt


def plot_table_candidates(image: np.ndarray, 
                         candidates: List[Tuple[int, int, int, int, int]], 
                         color: Tuple[int, int, int] = (0, 255, 0),
                         thickness: int = 2,
                         show_area: bool = False,
                         figsize: Tuple[int, int] = (12, 8)) -> np.ndarray:
    """
    Draw green rectangles around detected table candidates on an image.
    
    Args:
        image: Input image as numpy array (BGR or RGB)
        candidates: List of tuples (x, y, width, height, area) from _detect_table_with_lines
        color: Rectangle color in BGR format (default: green)
        thickness: Rectangle border thickness in pixels
        show_area: Whether to display area text on rectangles
        figsize: Figure size for matplotlib display
        
    Returns:
        Image with drawn rectangles as numpy array
    """
    # Create a copy to avoid modifying the original image
    result_img = image.copy()
    
    # Draw rectangles for each candidate
    for i, (x, y, width, height, area) in enumerate(candidates):
        # Draw rectangle
        cv.rectangle(result_img, (x, y), (x + width, y + height), color, thickness)
        
        # Add area text if requested
        if show_area:
            text = f"Area: {area}"
            text_size = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            # Position text above the rectangle
            text_x = x
            text_y = max(y - 10, text_size[1] + 5)
            
            # Add background rectangle for text readability
            cv.rectangle(result_img, 
                        (text_x, text_y - text_size[1] - 5), 
                        (text_x + text_size[0] + 5, text_y + 5), 
                        (0, 0, 0), -1)
            
            # Add text
            cv.putText(result_img, text, (text_x + 2, text_y), 
                      cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return result_img


def display_detection_results(image: np.ndarray, 
                            candidates: List[Tuple[int, int, int, int, int]], 
                            title: str = "Table Detection Results",
                            figsize: Tuple[int, int] = (12, 8)) -> None:
    """
    Display the original image with detected table candidates using matplotlib.
    
    Args:
        image: Input image as numpy array (BGR format)
        candidates: List of tuples (x, y, width, height, area) from _detect_table_with_lines
        title: Plot title
        figsize: Figure size for matplotlib display
    """
    # Draw rectangles on the image
    result_img = plot_table_candidates(image, candidates, show_area=True)
    
    # Convert BGR to RGB for matplotlib
    if len(image.shape) == 3:
        result_img_rgb = cv.cvtColor(result_img, cv.COLOR_BGR2RGB)
    else:
        result_img_rgb = result_img
    
    # Create the plot
    plt.figure(figsize=figsize)
    plt.imshow(result_img_rgb, cmap='gray' if len(image.shape) == 2 else None)
    plt.title(f"{title} - Found {len(candidates)} candidates")
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def save_detection_results(image: np.ndarray, 
                          candidates: List[Tuple[int, int, int, int, int]], 
                          output_path: str,
                          show_area: bool = True) -> None:
    """
    Save the image with detected table candidates to a file.
    
    Args:
        image: Input image as numpy array (BGR format)
        candidates: List of tuples (x, y, width, height, area) from _detect_table_with_lines
        output_path: Path where to save the result image
        show_area: Whether to display area text on rectangles
    """
    # Draw rectangles on the image
    result_img = plot_table_candidates(image, candidates, show_area=show_area)
    
    # Save the image
    cv.imwrite(output_path, result_img)
    print(f"Detection results saved to: {output_path}")


def filter_candidates_by_area(candidates: List[Tuple[int, int, int, int, int]], 
                             min_area: Optional[int] = None, 
                             max_area: Optional[int] = None) -> List[Tuple[int, int, int, int, int]]:
    """
    Filter candidates by area constraints.
    
    Args:
        candidates: List of tuples (x, y, width, height, area) from _detect_table_with_lines
        min_area: Minimum area threshold (optional)
        max_area: Maximum area threshold (optional)
        
    Returns:
        Filtered list of candidates
    """
    filtered = []
    for candidate in candidates:
        x, y, width, height, area = candidate
        
        # Apply area filters
        if min_area is not None and area < min_area:
            continue
        if max_area is not None and area > max_area:
            continue
            
        filtered.append(candidate)
    
    return filtered


def get_candidate_info(candidates: List[Tuple[int, int, int, int, int]]) -> None:
    """
    Print information about detected candidates.
    
    Args:
        candidates: List of tuples (x, y, width, height, area) from _detect_table_with_lines
    """
    if not candidates:
        print("No candidates found.")
        return
    
    print(f"Found {len(candidates)} table candidates:")
    print("-" * 60)
    print(f"{'#':<3} {'X':<6} {'Y':<6} {'Width':<8} {'Height':<8} {'Area':<10}")
    print("-" * 60)
    
    for i, (x, y, width, height, area) in enumerate(candidates):
        print(f"{i+1:<3} {x:<6} {y:<6} {width:<8} {height:<8} {area:<10}")
    
    # Calculate statistics
    areas = [candidate[4] for candidate in candidates]
    print("-" * 60)
    print(f"Area statistics:")
    print(f"  Min area: {min(areas)}")
    print(f"  Max area: {max(areas)}")
    print(f"  Mean area: {np.mean(areas):.1f}")
    print(f"  Median area: {np.median(areas):.1f}")


# The following functions were designed for the dictionary format and are not compatible
# with the simplified _detect_table_with_lines function that returns just a list

# def plot_table_cells(...) - Not available with current simplified format
# def plot_table_lines(...) - Not available with current simplified format  
# def display_detection_debug(...) - Not available with current simplified format
# def get_detection_summary(...) - Not available with current simplified format