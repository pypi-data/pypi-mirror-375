# src/utils/escape_velocity.py

from ..imports import math, mul, div, add
from ..constants.planet_constants import get_body
from ..constants.distance_constants import convert as dconvert
from ..constants.time_constants import get_time_unit_conversions, normalize_time_unit

def _seconds_per(unit: str) -> float:
    """
    Map a time unit (alias-friendly) to seconds per that unit, using your time schema.
    """
    return get_time_unit_conversions(normalize_time_unit(unit))["conv"]["seconds"]

def escape_velocity_at(
    planet: str = "earth",
    distance: float = 0.0,
    *,
    input_units: str = "meters",     # how to interpret `distance`
    output_units: str = "meters",    # distance unit for the *speed*
    output_time: str = "s",          # time unit for the *speed*
    as_radius: bool = False          # False => `distance` is altitude above surface; True => radius from center
) -> dict:
    """
    Compute v_escape at a given location around `planet`.

    Args:
        planet: body name (must exist in PLANETS)
        distance: if as_radius=False => altitude above surface; if as_radius=True => radius from center
        input_units: units of `distance`
        output_units: distance unit of the returned speed
        output_time: time unit of the returned speed ('s'|'min'|'h' etc.)
        as_radius: interpret `distance` as radius-from-center when True

    Returns:
        {
          "ok": True,
          "planet": str,
          "radius_from_center": <float in output_units>,
          "v_escape": <float in output_units/output_time>,
          "v_escape_mps": <float in m/s>,
          "units": {"distance": output_units, "time": output_time}
        }
    """
    if not (isinstance(distance, (int, float)) and math.isfinite(distance) and distance >= 0):
        return {"ok": False, "error": "distance must be a non-negative number"}

    body = get_body(planet)
    mu = body["mu"]          # m^3/s^2
    R  = body["radius"]      # m

    # Determine radius from center in meters
    if as_radius:
        r_m = dconvert(distance, input_units, "meters")
    else:
        alt_m = dconvert(distance, input_units, "meters")
        r_m = add(R, alt_m)

    if r_m <= 0:
        return {"ok": False, "error": "computed radius is non-positive"}

    # v_esc (m/s)
    vesc_mps = math.sqrt(mul(2.0, div(mu, r_m)))

    # Convert speed to <output_units>/<output_time>
    vesc_units_per_sec = dconvert(vesc_mps, "meters", output_units)
    sec_per = _seconds_per(output_time)          # seconds per 1 output_time
    vesc_out = mul(vesc_units_per_sec, sec_per)  # <output_units>/<output_time>

    # Also return the radius in output_units for convenience
    r_out = dconvert(r_m, "meters", output_units)

    return {
        "ok": True,
        "planet": planet,
        "radius_from_center": r_out,
        "v_escape": vesc_out,
        "v_escape_mps": vesc_mps,
        "units": {"distance": output_units, "time": output_time}
    }
