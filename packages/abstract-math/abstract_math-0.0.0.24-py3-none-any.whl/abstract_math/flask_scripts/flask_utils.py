from abstract_flask import *  # must provide Blueprint, request, jsonify, get_request_data, get_logFile, offer_help
from ..solar_math import *
# Auto-generated routes
math_data_bp = Blueprint('math_data_bp', __name__, url_prefix='/utils')
logger = get_logFile('math_data_bp')

@math_data_bp.route("/normalized_velocity_conversioin", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/normalized_velocity_conversioin/", methods=["GET", "POST"], strict_slashes=False)
def normalizedVelocityConversioin(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(normalized_velocity_conversioin, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = normalized_velocity_conversioin(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/analyze_visible_surface", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/analyze_visible_surface/", methods=["GET", "POST"], strict_slashes=False)
def analyzeVisibleSurface(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(analyze_visible_surface, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = analyze_visible_surface(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/simulate_radial_flight", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/simulate_radial_flight/", methods=["GET", "POST"], strict_slashes=False)
def simulateRadialFlight(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(simulate_radial_flight, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = simulate_radial_flight(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/radial_travel", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/radial_travel/", methods=["GET", "POST"], strict_slashes=False)
def radialTravel(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(radial_travel, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = radial_travel(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_central_angle", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_central_angle/", methods=["GET", "POST"], strict_slashes=False)
def getCentralAngle(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_central_angle, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_central_angle(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_h_cap", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_h_cap/", methods=["GET", "POST"], strict_slashes=False)
def getHCap(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_h_cap, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_h_cap(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/spherical_cap_area", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/spherical_cap_area/", methods=["GET", "POST"], strict_slashes=False)
def sphericalCapArea(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(spherical_cap_area, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = spherical_cap_area(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/percent_visible", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/percent_visible/", methods=["GET", "POST"], strict_slashes=False)
def percentVisible(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(percent_visible, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = percent_visible(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/visible_area_flat", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/visible_area_flat/", methods=["GET", "POST"], strict_slashes=False)
def visibleAreaFlat(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(visible_area_flat, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = visible_area_flat(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/visible_surface_angle", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/visible_surface_angle/", methods=["GET", "POST"], strict_slashes=False)
def visibleSurfaceAngle(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(visible_surface_angle, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = visible_surface_angle(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_triangle_area", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_triangle_area/", methods=["GET", "POST"], strict_slashes=False)
def getTriangleArea(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_triangle_area, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_triangle_area(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_medians", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_medians/", methods=["GET", "POST"], strict_slashes=False)
def getMedians(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_medians, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_medians(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_triangle_medians", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_triangle_medians/", methods=["GET", "POST"], strict_slashes=False)
def getTriangleMedians(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_triangle_medians, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_triangle_medians(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_triangle_heights", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_triangle_heights/", methods=["GET", "POST"], strict_slashes=False)
def getTriangleHeights(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_triangle_heights, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_triangle_heights(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/compute_fov_triangle", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/compute_fov_triangle/", methods=["GET", "POST"], strict_slashes=False)
def computeFovTriangle(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(compute_fov_triangle, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = compute_fov_triangle(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/distance_per_time_to_mps", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/distance_per_time_to_mps/", methods=["GET", "POST"], strict_slashes=False)
def distancePerTimeToMps(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(distance_per_time_to_mps, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = distance_per_time_to_mps(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/mps_to_distance_per_time", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/mps_to_distance_per_time/", methods=["GET", "POST"], strict_slashes=False)
def mpsToDistancePerTime(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(mps_to_distance_per_time, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = mps_to_distance_per_time(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/escape_velocity_at", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/escape_velocity_at/", methods=["GET", "POST"], strict_slashes=False)
def escapeVelocityAt(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(escape_velocity_at, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = escape_velocity_at(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/normalize_time_unit", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/normalize_time_unit/", methods=["GET", "POST"], strict_slashes=False)
def normalizeTimeUnit(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(normalize_time_unit, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = normalize_time_unit(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_time_unit_conversions", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_time_unit_conversions/", methods=["GET", "POST"], strict_slashes=False)
def getTimeUnitConversions(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_time_unit_conversions, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_time_unit_conversions(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/time_factor", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/time_factor/", methods=["GET", "POST"], strict_slashes=False)
def timeFactor(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(time_factor, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = time_factor(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/convert_time", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/convert_time/", methods=["GET", "POST"], strict_slashes=False)
def convertTime(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(convert_time, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = convert_time(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/seconds_per", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/seconds_per/", methods=["GET", "POST"], strict_slashes=False)
def secondsPer(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(seconds_per, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = seconds_per(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_planet_vars", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_planet_vars/", methods=["GET", "POST"], strict_slashes=False)
def getPlanetVars(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_planet_vars, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_planet_vars(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/planet_radius", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/planet_radius/", methods=["GET", "POST"], strict_slashes=False)
def planetRadius(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(planet_radius, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = planet_radius(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/planet_diameter", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/planet_diameter/", methods=["GET", "POST"], strict_slashes=False)
def planetDiameter(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(planet_diameter, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = planet_diameter(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/full_planet_surface_area", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/full_planet_surface_area/", methods=["GET", "POST"], strict_slashes=False)
def fullPlanetSurfaceArea(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(full_planet_surface_area, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = full_planet_surface_area(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/planet_volume", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/planet_volume/", methods=["GET", "POST"], strict_slashes=False)
def planetVolume(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(planet_volume, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = planet_volume(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/planet_circumference", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/planet_circumference/", methods=["GET", "POST"], strict_slashes=False)
def planetCircumference(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(planet_circumference, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = planet_circumference(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/planet_mass", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/planet_mass/", methods=["GET", "POST"], strict_slashes=False)
def planetMass(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(planet_mass, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = planet_mass(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/planet_surface_g", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/planet_surface_g/", methods=["GET", "POST"], strict_slashes=False)
def planetSurfaceG(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(planet_surface_g, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = planet_surface_g(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/escape_velocity", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/escape_velocity/", methods=["GET", "POST"], strict_slashes=False)
def escapeVelocity(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(escape_velocity, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = escape_velocity(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/pi", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/pi/", methods=["GET", "POST"], strict_slashes=False)
def pi(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(pi, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = pi(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/earth_radius", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/earth_radius/", methods=["GET", "POST"], strict_slashes=False)
def earthRadius(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(earth_radius, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = earth_radius(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/earth_diameter", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/earth_diameter/", methods=["GET", "POST"], strict_slashes=False)
def earthDiameter(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(earth_diameter, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = earth_diameter(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/full_earth_surface_area", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/full_earth_surface_area/", methods=["GET", "POST"], strict_slashes=False)
def fullEarthSurfaceArea(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(full_earth_surface_area, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = full_earth_surface_area(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/earth_volume", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/earth_volume/", methods=["GET", "POST"], strict_slashes=False)
def earthVolume(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(earth_volume, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = earth_volume(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/earth_circumference", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/earth_circumference/", methods=["GET", "POST"], strict_slashes=False)
def earthCircumference(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(earth_circumference, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = earth_circumference(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/distance_per_sec_to_mps", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/distance_per_sec_to_mps/", methods=["GET", "POST"], strict_slashes=False)
def distancePerSecToMps(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(distance_per_sec_to_mps, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = distance_per_sec_to_mps(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_body", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_body/", methods=["GET", "POST"], strict_slashes=False)
def getBody(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_body, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_body(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/g_at_radius", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/g_at_radius/", methods=["GET", "POST"], strict_slashes=False)
def gAtRadius(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(g_at_radius, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = g_at_radius(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/normalize_distance_unit", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/normalize_distance_unit/", methods=["GET", "POST"], strict_slashes=False)
def normalizeDistanceUnit(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(normalize_distance_unit, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = normalize_distance_unit(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/get_distance_unit_conversions", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/get_distance_unit_conversions/", methods=["GET", "POST"], strict_slashes=False)
def getDistanceUnitConversions(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(get_distance_unit_conversions, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = get_distance_unit_conversions(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@math_data_bp.route("/convert", methods=["GET", "POST"], strict_slashes=False)
@math_data_bp.route("/convert/", methods=["GET", "POST"], strict_slashes=False)
def convert(*args, **kwargs):
    data = get_request_data(request)
    help_offered = offer_help(convert, data=data, req=request)
    if help_offered:
        return help_offered
    try:
        response = convert(**data)
        if response is None:
            return jsonify({"error": "no response"}), 400
        return jsonify({"result": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
