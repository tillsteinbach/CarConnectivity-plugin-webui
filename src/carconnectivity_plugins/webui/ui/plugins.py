""" Plugins status UI module for the web UI"""
from __future__ import annotations
from typing import TYPE_CHECKING

import flask
from flask_login import login_required

if TYPE_CHECKING:
    from carconnectivity.carconnectivity import CarConnectivity

bp_plugins = flask.Blueprint('plugins', __name__, url_prefix='/plugins')


@bp_plugins.route('/', methods=['GET'])
def root():
    """
    Redirects to the 'plugins.status' URL.

    This function uses Flask's redirect and url_for functions to redirect
    the user to the 'plugins.status' endpoint.

    Returns:
        A Flask redirect response to the 'plugins.status' URL.
    """
    return flask.redirect(flask.url_for('plugins.status'))


@bp_plugins.route('/status', methods=['GET'])
@login_required
def status() -> str:
    """
    Render the status page for car connectivity plugins.

    This function checks if the 'car_connectivity' extension is present and connected in the current Flask application.
    If not, it aborts with a 500 status code and an error message. If the extension is connected, it retrieves the
    car connectivity instance and renders the 'plugins/status.html' template with the current application context
    and the list of plugins.

    Returns:
        Response: The rendered template for the status page.

    Raises:
        HTTPException: If the 'car_connectivity' extension is not connected.
    """
    if 'car_connectivity' not in flask.current_app.extensions or flask.current_app.extensions['car_connectivity'] is None:
        flask.abort(500, "car_connectivity instance not connected")
    car_connectivity: CarConnectivity = flask.current_app.extensions['car_connectivity']
    return flask.render_template('plugins/status.html', current_app=flask.current_app, plugins=car_connectivity.plugins.plugins.values())
