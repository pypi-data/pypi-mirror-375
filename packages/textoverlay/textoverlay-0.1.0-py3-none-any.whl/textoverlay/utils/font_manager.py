import os
import platform
from PIL import ImageFont, ImageColor
from typing import List, Dict, Tuple, Optional
import json
import urllib.request
import errno
import glob
import re

class FontManager:
    def __init__(self):
        self.system_fonts = self._discover_system_fonts()
        self.color_presets = self._load_color_presets()
        self.size_presets = [12, 16, 20, 24, 28, 32, 36, 42, 48, 56, 64, 72, 84, 96]
        
        # Curated, tasteful color palette (names mapped to RGB)
        # Neutral/minimal and professional-friendly accents only
        self.curated_colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "charcoal": (54, 69, 79),         # deep gray-blue
            "slate": (99, 110, 114),          # muted slate gray
            "light gray": (230, 230, 230),
            "gray": (128, 128, 128),
            "navy": (0, 51, 102),             # refined navy
            "indigo": (48, 63, 159),
            "teal": (0, 121, 121),
            "forest": (34, 139, 34),          # forest green
            "olive": (97, 108, 64),
            "burgundy": (128, 0, 32),
            "wine": (90, 24, 38),
            "gold": (212, 175, 55),           # softened gold
            "amber": (240, 170, 0),           # refined amber
            "sand": (199, 178, 153),
            "coral": (233, 92, 88),
            # Brand-inspired curated names
            "spotify green": (29, 185, 84),
            "spotify black": (25, 20, 20),
            "instagram orange": (245, 133, 41),
            "instagram pink": (221, 42, 123),
            "instagram purple": (129, 52, 175),
            "instagram blue": (81, 91, 212),
            "instagram yellow": (254, 218, 119),
            "coca-cola red": (228, 26, 28),
            "coca-cola dark red": (125, 0, 0),
            "google blue": (66, 133, 244),
            "google red": (234, 67, 53),
            "google yellow": (251, 188, 5),
            "google green": (52, 168, 83),
            "google charcoal": (32, 33, 36),
            "apple gray": (163, 170, 174),
            "apple light": (245, 245, 247),
            "apple graphite": (29, 29, 31),
            "airbnb coral": (255, 56, 92),
            "airbnb yellow": (255, 180, 0),
            "airbnb teal": (0, 166, 153),
            "airbnb orange": (252, 100, 45),
            "airbnb gray": (72, 72, 72),
            "netflix red": (229, 9, 20),
            "netflix black": (34, 31, 31),
            "netflix crimson": (184, 29, 36),
            "nike black": (17, 17, 17),
            "nike gray": (126, 126, 126),
            "nike red": (255, 59, 48),
            "starbucks green": (0, 112, 74),
            "starbucks mint": (212, 233, 226),
            "starbucks dark green": (30, 57, 50),
            "microsoft blue": (0, 120, 212),
            "microsoft red": (232, 17, 35),
            "microsoft green": (16, 124, 16),
            "microsoft gold": (255, 185, 0),
            "microsoft purple": (92, 45, 145),
        }
        # Aliases -> canonical curated names
        self._alias_map = {
            "grey": "gray",
            "lightgrey": "light gray",
            "light gray": "light gray",
            "darkgrey": "charcoal",
            "darkgray": "charcoal",
            "forest green": "forest",
            # Brand shortcuts
            "spotify": "spotify green",
            "instagram": "instagram pink",
            "insta": "instagram pink",
            "coca cola": "coca-cola red",
            "coke": "coca-cola red",
            "google": "google blue",
            "apple": "apple graphite",
            "airbnb": "airbnb coral",
            "netflix": "netflix red",
            "nike": "nike black",
            "starbucks": "starbucks green",
            "microsoft": "microsoft blue",
        }
    
    def _discover_system_fonts(self) -> Dict[str, str]:
        """Discover available system fonts"""
        fonts = {}
        
        # Also look inside project-local fonts folders so users can drop TTFs there
        project_fonts_dir = os.path.join(os.getcwd(), "data", "fonts")
        extra_fonts_dir = os.path.join(os.getcwd(), "fonts")
        font_dirs = [
            extra_fonts_dir,
            project_fonts_dir,
            "C:/Windows/Fonts/",
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/")
        ]
        
        # Additionally scan npm-installed webfont packages (typeface-*) if present
        try:
            typeface_dirs = glob.glob(os.path.join(os.getcwd(), "node_modules", "typeface-*", "files"))
        except Exception:
            typeface_dirs = []
        
        # Restricted to the requested font family names and likely file patterns
        common_fonts = {
            # Brush/Script
            "AlexBrush-Regular": [
                "AlexBrush-Regular.ttf", "AlexBrush-Regular.otf",
                "AlexBrush.ttf", "AlexBrush.otf"
            ],
            "Allura-Regular": [
                "Allura-Regular.ttf", "Allura-Regular.otf",
                "Allura.ttf", "Allura.otf"
            ],
            "AmaticSC-Regular": [
                "AmaticSC-Regular.ttf", "AmaticSC-Regular.otf",
                "AmaticSC.ttf", "AmaticSC.otf"
            ],
            "Canterbury": [
                "Canterbury.ttf", "Canterbury.otf"
            ],
            # Josefin Sans
            "JosefinSans-Bold": [
                "JosefinSans-Bold.ttf", "JosefinSans-Bold.otf"
            ],
            "JosefinSans-BoldItalic": [
                "JosefinSans-BoldItalic.ttf", "JosefinSans-BoldItalic.otf"
            ],
            "JosefinSans-Italic": [
                "JosefinSans-Italic.ttf", "JosefinSans-Italic.otf"
            ],
            "JosefinSans-Light": [
                "JosefinSans-Light.ttf", "JosefinSans-Light.otf"
            ],
            "JosefinSans-LightItalic": [
                "JosefinSans-LightItalic.ttf", "JosefinSans-LightItalic.otf"
            ],
            "JosefinSans-Regular": [
                "JosefinSans-Regular.ttf", "JosefinSans-Regular.otf",
                "JosefinSans.ttf", "JosefinSans.otf"
            ],
            # Open Sans
            "OpenSans-BoldItalic": [
                "OpenSans-BoldItalic.ttf", "OpenSans-BoldItalic.otf"
            ],
            "OpenSans-Italic": [
                "OpenSans-Italic.ttf", "OpenSans-Italic.otf"
            ],
            "OpenSans-Regular": [
                "OpenSans-Regular.ttf", "OpenSans-Regular.otf",
                "OpenSans.ttf", "OpenSans.otf"
            ],
            "OpenSans-SemiboldItalic": [
                "OpenSans-SemiboldItalic.ttf", "OpenSans-SemiboldItalic.otf",
                "OpenSans-SemiBoldItalic.ttf", "OpenSans-SemiBoldItalic.otf"
            ],
            # Quicksand
            "Quicksand-Bold": [
                "Quicksand-Bold.ttf", "Quicksand-Bold.otf"
            ],
            "Quicksand-BoldItalic": [
                "Quicksand-BoldItalic.ttf", "Quicksand-BoldItalic.otf"
            ],
            "Quicksand-LightItalic": [
                "Quicksand-LightItalic.ttf", "Quicksand-LightItalic.otf"
            ],
            "Quicksand_Dash": [
                "Quicksand_Dash.ttf", "Quicksand_Dash.otf",
                "Quicksand-Dash.ttf", "Quicksand-Dash.otf"
            ],
            # Roboto
            "Roboto-Black": [
                "Roboto-Black.ttf", "Roboto-Black.otf"
            ],
            "Roboto-BlackItalic": [
                "Roboto-BlackItalic.ttf", "Roboto-BlackItalic.otf"
            ],
            "Roboto-Bold": [
                "Roboto-Bold.ttf", "Roboto-Bold.otf"
            ],
        }
        
        # Ensure project fonts dir exists (non-fatal if it cannot be created)
        try:
            os.makedirs(project_fonts_dir, exist_ok=True)
        except Exception:
            pass

        # Search for fonts
        for font_name, filenames in common_fonts.items():
            for font_dir in font_dirs:
                if os.path.exists(font_dir):
                    for filename in filenames:
                        font_path = os.path.join(font_dir, filename)
                        if os.path.exists(font_path):
                            fonts[font_name] = font_path
                            break
                    if font_name in fonts:
                        break
        
        # Map npm typeface packages to curated names by weight/style
        # Supports: typeface-josefin-sans, typeface-open-sans, typeface-quicksand
        for tdir in typeface_dirs:
            try:
                pkg_dir = os.path.dirname(tdir)  # .../node_modules/typeface-xxx
                pkg_name = os.path.basename(pkg_dir).lower()
                family = pkg_name.replace("typeface-", "")
                for f in os.listdir(tdir):
                    if not f.lower().endswith(".ttf"):
                        continue
                    fname = f.lower()
                    path = os.path.join(tdir, f)
                    # Extract numeric weight from filename if present (e.g., -400-)
                    weight = 400
                    m = re.search(r"-(100|200|300|400|500|600|700|800|900)-", fname)
                    if m:
                        try:
                            weight = int(m.group(1))
                        except Exception:
                            weight = 400
                    italic = ("italic" in fname)
                    key = None
                    if family == "josefin-sans":
                        if weight == 300 and not italic:
                            key = "JosefinSans-Light"
                        elif weight == 300 and italic:
                            key = "JosefinSans-LightItalic"
                        elif weight == 400 and not italic:
                            key = "JosefinSans-Regular"
                        elif weight == 400 and italic:
                            key = "JosefinSans-Italic"
                        elif weight == 700 and not italic:
                            key = "JosefinSans-Bold"
                        elif weight == 700 and italic:
                            key = "JosefinSans-BoldItalic"
                    elif family == "open-sans":
                        if weight == 400 and not italic:
                            key = "OpenSans-Regular"
                        elif weight == 400 and italic:
                            key = "OpenSans-Italic"
                        elif weight == 600 and italic:
                            key = "OpenSans-SemiboldItalic"
                        elif weight == 700 and italic:
                            key = "OpenSans-BoldItalic"
                    elif family == "quicksand":
                        if weight == 700 and not italic:
                            key = "Quicksand-Bold"
                        elif weight == 700 and italic:
                            key = "Quicksand-BoldItalic"
                        elif weight == 300 and italic:
                            key = "Quicksand-LightItalic"
                    if key and key not in fonts:
                        fonts[key] = path
            except Exception:
                # Non-fatal: skip malformed packages
                pass
        
        # Additionally scan project 'fonts/' recursively for variable fonts and any other TTF/OTF
        if os.path.exists(extra_fonts_dir):
            try:
                # Map common variable font files to curated keys
                # Josefin Sans
                js_var = glob.glob(os.path.join(extra_fonts_dir, "**", "JosefinSans-VariableFont_wght.ttf"), recursive=True)
                if js_var and "JosefinSans-Regular" not in fonts:
                    fonts["JosefinSans-Regular"] = js_var[0]
                js_ivar = glob.glob(os.path.join(extra_fonts_dir, "**", "JosefinSans-Italic-VariableFont_wght.ttf"), recursive=True)
                if js_ivar and "JosefinSans-Italic" not in fonts:
                    fonts["JosefinSans-Italic"] = js_ivar[0]
                # Open Sans
                os_var = glob.glob(os.path.join(extra_fonts_dir, "**", "OpenSans-VariableFont_wdth,wght.ttf"), recursive=True)
                if os_var and "OpenSans-Regular" not in fonts:
                    fonts["OpenSans-Regular"] = os_var[0]
                os_ivar = glob.glob(os.path.join(extra_fonts_dir, "**", "OpenSans-Italic-VariableFont_wdth,wght.ttf"), recursive=True)
                if os_ivar and "OpenSans-Italic" not in fonts:
                    fonts["OpenSans-Italic"] = os_ivar[0]
                # Quicksand
                qs_var = glob.glob(os.path.join(extra_fonts_dir, "**", "Quicksand-VariableFont_wght.ttf"), recursive=True)
                if qs_var and "Quicksand-Regular" not in fonts:
                    fonts["Quicksand-Regular"] = qs_var[0]
                
                # Generic: add any other TTF/OTF by file base name
                for fp in glob.glob(os.path.join(extra_fonts_dir, "**", "*.ttf"), recursive=True) + \
                           glob.glob(os.path.join(extra_fonts_dir, "**", "*.otf"), recursive=True):
                    key = os.path.splitext(os.path.basename(fp))[0]
                    if key not in fonts:
                        fonts[key] = fp
            except Exception:
                pass

        # Add default fallback (PIL built-in)
        fonts["Default"] = None
        
        return fonts

    def download_missing_curated_fonts(self, dest_dir: str = os.path.join("data", "fonts")) -> Dict[str, str]:
        """Download curated fonts that are missing into dest_dir.

        Returns a mapping of font_name -> local_path for successfully downloaded fonts.
        Fonts that are not available via Google Fonts (e.g., Canterbury, Quicksand_Dash)
        are skipped and must be installed manually.
        """
        # Map our curated font keys to likely Google Fonts GitHub raw URLs
        # Note: We target the static TTFs when available.
        base = "https://raw.githubusercontent.com/google/fonts/main"
        urls: Dict[str, List[str]] = {
            # Alex Brush
            "AlexBrush-Regular": [f"{base}/ofl/alexbrush/AlexBrush-Regular.ttf"],
            # Allura
            "Allura-Regular": [f"{base}/ofl/allura/Allura-Regular.ttf"],
            # Amatic SC
            "AmaticSC-Regular": [f"{base}/ofl/amaticsc/AmaticSC-Regular.ttf"],
            # Josefin Sans
            "JosefinSans-Bold": [f"{base}/ofl/josefinsans/static/JosefinSans-Bold.ttf"],
            "JosefinSans-BoldItalic": [f"{base}/ofl/josefinsans/static/JosefinSans-BoldItalic.ttf"],
            "JosefinSans-Italic": [f"{base}/ofl/josefinsans/static/JosefinSans-Italic.ttf"],
            "JosefinSans-Light": [f"{base}/ofl/josefinsans/static/JosefinSans-Light.ttf"],
            "JosefinSans-LightItalic": [f"{base}/ofl/josefinsans/static/JosefinSans-LightItalic.ttf"],
            "JosefinSans-Regular": [f"{base}/ofl/josefinsans/static/JosefinSans-Regular.ttf"],
            # Open Sans
            "OpenSans-BoldItalic": [f"{base}/ofl/opensans/static/OpenSans-BoldItalic.ttf"],
            "OpenSans-Italic": [f"{base}/ofl/opensans/static/OpenSans-Italic.ttf"],
            "OpenSans-Regular": [f"{base}/ofl/opensans/static/OpenSans-Regular.ttf"],
            "OpenSans-SemiboldItalic": [f"{base}/ofl/opensans/static/OpenSans-SemiBoldItalic.ttf"],
            # Quicksand
            "Quicksand-Bold": [f"{base}/ofl/quicksand/static/Quicksand-Bold.ttf"],
            "Quicksand-BoldItalic": [f"{base}/ofl/quicksand/static/Quicksand-BoldItalic.ttf"],
            "Quicksand-LightItalic": [f"{base}/ofl/quicksand/static/Quicksand-LightItalic.ttf"],
            # Roboto (Apache license path)
            "Roboto-Black": [f"{base}/apache/roboto/static/Roboto-Black.ttf"],
            "Roboto-BlackItalic": [f"{base}/apache/roboto/static/Roboto-BlackItalic.ttf"],
            "Roboto-Bold": [f"{base}/apache/roboto/static/Roboto-Bold.ttf"],
        }

        # Fonts not on Google Fonts repo (manual install suggested)
        manual_only = {"Canterbury", "Quicksand_Dash"}

        # Prepare destination directory
        try:
            os.makedirs(dest_dir, exist_ok=True)
        except OSError as e:
            if e.errno not in (errno.EEXIST,):
                raise

        # Determine missing fonts
        current = self._discover_system_fonts()
        missing = [name for name in urls.keys() if name not in current or not current.get(name)]

        downloaded: Dict[str, str] = {}
        for name in missing:
            candidates = urls.get(name, [])
            target = os.path.join(dest_dir, f"{name}.ttf")
            for u in candidates:
                try:
                    print(f"Downloading {name} from {u} ...")
                    urllib.request.urlretrieve(u, target)
                    downloaded[name] = target
                    break
                except Exception as ex:
                    print(f"Failed to download {name} from {u}: {ex}")
            if name not in downloaded:
                print(f"Unable to download {name}. You may need to install it manually.")

        if manual_only & set(missing):
            print("The following fonts are not hosted on the Google Fonts repo and must be installed manually:")
            for n in sorted(manual_only & set(missing)):
                print(f"  - {n}")

        # Refresh discovered fonts after download
        self.system_fonts = self._discover_system_fonts()
        return downloaded
    
    def _load_color_presets(self) -> Dict[str, Dict]:
        """Load predefined color schemes"""
        return {
            "Classic": {
                "White": (255, 255, 255),
                "Black": (0, 0, 0),
                "Gray": (128, 128, 128),
                "Dark Gray": (64, 64, 64),
            },
            "Vibrant": {
                "Red": (255, 0, 0),
                "Blue": (0, 100, 255),
                "Green": (0, 200, 0),
                "Orange": (255, 165, 0),
                "Purple": (128, 0, 128),
            },
            "Professional": {
                "Navy": (0, 51, 102),
                "Burgundy": (128, 0, 32),
                "Forest Green": (34, 139, 34),
                "Charcoal": (54, 69, 79),
                "Gold": (255, 215, 0),
            },
            "Pastel": {
                "Light Blue": (173, 216, 230),
                "Light Pink": (255, 182, 193),
                "Light Green": (144, 238, 144),
                "Light Yellow": (255, 255, 224),
                "Lavender": (230, 230, 250),
            },
            # Brand palettes
            "Spotify Vibe": {
                "Spotify Green": (29, 185, 84),
                "Deep Black": (25, 20, 20),
                "White": (255, 255, 255),
                "Rich Black": (18, 18, 18),
                "Gray 5353": (83, 83, 83),
            },
            "Instagram Gradient": {
                "Orange": (245, 133, 41),
                "Pink": (221, 42, 123),
                "Purple": (129, 52, 175),
                "Blue": (81, 91, 212),
                "Yellow": (254, 218, 119),
            },
            "Coca-Cola Classic": {
                "Coke Red": (228, 26, 28),
                "White": (255, 255, 255),
                "Black": (0, 0, 0),
                "Very Light Gray": (245, 245, 245),
                "Dark Red": (125, 0, 0),
            },
            "Google Material": {
                "Blue": (66, 133, 244),
                "Red": (234, 67, 53),
                "Yellow": (251, 188, 5),
                "Green": (52, 168, 83),
                "Charcoal": (32, 33, 36),
            },
            "Apple Minimal": {
                "Black": (0, 0, 0),
                "Gray": (163, 170, 174),
                "Light": (245, 245, 247),
                "Graphite": (29, 29, 31),
                "White": (255, 255, 255),
            },
            "Airbnb Warm": {
                "Coral": (255, 56, 92),
                "Sun": (255, 180, 0),
                "Teal": (0, 166, 153),
                "Orange": (252, 100, 45),
                "Gray": (72, 72, 72),
            },
            "Netflix Bold": {
                "Red": (229, 9, 20),
                "Near Black": (34, 31, 31),
                "White": (255, 255, 255),
                "Crimson": (184, 29, 36),
                "Black": (0, 0, 0),
            },
            "Nike Energy": {
                "Deep Black": (17, 17, 17),
                "White": (255, 255, 255),
                "Light": (245, 245, 245),
                "Gray": (126, 126, 126),
                "Red": (255, 59, 48),
            },
            "Starbucks Green": {
                "Green": (0, 112, 74),
                "White": (255, 255, 255),
                "Black": (0, 0, 0),
                "Mint": (212, 233, 226),
                "Dark Green": (30, 57, 50),
            },
            "Microsoft Fluent": {
                "Blue": (0, 120, 212),
                "Red": (232, 17, 35),
                "Green": (16, 124, 16),
                "Gold": (255, 185, 0),
                "Purple": (92, 45, 145),
            },
            "Luxury Metallics": {
    "Gold": (212, 175, 55),
    "Silver": (192, 192, 192),
    "Rose Gold": (183, 110, 121),
    "Platinum": (229, 228, 226),
    "Bronze": (205, 127, 50),
    },

    "Jewel Tones": {
    "Ruby": (155, 17, 30),
    "Emerald": (0, 155, 119),
    "Sapphire": (15, 82, 186),
    "Amethyst": (153, 102, 204),
    "Topaz": (255, 200, 124),
    },

    "Deep & Luxurious": {
    "Midnight Blue": (25, 25, 112),
    "Oxblood": (88, 0, 0),
    "Dark Plum": (54, 5, 56),
    "Mahogany": (128, 0, 0),
    "Forest Green Deep": (1, 50, 32),
    },

    "Sophisticated Neutrals": {
    "Ivory": (255, 255, 240),
    "Champagne": (247, 231, 206),
    "Taupe": (72, 60, 50),
    "Cocoa": (92, 64, 51),
    "Graphite": (45, 45, 48),
    },

        }
    
    def get_available_fonts(self) -> List[str]:
        """Get list of available font names"""
        return list(self.system_fonts.keys())
    
    def get_font_path(self, font_name: str) -> Optional[str]:
        """Get path to font file"""
        return self.system_fonts.get(font_name)
    
    def get_color_schemes(self) -> Dict[str, Dict]:
        """Get all color schemes"""
        return self.color_presets
    
    def get_size_presets(self) -> List[int]:
        """Get predefined font sizes"""
        return self.size_presets
    
    def create_font(self, font_name: str, size: int) -> ImageFont.ImageFont:
        """Create PIL font object"""
        font_path = self.get_font_path(font_name)
        
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
        
        # Fallback to default font
        try:
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()
    
    def validate_color(self, color_input) -> Tuple[int, int, int]:
        """Validate and convert color input to RGB tuple.
        Prefers curated names; falls back to PIL named colors/hex.
        """
        if isinstance(color_input, tuple) and len(color_input) == 3:
            return tuple(max(0, min(255, int(c))) for c in color_input)
        
        if isinstance(color_input, str):
            name = color_input.strip()
            lower = name.lower()
            # Normalize via alias map
            canonical = self._alias_map.get(lower, lower)
            # Prefer curated mapping when available
            if canonical in self.curated_colors:
                return self.curated_colors[canonical]
            # Hex or other named colors via PIL
            try:
                if name.startswith('#'):
                    return ImageColor.getrgb(name)
                # If not curated but recognized by PIL, accept
                return ImageColor.getrgb(name)
            except Exception:
                pass
        
        # Default to black
        return (0, 0, 0)

    def get_curated_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """Return curated color name -> RGB mapping (lowercase names)."""
        return dict(self.curated_colors)

    def get_alias_map(self) -> Dict[str, str]:
        """Return alias mapping for color names (lowercase)."""
        return dict(self._alias_map)
    
