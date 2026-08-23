# Changelog

All notable changes to this project will be documented in this file.

## [2026-08-23]
### Fixed (Dead-Link Handling)
- **`'NoneType' object has no attribute 'write_gatt_char'`**: The candidate loop re-read
  `self.connected_client` on every attempt, which the disconnect callback clears mid-loop, so a
  link failure surfaced as an AttributeError and buried the real cause. The client is now held
  locally for the duration of the write.
- **Stop Retrying A Dead Link**: `Not connected`, `Unreachable` and the WinError codes for "object
  closed" and "method called at an unexpected time" mean the link is gone, not that this
  characteristic refused. Remaining candidates are skipped instead of producing one failure each.
  A genuine per-characteristic refusal such as `Insufficient Authentication` still falls through
  to the next match.

### Added (Connect & Send — spec 002)
- **Order Goes Out With The Connection**: Connect now runs the whole exchange — connect, discover,
  `AT+CONNECT`, read the reply, write the order, read the reply — without waiting on further
  clicks. The peer closes its GATT server about 60s after its user taps pay, and operator typing
  was consuming that window; a run that missed it is what produced the `Unreachable` failure.
- **Auto Send Guards**: The order is sent only when the message field is non-empty *and* the new
  `Auto Send on Connect` switch is on, so nothing fires unintentionally. A failed handshake skips
  the order entirely rather than producing a second failure.
- **Time Budget In The Log**: Discovery, handshake and the full exchange each report their elapsed
  time since Connect, with a warning when the total passes 60s.
- **Faster Discovery**: The scan cycle drops from 5s+1s to 3s+0.5s, since a scan cycle is the first
  thing to eat into the peer's window.

### Changed (Write Timeouts)
- **No Queue Pile-Up**: A write with response blocks until the peer answers or the GATT layer gives
  up ~30s later. Sends pressed during that wait queued behind it and all failed together. Send is
  now rejected (with the reason logged) and the button disabled while a write is outstanding.
- **Stalled Writes Are Named**: A write that fails after 5s or more now logs how long it waited,
  distinguishing a peer that stopped responding from one that refused outright.
- **`Unreachable` Diagnosed**: This error now maps to the peer-gone hint instead of the generic
  branch, and the hint names all four ways ble-advertiser's server disappears — the 60s timer,
  receiving one order, the screen locking, and the app leaving the foreground.

### Fixed (Duplicate Characteristics)
- **"Multiple Characteristics with this UUID"**: Discovery returned the `fff0` service twice on
  device, so two `fff1` and two `fff2` characteristics were present. Every GATT call passed a UUID
  string,
  which Bleak cannot resolve when it matches more than one characteristic — the handshake and the
  initial read both failed with `Multiple Characteristics with this UUID, refer to your desired
  characteristic by the 'handle' attribute instead`. Reads and writes now address the
  characteristic object directly.
- **Duplicate Fallback**: All matching characteristics are kept. A write tries them in turn, so a
  stale duplicate no longer sinks the send, and the handshake pins the channel to whichever handle
  accepted it. Discovery logs a warning naming the duplicate handles.

### Changed (Layout)
- **Left Panels Follow The Window**: Only the Activity Logs panel responded to resizing. Detected
  Devices was pinned at 260px and the message field at 400px, so dragging the split divider or
  resizing the window clipped them. Both left panels now take a share of the height (3:2) and the
  message field expands with its panel.
- **Device Table Scrolls Both Ways**: The table scrolls horizontally as well as vertically, so
  narrowing the left panel scrolls the columns instead of cutting them off.

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
