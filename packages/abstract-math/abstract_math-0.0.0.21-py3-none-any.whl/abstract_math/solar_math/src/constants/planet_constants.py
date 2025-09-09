# src/constants/planet_constants.py
from ..imports import *               # <-- add this line
from .distance_constants import *
from .time_constants import *
# -------------------------
# Physical constants (SI)
# -------------------------
G = 6.67430e-11  # m^3 kg^-1 s^-2
g0 = 9.80665     # m/s^2

try:
    MU_MOON
except NameError:
    MU_MOON = 4.9048695e12  # m^3/s^2

# -------------------------
# Bodies (your data)
# -------------------------
PLANETS = [
    { "name":'Sun',"m0_deg":0,"mu":1.32712440018e20,"a":0,"e":0,"radiusPx":20,"color":'yellow',"radius":696000000,"escapeVel":61770,"n":0,"peri_lon_deg":0 },
    { "name":'Mercury',"m0_deg":252.25032350,"mu":2.20320e13,"a":5.7909927e10,"e":0.20563593,"radiusPx":4,"color":'#a6a6a6',"radius":2440000,"escapeVel":4300,"n":1,"peri_lon_deg":77.45779628 },
    { "name":'Venus',"m0_deg":181.97909950,"mu":3.24859e14,"a":1.0820948e11,"e":0.00677672,"radiusPx":7,"color":'#e0c16b',"radius":6052000,"escapeVel":10400,"n":2,"peri_lon_deg":131.60246718 },
    { "name":'Earth',"m0_deg":100.46457166,"mu":3.98600e14,"a":1.49598261e11,"e":0.01671123,"radiusPx":8,"color":'#4e6ef2',"radius":6371000,"escapeVel":11200,"n":3,"peri_lon_deg":102.93768193 },
    { "name":'Mars',"m0_deg":-4.55343205,"mu":4.28284e13,"a":2.2793664e11,"e":0.09339410,"radiusPx":6,"color":'#c1440e',"radius":3390000,"escapeVel":5030,"n":4,"peri_lon_deg":-23.94362959 },
    { "name":'Jupiter',"m0_deg":34.39644051,"mu":1.26687e17,"a":7.7841200e11,"e":0.04838624,"radiusPx":14,"color":'#d2a679',"radius":71492000,"escapeVel":59500,"n":5,"peri_lon_deg":14.72847983 },
    { "name":'Saturn',"m0_deg":49.95424423,"mu":3.79312e16,"a":1.4267254e12,"e":0.05386179,"radiusPx":12,"color":'#e3c168',"radius":60268000,"escapeVel":35500,"n":6,"peri_lon_deg":92.59887831 },
    { "name":'Uranus',"m0_deg":313.23810451,"mu":5.79394e15,"a":2.8706582e12,"e":0.04725744,"radiusPx":10,"color":'#7fbde8',"radius":25559000,"escapeVel":21300,"n":7,"peri_lon_deg":170.95427630 },
    { "name":'Neptune',"m0_deg":-55.12002969,"mu":6.83653e15,"a":4.4983964e12,"e":0.00859048,"radiusPx":10,"color":'#4363d8',"radius":24764000,"escapeVel":23500,"n":8,"peri_lon_deg":44.96476227 },
    { "name":'Moon',"m0_deg":0,"mu":MU_MOON,"a":3.844e8,"e":0.0549,"radiusPx":5,"color":'lightgray',"radius":1.737e6,"escapeVel":2380,"n":9}
]

# -------------------------
# Body enrichment + lookup
# -------------------------
def _enrich_body(b: Dict[str, Any]) -> Dict[str, Any]:
    """Add derived diameter, mass, surface g."""
    mu = b["mu"]
    r  = b["radius"]
    if "diameter" not in b or not b["diameter"]:
        b["diameter"] = mul(2.0, r)
    b["mass"] = div(mu, G)
    surf_g = div(mu, mul(r, r))
    b["surface_g"] = surf_g
    b["surface_g_g0"] = div(surf_g, g0)
    return b

_NAME_ALIASES = {"sol": "sun", "terra": "earth", "luna": "moon"}
def _normalize_name(name: str) -> str:
    n = name.strip().lower()
    return _NAME_ALIASES.get(n, n)

