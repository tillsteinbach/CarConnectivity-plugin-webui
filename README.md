

# CarConnectivity Plugin for A Web based User Interface
[![GitHub sourcecode](https://img.shields.io/badge/Source-GitHub-green)](https://github.com/tillsteinbach/CarConnectivity-plugin-webui/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/tillsteinbach/CarConnectivity-plugin-webui)](https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/latest)
[![GitHub](https://img.shields.io/github/license/tillsteinbach/CarConnectivity-plugin-webui)](https://github.com/tillsteinbach/CarConnectivity-plugin-webui/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/tillsteinbach/CarConnectivity-plugin-webui)](https://github.com/tillsteinbach/CarConnectivity-plugin-webui/issues)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/carconnectivity-plugin-webui?label=PyPI%20Downloads)](https://pypi.org/project/carconnectivity-plugin-webui/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/carconnectivity-plugin-webui)](https://pypi.org/project/carconnectivity-plugin-webui/)
[![Donate at PayPal](https://img.shields.io/badge/Donate-PayPal-2997d8)](https://www.paypal.com/donate?hosted_button_id=2BVFF5GJ9SXAJ)
[![Sponsor at Github](https://img.shields.io/badge/Sponsor-GitHub-28a745)](https://github.com/sponsors/tillsteinbach)

## CarConnectivity will become the successor of [WeConnect-python](https://github.com/tillsteinbach/WeConnect-python) in 2025 with similar functionality but support for other brands beyond Volkswagen!

[CarConnectivity](https://github.com/tillsteinbach/CarConnectivity) is a python API to connect to various car services. This plugin allows you to use a browser to interact with CarConnectivity.

<img src="https://raw.githubusercontent.com/tillsteinbach/CarConnectivity-plugin-webui/main/screenshots/screenshot1.png" width="300">

## How to install

### Install using PIP
If you want to use CarConnectivity Web UI, the easiest way is to obtain it from [PyPI](https://pypi.org/project/carconnectivity-plugin-webui/). Just install instead using:
```bash
pip3 install carconnectivity-plugin-webui
```
after you installed CarConnectivity

## Configuration
In your carconnectivity.json configuration add a section for the webui plugin like this. A documentation of all possible config options can be found [here](https://github.com/tillsteinbach/CarConnectivity-plugin-webui/tree/main/doc/Config.md).
```
{
    "carConnectivity": {
        "connectors": [
            ...
        ]
        "plugins": [
            {
                "type": "webui",
                "config": {
                    "username": "admin", // Admin username for login
                    "password": "secret" // Admin password for login
                }
            }
        ]
    }
}
```

## How to use
You will default find the webinterface on http port 4000 on the machine that is hosting carconnectivity. You can change interface with the `host` parameter and the port with the `port parameter`.
Always set your personal username and password to protect your data from theft.

## Updates
If you want to update, the easiest way is:
```bash
pip3 install carconnectivity-plugin-webui --upgrade
```
