""" Garage UI module for the web UI"""
from __future__ import annotations
from typing import TYPE_CHECKING

import io
import json
from base64 import b64encode

import flask
from flask_login import login_required

from carconnectivity_plugins.webui.ui.cache import cache

# pylint: disable=duplicate-code
SUPPORT_IMAGES = False  # pylint: disable=invalid-name
try:
    from PIL import Image  # pylint: disable=unused-import # noqa: F401
    SUPPORT_IMAGES = True  # pylint: disable=invalid-name
except ImportError:
    pass
# pylint: enable=duplicate-code

if TYPE_CHECKING:
    from typing import Optional, Dict

    from werkzeug import Response

    from carconnectivity.carconnectivity import CarConnectivity
    from carconnectivity.vehicle import GenericVehicle

blueprint = flask.Blueprint(name='garage', import_name='garage', url_prefix='/garage')


@blueprint.route('/', methods=['GET'])
@login_required
def garage() -> str:
    """
    Renders the garage page if the car_connectivity instance is connected.

    This function checks if the 'car_connectivity' extension is present and connected
    in the current Flask application context. If not, it aborts with a 500 status code.
    If the extension is connected, it retrieves the CarConnectivity instance and renders
    the 'garage/garage.html' template with the current application context and the garage
    data from the CarConnectivity instance.

    Returns:
        Response: The rendered 'garage/garage.html' template.

    Raises:
        HTTPException: If the 'car_connectivity' extension is not present or not connected.
    """
    if 'car_connectivity' not in flask.current_app.extensions or flask.current_app.extensions['car_connectivity'] is None:
        flask.abort(500, "car_connectivity instance not connected")
    car_connectivity: CarConnectivity = flask.current_app.extensions['car_connectivity']
    return flask.render_template('garage/garage.html', current_app=flask.current_app, garage=car_connectivity.garage)


@blueprint.route('/json', methods=['GET'])
@cache.cached(timeout=5)
@login_required
def garage_json() -> flask.Response:
    """
    Retrieve the garage data as a JSON response.
    This endpoint returns the current state of all vehicles in the garage as JSON.
    The response includes cache control headers to allow private caching for 5 seconds.
    Returns:
        flask.Response: A Flask response object containing the garage data in JSON format
            with appropriate cache control headers (max-age=5, private).
    Raises:
        500: If the car_connectivity instance is not connected or available in the
            application extensions.
        404: If the garage is not found or is None in the car_connectivity instance.
    Note:
        The response is cached privately for 5 seconds to reduce server load while
        ensuring reasonably fresh data.
    """
    # pylint: disable=duplicate-code
    if 'car_connectivity' not in flask.current_app.extensions or flask.current_app.extensions['car_connectivity'] is None:
        flask.abort(500, "car_connectivity instance not connected")
    car_connectivity: CarConnectivity = flask.current_app.extensions['car_connectivity']
    if car_connectivity.garage is None:
        flask.abort(404, "Garage not found")
    pretty: bool = flask.request.args.get('pretty', default=False, type=bool)
    in_locale: bool = flask.request.args.get('in_locale', default=False, type=bool)
    with_locale: Optional[str] = flask.request.args.get('with_locale', default=None, type=str)

    if with_locale is not None:
        with_local_str: Optional[str] = with_locale
    elif in_locale:
        with_local_str = car_connectivity.connectors.connectors['webui'].active_config['locale']
    else:
        with_local_str = None
    vehicle_json_str: str = car_connectivity.garage.as_json(pretty=pretty, in_locale=with_local_str)
    response = flask.Response(vehicle_json_str, mimetype="text/json")
    response.cache_control.max_age = 5
    response.cache_control.private = True
    response.cache_control.public = False
    return response
    # pylint: enable=duplicate-code


@blueprint.route('/<string:vin>/', methods=['GET'])
@login_required
def vehicle(vin: str) -> str:
    """
    Render the garage template for a vehicle.

    This function checks if the 'car_connectivity' extension is available in the current Flask application context.
    If the extension is not available or not connected, it aborts the request with a 500 status code.
    Otherwise, it retrieves the CarConnectivity instance and renders the 'garage/garage.html' template.

    Args:
        vin (str): The Vehicle Identification Number of the vehicle.

    Returns:
        Response: The rendered 'garage/garage.html' template with the current application context and garage data.

    Raises:
        HTTPException: If the 'car_connectivity' extension is not available or not connected.
    """
    if 'car_connectivity' not in flask.current_app.extensions or flask.current_app.extensions['car_connectivity'] is None:
        flask.abort(500, "car_connectivity instance not connected")
    car_connectivity: CarConnectivity = flask.current_app.extensions['car_connectivity']
    vehicle_obj: Optional[GenericVehicle] = car_connectivity.garage.get_vehicle(vin)
    if vehicle_obj is None:
        flask.abort(404, f"Vehicle with VIN {vin} not found")
    return flask.render_template('garage/vehicle.html', current_app=flask.current_app, vehicle=vehicle_obj)


