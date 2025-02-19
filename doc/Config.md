

# CarConnectivity Plugin for Web UI Config Options
The configuration for CarConnectivity is a .json file.
## General format
The general format is a `carConnectivity` section, followed by a list of connectors and plugins.
In the `carConnectivity` section you can set the global `log_level`.
Each connector or plugin needs a `type` attribute and a `config` section.
The `type` and config options specific to your connector or plugin can be found on their respective project page.
```json
{
    "carConnectivity": {
        "log_level": "error", // set the global log level, you can set individual log levels in the connectors and plugins
        "connectors": [
            {
                "type": "skoda", // Definition for a MySkoda account
                "config": {
                    "interval": 600, // Interval in which the server is checked in seconds
                    "username": "test@test.de", // Username of your MySkoda Account
                    "password": "testpassword123" // Password of your MySkoda Account
                }
            },
            {
                "type": "volkswagen", // Definition for a Volkswagen account
                "config": {
                    "interval": 300, // Interval in which the server is checked in seconds
                    "username": "test@test.de", // Username of your Volkswagen Account
                    "password": "testpassword123" // Username of your Volkswagen Account
                }
            }
        ],
        "plugins": [
            {
                "type": "webui", // Minimal definition for the MQTT Connection
                "config": {
                }
            }
        ]
    }
}
```
### Web UI Plugin Options
These are the valid options for the Web UI plugin
```json
{
    "carConnectivity": {
        "connectors": [],
        "plugins": [
            {
                "type": "webui", // Definition for the MQTT plugin
                "disabled": false, // You can disable plugins without removing them from the config completely
                "config": {
                    "log_level": "error", // The log level for the plugin. Otherwise uses the global log level
                    "host": "localhost", // The host to listen on, default is 0.0.0.0 meaning all interfaces
                    "port": 4000, // Port to listen on, default is 4000, to run on port 80 CarConnectivity must run with priviliges
                    "username": "admin", // Admin username for login
                    "password": "secret", // Admin password for login
                    "users": [{ // Additional users
                        "username": "testuser",
                        "password": "testpassword"
                    }],
                    "app_config": { // Special configuration parameters
                        "SECRET_KEY": "3edf9a3f2131232e55be5b07269061f848", // SECRET_KEY can be set fixed (otherwise session cookies will invalidate more often)
                        "LOGIN_DISABLED": true, // If you prefere to not use password security at all (use this with caution and only if the webinterface is not reachable from the internet)
                    }
                }
            }
        ]
    }
}
```

### Connector Options
Valid Options for connectors can be found here:
* [CarConnectivity-connector-skoda Config Options](https://github.com/tillsteinbach/CarConnectivity-connector-skoda/tree/main/doc/Config.md)
* [CarConnectivity-connector-volkswagen Config Options](https://github.com/tillsteinbach/CarConnectivity-connector-volkswagen/tree/main/doc/Config.md)
* [CarConnectivity-connector-tronity Config Options](https://github.com/tillsteinbach/CarConnectivity-connector-tronity/tree/main/doc/Config.md)