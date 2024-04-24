"""Unit conversion helpers."""

def m2pt(x, pt_size=0.0254/72.0):
    """Converts distance from meters to points. Default value is PDF point size."""
    return x / pt_size

def pt2m(x, pt_size=0.0254/72.0):
    """Converts distance from points to meters. Default value is PDF point size."""
    return x * pt_size

def m2in(x):
    """Converts distance from meters to inches."""
    return x / 0.0254

def m2px(x, resolution):
    """Converts distance from meters to pixels at the given resolution in DPI/PPI."""
    return m2in(x) * resolution
