import numpy as np
from textoverlay.utils.vision import integral_image, mean_from_integral
from typing import List, Tuple, Dict

class RegionAnalyzer:
    def __init__(self, img_bgr, sal_map, edge_map, var_map):
        self.img_bgr = img_bgr
        self.sal_map = sal_map
        self.edge_map = edge_map
        self.var_map = var_map
        self.h, self.w = sal_map.shape
        
        # Create integral images for fast computation
        self.integrals = {
            'sal': integral_image(sal_map.astype(np.float32)),
            'edge': integral_image(edge_map.astype(np.float32)),
            'var': integral_image(var_map.astype(np.float32)),
        }
    
    def analyze_regions(self, text_length: int = 10) -> Dict[str, List[Tuple]]:
        """Find optimal placement regions including requested positions.
        Regions covered:
          - left, center, right (full-height thirds)
          - center_left, center_middle, center_right (middle row thirds)
          - bottom_left, bottom_center, bottom_right (bottom row thirds)
        """
        
        # Define thirds
        x_third = self.w // 3
        y_third = self.h // 3
        
        # Full-height columns
        left_region = (0, 0, x_third, self.h)
        center_region = (x_third, 0, 2 * x_third, self.h)
        right_region = (2 * x_third, 0, self.w, self.h)
        
        # Middle row thirds
        center_left_region = (0, y_third, x_third, 2 * y_third)
        center_middle_region = (x_third, y_third, 2 * x_third, 2 * y_third)
        center_right_region = (2 * x_third, y_third, self.w, 2 * y_third)
        
        # Bottom row thirds
        bottom_left_region = (0, 2 * y_third, x_third, self.h)
        bottom_center_region = (x_third, 2 * y_third, 2 * x_third, self.h)
        bottom_right_region = (2 * x_third, 2 * y_third, self.w, self.h)
        
        # Ordered mapping to preserve prompt order
        regions = {
            'left': left_region,
            'center': center_region,
            'right': right_region,
            'center_left': center_left_region,
            'center_middle': center_middle_region,
            'center_right': center_right_region,
            'bottom_left': bottom_left_region,
            'bottom_center': bottom_center_region,
            'bottom_right': bottom_right_region,
        }
        
        # Inner margin to keep boxes away from image edges for a more balanced look
        inner_margin = max(10, int(0.04 * min(self.w, self.h)))
        
        results = {}
        
        for position, (x_start, y_start, x_end, y_end) in regions.items():
            candidates = self._find_candidates_in_region(
                x_start, y_start, x_end, y_end, text_length, inner_margin
            )
            results[position] = candidates
        
        return results
    
    def _find_candidates_in_region(self, x_start, y_start, x_end, y_end, text_length, inner_margin: int = 0) -> List[Tuple]:
        """Find best text placement candidates within a specific region, respecting inner margins"""
        candidates = []
        
        # Apply inner margins
        x0r = max(0, x_start + inner_margin)
        y0r = max(0, y_start + inner_margin)
        x1r = min(self.w, x_end - inner_margin)
        y1r = min(self.h, y_end - inner_margin)
        if x1r <= x0r or y1r <= y0r:
            return []
        
        # Calculate region dimensions
        region_width = x1r - x0r
        region_height = y1r - y0r
        region_aspect_ratio = region_width / region_height if region_height > 0 else 1
        
        # Estimate text box dimensions based on layout preference
        if region_aspect_ratio > 1.5:  # Wide region - prefer horizontal layout
            # For horizontal layout: wider, shorter boxes
            estimated_width = min(int(text_length * 15), int(region_width * 0.9))
            estimated_height = max(40, min(80, int(region_height * 0.3)))
        else:  # Narrow region - allow vertical stacking
            # For vertical layout: narrower, taller boxes
            estimated_width = min(int(text_length * 12), int(region_width * 0.85))
            estimated_height = max(30, min(int(region_height * 0.6), int(estimated_width * 0.4)))
        
        # Generate multiple candidate boxes within the region
        step_x = max(10, int((region_width - estimated_width) / 5)) if region_width > estimated_width else 10
        step_y = max(10, int((region_height - estimated_height) / 6)) if region_height > estimated_height else 10
        
        for y in range(y0r, max(y0r + 1, int(y1r - estimated_height)), step_y):
            for x in range(x0r, max(x0r + 1, int(x1r - estimated_width)), step_x):
                box = (x, y, x + int(estimated_width), y + int(estimated_height))
                score = self._score_box(box)
                candidates.append((score, box))
        
        # Sort by score (higher is better) and return top candidates
        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates[:5]  # Return top 5 candidates per region
    
    def _score_box(self, box) -> float:
        """Score a text placement box (higher = better placement)"""
        x0, y0, x1, y1 = box
        
        # Ensure box is within image bounds
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        
        if x0 >= x1 or y0 >= y1:
            return 0.0
        
        # Calculate metrics using integral images
        sal_mean = mean_from_integral(self.integrals['sal'], x0, y0, x1, y1)
        edge_mean = mean_from_integral(self.integrals['edge'], x0, y0, x1, y1)
        var_mean = mean_from_integral(self.integrals['var'], x0, y0, x1, y1)
        
        # Score calculation (lower saliency, edges, variance = better)
        sal_score = 1.0 - sal_mean  # Lower saliency is better
        edge_score = 1.0 - edge_mean  # Lower edge density is better
        var_score = 1.0 - var_mean  # Lower variance is better
        
        # Border penalty (avoid edges of image)
        border_penalty = 0.0
        margin = 20
        if x0 < margin or y0 < margin or x1 > (self.w - margin) or y1 > (self.h - margin):
            border_penalty = 0.3
        
        # Weighted final score
        score = (0.4 * sal_score + 0.3 * edge_score + 0.3 * var_score) - border_penalty
        return max(0.0, score)
    
    def get_best_options(self, text: str) -> Dict[str, Dict]:
        """Get the best placement option for each position with metadata"""
        text_length = len(text)
        region_results = self.analyze_regions(text_length)
        
        best_options = {}
        
        for position, candidates in region_results.items():
            if candidates:
                score, box = candidates[0]  # Best candidate
                x0, y0, x1, y1 = box
                
                # Calculate additional metadata
                center_x = (x0 + x1) // 2
                center_y = (y0 + y1) // 2
                
                # Get background color for this region
                bg_patch = self.img_bgr[y0:y1, x0:x1]
                if bg_patch.size > 0:
                    bg_color = tuple(map(int, bg_patch.reshape(-1, 3).mean(axis=0)))
                else:
                    bg_color = (128, 128, 128)
                
                best_options[position] = {
                    'box': box,
                    'score': score,
                    'center': (center_x, center_y),
                    'bg_color': bg_color,
                    'saliency': mean_from_integral(self.integrals['sal'], x0, y0, x1, y1),
                    'recommended_font_size': self._estimate_font_size(box),
                    'quality': 'excellent' if score > 0.7 else 'good' if score > 0.5 else 'fair'
                }
        
        return best_options
    
    def _estimate_font_size(self, box) -> int:
        """Estimate optimal font size for a given box"""
        x0, y0, x1, y1 = box
        box_height = y1 - y0
        box_width = x1 - x0
        
        # Base font size on box dimensions
        height_based = int(box_height * 0.6)
        width_based = int(box_width * 0.08)
        
        # Use the smaller of the two, with reasonable bounds
        font_size = min(height_based, width_based)
        return max(12, min(font_size, 72))

def analyze_image_regions(img_bgr, sal_map, edge_map, var_map, text: str) -> Dict[str, Dict]:
    """Main function to analyze image and return placement options"""
    analyzer = RegionAnalyzer(img_bgr, sal_map, edge_map, var_map)
    return analyzer.get_best_options(text)
