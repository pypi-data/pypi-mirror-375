import numpy as np
import cv2 as cv
from collections import deque
from typing import List, Tuple
from .preprocess import _box1d
# ---------------- helpers ----------------

def _ensure_odd(k: int, lo: int = 3) -> int:
    k = max(lo, int(k))
    return k if (k % 2 == 1) else (k + 1)


def _rolling_max_deque(x: np.ndarray, win: int) -> np.ndarray:
    n = x.size
    if win <= 1: return x.copy()
    pad = win // 2
    xp = np.pad(x, (pad, pad), mode='reflect')
    dq = deque()
    out = np.empty(n, dtype=x.dtype)
    for i in range(xp.size):
        while dq and xp[i] >= dq[-1][1]:
            dq.pop()
        dq.append((i, xp[i]))
        if dq[0][0] <= i - win:
            dq.popleft()
        if i >= win - 1:
            out[i - (win - 1)] = dq[0][1]
    return out

def _find_gutters(
    proj_s: np.ndarray,
    *,
    alpha: float = 0.18,
    local_win: int = 61,
    min_gutter_h: int = 2,
    min_dist: int = 6,
    prominence: float = 0.12
) -> Tuple[List[Tuple[int,int]], List[int]]:
    n = proj_s.size
    local_win = _ensure_odd(local_win, 3)

    rmax = _rolling_max_deque(proj_s, local_win)
    thr = alpha * np.maximum(rmax, 1e-6)
    low = proj_s < thr

    gutters = []
    i = 0
    while i < n:
        if low[i]:
            j = i + 1
            while j < n and low[j]:
                j += 1
            if (j - i) >= min_gutter_h:
                gutters.append((i, j - 1))
            i = j
        else:
            i += 1
    if not gutters:
        return [], []

    neigh = _box1d(proj_s, local_win)
    def depth(c: int) -> float:
        m = neigh[min(max(c, 0), n - 1)]
        return 0.0 if m <= 1e-6 else (m - proj_s[c]) / m

    cleaned, centers = [], []
    for a, b in gutters:
        c = (a + b) // 2
        if centers and (c - centers[-1]) < min_dist:
            if proj_s[c] < proj_s[centers[-1]]:
                cleaned[-1] = (a, b)
                centers[-1] = c
            continue
        if depth(c) >= float(prominence):
            cleaned.append((a, b))
            centers.append(c)
    return cleaned, centers

# ---------------- main API ----------------

def detect_gutter(
    img: np.ndarray,
    *,
    smooth_win_rows: int = 41,
    alpha: float = 0.18,
    local_win: int = 61,
    min_gutter_h: int = 2,
    min_dist: int = 6,
    prominence: float = 0.12,
    min_gutters_in_band: int = 4,
    gap_break_mult: float = 4.0,
    min_band_height: int = 10
) -> List[Tuple[int,int,int,int,int]]:
    """
    Detect horizontal gutter bands in an image.
    Returns a list of tuples: (x, y, bw, bh, area).
    """
    # 1) Convert to grayscale if needed
    if img.ndim == 3:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # 2) Binarize: text=1, bg=0
    _, bw = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    bw = 255 - bw
    ink = (bw > 0).astype(np.uint8)

    H, W = ink.shape

    # 3) Row projection
    row_ink = ink.sum(axis=1).astype(np.float32)

    # 4) Smooth projection
    sw = _ensure_odd(smooth_win_rows, 5)
    row_ink_s = _box1d(row_ink, sw)

    # 5) Detect gutters
    gutters, centers = _find_gutters(
        row_ink_s,
        alpha=alpha,
        local_win=local_win,
        min_gutter_h=min_gutter_h,
        min_dist=min_dist,
        prominence=prominence
    )
    if len(centers) < min_gutters_in_band:
        return []

    centers = np.asarray(centers, dtype=int)
    d = np.diff(centers)
    med = float(np.median(d)) if d.size else 0.0
    gap_break = max(int(round(gap_break_mult * max(med, 1.0))), 16)

    # 6) Group into bands
    runs = []
    start = 0
    for i in range(1, len(centers)):
        if (centers[i] - centers[i-1]) > gap_break:
            runs.append((start, i-1))
            start = i
    runs.append((start, len(centers)-1))

    # 7) Build bounding boxes
    boxes: List[Tuple[int,int,int,int,int]] = []
    for s, e in runs:
        if (e - s + 1) < min_gutters_in_band:
            continue
        y0 = gutters[s][0]
        y1 = gutters[e][1] + 1
        y0 = max(0, int(y0))
        y1 = min(H, int(y1))
        bh = y1 - y0
        if bh < min_band_height:
            continue
        x0 = 0
        bw = W
        boxes.append((x0, y0, bw, bh, bw * bh))
    return boxes

