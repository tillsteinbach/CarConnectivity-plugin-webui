"""Module implements the plugin to provide a web based ui."""
from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import threading

from carconnectivity.errors import ConfigurationError
from carconnectivity.util import config_remove_credentials
from carconnectivity_plugins.base.plugin import BasePlugin
from carconnectivity_plugins.webui.ui.webui import WebUI
from carconnectivity_plugins.webui._version import __version__

if TYPE_CHECKING:
    from typing import Dict, Optional
    from carconnectivity.carconnectivity import CarConnectivity

LOG: logging.Logger = logging.getLogger("carconnectivity.plugins.webui")


class Plugin(BasePlugin):  # pylint: disable=too-many-instance-attributes
    """
    Plugin class for Web User Interface.
    Args:
        car_connectivity (CarConnectivity): An instance of CarConnectivity.
        config (Dict): Configuration dictionary containing connection details.
    """
    def __init__(self, plugin_id: str, car_connectivity: CarConnectivity, config: Dict) -> None:  # pylint: disable=too-many-branches, too-many-statements
        BasePlugin.__init__(self, plugin_id=plugin_id, car_connectivity=car_connectivity, config=config, log=LOG)

        self.webthread: Optional[threading.Thread] = None

        werkzeug_logger: logging.Logger = logging.getLogger('werkzeug')
        if 'log_level' in self.active_config and self.active_config['log_level'] is not None:
            werkzeug_logger.setLevel(self.active_config['log_level'])
        werkzeug_logger.addHandler(self.log_storage)

        if 'host' not in config or not config['host']:
            self.active_config['host'] = '0.0.0.0'  # nosec
        else:
            self.active_config['host'] = config['host']

        if 'port' in config and config['port'] is not None:
            self.active_config['port'] = config['port']
            if not self.active_config['port'] or self.active_config['port'] < 1 or self.active_config['port'] > 65535:
                raise ConfigurationError('Invalid port specified in config ("port" out of range, must be 1-65535)')
        else:
            self.active_config['port'] = 4000

        users: Dict[str, str] = {}
        if 'username' in config and config['username'] is not None \
                and 'password' in config and config['password'] is not None:
            users[config['username']] = config['password']

        if 'users' in config and config['users'] is not None:
            for user in config['users']:
                if 'username' in user and 'password' in user:
                    users[user['username']] = user['password']
        self.active_config['passwords'] = users

        if 'app_config' in config:
            self.active_config['app_config'] = config['app_config']
        else:
            self.active_config['app_config'] = {}

        self.webui = WebUI(car_connectivity=car_connectivity, host=self.active_config['host'], port=self.active_config['port'],
                           app_config=self.active_config['app_config'], users=users)

        LOG.info("Loading webui plugin with config %s", config_remove_credentials(config))

    def startup(self) -> None:
        LOG.info("Starting WebUI plugin")
        self.webui.load_blueprints()
        self.webthread = threading.Thread(target=self.webui.server.serve_forever)
        self.webthread.start()
        LOG.debug("Starting WebUI plugin done")

    def shutdown(self) -> None:
        """
        Shuts down the connector by persisting current state, closing the session,
        and cleaning up resources.
        """
        self.webui.server.shutdown()
        return super().shutdown()

    def get_version(self) -> str:
        return __version__

    def get_type(self) -> str:
        return "carconnectivity-plugin-webui"
