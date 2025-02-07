""" Garage UI module for the web UI"""
from __future__ import annotations
from typing import TYPE_CHECKING

import flask
from flask_login import login_required

if TYPE_CHECKING:
    from carconnectivity.carconnectivity import CarConnectivity

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
    del vin
    if 'car_connectivity' not in flask.current_app.extensions or flask.current_app.extensions['car_connectivity'] is None:
        flask.abort(500, "car_connectivity instance not connected")
    car_connectivity: CarConnectivity = flask.current_app.extensions['car_connectivity']
    return flask.render_template('garage/garage.html', current_app=flask.current_app, garage=car_connectivity.garage)
