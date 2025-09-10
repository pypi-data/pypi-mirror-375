# render.py
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import math
from textoverlay.utils.vision import mean_color_in_box

def luminance(rgb):
    # rgb in 0-255
    r,g,b = [c/255.0 for c in rgb]
    def srgb_to_lin(c):
        if c <= 0.04045:
            return c/12.92
        return ((c+0.055)/1.055)**2.4
    r_l = srgb_to_lin(r); g_l = srgb_to_lin(g); b_l = srgb_to_lin(b)
    return 0.2126*r_l + 0.7152*g_l + 0.0722*b_l

def contrast_ratio(l1, l2):
    # l1 and l2 are linear luminances (0..1); formula: (L1+0.05)/(L2+0.05)
    L1 = max(l1, l2)
    L2 = min(l1, l2)
    return (L1 + 0.05) / (L2 + 0.05)

def pick_text_color(bg_rgb):
    # return RGB fill color (255,255,255) or (0,0,0) depending on WCAG-like heuristic
    l = luminance(bg_rgb)
    white_l = luminance((255,255,255))
    black_l = luminance((0,0,0))
    if contrast_ratio(white_l, l) >= contrast_ratio(black_l, l):
        return (255,255,255)
    else:
        return (0,0,0)

def get_text_size(draw, text, font):
    """Get text size using modern PIL method"""
    try:
        # Try new method first (PIL >= 8.0.0)
        bbox = draw.textbbox((0, 0), text, font=font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])
    except AttributeError:
        # Fall back to deprecated method for older PIL
        return draw.textsize(text, font=font)

def choose_optimal_layout(draw, text, box, font_path, font_size):
    """Choose between horizontal and vertical text layout based on box dimensions"""
    x0, y0, x1, y1 = box
    box_width = x1 - x0 - 20  # padding
    box_height = y1 - y0 - 20  # padding
    
    if font_path is None:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, font_size)
    
    # Test if text fits horizontally in one line
    single_line_width, single_line_height = get_text_size(draw, text, font)
    
    # Calculate aspect ratio of the box
    box_aspect_ratio = box_width / box_height if box_height > 0 else 1
    
    # If text fits horizontally and box is wide enough, prefer horizontal layout
    if (single_line_width <= box_width and 
        single_line_height <= box_height and 
        box_aspect_ratio > 1.5):  # Wide box preference
        return 'horizontal', [text]
    
    # Otherwise, use vertical wrapping
    return 'vertical', wrap_text_to_lines(draw, text, font, box_width)

def wrap_text_to_lines(draw, text, font, max_width):
    """Wrap text into multiple lines based on width constraint"""
    lines = []
    words = text.split()
    cur = ""
    
    for w in words:
        test = cur + (" " if cur else "") + w
        if get_text_size(draw, test, font)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    
    return lines

def draw_text_with_stroke(img_pil, box, text, font_path=None, font_size=48, fill=None, stroke_width=2):
    draw = ImageDraw.Draw(img_pil)
    x0, y0, x1, y1 = box
    
    # Choose optimal layout strategy
    layout_type, lines = choose_optimal_layout(draw, text, box, font_path, font_size)
    
    if font_path is None:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, font_size)
    
    # Calculate total text dimensions
    line_heights = [get_text_size(draw, line, font)[1] for line in lines]
    total_h = sum(line_heights)
    max_line_width = max([get_text_size(draw, line, font)[0] for line in lines])
    
    # Center the text block vertically
    start_y = y0 + ((y1 - y0) - total_h) // 2
    
    # Draw each line
    current_y = start_y
    for i, line in enumerate(lines):
        tw, th = get_text_size(draw, line, font)
        
        # Center horizontally
        x = x0 + ((x1 - x0) - tw) // 2
        
        # Draw stroke (outline)
        if stroke_width > 0:
            stroke_fill = (0, 0, 0) if sum(fill) > 382 else (255, 255, 255)
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx == 0 and dy == 0:
                        continue
                    draw.text((x + dx, current_y + dy), line, font=font, fill=stroke_fill)
        
        # Draw main text
        draw.text((x, current_y), line, font=font, fill=fill)
        current_y += th
    
    return img_pil

def render_text_on_image(img_bgr: np.ndarray, box, text, font_path=None):
    # img_bgr: HxWx3 (BGR)
    img_pil = Image.fromarray(img_bgr[:,:,::-1])  # convert to RGB PIL
    x0,y0,x1,y1 = box
    # compute background color
    bg_rgb = mean_color_in_box(img_bgr, x0,y0,x1,y1)
    fill = pick_text_color(bg_rgb)
    # estimate font size roughly to fit box height
    box_h = y1 - y0
    font_size = max(12, int(box_h * 0.45))  # heuristic
    # stroke width small
    stroke_w = max(1, int(font_size*0.06))
    out = draw_text_with_stroke(img_pil, box, text, font_path=font_path, font_size=font_size, fill=fill, stroke_width=stroke_w)
    return np.array(out)[:,:,::-1]  # return BGR
