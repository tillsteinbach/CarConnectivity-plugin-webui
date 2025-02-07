""" Connectors UI module for the web UI"""
from __future__ import annotations
from typing import TYPE_CHECKING

import flask
from flask_login import login_required

if TYPE_CHECKING:
    from carconnectivity.carconnectivity import CarConnectivity

bp_connectors = flask.Blueprint('connectors', __name__, url_prefix='/connectors')


@bp_connectors.route('/status', methods=['GET'])
@login_required
def status():
    """
    Render the status page for car connectivity.

    This function checks if the 'car_connectivity' extension is available in the current Flask application.
    If the extension is not available or not connected, it aborts the request with a 500 status code.
    Otherwise, it retrieves the car connectivity instance and renders the 'connectors/status.html' template
    with the current application context and the list of connectors.

    Returns:
        A rendered HTML template for the status page.

    Raises:
        werkzeug.exceptions.HTTPException: If the 'car_connectivity' extension is not available or not connected.
    """
    if 'car_connectivity' not in flask.current_app.extensions or flask.current_app.extensions['car_connectivity'] is None:
        flask.abort(500, "car_connectivity instance not connected")
    car_connectivity: CarConnectivity = flask.current_app.extensions['car_connectivity']
    return flask.render_template('connectors/status.html', current_app=flask.current_app, connectors=car_connectivity.connectors.connectors.values())
