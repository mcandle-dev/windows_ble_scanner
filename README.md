# Windows BLE Scanner & Decoder

This is a Windows-based BLE (Bluetooth Low Energy) scanner developed using Python, **Bleak**, and **Flet**. It is designed to scan for nearby BLE devices and decode specific data (Phone and Card numbers) hidden within their Service UUIDs.

## Features

- **Real-time BLE Scanning:** Discover nearby devices and monitor their RSSI (Signal Strength).
- **UUID Data Decoding:**
  - Extracts 16-character phone numbers from the first three segments of a 128-bit UUID.
  - Extracts card numbers from the fourth segment of the UUID.
  - Fallback ASCII decoding for custom encoded data.
- **Dynamic Filtering:** Search for specific devices by name using the "Filter" field.
- **GATT Interaction:** 
  - Connect to devices to read characteristic data (e.g., Order Information).
  - Write custom messages to writable characteristics.
- **Modern UI:** Built with Flet (Flutter for Python) with a sleek dark mode and responsive toggle buttons.

## Environment Setup

### Prerequisites
- Python 3.10+
- Windows OS (with Bluetooth hardware)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/mcandle-dev/windows_ble_scanner.git
   cd windows_ble_scanner
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install bleak flet
   ```

## Usage
Run the application using:
```bash
python main.py
```

1. Enter a device name filter if desired.
2. Click **Start Scan** to begin discovery.
3. Decoded phone and card numbers will appear in the list.
4. Click **Connect** next to a device to explore its GATT services and send data.

## Project Structure
- `main.py`: The entry point and main logic of the application.
- `logs/`: Contains daily progress and work logs.
- `requirements.md`: Original project requirements and specifications.

## Authors
- Developed as an MVP based on user requirements.
- Reference: [ble-advertiser](https://github.com/mcandle-dev/ble-advertiser)
