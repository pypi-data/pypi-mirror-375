# run_overlay.py
import argparse
import cv2
import numpy as np
from u2net import load_u2like
from vision import infer_saliency, edge_map_gray, local_variance
from layout import pick_best_region
from render import render_text_on_image
import os

def main(args):
    img_path = args.image
    assert os.path.exists(img_path), "image not found"
    device = "cuda" if (args.gpu and __import__("torch").cuda.is_available()) else "cpu"
    print("Loading model...")
    model = load_u2like(device=device, weight_path=args.weights if args.weights else None)

    img_bgr = cv2.imread(img_path)
    if img_bgr is None:
        raise RuntimeError("cv2 failed to read image")

    print("Running saliency inference...")
    sal = infer_saliency(model, img_bgr, device=device, target_size=(320,320))
    edge = edge_map_gray(img_bgr)
    var = local_variance(img_bgr, ksize=15)

    print("Selecting region...")
    picks, scored = pick_best_region(img_bgr, sal, edge, var, max_candidates=1)
    if not picks:
        print("No candidate found; aborting")
        return
    box = picks[0]
    print("Best box:", box)
    out_bgr = render_text_on_image(img_bgr, box, args.text, font_path=args.font)

    out_file = args.out if args.out else "overlay_out.png"
    cv2.imwrite(out_file, out_bgr)
    print("Wrote:", out_file)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--image", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--weights", default=None, help="optional .pth weights for U2-like network")
    p.add_argument("--font", default=None, help="path to .ttf font to use")
    p.add_argument("--out", default=None)
    p.add_argument("--gpu", action="store_true")
    args = p.parse_args()
    main(args)