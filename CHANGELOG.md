# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- No unreleased changes so far

## [0.7.1] - 2026-01-23
### Added
- Possibility for links in bootstrap tables via jquery

## [0.7] - 2026-01-11
## Changed
- Inherit locale from carconnectivity config root
- Pass flask app to PluginUI

## [0.6] - 2026-01-04
### Added
- Support for initializing attributes on startup form static entries in the configuration
- Added support for https
- Output of vehicle data in json format

Note: This plugin is required for compatibility with CarConnectivity version 0.11 and higher.

## [0.5.3] - 2025-11-29
### Fixed
- Show only images when images feature is enabled and actual vehicle image is available

### Added
- Add possibility to show enabled features for plugins and connectors in the web UI

## [0.5.2] - 2025-11-02
### Changed
- Updated dependencies

### Fixed
- Hide window heating from overview and only dispaly in extra tab (thanks to user @acfischer42)

## [0.5.1] - 2025-06-20
### Changed
- Updated dependencies

## [0.5] - 2025-04-17
### Fixed
- added missing time_format config option that caused the connector to crash when locale was configured

### Added
- Values are now displayed with the right precision

### Changed
- Updated dependencies

## [0.4] - 2025-04-02
### Fixed
- Allowes to have multiple instances of plugins and connectors running

### Changed
- Empty tabs in vehicle view are now hidden
- Updated dependencies

## [0.3.1] - 2025-03-02
### Fixes
- Login required to access logs

## [0.3] - 2025-03-02
### Added
- Support for window heating attributes
- More error output for locales

## [0.2] - 2025-03-02
### Added
- Default take locale from system
- Convert values to unit of locale
- Added Maintainance view in vehicle status page

## [0.1.2] - 2025-02-20
### Fixes
- Fix bug when loglevel is not configured

## [0.1.1] - 2025-02-20
### Added
- Plugin UI root

## [0.1] - 2025-02-19
Initial release, let's go and give this to the public to try out...

[unreleased]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/compare/v0.7.1...HEAD
[0.7.1]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.7.1
[0.7]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.7
[0.6]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.6
[0.5.3]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.5.3
[0.5.2]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.5.2
[0.5.1]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.5.1
[0.5]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.5
[0.4]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.4
[0.3.1]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.3.1
[0.3]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.3
[0.2]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.2
[0.1.2]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.1.2
[0.1.1]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.1.1
[0.1]: https://github.com/tillsteinbach/CarConnectivity-plugin-webui/releases/tag/v0.1
