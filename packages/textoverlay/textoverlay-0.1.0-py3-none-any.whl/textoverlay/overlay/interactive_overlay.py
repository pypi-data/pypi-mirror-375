# interactive_overlay.py
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import argparse
import os
import time
from typing import Dict, List, Tuple, Optional

from textoverlay.models.u2net import load_u2like
from textoverlay.utils.vision import infer_saliency, edge_map_gray, local_variance
from textoverlay.models.advanced_layout import analyze_image_regions
from textoverlay.utils.font_manager import FontManager, TextStyleConfig, get_font_recommendations
from textoverlay.utils.render import get_text_size

def pick_modern_sans(font_manager: FontManager) -> str:
    """Pick a modern, clean, sans-serif font available on the system."""
    prefer = [
        # Prefer the curated set configured in FontManager
        "OpenSans-Regular", "Roboto-Bold", "JosefinSans-Regular", "Quicksand-Bold",
        "Roboto-Black", "OpenSans-Italic", "JosefinSans-Bold",
        "Default",
    ]
    available = set(font_manager.get_available_fonts())
    for name in prefer:
        if name in available:
            return name
    return "Default"

# --- Curated color helpers ---
def _srgb_to_linear(c: float) -> float:
    c = float(c) / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def _relative_luminance(rgb: Tuple[int, int, int]) -> float:
    r, g, b = rgb
    R = _srgb_to_linear(r)
    G = _srgb_to_linear(g)
    B = _srgb_to_linear(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def _contrast_ratio(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    L1 = _relative_luminance(c1)
    L2 = _relative_luminance(c2)
    Lh, Ll = (L1, L2) if L1 >= L2 else (L2, L1)
    return (Lh + 0.05) / (Ll + 0.05)

def _should_use_overlay(bg_rgb: Tuple[int, int, int]) -> bool:
    """Overlay works best on midtones. Avoid on very light/dark backgrounds."""
    L = _relative_luminance(bg_rgb)
    return 0.2 <= L <= 0.8

def _pick_auto_text_color(bg_rgb: Tuple[int, int, int], curated: Dict[str, Tuple[int, int, int]]) -> Tuple[int, int, int]:
    """Pick a tasteful color from curated palette by maximizing contrast.
    Prefer neutral/minimal options; ensure strong contrast where possible.
    """
    preferred_order = [
        "white", "black", "charcoal", "light gray", "slate", "navy", "gold", "sand"
    ]
    candidates = [(n, curated[n]) for n in preferred_order if n in curated]
    if not candidates:
        return (255, 255, 255)
    best = max(candidates, key=lambda kv: _contrast_ratio(kv[1], bg_rgb))
    return best[1]

class InteractiveTextOverlay:
    def __init__(self, model_weights: str = None):
        self.device = "cpu"
        print("Loading U2Net model...")
        self.model = load_u2like(device=self.device, weight_path=model_weights)
        self.font_manager = FontManager()
        
    def analyze_image(self, img_path: str, text: str) -> Dict:
        """Analyze image and generate placement options"""
        print("Analyzing image...")
        
        # Load image
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            raise ValueError(f"Could not load image: {img_path}")
        
        # Generate saliency and feature maps
        print("Generating saliency map...")
        sal_map = infer_saliency(self.model, img_bgr, device=self.device, target_size=(320, 320))
        edge_map = edge_map_gray(img_bgr)
        var_map = local_variance(img_bgr, ksize=15)
        
        # Analyze regions
        print("Finding optimal placement regions...")
        placement_options = analyze_image_regions(img_bgr, sal_map, edge_map, var_map, text)
        
        return {
            'image': img_bgr,
            'saliency': sal_map,
            'edge_map': edge_map,
            'var_map': var_map,
            'placement_options': placement_options,
            'text': text
        }
    
    def generate_previews(self, analysis_result: Dict, style_configs: List[TextStyleConfig] = None) -> Dict[str, List[Dict]]:
        """Generate preview images for each placement option and style"""
        img_bgr = analysis_result['image']
        placement_options = analysis_result['placement_options']
        text = analysis_result['text']
        
        previews = {}
        
        for position, option_data in placement_options.items():
            if not option_data:
                continue
                
            position_previews = []
            
            # Get style configurations
            if style_configs is None:
                bg_color = option_data['bg_color']
                style_configs = get_font_recommendations(bg_color)[:3]  # Top 3 recommendations
            
            for i, style_config in enumerate(style_configs):
                # Create preview image
                preview_img = self._create_preview(
                    img_bgr.copy(), 
                    option_data['box'], 
                    text, 
                    style_config
                )
                
                position_previews.append({
                    'preview_image': preview_img,
                    'style_config': style_config,
                    'option_data': option_data,
                    'style_name': f"Style {i+1}",
                    'description': self._get_style_description(style_config)
                })
            
            previews[position] = position_previews
        
        return previews
    
    def _create_preview(self, img_bgr: np.ndarray, box: Tuple[int, int, int, int], 
                       text: str, style_config: TextStyleConfig, orientation: str = "vertical") -> np.ndarray:
        """Create a preview image with text overlay"""
        # Convert to PIL for text rendering
        img_pil = Image.fromarray(img_bgr[:,:,::-1])  # BGR to RGB
        draw = ImageDraw.Draw(img_pil)
        
        # Create font
        font = self.font_manager.create_font(style_config.font_name, style_config.font_size)
        
        # Draw bounding box for visualization
        x0, y0, x1, y1 = box
        draw.rectangle([x0, y0, x1, y1], outline=(255, 255, 0), width=2)
        
        # Wrap text to fit box based on orientation
        wrapped_lines = self._wrap_text(draw, text, font, x1 - x0 - 10, orientation)
        
        # Calculate text positioning with line spacing and stroke padding
        line_gap = max(2, int(0.20 * (getattr(font, 'size', 24))))
        stroke_pad = max(0, style_config.stroke_width)
        line_heights = [get_text_size(draw, line, font)[1] for line in wrapped_lines]
        total_height = sum(line_heights) + max(0, len(wrapped_lines) - 1) * (line_gap + 2 * stroke_pad)
        y_start = y0 + ((y1 - y0) - total_height) // 2
        
        # Draw text with stroke
        for idx, line in enumerate(wrapped_lines):
            text_width, text_height = get_text_size(draw, line, font)
            x_pos = x0 + ((x1 - x0) - text_width) // 2
            
            # Draw stroke
            if style_config.stroke_width > 0:
                for dx in range(-style_config.stroke_width, style_config.stroke_width + 1):
                    for dy in range(-style_config.stroke_width, style_config.stroke_width + 1):
                        if dx == 0 and dy == 0:
                            continue
                        draw.text((x_pos + dx, y_start + dy), line, 
                                font=font, fill=style_config.stroke_color)
            
            # Draw main text
            draw.text((x_pos, y_start), line, font=font, fill=style_config.color)
            # Advance y by height + gap + stroke padding on both sides to avoid overlap
            y_start += text_height + (line_gap + 2 * stroke_pad if idx < len(wrapped_lines) - 1 else 0)
        
        # Convert back to BGR
        return np.array(img_pil)[:,:,::-1]
    
    def create_preview_custom(self, img_bgr: np.ndarray, coords: Tuple[int, int], 
                             text: str, font_size: int = 24) -> np.ndarray:
        """Create a preview image with text at custom coordinates."""
        # Estimate a box around the click point
        box = self._estimate_box_from_click(img_bgr.shape, coords, len(text))
        
        # Get background color from the estimated box area
        x0, y0, x1, y1 = box
        H, W = img_bgr.shape[:2]
        x0 = max(0, min(W, int(x0)))
        x1 = max(0, min(W, int(x1)))
        y0 = max(0, min(H, int(y0)))
        y1 = max(0, min(H, int(y1)))
        
        if x1 > x0 and y1 > y0:
            patch = img_bgr[y0:y1, x0:x1]
            if patch.size > 0:
                bg_color = tuple(map(int, patch.reshape(-1, 3).mean(axis=0)))
            else:
                bg_color = (128, 128, 128)
        else:
            bg_color = (128, 128, 128)
        
        # Create a simple style config for preview
        curated = self.font_manager.get_curated_colors()
        text_color = _pick_auto_text_color(bg_color, curated)
        
        style_config = TextStyleConfig(
            font_name=pick_modern_sans(self.font_manager),
            font_size=font_size,
            color=text_color,
            stroke_width=1,
            stroke_color=(0, 0, 0) if sum(text_color) > 384 else (255, 255, 255),
            opacity=0.9,
            blend_mode="overlay",
            shadow=True
        )
        
        # Create preview using the existing _create_preview method
        return self._create_preview(img_bgr.copy(), box, text, style_config)
    
    def _wrap_text(self, draw: ImageDraw.Draw, text: str, font, max_width: int, orientation: str = "vertical") -> List[str]:
        """Wrap text to fit within specified width
        
        Args:
            orientation: 'vertical' for multi-line wrapping, 'horizontal' for single-line
        """
        if orientation == "horizontal":
            # For horizontal layout, keep text as single line (no wrapping)
            return [text]
        
        # Vertical layout - wrap text as before
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if get_text_size(draw, test_line, font)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _get_style_description(self, style_config: TextStyleConfig) -> str:
        """Generate human-readable style description"""
        return f"{style_config.font_name}, {style_config.font_size}px"
    
    def save_previews(self, previews: Dict, output_dir: str = "previews"):
        """Save preview images to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        for position, position_previews in previews.items():
            for i, preview_data in enumerate(position_previews):
                filename = f"{position}_style_{i+1}.png"
                filepath = os.path.join(output_dir, filename)
                
                cv2.imwrite(filepath, preview_data['preview_image'])
                saved_files.append(filepath)
                
                print(f"Saved: {filepath}")
                print(f"  Position: {position.title()}")
                print(f"  Style: {preview_data['description']}")
                print(f"  Quality: {preview_data['option_data']['quality']}")
                print()
        
        return saved_files
    
    def display_options(self, analysis_result: Dict):
        """Display placement options in a user-friendly format"""
        placement_options = analysis_result['placement_options']
        
        print("\n" + "="*60)
        print("TEXT PLACEMENT OPTIONS")
        print("="*60)
        
        for position, option_data in placement_options.items():
            if not option_data:
                print(f"\n{position.upper()}: No suitable placement found")
                continue
                
            print(f"\n{position.upper()} PLACEMENT:")
            print(f"  Quality: {option_data['quality'].title()}")
            print(f"  Score: {option_data['score']:.2f}")
            print(f"  Recommended font size: {option_data['recommended_font_size']}px")
            print(f"  Background color: RGB{option_data['bg_color']}")
            print(f"  Saliency level: {option_data['saliency']:.3f} (lower is better)")
    
    def prompt_position(self, analysis_result: Dict) -> Tuple[str, Dict]:
        """Interactively prompt user to choose placement region or Custom (click)."""
        placement_options = analysis_result['placement_options']
        valid = [(pos, data) for pos, data in placement_options.items() if data]
        if not valid:
            raise ValueError("No suitable placement options found.")
        
        print("\nSelect placement region:")
        for idx, (pos, data) in enumerate(valid, 1):
            print(f"  {idx}. {pos.title()} - quality: {data['quality']} (score {data['score']:.2f})")
        custom_index = len(valid) + 1
        print(f"  {custom_index}. Custom (click to place)")
        
        while True:
            choice = input(f"Enter 1-{custom_index}: ").strip()
            if choice.isdigit():
                i = int(choice)
                if 1 <= i <= len(valid):
                    return valid[i-1]
                if i == custom_index:
                    print("Opening custom click window... (Press Esc to cancel)")
                    return self.prompt_custom_position(analysis_result)
            print("Invalid selection. Try again.")

    def _estimate_box_from_click(self, img_shape, click_xy, text_len: int) -> Tuple[int, int, int, int]:
        """Estimate a reasonable text box centered at click point."""
        H, W = img_shape[:2]
        cx, cy = int(click_xy[0]), int(click_xy[1])
        # Approximate width based on text length and image size
        est_w = int(min(max(W * 0.22, text_len * 12), W * 0.5))
        est_h = int(max(30, est_w * 0.18))
        margin = max(10, int(0.04 * min(W, H)))
        half_w = est_w // 2
        half_h = est_h // 2
        x0 = max(margin, min(W - margin - est_w, cx - half_w))
        y0 = max(margin, min(H - margin - est_h, cy - half_h))
        x1 = x0 + est_w
        y1 = y0 + est_h
        return (int(x0), int(y0), int(x1), int(y1))

    def _compute_option_from_box(self, img_bgr, sal_map, edge_map, var_map, box) -> Dict:
        x0, y0, x1, y1 = box
        # Clamp
        H, W = sal_map.shape[:2]
        x0 = max(0, min(W, int(x0))); x1 = max(0, min(W, int(x1)))
        y0 = max(0, min(H, int(y0))); y1 = max(0, min(H, int(y1)))
        if x0 >= x1 or y0 >= y1:
            raise ValueError("Invalid custom box selection.")
        # Means
        sal_mean = float(sal_map[y0:y1, x0:x1].mean()) if sal_map is not None else 0.5
        edge_mean = float(edge_map[y0:y1, x0:x1].mean()) if edge_map is not None else 0.5
        var_mean = float(var_map[y0:y1, x0:x1].mean()) if var_map is not None else 0.5
        # Score like advanced_layout
        sal_score = 1.0 - sal_mean
        edge_score = 1.0 - edge_mean
        var_score = 1.0 - var_mean
        border_penalty = 0.0
        margin = 20
        if x0 < margin or y0 < margin or x1 > (W - margin) or y1 > (H - margin):
            border_penalty = 0.3
        score = max(0.0, (0.4 * sal_score + 0.3 * edge_score + 0.3 * var_score) - border_penalty)
        # BG color (BGR mean, to match existing behavior)
        patch = img_bgr[y0:y1, x0:x1]
        if patch.size > 0:
            bg_color = tuple(map(int, patch.reshape(-1, 3).mean(axis=0)))
        else:
            bg_color = (128, 128, 128)
        # Font size recommendation similar to advanced_layout
        box_h = y1 - y0; box_w = x1 - x0
        height_based = int(box_h * 0.6)
        width_based = int(box_w * 0.08)
        font_size = max(12, min(min(height_based, width_based), 72))
        quality = 'excellent' if score > 0.7 else 'good' if score > 0.5 else 'fair'
        return {
            'box': (x0, y0, x1, y1),
            'score': score,
            'center': ((x0 + x1) // 2, (y0 + y1) // 2),
            'bg_color': bg_color,
            'saliency': sal_mean,
            'recommended_font_size': font_size,
            'quality': quality,
        }

    def prompt_custom_position(self, analysis_result: Dict) -> Tuple[str, Dict]:
        """Let user click on the image to place text; returns ('custom', option_data).

        Adds window sizing/positioning and a timeout with manual coordinate fallback
        to avoid indefinite waiting if the OpenCV window cannot receive events.
        """
        img_bgr = analysis_result['image']
        sal_map = analysis_result.get('saliency')
        edge_map = analysis_result.get('edge_map')
        var_map = analysis_result.get('var_map')
        text = analysis_result.get('text', '')

        disp = img_bgr.copy()
        clicked = {'pt': None}
        H, W = disp.shape[:2]

        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked['pt'] = (x, y)
                print(f"Clicked at: ({x}, {y})")

        win = 'Click to place text (press Esc to cancel)'
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
        # Attempt to size and position the window for visibility
        try:
            target_w = min(W, 1200)
            target_h = min(H, 800)
            cv2.resizeWindow(win, target_w, target_h)
            cv2.moveWindow(win, 60, 60)
        except Exception:
            pass

        # Show BGR image and keep window responsive
        cv2.imshow(win, disp)
        # Nudge the event loop so window reliably appears on some platforms
        cv2.waitKey(1)
        cv2.setMouseCallback(win, on_mouse)
        timeout_s = 20.0
        start_t = time.time()
        while clicked['pt'] is None:
            # Re-show frame to ensure window stays responsive on some platforms
            cv2.imshow(win, disp)
            key = cv2.waitKey(16) & 0xFF  # ~60 FPS event pump
            if key == 27:  # Esc
                break
            # If user closed the window, abort gracefully
            try:
                if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except Exception:
                # On some builds this can throw transiently; continue pumping events
                continue
            # Timeout fallback
            if (time.time() - start_t) > timeout_s:
                print("\nTimed out waiting for click.")
                break
        cv2.destroyWindow(win)

        if clicked['pt'] is None:
            # Manual coordinate fallback
            while True:
                manual = input("Enter coordinates as 'x,y' to place manually, or press Enter to cancel: ").strip()
                if not manual:
                    raise KeyboardInterrupt('Custom placement cancelled.')
                if ',' in manual:
                    try:
                        xs, ys = manual.split(',', 1)
                        x = max(0, min(W - 1, int(xs.strip())))
                        y = max(0, min(H - 1, int(ys.strip())))
                        clicked['pt'] = (x, y)
                        print(f"Using manual point: ({x}, {y})")
                        break
                    except Exception:
                        pass
                print("Invalid format. Please enter as x,y (e.g., 320,240)")

        box = self._estimate_box_from_click(img_bgr.shape, clicked['pt'], len(text))
        option_data = self._compute_option_from_box(img_bgr, sal_map, edge_map, var_map, box)
        return 'custom', option_data
    
    def prompt_font_family(self) -> str:
        """Prompt user to choose a font family from the configured fonts only."""
        available = [f for f in self.font_manager.get_available_fonts() if f != "Default"]
        if not available:
            print("\nNo specified fonts found on system. Falling back to Default.")
            return "Default"

        print("\nSelect font family:")
        for idx, name in enumerate(available, 1):
            print(f"  {idx}. {name}")
        
        while True:
            choice = input(f"Enter 1-{len(available)}: ").strip()
            if choice.isdigit():
                i = int(choice)
                if 1 <= i <= len(available):
                    return available[i-1]
            print("Invalid selection. Try again.")
    
    def prompt_font_size(self, recommended: int) -> int:
        """Prompt user to choose a font size (presets or custom)."""
        presets = self.font_manager.get_size_presets()
        print(f"\nRecommended font size: {recommended}px")
        print("Size presets:")
        for idx, s in enumerate(presets, 1):
            print(f"  {idx}. {s}px")
        
        while True:
            val = input("Enter preset number or custom size (e.g., 36): ").strip()
            if val.isdigit():
                n = int(val)
                if 1 <= n <= len(presets):
                    return presets[n-1]
                # accept custom numeric size within sensible bounds
                if 8 <= n <= 200:
                    return n
            print("Invalid value. Try again.")
    
    def _parse_rgb_string(self, s: str) -> Optional[Tuple[int, int, int]]:
        """Parse 'R,G,B' strings into an RGB tuple or return None if invalid."""
        if "," in s:
            try:
                parts = [p.strip() for p in s.split(",")]
                if len(parts) != 3:
                    return None
                r, g, b = [max(0, min(255, int(x))) for x in parts]
                return (r, g, b)
            except Exception:
                return None
        return None
    
    def prompt_text_orientation(self) -> str:
        """Prompt user to choose text orientation (vertical/horizontal)."""
        print("\nSelect text orientation:")
        print("  1. Vertical (multi-line, wrapped text)")
        print("  2. Horizontal (single-line, no wrapping)")
        
        while True:
            choice = input("Enter 1 or 2: ").strip()
            if choice == "1":
                return "vertical"
            elif choice == "2":
                return "horizontal"
            print("Invalid selection. Enter 1 for vertical or 2 for horizontal.")
    
    def prompt_text_color(self, bg_color: Tuple[int, int, int]) -> Optional[Tuple[int, int, int]]:
        """Prompt the user to type a COLOR NAME only (no codes). Return RGB or None for auto."""
        curated = self.font_manager.get_curated_colors()
        aliases = self.font_manager.get_alias_map()
        brightness = sum(bg_color) / 3.0
        if brightness > 128:
            # Light background -> darker tasteful tones + brand accents
            suggestions = [n for n in ["charcoal", "navy", "burgundy", "black", "slate"] if n in curated]
            brand_candidates = [
                "spotify green", "coca-cola red", "google blue", "netflix red",
                "starbucks green", "microsoft blue", "instagram pink",
            ]
        else:
            # Dark background -> light/minimal accents + brand brights that pop on dark
            suggestions = [n for n in ["white", "light gray", "gold", "sand", "teal"] if n in curated]
            brand_candidates = [
                "white", "apple light", "instagram yellow", "nike gray", "apple gray",
            ]
        brand_suggestions = [n for n in brand_candidates if n in curated]
        # Merge and deduplicate while preserving order
        suggestions = list(dict.fromkeys(suggestions + brand_suggestions))
        # Allowed names are curated + aliases
        allowed_names = set(curated.keys()) | set(aliases.keys())
         
        print("\nText color selection (type the NAME of the color):")
        print("  Press Enter to use recommended (auto-contrast)")
        print("  Examples: white, black, navy, gold, charcoal, slate, spotify green, coca-cola red")
        print("  Suggested for this background:", ", ".join(suggestions))
          
        while True:
            name = input("Enter color name (or press Enter for auto): ").strip()
            if name == "":
                return None
            if name.startswith('#') or ',' in name:
                print("Please enter a color NAME only (e.g., 'white', 'navy', 'gold').")
                continue
            lower = name.lower()
            # Normalize via alias, then prefer curated mapping
            canonical = aliases.get(lower, lower)
            if canonical in curated:
                return curated[canonical]
            # Fallback: try PIL named colors via validator
            rgb = self.font_manager.validate_color(name)
            if isinstance(rgb, tuple) and len(rgb) == 3:
                # Reject unknown names that silently fall back to black unless explicitly 'black'
                if canonical != "black" and rgb == (0, 0, 0) and canonical not in curated:
                    print("Unknown color name. Try: " + ", ".join(suggestions))
                    continue
                return rgb
            print("Unknown color name. Try something like: " + ", ".join(suggestions))
     
    def build_style_config(self, font_name: str, font_size: int, bg_color: Tuple[int, int, int],
                           text_color: Optional[Tuple[int, int, int]] = None,
                           opacity: float = 0.9, blend_mode: str = "overlay", shadow: bool = True) -> TextStyleConfig:
        """Build a TextStyleConfig with curated color, adaptive blend, and background-aware stroke."""
        curated = self.font_manager.get_curated_colors()
        # Choose color (auto or user-specified)
        color = _pick_auto_text_color(bg_color, curated) if text_color is None else text_color
        color = tuple(int(x) for x in color)
        # Contrast between text and background
        cr = _contrast_ratio(color, bg_color)
        # Stroke should contrast with the TEXT (avoid same-color outline thickening)
        text_brightness = sum(color) / 3.0
        stroke_color = (255, 255, 255) if text_brightness < 128 else (0, 0, 0)
        # Adaptive stroke width by contrast ratio (WCAG-inspired)
        if cr >= 7.0:
            stroke_width = 0
        elif cr >= 4.5:
            stroke_width = 1
        else:
            stroke_width = 2
        # Overlay only on mid-tones; auto-switch to normal on very light/dark BGs
        effective_blend = blend_mode
        if blend_mode == "overlay" and not _should_use_overlay(bg_color):
            effective_blend = "normal"
        cfg = TextStyleConfig(
            font_name=font_name,
            font_size=font_size,
            color=color,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            opacity=float(max(0.0, min(1.0, opacity))),
            blend_mode=effective_blend,
            shadow=bool(shadow),
            shadow_offset=(1, 1),
            shadow_blur=2,
            shadow_color_rgba=(0, 0, 0, 60)
        )
        return cfg

    def create_final_overlay(self, img_bgr: np.ndarray, box: Tuple[int, int, int, int], 
                           text: str, style_config: TextStyleConfig, output_path: str,
                           saliency: Optional[np.ndarray] = None, behind_subject: bool = False,
                           orientation: str = "vertical"):
        """Create final overlay image. If behind_subject is True, occlude text with subject using saliency."""
        # Base image
        base = Image.fromarray(img_bgr[:,:,::-1]).convert("RGB")
        W, H = base.size

        # Draw text onto a transparent RGBA layer
        text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        font = self.font_manager.create_font(style_config.font_name, style_config.font_size)

        # Wrap text to fit box based on orientation
        if orientation == "horizontal":
            # For horizontal, use full image width if text exceeds box width
            text_width = get_text_size(draw, text, font)[0]
            box_width = box[2] - box[0] - 10
            if text_width > box_width:
                # Expand box horizontally to fit text
                img_width = img_bgr.shape[1]
                margin = 20
                new_width = min(text_width + 20, img_width - 2 * margin)
                center_x = (box[0] + box[2]) // 2
                new_x0 = max(margin, center_x - new_width // 2)
                new_x1 = min(img_width - margin, new_x0 + new_width)
                box = (new_x0, box[1], new_x1, box[3])
        
        wrapped_lines = self._wrap_text(draw, text, font, box[2] - box[0] - 10, orientation)
        
        # Calculate text positioning with line spacing and stroke padding
        line_gap = max(2, int(0.20 * (getattr(font, 'size', 24))))
        stroke_pad = max(0, style_config.stroke_width)
        line_heights = [get_text_size(draw, line, font)[1] for line in wrapped_lines]
        total_height = sum(line_heights) + max(0, len(wrapped_lines) - 1) * (line_gap + 2 * stroke_pad)
        y_start = box[1] + ((box[3] - box[1]) - total_height) // 2

        # Optional soft shadow rendered on a separate layer
        shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if getattr(style_config, 'shadow', True):
            shadow_draw = ImageDraw.Draw(shadow_layer)
        
        for idx, line in enumerate(wrapped_lines):
            text_width, text_height = get_text_size(draw, line, font)
            x_pos = box[0] + ((box[2] - box[0]) - text_width) // 2

            # Stroke
            if style_config.stroke_width > 0:
                for dx in range(-style_config.stroke_width, style_config.stroke_width + 1):
                    for dy in range(-style_config.stroke_width, style_config.stroke_width + 1):
                        if dx == 0 and dy == 0:
                            continue
                        draw.text((x_pos + dx, y_start + dy), line, font=font, fill=style_config.stroke_color)

            # Shadow (subtle, blurred)
            if getattr(style_config, 'shadow', True):
                sx = x_pos + getattr(style_config, 'shadow_offset', (2,2))[0]
                sy = y_start + getattr(style_config, 'shadow_offset', (2,2))[1]
                sc = getattr(style_config, 'shadow_color_rgba', (0,0,0,90))
                shadow_draw.text((sx, sy), line, font=font, fill=sc)

            # Main text
            draw.text((x_pos, y_start), line, font=font, fill=style_config.color)
            # Advance y by height + gap + stroke padding on both sides to avoid overlap
            y_start += text_height + (line_gap + 2 * stroke_pad if idx < len(wrapped_lines) - 1 else 0)

        # Blur the shadow layer and combine with text layer
        if getattr(style_config, 'shadow', True):
            blur_radius = int(getattr(style_config, 'shadow_blur', 4))
            if blur_radius > 0:
                shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        text_with_shadow = Image.alpha_composite(shadow_layer, text_layer)

        # Composite with optional subject masking and blend mode
        if behind_subject and saliency is not None:
            # Build subject mask (255=subject/foreground)
            sal = (np.clip(saliency, 0.0, 1.0) * 255).astype(np.uint8)
            # Threshold and slightly dilate/blur to avoid halos
            _, bin_mask = cv2.threshold(sal, 128, 255, cv2.THRESH_BINARY)
            bin_mask = cv2.dilate(bin_mask, np.ones((3,3), np.uint8), iterations=1)
            bin_mask = cv2.GaussianBlur(bin_mask, (0,0), sigmaX=1.2)
            inv_mask = 255 - bin_mask  # where text can appear

            # Convert masks to PIL L images
            inv_mask_pil = Image.fromarray(inv_mask).convert('L')

            # Keep text only where background is visible (inv_mask)
            masked_text = Image.composite(text_with_shadow, Image.new('RGBA', (W, H), (0,0,0,0)), inv_mask_pil)
            if getattr(style_config, 'blend_mode', 'overlay') == 'overlay':
                final_rgb = overlay_blend(base, masked_text, getattr(style_config, 'opacity', 0.9))
                final_rgba = final_rgb.convert('RGBA')
            else:
                # Scale alpha by opacity for normal blend
                a = masked_text.split()[3].point(lambda p: int(p * float(getattr(style_config, 'opacity', 0.9))))
                masked_text.putalpha(a)
                final_rgba = Image.alpha_composite(base.convert('RGBA'), masked_text)
        else:
            if getattr(style_config, 'blend_mode', 'overlay') == 'overlay':
                final_rgb = overlay_blend(base, text_with_shadow, getattr(style_config, 'opacity', 0.9))
                final_rgba = final_rgb.convert('RGBA')
            else:
                a = text_with_shadow.split()[3].point(lambda p: int(p * float(getattr(style_config, 'opacity', 0.9))))
                text_with_shadow.putalpha(a)
                final_rgba = Image.alpha_composite(base.convert('RGBA'), text_with_shadow)

        final_img = np.array(final_rgba.convert('RGB'))[:,:,::-1]
        cv2.imwrite(output_path, final_img)
        print(f"Final overlay saved: {output_path}")
        return final_img

def overlay_blend(base_rgb: Image.Image, overlay_rgba: Image.Image, opacity: float) -> Image.Image:
    """Apply Overlay blend mode of overlay_rgba onto base_rgb with given opacity [0..1]."""
    base = np.asarray(base_rgb).astype(np.float32) / 255.0  # HxWx3
    over = np.asarray(overlay_rgba).astype(np.float32) / 255.0  # HxWx4
    if over.shape[2] == 4:
        alpha = over[..., 3]
        over_rgb = over[..., :3]
    else:
        alpha = np.ones(over.shape[:2], dtype=np.float32)
        over_rgb = over
    # Effective alpha
    a = np.clip(alpha * float(max(0.0, min(1.0, opacity))), 0.0, 1.0)[..., None]
    # Overlay formula per channel
    b = base
    o = over_rgb
    low = 2.0 * b * o
    high = 1.0 - 2.0 * (1.0 - b) * (1.0 - o)
    overlay_rgb = np.where(b <= 0.5, low, high)
    out_rgb = b * (1.0 - a) + overlay_rgb * a
    out = (np.clip(out_rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    return Image.fromarray(out).convert("RGB")

def main():
    parser = argparse.ArgumentParser(description="Interactive Text Overlay Tool")
    parser.add_argument("--image", required=True, help="Input image path")
    parser.add_argument("--text", required=True, help="Text to overlay")
    parser.add_argument("--weights", default="textoverlay/models/checkpoints/u2net.pth", help="U2Net model weights")
    parser.add_argument("--output", default="final_overlay.png", help="Output image path")
    parser.add_argument("--behind", action="store_true", help="Place text behind subject (occluded by foreground)")
    # New styling and selection options
    parser.add_argument("--preferred-area", choices=[
        "left","center","right",
        "center_left","center_middle","center_right",
        "bottom_left","bottom_center","bottom_right",
        "custom"
    ], default=None,
        help="Preferred placement area; include 'custom' to click a point for placement")
    parser.add_argument("--font-family", default=None, help="Font family name (e.g., Calibri, Arial)")
    parser.add_argument("--font-size", type=int, default=None, help="Font size in px; default uses recommended, capped proportionally")
    parser.add_argument("--text-color", default=None, help="Named color; supports curated and brand names (e.g., 'spotify green', 'coca-cola red'); default uses harmonized recommendation")
    parser.add_argument("--opacity", type=float, default=0.9, help="Text layer opacity (0..1)")
    parser.add_argument("--blend", choices=["overlay","normal"], default="overlay", help="Blend mode for compositing")
    parser.add_argument("--no-shadow", action="store_true", help="Disable soft shadow under text")
    parser.add_argument("--orientation", choices=["vertical", "horizontal"], default=None, help="Text orientation: vertical (multi-line) or horizontal (single-line)")

    args = parser.parse_args()
    
    # Initialize overlay system
    overlay_system = InteractiveTextOverlay(args.weights)
    
    # Analyze image
    analysis = overlay_system.analyze_image(args.image, args.text)
    
    # Display options
    overlay_system.display_options(analysis)
    
    placement_options = analysis['placement_options']
    # Optional non-interactive selection honoring preferred area and style
    if args.preferred_area:
        if args.preferred_area == 'custom':
            # Offer placement options first; only open a window if "Custom" is chosen.
            position_name, option_data = overlay_system.prompt_position(analysis)
            # Font family: use flag if provided, else interactive prompt
            if args.font_family:
                font_name = args.font_family
            else:
                font_name = overlay_system.prompt_font_family()
            # Font size: compute cap; use flag if provided, else interactive prompt (seeded with recommended)
            recommended_size = option_data.get('recommended_font_size', 24)
            W = analysis['image'].shape[1]
            H = analysis['image'].shape[0]
            cap = max(16, int(min(W, H) * 0.05))
            if args.font_size:
                font_size = args.font_size
            else:
                font_size = overlay_system.prompt_font_size(min(recommended_size, cap))
            # Text color: use flag if provided, else interactive color-name prompt
            if args.text_color:
                chosen_color = overlay_system.font_manager.validate_color(args.text_color)
            else:
                chosen_color = overlay_system.prompt_text_color(option_data['bg_color'])
            # Text orientation prompt
            text_orientation = args.orientation or overlay_system.prompt_text_orientation()
            style_config = overlay_system.build_style_config(
                font_name, font_size, option_data['bg_color'], chosen_color,
                opacity=args.opacity, blend_mode=args.blend, shadow=(not args.no_shadow)
            )
        elif placement_options.get(args.preferred_area):
            # Non-custom area selected via flag: respect CLI flags, do not prompt
            position_name = args.preferred_area
            option_data = placement_options[args.preferred_area]
            # Font family
            font_name = args.font_family or pick_modern_sans(overlay_system.font_manager)
            # Proportional size: cap by ~5% of min dimension, and not less than recommended
            recommended_size = option_data.get('recommended_font_size', 24)
            W = analysis['image'].shape[1]
            H = analysis['image'].shape[0]
            cap = max(16, int(min(W, H) * 0.05))
            font_size = args.font_size or min(recommended_size, cap)
            # Color: harmonized with palette via recommendation unless user provided
            chosen_color = overlay_system.font_manager.validate_color(args.text_color) if args.text_color else None
            style_config = overlay_system.build_style_config(
                font_name, font_size, option_data['bg_color'], chosen_color,
                opacity=args.opacity, blend_mode=args.blend, shadow=(not args.no_shadow)
            )
        else:
            # Fallback to fully interactive flow if the requested area is unavailable
            position_name, option_data = overlay_system.prompt_position(analysis)
            font_name = overlay_system.prompt_font_family()
            recommended_size = option_data.get('recommended_font_size', 24)
            font_size = overlay_system.prompt_font_size(recommended_size)
            chosen_color = overlay_system.prompt_text_color(option_data['bg_color'])
            text_orientation = args.orientation or overlay_system.prompt_text_orientation()
            style_config = overlay_system.build_style_config(
                font_name, font_size, option_data['bg_color'], chosen_color,
                opacity=args.opacity, blend_mode=args.blend, shadow=(not args.no_shadow)
            )
    else:
        # Interactive selection flow
        position_name, option_data = overlay_system.prompt_position(analysis)
        font_name = overlay_system.prompt_font_family()
        recommended_size = option_data.get('recommended_font_size', 24)
        font_size = overlay_system.prompt_font_size(recommended_size)
        chosen_color = overlay_system.prompt_text_color(option_data['bg_color'])
        # Text orientation prompt
        text_orientation = args.orientation or overlay_system.prompt_text_orientation()
        style_config = overlay_system.build_style_config(
            font_name, font_size, option_data['bg_color'], chosen_color,
            opacity=args.opacity, blend_mode=args.blend, shadow=(not args.no_shadow)
        )
    
    print(f"\nCreating final overlay using {position_name} position...")
    # Decide if the chosen region contains sufficient subject to warrant occlusion
    sal = analysis.get('saliency')
    auto_behind = False
    if sal is not None and option_data.get('box') is not None:
        x0, y0, x1, y1 = option_data['box']
        H, W = sal.shape[:2]
        x0 = max(0, min(W, int(x0)))
        x1 = max(0, min(W, int(x1)))
        y0 = max(0, min(H, int(y0)))
        y1 = max(0, min(H, int(y1)))
        if x1 > x0 and y1 > y0:
            region = sal[y0:y1, x0:x1]
            if region.size:
                subject_fraction = float((region > 0.5).mean())
                auto_behind = subject_fraction >= 0.15  # threshold: at least 15% subject pixels
                print(f"Subject presence in selected area: {subject_fraction:.2%}. "
                      f"Occlusion: {'ON' if auto_behind else 'OFF'}.")
    # Final decision: only place behind if subject is present
    use_behind = auto_behind
    if args.behind and not auto_behind:
        print("--behind requested, but no sufficient subject detected in the selected area; drawing in front.")

    overlay_system.create_final_overlay(
        analysis['image'],
        option_data['box'],
        args.text,
        style_config,
        args.output,
        saliency=sal,
        behind_subject=use_behind,
        orientation=text_orientation
    )

if __name__ == "__main__":
    main()