from ..imports import *
from ..constants import *
# --- Spherical cap (true horizon-limited visibility) ---
def get_central_angle(r_m: float, h_m: float) -> float:
    """Angle at Earth's center from observer to horizon (radians)."""
    rh = add(r_m, h_m)
    # clamp to avoid domain issues
    val = max(-1.0, min(1.0, div(r_m, rh)))
    return math.acos(val)

def get_h_cap(r_m: float, h_m: float, theta: Optional[float] = None) -> float:
    """Spherical cap height (meters)."""
    if theta is None:
        theta = get_central_angle(r_m, h_m)
    return mul(r_m, sub(1.0, math.cos(theta)))

def spherical_cap_area(observer_altitude: float, units: str = 'meters'):
    """
    Visible spherical cap area from altitude (same units as input returned in unit^2).
    """
    r_m = earth_radius('meters')
    h_m = convert(observer_altitude, units, 'meters')

    theta = get_central_angle(r_m, h_m)
    h_cap_m = get_h_cap(r_m, h_m, theta)
    area_m2 = mul(2 * pi() * r_m, h_cap_m)  # 2π R h
    # return in requested units^2
    area_u2 = mul(area_m2, exp(_factor('meters', units), 2))
    return area_u2, convert(h_cap_m, 'meters', units), theta

def percent_visible(observer_altitude: float, units: str = 'meters') -> float:
    cap_area_u2, _, _ = spherical_cap_area(observer_altitude, units)
    full_area_u2 = full_earth_surface_area(units)
    return mul(div(cap_area_u2, full_area_u2), 100.0)

# --- Camera/FOV flat-projection helper (approximate) ---
def visible_area_flat(fov_degrees: float, altitude_m: float, units: str = 'meters'):
    """
    Given altitude in meters, return (area_m2, visible_radius_m). `units` arg is ignored,
    kept for backward compatibility.
    """
    fov_radians = math.radians(fov_degrees)
    visible_radius_m = altitude_m * math.tan(fov_radians / 2.0)
    area_m2 = math.pi * (visible_radius_m ** 2)
    return area_m2, visible_radius_m

def visible_surface_angle(visible_radius: float, sphere_radius: float) -> tuple[float, float]:
    """Chord-based angular span (approximate)."""
    chord_length = mul(2.0, visible_radius)
    angle_rad = mul(2.0, math.asin(div(chord_length, mul(2.0, sphere_radius))))
    angle_deg = math.degrees(angle_rad)
    return angle_rad, angle_deg

# --- FOV triangle pack (kept but made unit-consistent) ---
def get_triangle_area(a: float, b: float, c: float):
    s = (a + b + c) / 2.0
    area = math.sqrt(max(0.0, s * (s - a) * (s - b) * (s - c)))
    return area, s

def get_medians(a: float, b: float, c: float) -> float:
    # median from side 'a'
    return 0.5 * math.sqrt(max(0.0, 2*b*b + 2*c*c - a*a))

def get_triangle_medians(a: float, b: float, c: float):
    return {"ma": get_medians(b, c, a), "mb": get_medians(a, c, b), "mc": get_medians(a, b, c)}

def get_triangle_heights(a: float, b: float, c: float, area: float):
    ha = mul(2.0, div(area, a))
    hb = mul(2.0, div(area, b))
    hc = mul(2.0, div(area, c))
    return {"ha": ha, "hb": hb, "hc": hc}

def compute_fov_triangle(altitude: float, fov_angle_deg: float, units: str = 'meters'):
    """Simple isosceles triangle model for a camera at altitude."""
    a = convert(altitude, units, 'meters')
    fov_angle_rad = math.radians(fov_angle_deg)
    base = 2.0 * a * math.tan(fov_angle_rad / 2.0)
    b = c = a

    # Triangle inequality guard
    if not ((base + b > c) and (base + c > b) and (b + c > base)):
        return {"error": "Invalid triangle geometry. Lower FOV or increase altitude.",
                "sides": {"a": base, "b": b, "c": c}}

    triangle_area, s = get_triangle_area(base, b, c)
    medians = get_triangle_medians(base, b, c)
    heights = get_triangle_heights(base, b, c, triangle_area)
    vertices = {"A": (0, 0), "B": (base / 2.0, a), "C": (-base / 2.0, a)}
    inradius = div(triangle_area, s)
    circumradius = 0.5 * a  # right-ish simplification for this layout

    return {
        "sides": {"a": base, "b": b, "c": c},
        "area": triangle_area,
        "perimeter": base + 2.0 * a,
        "semiperimeter": s,
        "heights": heights,
        "medians": medians,
        "vertices": vertices,
        "inradius": inradius,
        "circumradius": circumradius
    }


