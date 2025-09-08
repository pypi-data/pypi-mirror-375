import cv2 as cv
import numpy as np

def detect_tables(image):
    img = cv.cvtColor(image, cv.COLOR_RGB2GRAY)

    # --- preprocess ---
    img = cv.fastNlMeansDenoising(img, None, 10, 7, 21)
    thr = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 35, 11)

    h, w = thr.shape
    horiz = cv.morphologyEx(thr, cv.MORPH_OPEN, cv.getStructuringElement(cv.MORPH_RECT,(max(10,w//40),1)))
    vert  = cv.morphologyEx(thr, cv.MORPH_OPEN, cv.getStructuringElement(cv.MORPH_RECT,(1,max(10,h//40))))
    grid = cv.bitwise_or(horiz, vert)

    # line-based candidates
    c1, _ = cv.findContours(grid, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cand = [cv.boundingRect(c) for c in c1 if cv.contourArea(c) > 0.005*h*w]

    # whitespace-based fallback on the whole page (simple version)
    inv = (thr>0).astype(np.uint8)
    row_ink = cv.blur(inv.sum(axis=1).astype(np.float32).reshape(-1,1),(21,1)).ravel()
    rows = np.where(row_ink < 0.25*row_ink.max())[0]
    # take longest contiguous valley run as table band
    if len(rows)>0:
        s, e = rows[0], rows[0]
        best = (0,0)
        for i in range(1,len(rows)):
            if rows[i] == rows[i-1]+1:
                e = rows[i]
            else:
                if e-s > best[1]-best[0]: best = (s,e)
                s, e = rows[i], rows[i]
        if e-s > best[1]-best[0]: best = (s,e)
        y0, y1 = best[0], best[1]
        # vertical projection inside that band
        band = inv[y0:y1, :]
        col_ink = cv.blur(band.sum(axis=0).astype(np.float32).reshape(1,-1),(1,21)).ravel()
        cols = np.where(col_ink < 0.25*col_ink.max())[0]
        if len(cols)>0:
            x0, x1 = cols.min(), cols.max()
            cand.append((int(x0), int(y0), int(x1-x0), int(y1-y0)))

    # merge overlapping boxes (greedy)
    def iou(a,b):
        ax,ay,aw,ah = a; bx,by,bw,bh = b
        x1,y1 = max(ax,bx), max(ay,by)
        x2,y2 = min(ax+aw,bx+bw), min(ay+ah,by+bh)
        inter = max(0,x2-x1)*max(0,y2-y1)
        union = aw*ah + bw*bh - inter
        return inter/union if union else 0

    merged = []
    for r in cand:
        placed = False
        for i,m in enumerate(merged):
            if iou(r,m) > 0.3:
                x = min(r[0], m[0]); y = min(r[1], m[1])
                x2 = max(r[0]+r[2], m[0]+m[2]); y2 = max(r[1]+r[3], m[1]+m[3])
                merged[i] = (x,y,x2-x,y2-y)
                placed = True
                break
        if not placed:
            merged.append(r)

    # filter by minimal internal structure
    results = []
    for (x,y,w0,h0) in merged:
        roi_h = horiz[y:y+h0, x:x+w0].sum()/(255)
        roi_v = vert [y:y+h0, x:x+w0].sum()/(255)
        if (roi_h/w0 > 2) and (roi_v/h0 > 2):  # at least a couple of lines inside
            results.append((x,y,w0,h0, w0 * h0))
    return results
