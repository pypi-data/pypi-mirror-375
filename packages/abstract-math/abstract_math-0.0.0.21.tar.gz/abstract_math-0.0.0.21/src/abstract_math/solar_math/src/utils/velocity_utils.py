#src/utils/velocity_utils.py
from ..imports import *
from ..constants import *

def distance_per_time_to_mps(v: float, dist_units: str, time_units: str) -> float:
    """
    Convert <v> in (<dist_units>/<time_units>) to m/s.
    """
    # distance: unit -> meters
    norm_dist_unit = normalize_distance_unit(dist_units)   # <-- was normalize_time_unit
    meters_per_unit = get_distance_unit_conversions(norm_dist_unit)["conv"]["meters"]
    v_meters_per_timeunit = mul(v, meters_per_unit)

    # time: timeunit -> seconds
    sec_per_time = seconds_per(time_units)                 # from time_constants.py
    return div(v_meters_per_timeunit, sec_per_time)

def mps_to_distance_per_time(v_mps: float, dist_units: str, time_units: str) -> float:
    """
    Convert m/s to <dist_units>/<time_units>.
    """
    norm_dist_unit = normalize_distance_unit(dist_units)
    meters_per_unit = get_distance_unit_conversions(norm_dist_unit)["conv"]["meters"]
    v_units_per_sec = div(v_mps, meters_per_unit)          # [dist_units / s]
    sec_per_time = seconds_per(time_units)
    return mul(v_units_per_sec, sec_per_time)              # [dist_units / time_units]