class TextStyleConfig:
    def __init__(self, font_name: str = "Default", font_size: int = 24, 
                 color: Tuple[int, int, int] = (255, 255, 255), 
                 stroke_width: int = 2, stroke_color: Tuple[int, int, int] = (0, 0, 0),
                 opacity: float = 0.9, blend_mode: str = "overlay",
                 shadow: bool = True, shadow_offset: Tuple[int, int] = (2, 2),
                 shadow_blur: int = 4, shadow_color_rgba: Tuple[int, int, int, int] = (0, 0, 0, 90)):
        self.font_name = font_name
        self.font_size = font_size
        self.color = color
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        # New styling fields
        self.opacity = float(max(0.0, min(1.0, opacity)))
        self.blend_mode = blend_mode
        self.shadow = bool(shadow)
        self.shadow_offset = shadow_offset
        self.shadow_blur = int(max(0, shadow_blur))
        self.shadow_color_rgba = shadow_color_rgba
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'font_name': self.font_name,
            'font_size': self.font_size,
            'color': self.color,
            'stroke_width': self.stroke_width,
            'stroke_color': self.stroke_color,
            'opacity': self.opacity,
            'blend_mode': self.blend_mode,
            'shadow': self.shadow,
            'shadow_offset': self.shadow_offset,
            'shadow_blur': self.shadow_blur,
            'shadow_color_rgba': self.shadow_color_rgba,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TextStyleConfig':
        """Create from dictionary"""
        return cls(
            font_name=data.get('font_name', 'Default'),
            font_size=data.get('font_size', 24),
            color=tuple(data.get('color', (255, 255, 255))),
            stroke_width=data.get('stroke_width', 2),
            stroke_color=tuple(data.get('stroke_color', (0, 0, 0))),
            opacity=float(data.get('opacity', 0.9)),
            blend_mode=data.get('blend_mode', 'overlay'),
            shadow=bool(data.get('shadow', True)),
            shadow_offset=tuple(data.get('shadow_offset', (2, 2))),
            shadow_blur=int(data.get('shadow_blur', 4)),
            shadow_color_rgba=tuple(data.get('shadow_color_rgba', (0, 0, 0, 90)))
        )

