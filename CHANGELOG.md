# Changelog

All notable changes to this project will be documented in this file.

## [2026-01-25]
### Changed
- **UI Layout**: Relocated 'Write Channel Response' switch to the 'Connection Information' header line for better space utilization.
- **UI Spacing**: Increased the height of the 'Connection Information' section by reducing the 'Detected Devices' section height.
- **Connection Logic**: Implemented explicit disconnection logic when stopping scans or starting new connections to prevent "zombie" connection errors.
- **Button UX**: Updated 'Start/Stop Scan' button to show consistent state (Red/Stop, Blue/Start) and automatically reset when a connection is established.

## [Unreleased]

## [2026-01-19]
### Added
- **UI Layout Update**: Refactored the main interface to a 50:50 split between "Detected Devices" and "Activity Logs" for better visibility and simplified access to connection buttons. Resizable divider is maintained.
- **Auto-Save Logs**: Added a "Save" button to the "Activity Logs" panel.
  - Logs are automatically saved to the `./logs` directory locally.
  - Filename format: `ble_YYYYMMDD_HHMMSS.txt`.
  - Removed reliance on `FilePicker` to ensure stability across different Flet versions.

### Fixed
- **UI Rendering Issues**: Resolved "Unknown control" and red overlay errors caused by improper `FilePicker` initialization in Flet 0.80.x.
- **Icon Compatibility**: Fixed `AttributeError` for 'SAVE' icon by ensuring correct reference for the installed Flet library version.
