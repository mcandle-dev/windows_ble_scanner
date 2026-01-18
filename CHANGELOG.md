# Changelog

All notable changes to this project will be documented in this file.

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
