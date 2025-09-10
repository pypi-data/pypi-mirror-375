"""
TextOverlay - Intelligent text overlay on images

A Python package that provides smart text positioning on images using
computer vision and core deep learning techniques to intelligently lay text over images.
"""

__version__ = "0.1.0"
__author__ = "Yug Makhecha"
__email__ = "yugmakhecha1710@gmail.com"


_import_errors = []
_successful_imports = []
_available_functions = {}

def _try_import(module_name, items, optional=False):
    """
    Try to import specific items from a module with fallback strategies.
    """
    imported = {}
    
    
    possible_paths = []
    base_module = __name__ or 'textoverlay'
    
    if module_name.startswith('.'):
        
        relative_name = module_name[1:] 
        possible_paths = [
            f"{base_module}.{relative_name}",
            relative_name,
            f"textoverlay.{relative_name}"
        ]
    else:
        
        possible_paths = [
            module_name,
            f"{base_module}.{module_name}",
            f"textoverlay.{module_name}"
        ]
    

    for full_path in possible_paths:
        try:
            import importlib
            module = importlib.import_module(full_path)
            
           
            for item in items:
                if hasattr(module, item):
                    imported[item] = getattr(module, item)
                else:
                    raise AttributeError(f"Module {full_path} has no attribute '{item}'")
            
            _successful_imports.append(f"{full_path}: {list(imported.keys())}")
            break  
            
        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            continue  
    
    
    if not imported and items:
        error_msg = f"Could not import {items} from any of: {possible_paths}"
        _import_errors.append(error_msg)
        
        if not optional:
            
            pass  
    
    return imported


import sys

layout_functions = _try_import('layout', [
    'pick_best_region', 
    'generate_candidates', 
    'score_box'
])

render_functions = _try_import('render', [
    'render_text_on_image'
])

vision_functions = _try_import('vision', [
    'infer_saliency',
    'edge_map_gray', 
    'local_variance',
    'integral_image',
    'mean_from_integral'
])


overlay_functions = _try_import('overlay.interactive_overlay', [
    'InteractiveTextOverlay',
    'pick_modern_sans'
])


advanced_functions = _try_import('models.advanced_layout', [
    'RegionAnalyzer',
    'analyze_image_regions'
], optional=True)

ml_functions = _try_import('models.u2net', [
    'U2NET',
    'U2NETP', 
    'load_u2like'
], optional=True)


_available_functions.update(layout_functions)
_available_functions.update(render_functions)
_available_functions.update(vision_functions)
_available_functions.update(overlay_functions)
_available_functions.update(advanced_functions)
_available_functions.update(ml_functions)

globals().update(_available_functions)

__all__ = list(_available_functions.keys())


def get_import_status():
    """Get detailed information about imports."""
    return {
        'successful_imports': _successful_imports,
        'import_errors': _import_errors,
        'available_functions': sorted(__all__),
        'total_available': len(__all__),
        'total_errors': len(_import_errors)
    }

def check_dependencies():
    """Check if dependencies are available."""
    deps_status = {}
    
    deps_to_check = {
        'PIL': 'Pillow',
        'cv2': 'OpenCV', 
        'numpy': 'NumPy',
        'matplotlib': 'Matplotlib',
        'torch': 'PyTorch (optional)',
        'torchvision': 'TorchVision (optional)'
    }
    
    for import_name, display_name in deps_to_check.items():
        try:
            __import__(import_name)
            deps_status[display_name] = "✓ Available"
        except ImportError:
            is_optional = "(optional)" in display_name
            deps_status[display_name] = "✗ Missing" + ("" if is_optional else " - required")
            
    return deps_status

def list_functions():
    """List all available functions."""
    if not __all__:
        print("No functions available through package imports.")
        print("\n However, your script might still work!")
        print("   The interactive_overlay module seems to import its own dependencies.")
        return
    
    print(f"TextOverlay Package Functions ({len(__all__)} available)")
    print("=" * 60)
    
    categories = {
        'Layout & Positioning': ['pick_best_region', 'generate_candidates', 'score_box'],
        'Text Rendering': ['render_text_on_image'], 
        'Vision Processing': ['infer_saliency', 'edge_map_gray', 'local_variance', 'integral_image', 'mean_from_integral'],
        'Interactive Tools': ['InteractiveTextOverlay', 'pick_modern_sans'],
        'Advanced Layout': ['RegionAnalyzer', 'analyze_image_regions'],
        'ML Models': ['U2NET', 'U2NETP', 'load_u2like']
    }
    
    for category, functions in categories.items():
        available = [f for f in functions if f in __all__]
        if available:
            print(f"\n📁 {category}:")
            for func in available:
                print(f"   • {func}")

def get_version():
    """Get package version info."""
    return {
        'version': __version__,
        'author': __author__,
        'functions_available': len(__all__),
        'status': 'Working' if len(__all__) > 0 else 'Limited functionality'
    }

# Only print status if we're being imported interactively, not during module execution
if not getattr(sys, '_called_from_test', False):
    if len(_available_functions) > 0:
        print(f"✅ TextOverlay v{__version__} ready - {len(__all__)} functions loaded")
    else:
        print(f"⚠️  TextOverlay v{__version__} - limited import success, but interactive_overlay should work")

# Make sure InteractiveTextOverlay is available even if imports failed
# This is a fallback for the main use case
if 'InteractiveTextOverlay' not in globals():
    try:
        from .overlay.interactive_overlay import InteractiveTextOverlay, pick_modern_sans
        globals().update({'InteractiveTextOverlay': InteractiveTextOverlay, 'pick_modern_sans': pick_modern_sans})
        if 'InteractiveTextOverlay' not in __all__:
            __all__.extend(['InteractiveTextOverlay', 'pick_modern_sans'])
    except ImportError:
        pass  # The module will still work via direct execution