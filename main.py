import asyncio
import re
import flet as ft
from bleak import BleakScanner, BleakClient

# --- Constants & Config ---
DEFAULT_WRITE_UUID = "00002a00-0000-1000-8000-00805f9b34fb" 

class BLEScannerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.devices = {}  # address: {name, phone, card, rssi, uuids}
        self.connected_client = None
        self.is_scanning = False
        self.scanning_task = None

        self.setup_ui()

    def setup_ui(self):
        self.page.title = "Windows BLE Scanner & Decoder"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20
        self.page.window_width = 1000
        self.page.window_height = 800

        # Flet 0.80+ Colors and Icons are case-sensitive or moved.
        # Using string literals for colors and icons is more robust across versions.
        
        self.scan_btn = ft.FilledButton(
            "Start Scan", icon="play_arrow", on_click=self.toggle_scan,
            style=ft.ButtonStyle(bgcolor="blue700", color="white")
        )
        
        self.filter_input = ft.TextField(
            label="Filter by Device Name (e.g. Mcam)",
            width=300,
            on_change=self.apply_filter
        )
        
        self.device_list = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name (MAC)")),
                ft.DataColumn(ft.Text("Phone Number")),
                ft.DataColumn(ft.Text("Card Number")),
                ft.DataColumn(ft.Text("RSSI"), numeric=True),
                ft.DataColumn(ft.Text("Action")),
            ],
            rows=[],
        )

        self.order_info_text = ft.Text("Order Information: None", size=16, weight="bold", color="amber300")
        self.message_input = ft.TextField(label="Message to Send", width=400)
        self.send_btn = ft.FilledButton("Send", on_click=self.send_data, disabled=True)
        self.status_text = ft.Text("Status: Idle", color="grey400")

        # Layout
        self.page.add(
            ft.Row([
                ft.Text("BLE Scanner MVP", size=32, weight="bold"),
                ft.Row([self.filter_input, self.scan_btn], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Column([
                ft.Text("Detected Devices", size=20, weight="bold"),
                ft.Container(content=ft.Column([self.device_list], scroll=ft.ScrollMode.ALWAYS), height=350, border=ft.Border.all(width=1, color="grey800"), border_radius=10),
            ]),
            ft.Divider(),
            ft.Column([
                ft.Text("Connection Information", size=20, weight="bold"),
                self.order_info_text,
                ft.Row([self.message_input, self.send_btn]),
                self.status_text
            ])
        )

    def apply_filter(self, e):
        """Manually trigger a UI update to reflect the filter immediately if needed, 
        but the run_scan loop will handle it naturally."""
        self.page.update()

    def decode_uuid_data(self, uuids):
        """
        Extracts phone and card numbers from Service UUID strings.
        Handle both literal hex segments and ASCII conversion.
        """
        phone = ""
        card = ""
        
        for uuid in uuids:
            parts = uuid.split("-")
            
            # --- Rule A: Literal Hex Segments (User's specific Request) ---
            # If standard 8-4-4-4-12 UUID format
            if len(parts) == 5:
                # Phone = Segments 1, 2, 3 concatenated (8+4+4 = 16 hex chars)
                # Card = Segment 4 (4 hex chars)
                lit_phone = f"{parts[0]}{parts[1]}{parts[2]}"
                lit_card = parts[3]
                
                # Check if these literal parts contain data (e.g., starting with 010 for phone)
                # If they look like literal data, we use them.
                if lit_phone.startswith("010") or lit_phone.startswith("1234"):  # Added 1234 for user's example
                    phone = lit_phone
                    card = lit_card
                    break

            # --- Rule B: ASCII Conversion (Fallback) ---
            clean_uuid = uuid.replace("-", "")
            try:
                decoded_str = bytes.fromhex(clean_uuid).decode('ascii', errors='ignore')
                phone_match = re.search(r'010\d{8}', decoded_str)
                if phone_match:
                    phone = phone_match.group()
                
                card_match = re.search(r'\d{8,16}', decoded_str)
                if card_match and card_match.group() != phone:
                    card = card_match.group()
                
                if phone or card:
                    break
            except:
                continue
                
        return phone, card

    async def run_scan(self):
        self.is_scanning = True
        self.scan_btn.text = "Stop Scan"
        self.scan_btn.icon = "stop"
        self.scan_btn.style = ft.ButtonStyle(bgcolor="red700", color="white")
        self.status_text.value = "Status: Scanning..."
        self.page.update()

        print("\n" + "="*50)
        print("Starting BLE Scan...")
        print("="*50)

        while self.is_scanning:
            try:
                # return_adv=True returns a dict: {address: (device, advertisement_data)}
                devices_dict = await BleakScanner.discover(timeout=5.0, return_adv=True)
                self.device_list.rows.clear()
                
                for address, (d, adv) in devices_dict.items():
                    name = d.name or "Unknown"
                    filter_val = self.filter_input.value.lower()
                    
                    # Filtering Logic (Like search)
                    if filter_val and filter_val not in name.lower():
                        continue

                    # adv.service_uuids is a list of UUID strings
                    uuids = adv.service_uuids or []
                    phone, card = self.decode_uuid_data(uuids)
                    rssi = adv.rssi  # Get RSSI from AdvertisementData
                    
                    # Console Logging
                    print(f"[SCAN] Found: {d.name or 'Unknown'} ({address}) | RSSI: {rssi}")
                    if uuids: print(f"  - UUIDs: {uuids}")
                    if phone: print(f"  - DECODED PHONE: {phone}")
                    if card: print(f"  - DECODED CARD: {card}")

                    self.devices[d.address] = {
                        "device": d,
                        "phone": phone,
                        "card": card,
                        "rssi": rssi
                    }

                    self.device_list.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(f"{d.name or 'Unknown'} ({d.address})")),
                                ft.DataCell(ft.Text(phone or "-")),
                                ft.DataCell(ft.Text(card or "-")),
                                ft.DataCell(ft.Text(str(rssi))),
                                ft.DataCell(ft.FilledButton("Connect", on_click=lambda e, addr=d.address: self.page.run_task(self.connect_device, addr))),
                            ]
                        )
                    )
                self.page.update()
            except Exception as ex:
                self.status_text.value = f"Status: Scan error ({str(ex)})"
                self.page.update()
            
            await asyncio.sleep(1)

    async def toggle_scan(self, e):
        if self.is_scanning:
            self.is_scanning = False
            self.scan_btn.text = "Start Scan"
            self.scan_btn.icon = "play_arrow"
            self.scan_btn.style = ft.ButtonStyle(bgcolor="blue700", color="white")
            self.status_text.value = "Status: Idle"
            print("\nScan Stopped by User.")
        else:
            self.scanning_task = asyncio.create_task(self.run_scan())
        self.page.update()

    async def connect_device(self, address):
        self.status_text.value = f"Status: Connecting to {address}..."
        self.page.update()
        
        try:
            client = BleakClient(address)
            await client.connect()
            self.connected_client = client
            self.status_text.value = f"Status: Connected to {address}"
            self.send_btn.disabled = False
            # Explore Services and Characteristics
            print(f"\n[GATT] Discovering services for {address}...")
            services = client.services # In modern bleak, this is a property
            found_info = False
            
            for service in services:
                print(f"  [Service] {service.uuid} ({service.description})")
                for char in service.characteristics:
                    print(f"    [Char] {char.uuid} | Props: {char.properties}")
                    if "read" in char.properties:
                        try:
                            data = await client.read_gatt_char(char.uuid)
                            decoded = data.decode('utf-8', errors='ignore')
                            if decoded.strip():
                                print(f"      -> Read Data: {decoded}")
                                self.order_info_text.value = f"Order Information: {decoded}"
                                found_info = True
                                # Not breaking here so we can see all UUIDs in logs
                        except:
                            continue
            
            if not found_info:
                self.order_info_text.value = "Order Information: No readable data found."
                
        except Exception as ex:
            self.status_text.value = f"Status: Connection failed ({str(ex)})"
        
        self.page.update()

    async def send_data(self, e):
        if not self.connected_client or not self.message_input.value:
            return
        
        try:
            msg = self.message_input.value.encode('utf-8')
            target_char = None
            for s in self.connected_client.services:
                for c in s.characteristics:
                    if "write" in c.properties or "write-without-response" in c.properties:
                        target_char = c.uuid
                        break
                if target_char: break
            
            if target_char:
                await self.connected_client.write_gatt_char(target_char, msg)
                self.status_text.value = f"Status: Data sent to {target_char}"
            else:
                self.status_text.value = "Status: No writable characteristic found."
        except Exception as ex:
            self.status_text.value = f"Status: Send failed ({str(ex)})"
            
        self.page.update()

async def main(page: ft.Page):
    app = BLEScannerApp(page)

if __name__ == "__main__":
    ft.run(main)
