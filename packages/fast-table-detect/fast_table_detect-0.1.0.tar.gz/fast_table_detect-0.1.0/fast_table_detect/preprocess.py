
from typing import Tuple, List, Any, Dict
import numpy as np
import cv2 as cv

def _otsu(gray: np.ndarray, 
                  gaussian_kernel: Tuple[int, int] = (5, 5),
                  gaussian_sigma: float = 0,
                  ) -> Tuple[int, np.ndarray]:
    """
    Preprocess an image for table detection by applying
    Gaussian blur, thresholding.
    
    Args:
        img: Input BGR image as numpy array
        gaussian_kernel: Kernel size for Gaussian blur (width, height)
        gaussian_sigma: Standard deviation for Gaussian kernel. If 0, calculated from kernel size
        
    Returns:
        Binary edge-detected image as numpy array
    """
    blur = cv.GaussianBlur(gray, gaussian_kernel, gaussian_sigma)
    thresh, img_bin = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    img_bin = cv.bitwise_not(img_bin)
    return thresh, img_bin

def _canny(gray: np.ndarray, ret: int) -> np.ndarray:
    """
    Apply Canny edge detection with thresholds derived from threshold value.
    
    Args:
        gray: Grayscale image as numpy array
        ret: Threshold value used to calculate Canny low/high thresholds
        
    Returns:
        Binary edge-detected image as numpy array
    """
    low = max(0, int(ret/2))
    high = min(255, int(ret))
    edges = cv.Canny(gray, low, high)
    return edges

def _projection(img, axis, y0=None, y1=None, x0=None, x1=None):
    """
    Sum of ink along axis (axis=1 for rows, axis=0 for columns).
    Optional cropping.
    """
    H, W = img.shape[:2]
    if y0 is None: y0 = 0
    if y1 is None: y1 = H
    if x0 is None: x0 = 0
    if x1 is None: x1 = W
    roi = img[y0:y1, x0:x1]
    return roi.sum(axis=axis).astype(np.float32)


def _box1d(x: np.ndarray, k: int) -> np.ndarray:
    if k <= 1:
        return x.astype(np.float32)
    pad = k // 2
    xp = np.pad(x.astype(np.float32), (pad, pad), mode='reflect')
    ker = np.ones(k, dtype=np.float32) / float(k)
    return np.convolve(xp, ker, mode='valid')

def _angle_scan_score(ink_small, angles, smooth_k=31):
    """
    For each angle, rotate and compute row-ink projection variance.
    Higher variance => sharper gutters/lines.
    """
    H, W = ink_small.shape
    c = (W / 2, H / 2)
    best_angle, best_score = 0.0, -1.0
    for a in angles:
        M = cv.getRotationMatrix2D(c, a, 1.0)
        rot = cv.warpAffine(ink_small, M, (W, H), flags=cv.INTER_NEAREST, borderValue=0)
        proj = _projection(rot, axis=1)
        proj_s = _box1d(proj, smooth_k)
        score = np.var(proj_s)
        if score > best_score:
            best_score, best_angle = score, a
    return best_angle


def _deskew_small_scan(img, max_angle=3.0, step=0.25):
    """
    Deskew by scanning a small angle range and picking the angle
    that maximizes row-projection variance.
    """
    # downscale for speed
    scale = 1000.0 / max(img.shape)  # bring max dim near 1000px
    scale = min(1.0, scale)
    if scale < 1.0:
        small = cv.resize(img, (int(img.shape[1]*scale), int(img.shape[0]*scale)), interpolation=cv.INTER_NEAREST)
    else:
        small = img

    angles = np.arange(-max_angle, max_angle + 1e-6, step)
    best_angle = _angle_scan_score(small, angles)
    return float(best_angle)


def _rotate_image(img, angle_deg):
    H, W = img.shape[:2]
    c = (W / 2, H / 2)
    M = cv.getRotationMatrix2D(c, angle_deg, 1.0)
    return cv.warpAffine(img, M, (W, H), flags=cv.INTER_NEAREST, borderValue=0)


def preprocess(img: np.ndarray, kernel=(5,5), sigma=0)->np.ndarray:
    gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    thresh, image_bin = _otsu(gray, gaussian_kernel=kernel, gaussian_sigma=sigma)
    best_angle = _deskew_small_scan(image_bin)
    return _rotate_image(image_bin, best_angle)

