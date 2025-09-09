#src/constants/time_constants.py
# --- Time unit schema (seconds-per-unit) ---
second = 1.0
minute = 60.0 * second
hour   = 60.0 * minute
day    = 24.0 * hour

SECONDS = {"strings": ['s', 'sec', 'secs', 'second', 'seconds'],
           "conv": {"seconds": 1.0}}
MINUTES = {"strings": ['min', 'mins', 'minute', 'minutes'],
           "conv": {"seconds": minute}}
HOURS   = {"strings": ['h', 'hr', 'hrs', 'hour', 'hours'],
           "conv": {"seconds": hour}}
DAYS    = {"strings": ['d', 'day', 'days'],
           "conv": {"seconds": day}}

TIME_CONVERSIONS = {
    "seconds": SECONDS,
    "minutes": MINUTES,
    "hours":   HOURS,
    "days":    DAYS,
}
ALL_TIME_UNITS = ("seconds", "minutes", "hours", "days")

def normalize_time_unit(unit: str) -> str:
    u = unit.strip().lower()
    if u in TIME_CONVERSIONS:
        return u
    for key, values in TIME_CONVERSIONS.items():
        if u in values.get("strings", []):
            return key
    raise ValueError(f"Unknown time unit '{unit}'. Supported: {list(TIME_CONVERSIONS.keys())}")

def get_time_unit_conversions(unit: str) -> dict:
    return TIME_CONVERSIONS[normalize_time_unit(unit)]

def time_factor(unit_from: str, unit_to: str) -> float:
    """
    multiplicative factor s.t.
      value_in_to = value_in_from * _time_factor(unit_from, unit_to)

    seconds per 1 unit_from  /  seconds per 1 unit_to
    """
    sf = get_time_unit_conversions(unit_from)["conv"]["seconds"]  # sec / unit_from
    st = get_time_unit_conversions(unit_to)["conv"]["seconds"]    # sec / unit_to
    return sf / st

def convert_time(value: float, unit_from: str, unit_to: str) -> float:
    return value * time_factor(unit_from, unit_to)

def seconds_per(unit: str) -> float:
    """Return seconds in one <unit> (unit aliases supported)."""
    return get_time_unit_conversions(normalize_time_unit(unit))["conv"]["seconds"]