@blueprint.route('/<string:vin>-car.png', defaults={'conversion': None}, methods=['GET'])
@blueprint.route('/<string:vin>-car.png<string:conversion>', methods=['GET'])
@login_required
def vehicle_img(vin: str, conversion: Optional[str]) -> Response:
    """
    Retrieves the image of a vehicle based on its VIN (Vehicle Identification Number).

    Args:
        vin (str): The Vehicle Identification Number of the vehicle.
        conversion (Optional[str]): The desired format for the response. If '.json', the image will be returned as a base64-encoded JSON object.
        Otherwise, the image will be returned as a PNG file.

    Returns:
        Response: A Flask response object containing the vehicle image in the requested format.

    Raises:
        500: If the car_connectivity instance is not connected.
        404: If the vehicle with the given VIN is not found or has no car picture.
    """
    if 'car_connectivity' not in flask.current_app.extensions or flask.current_app.extensions['car_connectivity'] is None:
        flask.abort(500, "car_connectivity instance not connected")
    car_connectivity: CarConnectivity = flask.current_app.extensions['car_connectivity']
    vehicle_obj: Optional[GenericVehicle] = car_connectivity.garage.get_vehicle(vin)
    if vehicle_obj is None:
        if 'fallback' in flask.request.args:
            return flask.redirect(flask.url_for('static', filename=flask.request.args.get('fallback')))
        flask.abort(404, f"Vehicle with VIN {vin} not found")

    elif not SUPPORT_IMAGES:
        if 'fallback' in flask.request.args:
            return flask.redirect(flask.url_for('static', filename=flask.request.args.get('fallback')))
        flask.abort(500, "PIL module not available, cannot serve vehicle images")
    else:
        img_io = io.BytesIO()
        if 'car_picture' not in vehicle_obj.images.images or not vehicle_obj.images.images['car_picture'].enabled \
                or vehicle_obj.images.images['car_picture'].value is None:
            if 'fallback' in flask.request.args:
                return flask.redirect(flask.url_for('static', filename=flask.request.args.get('fallback')))
            flask.abort(404, f"Vehicle with VIN {vin} has no car picture")
        vehicle_obj.images.images['car_picture'].value.save(img_io, 'PNG')
        img_io.seek(0)
        if conversion == '.json':
            json_map: Dict[str, str] = {}
            json_map['type'] = 'image/png'
            json_map['encoding'] = 'base64'
            json_map['data'] = b64encode(img_io.read()).decode()
            return flask.Response(json.dumps(json_map), mimetype='application/json')
        return flask.send_file(img_io, mimetype='image/png')


@blueprint.route('/<string:vin>/json', methods=['GET'])
@cache.cached(timeout=5)
@login_required
def vehicle_json(vin: str) -> flask.Response:
    """
    Generate a JSON response containing the vehicle data for a given VIN.
    Args:
        vin (str): The Vehicle Identification Number of the vehicle to retrieve.
    Returns:
        flask.Response: A Flask response object containing the vehicle data as JSON
            with appropriate cache control headers (max_age=5, private, not public).
    Raises:
        500: If the car_connectivity instance is not connected or available.
        404: If no vehicle with the specified VIN is found in the garage.
    """

    if 'car_connectivity' not in flask.current_app.extensions or flask.current_app.extensions['car_connectivity'] is None:
        flask.abort(500, "car_connectivity instance not connected")
    car_connectivity: CarConnectivity = flask.current_app.extensions['car_connectivity']
    vehicle_obj: Optional[GenericVehicle] = car_connectivity.garage.get_vehicle(vin)
    if vehicle_obj is None:
        flask.abort(404, f"Vehicle with VIN {vin} not found")
    pretty: bool = flask.request.args.get('pretty', default=False, type=bool)
    in_locale: bool = flask.request.args.get('in_locale', default=False, type=bool)
    with_locale: Optional[str] = flask.request.args.get('with_locale', default=None, type=str)

    if with_locale is not None:
        with_local_str: Optional[str] = with_locale
    elif in_locale:
        with_local_str = car_connectivity.connectors.connectors['webui'].active_config['locale']
    else:
        with_local_str = None

    vehicle_json_str: str = vehicle_obj.as_json(pretty=pretty, in_locale=with_local_str)
    response = flask.Response(vehicle_json_str, mimetype="text/json")
    response.cache_control.max_age = 5
    response.cache_control.private = True
    response.cache_control.public = False
    return response
