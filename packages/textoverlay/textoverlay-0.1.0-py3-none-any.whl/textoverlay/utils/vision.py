# vision.py
import cv2
import numpy as np
import torch
from torchvision import transforms
from PIL import Image
from typing import Tuple

def pil_to_bgr_np(img_pil: Image.Image) -> np.ndarray:
    arr = np.array(img_pil.convert("RGB"))
    return arr[:,:,::-1]  # RGB -> BGR for OpenCV if needed

def preprocess_for_model(img_bgr: np.ndarray, target_size=(320,320)):
    # img_bgr: HxWx3 (0..255)
    h, w = img_bgr.shape[:2]
    img_rgb = img_bgr[:,:,::-1]
    img_resized = cv2.resize(img_rgb, (target_size[1], target_size[0]), interpolation=cv2.INTER_AREA)
    # to tensor normalized
    img_tensor = transforms.functional.to_tensor(img_resized)  # [0..1]
    # normalize with ImageNet stats
    img_tensor = transforms.functional.normalize(img_tensor, mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
    return img_tensor.unsqueeze(0), (w,h)

def infer_saliency(model, img_bgr: np.ndarray, device="cpu", target_size=(320,320)):
    x, orig_wh = preprocess_for_model(img_bgr, target_size)
    x = x.to(device)
    with torch.no_grad():
        outputs = model(x)          # U2Net returns tuple of outputs
        # Use the main output (first element)
        logits = outputs[0] if isinstance(outputs, tuple) else outputs
        probs = torch.sigmoid(logits).squeeze().cpu().numpy()
    probs = cv2.resize(probs, (orig_wh[0], orig_wh[1]), interpolation=cv2.INTER_CUBIC)
    probs = np.clip(probs, 0.0, 1.0)
    return probs  # float HxW

def edge_map_gray(img_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx*gx + gy*gy)
    mag = mag / (mag.max() + 1e-8)
    return mag  # 0..1

def local_variance(img_bgr: np.ndarray, ksize=15) -> np.ndarray:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    mean = cv2.blur(gray, (ksize,ksize))
    mean_sq = cv2.blur(gray*gray, (ksize,ksize))
    var = mean_sq - mean*mean
    var = np.clip(var, 0.0, None)
    # normalize by max for comparability
    if var.max() > 0:
        var = var / (var.max())
    return var

# Integral image helpers
def integral_image(arr: np.ndarray) -> np.ndarray:
    # expects 2D float array
    return cv2.integral(arr)[1:,1:].astype(np.float32)  # cv2.integral returns (H+1,W+1)

def mean_from_integral(integ: np.ndarray, x0, y0, x1, y1):
    # box inclusive [x0,x1), coords in pixel indices (x horizontal)
    # integ shape HxW (values are integral to that pixel)
    # convert to sums using standard integral image formula
    # ensure coords within bounds
    h,w = integ.shape
    x0_c = max(0, x0)
    y0_c = max(0, y0)
    x1_c = min(w, x1)
    y1_c = min(h, y1)
    if x0_c >= x1_c or y0_c >= y1_c:
        return 0.0
    A = integ[y0_c-1, x0_c-1] if (y0_c-1>=0 and x0_c-1>=0) else 0.0
    B = integ[y0_c-1, x1_c-1] if (y0_c-1>=0) else 0.0
    C = integ[y1_c-1, x0_c-1] if (x0_c-1>=0) else 0.0
    D = integ[y1_c-1, x1_c-1]
    s = D - B - C + A
    area = (y1_c - y0_c) * (x1_c - x0_c)
    return float(s / (area + 1e-8))

# simple function to estimate background color in a box
def mean_color_in_box(img_bgr: np.ndarray, x0, y0, x1, y1):
    h,w = img_bgr.shape[:2]
    x0 = max(0, x0); y0 = max(0, y0); x1 = min(w, x1); y1 = min(h, y1)
    if x0 >= x1 or y0 >= y1:
        return (0,0,0)
    patch = img_bgr[y0:y1, x0:x1].astype(np.float32)
    m = patch.reshape(-1,3).mean(axis=0)
    # return RGB tuple
    return (int(m[2]), int(m[1]), int(m[0]))  # convert BGR->RGB order