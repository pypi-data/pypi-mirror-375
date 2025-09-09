# adapt_units_api.py  (or wherever you glue this in)
from typing import *
from .src.constants.distance_constants import convert as dconvert, _factor as dfactor
from .src.constants.time_constants import seconds_per
from .src.constants.planet_constants import planet_radius, get_body, g_at_radius
from .src.utils.geometry_utils import visible_area_flat, visible_surface_angle
from .src.imports import math, mul, div, add  # your abstract_math ops
def normalized_velocity_conversioin(starting_velocity, input_time, input_units):
    sec_per_time = seconds_per(input_time)                             # sec / timeunit
    v_units_per_sec = div(starting_velocity, sec_per_time)             # <input_units> / s
    v0_mps = dconvert(v_units_per_sec, input_units, "meters")          # m / s
    return v0_mps

# --- Analyzer (prints a scan; no blocking input) ---
def analyze_visible_surface(
    altitude_step: float = 200.0,
    max_steps: int = 20,
    fov_range: tuple[int, int] = (20, 160),
    fov_interval: int = 10,
    input_units: str = 'meters',      # how to interpret altitude numbers
    display_units: str = 'meters',    # how to print areas/radii
    planet: str = 'earth',
    printit: bool = False
):
    """
    Scan altitudes/FOVs. Altitudes are interpreted in `input_units`.
    Results are printed in `display_units`.
    """
    # Planet radius and full area (compute in meters, convert for display)
    r_m = planet_radius(planet, 'meters')
    full_area_m2 = 4.0 * math.pi * (r_m ** 2)
    k_disp = dfactor('meters', display_units)      # linear meter->display factor
    full_area_disp = full_area_m2 * (k_disp ** 2)  # convert area to display units^2

    all_stats = {"output": "", "input_units": input_units,
                 "display_units": display_units, "vars": []}

    for i in range(1, max_steps + 1):
        all_stats["vars"].append({})
        altitude_in = altitude_step * i                       # input_units
        altitude_m  = dconvert(altitude_in, input_units, 'meters')

        all_stats["vars"][-1]['altitude_input'] = altitude_in
        all_stats["vars"][-1]['input_units']    = input_units
        all_stats["vars"][-1]['fov']            = []

        alt_pretty = dconvert(altitude_in, input_units, display_units)
        all_stats["output"] += (
            f"\n=== Altitude: {altitude_in} {input_units} (≈ {alt_pretty:.3f} {display_units}) ===\n"
        )

        for fov in range(fov_range[0], fov_range[1] + 1, fov_interval):
            # Compute visible area/radius in meters, convert to display units
            area_m2, vis_radius_m = visible_area_flat(fov, altitude_m, 'meters')
            area_disp = area_m2 * (k_disp ** 2)
            vis_radius_disp = dconvert(vis_radius_m, 'meters', display_units)

            # Span uses geometry only; r_m is in meters
            _, angle_deg = visible_surface_angle(vis_radius_m, r_m)

            coverage_pct = 100.0 * (area_disp / full_area_disp)

            fov_output = (
                f"FOV: {fov:>3}° | "
                f"Area: {area_disp:>12.2f} {display_units}² | "
                f"Span: {angle_deg:>7.2f}° | "
                f"Flat-visible: {coverage_pct:>6.3f}% | "
                f"visR≈{vis_radius_disp:.3f} {display_units}"
            )
            all_stats["output"] += fov_output + "\n"

            all_stats["vars"][-1]['fov'].append({
                "FOV": fov,
                "area": area_disp,
                "angle_deg": angle_deg,
                "coverage_pct": coverage_pct,
                "visible_radius": vis_radius_disp,
                "output": fov_output
            })

    if printit:
        print(all_stats.get('output'))
    return all_stats


def simulate_radial_flight(
    planet: str,
    start_altitude: float,
    start_units: str,
    v0_mps: float,
    dt_s: float = 1.0,
    max_steps: int = 5_000_000,
    target_altitude_m: Optional[float] = None
) -> dict:
    """
    Forward-Euler radial integrator (toy model).
    Returns a dict with SI (meters, seconds) internal results.
    """
    if not (isinstance(start_altitude, (int, float)) and start_altitude >= 0):
        return {"ok": False, "error": "Invalid start_altitude", "steps": 0}
    if not (isinstance(v0_mps, (int, float)) and math.isfinite(v0_mps)):
        return {"ok": False, "error": "Invalid starting_velocity (after unit conversion)", "steps": 0}
    if not (dt_s > 0):
        return {"ok": False, "error": "dt_s must be > 0", "steps": 0}

    body = get_body(planet)
    mu = body["mu"]
    R  = body["radius"]

    r0 = add(R, dconvert(start_altitude, start_units, "meters"))
    r  = r0
    v  = v0_mps   # outward positive, m/s
    t  = 0.0

    has_target = target_altitude_m is not None and target_altitude_m > 0
    r_target   = add(R, target_altitude_m if has_target else float("inf"))

    hit_surface = False
    hit_target  = False
    turned_back_below_start = False

    steps = 0
    for _ in range(max_steps):
        if r <= R:
            hit_surface = True
            break
        if has_target and r >= r_target:
            hit_target = True
            break

        a = - div(mu, mul(r, r))  # inward
        v = add(v, mul(a, dt_s))
        r = add(r, mul(v, dt_s))
        t = add(t, dt_s)
        steps += 1

        if (not has_target) and (v < 0) and (r < r0):
            turned_back_below_start = True
            break

    altitude_m = max(0.0, r - R)
    g_end      = g_at_radius(mu, r)
    g_surface  = g_at_radius(mu, R)
    traveled_m = max(0.0, altitude_m - (r0 - R))

    return {
        "ok": True,
        "planet": planet,
        "rFromCenter_m": r,
        "altitude_m": altitude_m,
        "vEnd_mps": v,
        "time_s": t,
        "gAtEnd_mps2": g_end,
        "gRatioSurface": div(g_end, g_surface),
        "steps": steps,
        "hitSurface": hit_surface,
        "hitTarget": hit_target,
        "turnedBackBelowStart": turned_back_below_start,
        "traveled_m": traveled_m,
        "vEsc_end_mps": math.sqrt(mul(2.0, div(mu, r))),
    }


