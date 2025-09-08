from typing import Tuple, List, Any, Dict
import numpy as np
import cv2 as cv
from .preprocess import preprocess
def _detect_lines(img: np.ndarray, use_hough_polish: bool = False)->Tuple[np.ndarray, np.ndarray]:
    bin_img = preprocess(img)
    h, w = bin_img.shape[:2]
    bin_thin = cv.morphologyEx(bin_img, cv.MORPH_OPEN, np.ones((2,2),np.uint8), iterations=1)
    k_horiz = max(10, w // 40)
    k_vert = max(10, h // 40)
    horiz_kernel = cv.getStructuringElement(cv.MORPH_RECT, (k_horiz, 1))
    vert_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, k_vert))
    horiz = cv.morphologyEx(bin_thin, cv.MORPH_OPEN, horiz_kernel, iterations=1)
    vert = cv.morphologyEx(bin_thin, cv.MORPH_OPEN, vert_kernel, iterations=1)
    if use_hough_polish:
        lines = cv.HoughLinesP(horiz, rho=1, theta=np.pi/180, threshold=80,
                                minLineLength=k_horiz, maxLineGap=k_horiz//2)
        horiz = np.zeros_like(horiz)
        if lines is not None:
            for l in lines[:,0,:]:
                x1,y1,x2,y2 = l
                cv.line(horiz, (x1,y1), (x2,y2), 255, 1)

        lines = cv.HoughLinesP(vert, rho=1, theta=np.pi/180, threshold=80,
                        minLineLength=k_vert, maxLineGap=k_vert//2)
        vert = np.zeros_like(vert)
        if lines is not None:
            for l in lines[:,0,:]:
                x1,y1,x2,y2 = l
                cv.line(vert, (x1,y1), (x2,y2), 255, 1)
    return horiz, vert

def detect_table_with_lines(horiz: np.ndarray, vert: np.ndarray, surface: float = 0.005)->List[Tuple[int,int,int,int,int]]:
    grid = cv.bitwise_or(horiz, vert)
    inter = cv.bitwise_and(horiz, vert)
    grid = cv.dilate(grid, np.ones((2,2), np.uint8), iterations=1)
    inter = cv.dilate(inter, np.ones((2,2), np.uint8), iterations=1)
    num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(grid, connectivity=8)
    page_area = grid.shape[0] * grid.shape[1]
    min_area = int(page_area * surface)
    candidates = []
    for i in range(1, num_labels):  # skip background
        x, y, bw, bh, area = stats[i]
        if area >= min_area:
            candidates.append((x, y, bw, bh, area))
    return candidates
