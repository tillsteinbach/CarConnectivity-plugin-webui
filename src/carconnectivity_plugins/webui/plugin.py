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
        BasePlugin.__init__(self, plugin_id=plugin_id, car_connectivity=car_connectivity, config=config)

        self.webthread: Optional[threading.Thread] = None

        # Configure logging
        if 'log_level' in config and config['log_level'] is not None:
            config['log_level'] = config['log_level'].upper()
            if config['log_level'] in logging._nameToLevel:
                LOG.setLevel(config['log_level'])
                self.log_level._set_value(config['log_level'])  # pylint: disable=protected-access
            else:
                raise ConfigurationError(f'Invalid log level: "{config["log_level"]}" not in {list(logging._nameToLevel.keys())}')

        if 'host' not in self.config or not self.config['host']:
            host: str = '0.0.0.0'
        else:
            host: str = self.config['host']

        if 'port' in self.config and self.config['port'] is not None:
            port: int = self.config['port']
            if not port or port < 1 or port > 65535:
                raise ConfigurationError('Invalid port specified in config ("port" out of range, must be 1-65535)')
        else:
            port: int = 4000

        users: Dict[str, str] = {}
        if 'username' in self.config and self.config['username'] is not None \
                and 'password' in self.config and self.config['password'] is not None:
            users[self.config['username']] = self.config['password']

        if 'users' in self.config and self.config['users'] is not None:
            for user in self.config['users']:
                if 'username' in user and 'password' in user:
                    users[user['username']] = user['password']

        if 'app_config' in self.config:
            app_config: Dict[str, str] = self.config['app_config']
        else:
            app_config = {}

        self.webui = WebUI(car_connectivity=car_connectivity, host=host, port=port, app_config=app_config, users=users)

        LOG.info("Loading webui plugin with config %s", config_remove_credentials(self.config))

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