_BODY_BY_NAME: Dict[str, Dict[str, Any]] = {}
for entry in PLANETS:
    _BODY_BY_NAME[entry["name"].lower()] = _enrich_body(dict(entry))

# -------------------------
# Public API
# -------------------------
def get_planet_vars(name: str, units: str = "meters") -> Dict[str, Any]:
    """
    Return body properties with radius/diameter in `units`.
    Mass in kg; mu in m^3/s^2; surface_g in m/s^2.
    """
    key = _normalize_name(name)
    body = _BODY_BY_NAME.get(key)
    if body is None:
        raise KeyError(f"Unknown body '{name}'. Available: {sorted(_BODY_BY_NAME.keys())}")

    units_norm = normalize_distance_unit(units)
    r_m = body["radius"]
    d_m = body["diameter"]
    
    out = dict(body)
    out["radius"] = convert(r_m, "meters", units_norm)
    out["diameter"] = convert(d_m, "meters", units_norm)
    out["radius_units"] = units_norm
    out["diameter_units"] = units_norm
    return out

def planet_radius(name: str = "earth", units: str = "meters") -> float:
    return get_planet_vars(name, units)["radius"]

def planet_diameter(name: str = "earth", units: str = "meters") -> float:
    return get_planet_vars(name, units)["diameter"]

def full_planet_surface_area(name: str = "earth", units: str = 'meters') -> float:
    r = planet_radius(name,units)
    return mul(4 * pi(), exp(r, 2))

def planet_volume(name: str = "earth", units: str = 'meters') -> float:
    r = planet_radius(name,units)
    return mul((4.0/3.0) * pi(), exp(r, 3))

def planet_circumference(name: str = "earth", units: str = 'meters') -> float:
    r = planet_radius(name,units)
    return mul(2 * pi(), r)

def planet_mass(name: str = "earth") -> float:
    return get_planet_vars(name)["mass"]

def planet_surface_g(name: str = "earth", as_g0: bool = False) -> float:
    v = get_planet_vars(name)["surface_g"]
    return div(v, g0) if as_g0 else v

def escape_velocity(name: str = "earth", altitude: float = 0.0, units: str = "meters") -> float:
    """
    Escape velocity (m/s) from altitude above surface.
    """
    mu = _BODY_BY_NAME[_normalize_name(name)]["mu"]
    r  = _BODY_BY_NAME[_normalize_name(name)]["radius"]  # meters
    h_m = convert(altitude, units, "meters")
    R = add(r, h_m)
    return math.sqrt(mul(2.0, div(mu, R)))

# -------------------------
# Earth-centric geometry utils (unit-consistent)
# -------------------------
def pi() -> float:
    return math.pi

def earth_radius(units: str = 'meters') -> float:
    return planet_radius('earth', units)

def earth_diameter(units: str = 'meters') -> float:
    return planet_diameter('earth', units)

def full_earth_surface_area(units: str = 'meters') -> float:
    r = earth_radius(units)
    return mul(4 * pi(), exp(r, 2))

def earth_volume(units: str = 'meters') -> float:
    r = earth_radius(units)
    return mul((4.0/3.0) * pi(), exp(r, 3))

def earth_circumference(units: str = 'meters') -> float:
    r = earth_radius(units)
    return mul(2 * pi(), r)

# =========================
# Radial toy + single-call wrapper
# =========================
def distance_per_sec_to_mps(v_per_sec: float, units: str) -> float:
    """Convert a speed given in `units`/s into m/s using your convert()."""
    # v [units/s] * (meters per 1 units) => [m/s]
    return mul(v_per_sec, get_distance_unit_conversions(_normalize_unit(units))["conv"]["meters"])


def get_body(planet: str) -> Dict[str, Any]:
    key = _normalize_name(planet)
    body = _BODY_BY_NAME.get(key)
    if not body:
        raise KeyError(f"Unknown body '{planet}'. Available: {sorted(_BODY_BY_NAME.keys())}")
    return body

def g_at_radius(mu: float, r_m: float) -> float:
    return div(mu, mul(r_m, r_m))
