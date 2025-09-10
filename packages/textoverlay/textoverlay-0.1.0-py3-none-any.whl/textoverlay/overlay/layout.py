# layout.py
import numpy as np
import cv2
from vision import integral_image, mean_from_integral

def generate_candidates(img_w, img_h, text_metrics_ratio=(0.5, 0.1), scales=[0.25, 0.20, 0.15], step_ratio=0.05):
    """
    text_metrics_ratio: (width_ratio,height_ratio) is approximate aspect for the text block relative to image
    scales: multipliers of image width to use for candidate box widths
    step_ratio: sliding step in fraction of width
    yields boxes as (x0,y0,x1,y1)
    """
    candidates = []
    for scale in scales:
        box_w = int(img_w * scale)
        box_h = int(box_w * (text_metrics_ratio[1]/text_metrics_ratio[0]))  # approximate height from aspect
        if box_h <= 0: box_h = max(20, int(img_h*0.08))
        step = max(1, int(img_w * step_ratio))
        for y in range(0, img_h - box_h + 1, max(1, int(step/2))):
            for x in range(0, img_w - box_w + 1, step):
                candidates.append((x, y, x+box_w, y+box_h))
    # also add corner & center fixed candidates
    center_w = int(img_w * 0.4)
    center_h = int(center_w * (text_metrics_ratio[1]/text_metrics_ratio[0]))
    cx = (img_w - center_w)//2
    cy = (img_h - center_h)//2
    candidates.append((0,0, int(img_w*0.45), int(img_h*0.2)))
    candidates.append((img_w-int(img_w*0.45), img_h-int(img_h*0.2), img_w, img_h))
    candidates.append((cx, cy, cx+center_w, cy+center_h))
    # unique and clip
    uniq = list(dict.fromkeys(candidates))
    return uniq

def score_box(box, integrals, weights=(1.0, 0.8, 0.6)):
    """
    integrals: dict with keys 'sal', 'edge', 'var' each integral image
    weights: w_sal, w_edge, w_var. Higher score = better placement.
    We compute:
       score = w1*(1 - mean_saliency) + w2*(1 - mean_edge) + w3*(1 - mean_variance)
    """
    x0,y0,x1,y1 = box
    w1,w2,w3 = weights
    sal_mean = mean_from_integral(integrals['sal'], x0, y0, x1, y1)
    edge_mean = mean_from_integral(integrals['edge'], x0, y0, x1, y1)
    var_mean = mean_from_integral(integrals['var'], x0, y0, x1, y1)
    score = w1*(1.0 - sal_mean) + w2*(1.0 - edge_mean) + w3*(1.0 - var_mean)
    # small penalty for being too close to image borders (optional)
    h,w = integrals['sal'].shape
    margin_x = min(x0, w - x1)
    margin_y = min(y0, h - y1)
    margin = min(margin_x, margin_y)
    bord_pen = 0.0
    if margin < 10:
        bord_pen = 0.2 * (1 - margin/10)
    return score - bord_pen

def pick_best_region(img_bgr, sal_map, edge_map, var_map, max_candidates=1):
    h,w = sal_map.shape
    integrals = {
        'sal': integral_image(sal_map.astype(np.float32)),
        'edge': integral_image(edge_map.astype(np.float32)),
        'var': integral_image(var_map.astype(np.float32)),
    }
    # a basic text-aspect guess: wide rectangle
    candidates = generate_candidates(w,h, text_metrics_ratio=(0.6,0.18), scales=[0.35,0.28,0.22], step_ratio=0.05)
    scored = []
    for box in candidates:
        s = score_box(box, integrals)
        scored.append((s, box))
    scored.sort(reverse=True, key=lambda x: x[0])
    picks = [b for _,b in scored[:max_candidates]]
    return picks, scored  # return list of top boxes and full ranked list