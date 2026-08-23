# Changelog

All notable changes to this project will be documented in this file.

## [2026-08-23]
### Changed (Device List)
- **One Row Per Phone**: Android rotates its BLE address every few minutes, so a single handset
  appeared in Detected Devices under three or more MACs at once. Rows are now keyed on what the
  device advertises (name + decoded card + phone) rather than its address, keeping the strongest
  signal — the address most likely to still be reachable — and marking collapsed duplicates as
  `+N MAC`. Devices that advertise nothing identifying still get one row per address.

### Fixed (Channel Selection)
- **Insufficient Authentication On Every Write**: A peer build exposes the GATT service on a
  non-standard base UUID (`0000fff1-1234-1234-8000-…`), so the exact-UUID match missed it and the
  fallback picked the phone's own Generic Media Control characteristic (`2b99`) — a SIG system
  characteristic that requires bonding, failing both the handshake and the send with
  `Insufficient Authentication`. Channel selection now also accepts the 16-bit short form
  (`fff1`/`fff2`) inside an `fff0` service, so either base resolves correctly.
- **Fallback No Longer Targets System Characteristics**: The five-entry blacklist is replaced by
  excluding the whole Bluetooth SIG base (`…-0000-1000-8000-00805f9b34fb`) from fallback
  selection. A phone exposes dozens of writable system characteristics; none is a valid target.
  When nothing qualifies, the scanner now writes nowhere rather than to a system characteristic.

### Added (Protocol)
- **Read The Peer's Reply**: The scanner now reads the response characteristic after the
  `AT+CONNECT` handshake and after every order write. The peer answers each command by loading a
  JSON status into `fff2` and waiting to be read — it declares NOTIFY but never sends one — so
  until now every acknowledgement and every parse error went unseen. The connect-time read is
  kept as a diagnostic log only: it runs before the handshake, when the peer still returns its
  `"No data"` placeholder, which was being displayed as Order Information.

### Fixed (Decoding)
- **Phone/Card Were Swapped**: `decode_uuid_data` read UUID segments 1-3 as the phone number and
  segment 4 as the card number. The advertiser lays the UUID out as
  `{card[0:8]}-{card[8:12]}-{card[12:16]}-0000-{phone4}00805F9B`, so segments 1-3 are the **card
  number**, segment 4 is fixed padding, and only the **last 4 digits of the phone** are carried at
  the head of segment 5. The constant `DECODED CARD: 0000` in the logs was this padding.
  The legacy iOS layout (phone suffix in segment 4) is still accepted.
- **Column Label**: `Phone No` → `Phone (last4)`, since only 4 digits are ever advertised.

### Added
- **AT+CONNECT Handshake**: The scanner now sends `AT+CONNECT` on the write channel right
  after GATT discovery. `ble-advertiser` (Android) waits for this command and shuts down its
  GATT server 60 seconds after advertising starts if it never arrives — which made Send fail
  while the UI still showed a live connection.
- **Disconnect Detection**: Registered a Bleak `disconnected_callback`. When the peer drops the
  link the UI now clears the Read/Write channel labels, disables Send, and logs the event.
  Previously Windows' cached GATT database left the UI showing a connection that was already gone.

### Changed
- **Start Scan**: Starting a scan now clears the previously detected devices before listing new ones.
- **Send Diagnostics**: A blocked Send now logs the specific precondition that failed
  (no connection / no write channel / empty message) instead of returning silently.
  A closed-connection write error additionally logs a hint about the peer's GATT server timeout.

### Fixed
- **Initial Read**: The read attempt was nested inside the fallback-selection branch, so when the
  fixed `fff2` target matched it was never actually read. The read now runs once after discovery
  against whichever channel was finally selected.
- **Send Error Handler**: The handler dereferenced `self.target_write_char`, which a concurrent
  disconnect could clear, faulting the error path itself. It now uses the local binding.

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