def get_font_recommendations(bg_color: Tuple[int, int, int], 
                           image_style: str = "photo") -> List[TextStyleConfig]:
    """Get recommended font styles based on background color and image type"""
    font_manager = FontManager()
    recommendations = []

    # Calculate background brightness
    brightness = sum(bg_color) / 3

    # Choose contrasting colors
    if brightness > 128:  # Light background
        text_colors = [(0, 0, 0), (64, 64, 64), (0, 51, 102)]
        stroke_colors = [(255, 255, 255), (200, 200, 200)]
    else:  # Dark background
        text_colors = [(255, 255, 255), (240, 240, 240), (255, 215, 0)]
        stroke_colors = [(0, 0, 0), (64, 64, 64)]

    # Available new fonts on this machine (exclude Default placeholder)
    available = [f for f, p in font_manager.system_fonts.items() if f != "Default" and p]

    # Curated sets from the new list
    creative_fonts = [
        "AlexBrush-Regular", "Allura-Regular", "AmaticSC-Regular", "Canterbury",
        "Quicksand-BoldItalic", "Quicksand-LightItalic", "Quicksand_Dash",
    ]
    professional_fonts = [
        "OpenSans-Regular", "OpenSans-Italic", "OpenSans-BoldItalic", "OpenSans-SemiboldItalic",
        "JosefinSans-Regular", "JosefinSans-Bold", "JosefinSans-LightItalic",
        "Roboto-Bold", "Roboto-Black", "Roboto-BlackItalic",
    ]
    default_fonts = [
        "OpenSans-Regular", "JosefinSans-Regular", "Quicksand-Bold", "Roboto-Bold"
    ]

    def pick_fonts(preferred: List[str], fallback: List[str]) -> List[str]:
        chosen = [f for f in preferred if f in available]
        if not chosen:
            chosen = [f for f in fallback if f in available]
        if not chosen:
            chosen = ["Default"]
        return chosen

    if image_style == "professional":
        fonts = pick_fonts(professional_fonts, default_fonts)
        sizes = [24, 28, 32]
    elif image_style == "creative":
        fonts = pick_fonts(creative_fonts, default_fonts)
        sizes = [28, 32, 36]
    else:  # Default/photo
        fonts = pick_fonts(default_fonts, professional_fonts)
        sizes = [24, 28, 32]

    # Generate recommendations (limit to 6 combos)
    for font in fonts[:3]:
        for size in sizes[:2]:
            for color in text_colors[:2]:
                recommendations.append(TextStyleConfig(
                    font_name=font,
                    font_size=size,
                    color=color,
                    stroke_width=2,
                    stroke_color=stroke_colors[0],
                    opacity=0.9,
                    blend_mode="overlay",
                    shadow=True,
                ))

    return recommendations[:6]
