"""Module implements the web ui"""
from __future__ import annotations
from typing import TYPE_CHECKING

import importlib

from datetime import timedelta
import base64
import threading
import time
import os
import sys
import uuid
import logging
from flask_bootstrap import Bootstrap5
import flask
import flask_login
import markupsafe

from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Length

from werkzeug.serving import make_server

from carconnectivity.attributes import GenericAttribute
from carconnectivity_connectors.base.ui.connector_ui import BaseConnectorUI

from carconnectivity_plugins.base.ui.plugin_ui import BasePluginUI
from carconnectivity_plugins.webui.ui.cache import cache
from carconnectivity_plugins.webui.ui.plugins import bp_plugins
from carconnectivity_plugins.webui.ui.connectors import bp_connectors
from carconnectivity_plugins.webui.ui.garage import blueprint as bp_garage

if TYPE_CHECKING:
    from typing import Dict, Optional, Literal
    from types import ModuleType

    from carconnectivity.carconnectivity import CarConnectivity
    from werkzeug.serving import BaseWSGIServer

LOG: logging.Logger = logging.getLogger("carconnectivity.plugins.webui")

csrf = CSRFProtect()


class LoginForm(FlaskForm):
    """
    LoginForm class represents a form for user login.

    Attributes:
        username (StringField): Field for entering the username with a length validator.
        password (PasswordField): Field for entering the password.
        remember_me (BooleanField): Checkbox to remember the user's login session.
        submit (SubmitField): Button to submit the login form.
    """
    username = StringField('User', validators=[Length(min=1, max=255)])
    password = PasswordField('Password')
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')


