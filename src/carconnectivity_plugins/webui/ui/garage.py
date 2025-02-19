""" Garage UI module for the web UI"""
from __future__ import annotations
from typing import TYPE_CHECKING

import io
import json
from base64 import b64encode

import flask
from flask_login import login_required

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