def radial_travel(
    start_distance: float,
    starting_velocity: float,
    input_units: str = "meters",    # distance part of starting_velocity & start_distance
    input_time: str = "s",          # time part of starting_velocity
    output_units: str = "meters",
    output_time: str = "s",
    planet: str = "earth",
    *,
    dt_s: float = 1.0,
    max_steps: int = 5_000_000,
    target_distance: Optional[float] = None  # in input_units above surface
) -> dict:
    """
    Single-call wrapper:

    - start_distance: altitude above surface (input_units)
    - starting_velocity: <input_units>/<input_time>
    """

    v0_mps = normalized_velocity_conversioin(starting_velocity, input_time, input_units)

    # Optional target altitude (to meters)
    target_alt_m = None
    if target_distance is not None:
        target_alt_m = dconvert(target_distance, input_units, "meters")

    # Integrate in SI
    sim = simulate_radial_flight(
        planet=planet,
        start_altitude=start_distance,
        start_units=input_units,
        v0_mps=v0_mps,
        dt_s=dt_s,
        max_steps=max_steps,
        target_altitude_m=target_alt_m
    )

    if not sim.get("ok", False):
        return sim

    # Distances for output
    alt_out  = dconvert(sim["altitude_m"], "meters", output_units)
    r_out    = dconvert(sim["rFromCenter_m"], "meters", output_units)
    trav_out = dconvert(sim["traveled_m"], "meters", output_units)

    # Velocity output: (output_units)/(output_time)
    sec_per_out = seconds_per(output_time)                             # sec / out_timeunit
    v_units_per_sec_out = dconvert(sim["vEnd_mps"], "meters", output_units)
    v_out = mul(v_units_per_sec_out, sec_per_out)

    # Escape velocity at end
    vesc_units_per_sec_out = dconvert(sim["vEsc_end_mps"], "meters", output_units)
    vesc_end_out = mul(vesc_units_per_sec_out, sec_per_out)

    # Escape velocity at destination (if provided)
    body = get_body(planet)
    mu = body["mu"]; R = body["radius"]
    destination_radius_m = None
    vesc_dest_out = None
    if target_alt_m is not None:
        destination_radius_m = add(R, target_alt_m)
        vesc_dest_mps = math.sqrt(mul(2.0, div(mu, destination_radius_m)))
        vesc_dest_units_per_sec = dconvert(vesc_dest_mps, "meters", output_units)
        vesc_dest_out = mul(vesc_dest_units_per_sec, sec_per_out)

    # Time output in requested unit
    t_out = div(sim["time_s"], sec_per_out)
    t_label = output_time if output_time in ("s", "sec", "seconds", "m", "min", "minutes", "h", "hr", "hours") else "s"

    return {
        "ok": True,
        "planet": planet,
        "inputs": {
            "start_distance": start_distance,
            "starting_velocity": starting_velocity,
            "input_units": input_units,
            "input_time": input_time,
            "output_units": output_units,
            "output_time": output_time,
            "target_distance": target_distance,
        },
        "altitude": alt_out,                      # in output_units
        "radius_from_center": r_out,              # in output_units
        "distance_traveled": trav_out,            # in output_units
        "velocity": v_out,                        # in output_units / output_time
        "velocity_escape_end": vesc_end_out,      # same units/time as velocity
        "velocity_escape_destination": vesc_dest_out,
        "destination_radius": (
            dconvert(destination_radius_m, "meters", output_units) if destination_radius_m is not None else None
        ),
        "time": t_out,                            # in output_time units
        "time_unit": t_label,
        "g_end_mps2": sim["gAtEnd_mps2"],         # keep SI precise for g
        "g_ratio_surface": sim["gRatioSurface"],
        "steps": sim["steps"],
        "hit_surface": sim["hitSurface"],
        "hit_target": sim["hitTarget"],
        "turned_back_below_start": sim["turnedBackBelowStart"],
    }