class WebUI:  # pylint: disable=too-few-public-methods
    """
    WebUI class for the Car Connectivity application.
    """
    # pylint: disable-next=too-many-arguments, too-many-positional-arguments, too-many-locals, too-many-statements
    def __init__(self, car_connectivity: CarConnectivity, host: str, port: int, app_config: Optional[Dict[str, str]] = None,
                 users: Optional[Dict[str, str]] = None) -> None:
        if app_config is None:
            app_config = {}
        self.users: Dict[str, Dict[str, str]] = {}
        if users is not None:
            for user, password in users.items():
                self.users[user] = {'password': password}

        self.car_connectivity: CarConnectivity = car_connectivity
        self.app = flask.Flask('CarConnectivity', template_folder=os.path.dirname(__file__) + '/templates', static_folder=os.path.dirname(__file__) + '/static')

        for app_config_key, app_config_value in app_config.items():
            self.app.config[app_config_key] = app_config_value
        if 'SECRET_KEY' not in self.app.config or self.app.config['SECRET_KEY'] is None:
            self.app.config['SECRET_KEY'] = uuid.uuid4().hex
        csrf.init_app(self.app)

        cache.init_app(self.app)

        bootstrap = Bootstrap5(self.app)  # pylint: disable=unused-variable # noqa

        login_manager: flask_login.LoginManager = flask_login.LoginManager()
        login_manager.login_view = "login"  # pyright: ignore[reportAttributeAccessIssue]
        login_manager.login_message = "You have to login to see this page"
        login_manager.login_message_category = "info"
        login_manager.init_app(self.app)

        class NoHealth(logging.Filter):  # pylint: disable=too-few-public-methods
            """
            A logging filter that excludes health check requests from the logs.

            This filter checks if the log record message contains the string 'GET /healthcheck'.
            If the string is found, the log record is excluded from the logs.

            Methods:
                filter(record): Determines if the log record should be logged.
            """
            def filter(self, record):
                return 'GET /healthcheck' not in record.getMessage()

        #  Disable logging for healthcheck
        logging.getLogger("werkzeug").addFilter(NoHealth())

        with self.app.app_context():
            if 'carconnectivity' not in flask.current_app.extensions:
                flask.current_app.extensions['car_connectivity'] = car_connectivity

        self.server: BaseWSGIServer = make_server(host, port, self.app, threaded=True)

        self.plugin_uis: Dict[str, BasePluginUI] = {}
        self.connector_uis: Dict[str, BaseConnectorUI] = {}

        @self.app.context_processor
        def utility_processor() -> Dict:
            def format_cc_element(element, alt_title: Optional[str] = None, with_tooltip: bool = True, linebreak: bool = False) -> str:
                if isinstance(element, GenericAttribute):
                    if not element.enabled:
                        return ''
                    return_str: markupsafe.Markup = markupsafe.Markup()
                    if alt_title is not None:
                        return_str += alt_title
                    else:
                        return_str += markupsafe.escape(element.name)
                    if len(return_str) > 0:
                        return_str += ': '
                    if with_tooltip:
                        return_str += markupsafe.Markup(f'<a href="#" data-toggle="tooltip" title="Last updated $$${element.last_updated}$$$ &#10;'  # nosec
                                                        f'Last changed $$${element.last_changed}$$$" class="js-convert-time-title text-decoration-none '
                                                        'text-reset">')
                    return_str += markupsafe.escape(str(element.value))
                    if element.unit is not None:
                        return_str += markupsafe.escape(str(element.unit))
                    if with_tooltip:
                        return_str += markupsafe.Markup('</a>')
                    if linebreak:
                        return_str += markupsafe.Markup('<br>')
                    return return_str
                return str(element)

            def ansi2html(ansi_str: str) -> str:
                ansi_str = markupsafe.escape(ansi_str)
                ansi_str = ansi_str.replace('\033[30m', markupsafe.Markup('<span style="color:black;">'))
                ansi_str = ansi_str.replace('\033[31m', markupsafe.Markup('<span style="color:red;">'))
                ansi_str = ansi_str.replace('\033[32m', markupsafe.Markup('<span style="color:green;">'))
                ansi_str = ansi_str.replace('\033[33m', markupsafe.Markup('<span style="color:yellow;">'))
                ansi_str = ansi_str.replace('\033[34m', markupsafe.Markup('<span style="color:blue;">'))
                ansi_str = ansi_str.replace('\033[35m', markupsafe.Markup('<span style="color:magenta;">'))
                ansi_str = ansi_str.replace('\033[36m', markupsafe.Markup('<span style="color:cyan;">'))
                ansi_str = ansi_str.replace('\033[37m', markupsafe.Markup('<span style="color:white;">'))
                ansi_str = ansi_str.replace('\033[90m', markupsafe.Markup('<span style="color:black;">'))
                ansi_str = ansi_str.replace('\033[91m', markupsafe.Markup('<span style="color:red;">'))
                ansi_str = ansi_str.replace('\033[92m', markupsafe.Markup('<span style="color:green;">'))
                ansi_str = ansi_str.replace('\033[93m', markupsafe.Markup('<span style="color:yellow;">'))
                ansi_str = ansi_str.replace('\033[94m', markupsafe.Markup('<span style="color:blue;">'))
                ansi_str = ansi_str.replace('\033[95m', markupsafe.Markup('<span style="color:magenta;">'))
                ansi_str = ansi_str.replace('\033[96m', markupsafe.Markup('<span style="color:cyan;">'))
                ansi_str = ansi_str.replace('\033[97m', markupsafe.Markup('<span style="color:white;">'))
                ansi_str = ansi_str.replace('\033[0m', markupsafe.Markup('</span>'))
                return ansi_str

            return {'format_cc_element': format_cc_element, 'ansi2html': ansi2html, 'timedelta': timedelta, 'hasattr': hasattr}

        @self.app.context_processor
        def inject_dict_for_all_templates() -> Dict:
            """ Build the navbar and pass this to Jinja for every route
            """
            plugins_sublinks = []
            connectors_sublinks = []
            # Build the Navigation Bar
            nav = [
                {"text": "Garage", "url": flask.url_for('garage.garage')},
                {
                    "text": "Connectors",
                    "sublinks": connectors_sublinks,
                    "url": flask.url_for('connectors.status')
                },
                {
                    "text": "Plugins",
                    "sublinks": plugins_sublinks,
                    "url": flask.url_for('plugins.status')
                },
                {"text": "Log", "url": flask.url_for('log')},
            ]
            if 'carconnectivity_connector_uis' in flask.current_app.extensions and flask.current_app.extensions['carconnectivity_connector_uis'] is not None:
                connector_uis: Dict = flask.current_app.extensions['carconnectivity_connector_uis']
                connectors_sublinks.append({"text": "Status", "url": flask.url_for('connectors.status')})
                connectors_sublinks.append({"divider": True})
                for connector_ui in connector_uis.values():
                    connector_nav = [
                        {
                            "text": connector_ui.get_title(),
                            "sublinks": connector_ui.get_nav_items(),
                            "url": flask.url_for('connectors.status')
                        }
                    ]
                    connectors_sublinks.extend(connector_nav)
            if 'carconnectivity_plugin_uis' in flask.current_app.extensions and flask.current_app.extensions['carconnectivity_plugin_uis'] is not None:
                plugin_uis: Dict = flask.current_app.extensions['carconnectivity_plugin_uis']
                plugins_sublinks.append({"text": "Status", "url": flask.url_for('plugins.status')})
                plugins_sublinks.append({"divider": True})
                for plugin_ui in plugin_uis.values():
                    plugin_nav = [
                        {
                            "text": plugin_ui.get_title(),
                            "sublinks": plugin_ui.get_nav_items(),
                            "url": flask.url_for('plugins.status')
                        }
                    ]
                    plugins_sublinks.extend(plugin_nav)
            return {'navbar': nav}

        @self.app.before_request
        def before_request_callback():
            pass
            # flask.g.versions = dict()
            # flask.g.versions['VWsFriend'] = __vwsfriend_version__
            # flask.g.versions['WeConnect Python Library'] = __weconnect_version__

        @self.app.route('/', methods=['GET'])
        def root():
            return flask.redirect(flask.url_for('garage.garage'))

        @self.app.route('/healthcheck', methods=['GET'])
        def healthcheck() -> Literal['ok', 'unhealthy']:
            if 'car_connectivity' not in flask.current_app.extensions:
                flask.abort(500, "car_connectivity instance not connected")
            car_connectivity: Optional[CarConnectivity] = flask.current_app.extensions['car_connectivity']
            if car_connectivity is not None:
                if car_connectivity.is_healthy():
                    return 'ok'
            return 'unhealthy'

        @self.app.route('/restart', methods=['GET'])
        @flask_login.login_required
        def restart():
            def delayed_restart():
                time.sleep(10)
                python = sys.executable
                os.execl(python, python, * sys.argv)  # nosec

            t = threading.Thread(target=delayed_restart)
            t.start()
            return flask.redirect(flask.url_for('restartrefresh'))

        @self.app.route('/restartrefresh', methods=['GET'])
        def restartrefresh():
            return flask.render_template('restart.html', current_app=flask.current_app)

        @login_manager.user_loader
        def user_loader(username) -> None | flask_login.UserMixin:
            if username not in self.users:
                return None

            user = flask_login.UserMixin()
            user.id = username  # pyright: ignore[reportAttributeAccessIssue]
            return user

        @login_manager.request_loader
        def load_user_from_request(request):
            auth = request.headers.get('Authorization')
            if auth and 'Basic ' in auth:
                auth = auth.replace('Basic ', '', 1)
                try:
                    auth = base64.b64decode(auth).decode("utf-8")
                except TypeError:
                    return None
                if ':' in auth:
                    user_pass = auth.split(":", 1)
                    if user_pass[0] in self.users and 'password' in self.users[user_pass[0]] and user_pass[1] == self.users[user_pass[0]]['password']:
                        user = flask_login.UserMixin()
                        user.id = user_pass[0]  # pyright: ignore[reportAttributeAccessIssue]
                        return user
            # finally, return None if both methods did not login the user
            return None

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            form = LoginForm()

            if form.validate_on_submit():
                username = form.username.data
                if username in self.users and 'password' in self.users[username] and form.password.data == self.users[username]['password']:
                    user = flask_login.UserMixin()
                    user.id = username  # pyright: ignore[reportAttributeAccessIssue]
                    remember = form.remember_me.data
                    flask_login.login_user(user, remember=remember)

                    next_page = flask.request.args.get('next', default='garage')
                    return flask.redirect(next_page)

                form.password.data = ''
                flask.flash('User unknown or password is wrong', 'danger')

            return flask.render_template('login/login.html', form=form, current_app=self.app)

        @self.app.route("/logout")
        @flask_login.login_required
        def logout():
            flask_login.logout_user()
            return flask.redirect('login')

        @self.app.route('/log', methods=['GET'])
        def log():
            if 'car_connectivity' not in flask.current_app.extensions:
                flask.abort(500, "car_connectivity instance not connected")
            car_connectivity: Optional[CarConnectivity] = flask.current_app.extensions['car_connectivity']
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            return flask.render_template('log.html', current_app=flask.current_app, car_connectivity=car_connectivity, formatter=formatter)

        @self.app.route('/about', methods=['GET'])
        def about():
            if 'car_connectivity' not in flask.current_app.extensions:
                flask.abort(500, "car_connectivity instance not connected")
            car_connectivity: Optional[CarConnectivity] = flask.current_app.extensions['car_connectivity']
            versions: Dict[str, str] = {}
            if car_connectivity is not None:
                if car_connectivity.version is not None and car_connectivity.version.enabled \
                        and car_connectivity.version.value is not None:
                    versions['CarConnectivity'] = car_connectivity.version.value
                if car_connectivity.connectors is not None and car_connectivity.connectors.enabled:
                    for connector in car_connectivity.connectors.connectors.values():
                        versions[connector.get_type()] = connector.get_version()
                if car_connectivity.plugins is not None and car_connectivity.plugins.enabled:
                    for plugin in car_connectivity.plugins.plugins.values():
                        versions[plugin.get_type()] = plugin.get_version()
            return flask.render_template('about.html', current_app=flask.current_app, versions=versions)

    def load_blueprints(self) -> None:
        """
        Load and register blueprints for plugins and connectors.

        This method iterates over all plugins and connectors in the car connectivity system,
        attempts to import their respective UI modules, and registers their blueprints with
        the Flask application. If a UI module or class is not found, it continues to the next
        plugin or connector.

        Raises:
            ModuleNotFoundError: If the UI module for a plugin or connector is not found.
            AttributeError: If the UI class for a plugin or connector is not found.
        """
        for plugin in self.car_connectivity.plugins.plugins.values():
            parent_name = '.'.join(plugin.__module__.split('.')[:-1])
            try:
                plugin_ui_module: ModuleType = importlib.import_module('.ui.plugin_ui', parent_name)
                plugin_ui_class = getattr(plugin_ui_module, 'PluginUI')
                plugin_ui_instance: BasePluginUI = plugin_ui_class(plugin)
                self.plugin_uis[plugin.get_type()] = plugin_ui_instance
                if plugin_ui_instance.blueprint is not None:
                    bp_plugins.register_blueprint(plugin_ui_instance.blueprint)
            except ModuleNotFoundError:
                continue
            except AttributeError:
                continue
        for connector in self.car_connectivity.connectors.connectors.values():
            parent_name = '.'.join(connector.__module__.split('.')[:-1])
            try:
                conenctor_ui_module: ModuleType = importlib.import_module('.ui.connector_ui', parent_name)
                connector_ui_class = getattr(conenctor_ui_module, 'ConnectorUI')
                connector_ui_instance: BaseConnectorUI = connector_ui_class(connector)
                self.connector_uis[connector.get_type()] = connector_ui_instance
                if connector_ui_instance.blueprint is not None:
                    bp_connectors.register_blueprint(connector_ui_instance.blueprint)
            except ModuleNotFoundError:
                continue
            except AttributeError:
                continue
        with self.app.app_context():
            flask.current_app.register_blueprint(bp_plugins)
            flask.current_app.register_blueprint(bp_connectors)
            flask.current_app.register_blueprint(bp_garage)
            flask.current_app.extensions['carconnectivity_plugin_uis'] = self.plugin_uis
            flask.current_app.extensions['carconnectivity_connector_uis'] = self.connector_uis
