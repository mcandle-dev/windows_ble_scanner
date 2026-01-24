import asyncio
import re
import datetime
import flet as ft
from bleak import BleakScanner, BleakClient

# --- Constants & Config ---
TARGET_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
TARGET_WRITE_UUID   = "0000fff1-0000-1000-8000-00805f9b34fb"
TARGET_READ_UUID    = "0000fff2-0000-1000-8000-00805f9b34fb"

class BLEScannerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.devices = {}  # address: {name, phone, card, rssi, uuids}
        self.connected_client = None
        self.target_write_char = None
        self.is_scanning = False
        self.scanning_task = None
        self.log_display = ft.ListView(expand=True, spacing=2, auto_scroll=True)
        self.all_logs = [] # Store raw logs for saving
        self.left_col_width = 500  # Initial width of left panel
        # self.file_picker = ft.FilePicker() # Removed due to UI issues
        # self.file_picker.on_result = self.on_save_file_result # Removed
        
        self.setup_ui()

    def log_message(self, msg, color="white"):
        """Appends a message to the UI log display."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {msg}"
        self.all_logs.append(log_entry)
        self.log_display.controls.append(
            ft.Text(log_entry, size=12, color=color, font_family="monospace")
        )
        if len(self.log_display.controls) > 100:
            self.log_display.controls.pop(0)
        
        # Keep internal log buffer manageable, but maybe a bit larger than UI
        if len(self.all_logs) > 1000:
            self.all_logs.pop(0)
        try:
            self.page.update()
        except:
            pass

    def setup_ui(self):
        self.page.clean()
        # self.page.overlay.clear() # No longer needed
        # self.page.overlay.append(self.file_picker) # Removed
        
        self.page.title = "Windows BLE Scanner & Decoder"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20
        self.page.window_maximized = True

        # Drag event for resizable layout
        def on_pan_update(e: ft.DragUpdateEvent):
            if e.primary_delta is not None:
                self.left_col_width += e.primary_delta
                if self.left_col_width < 300: self.left_col_width = 300
                elif self.left_col_width > 1200: self.left_col_width = 1200
                # Enable fixed width when dragging starts
                content_row.controls[0].expand = None
                content_row.controls[0].width = self.left_col_width
                self.page.update()

        # Flet 0.80+ Colors and Icons are case-sensitive or moved.
        # Using string literals for colors and icons is more robust across versions.
        
        self.scan_btn = ft.FilledButton(
            "Start Scan", icon="play_arrow", on_click=self.toggle_scan,
            style=ft.ButtonStyle(bgcolor="blue700", color="white")
        )
        
        self.filter_input = ft.TextField(
            label="Filter by Device Name (e.g. Mcam)",
            width=300,
            value="mcan",
            on_change=self.apply_filter
        )
        
        self.device_list = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name (MAC)")),
                ft.DataColumn(ft.Text("Phone No")),
                ft.DataColumn(ft.Text("Card No")),
                ft.DataColumn(ft.Text("RSSI"), numeric=True),
                ft.DataColumn(ft.Text("Action")),
            ],
            rows=[],
        )

        self.order_info_text = ft.Text("Order Information: None", size=16, weight="bold", color="amber300")
        self.read_char_text = ft.Text("Read Channel: -", size=14, color="grey400")
        self.write_char_text = ft.Text("Write Channel: -", size=14, color="grey400")
        self.message_input = ft.TextField(label="Message to Send", width=400)
        self.send_btn = ft.FilledButton("Send", on_click=self.send_data, disabled=True)
        self.status_text = ft.Text("Status: Idle", color="grey400")

        # Layout
        self.page.add(
            # Header Section
            ft.Row([
                ft.Text("BLE Scanner MVP", size=32, weight="bold"),
                ft.Row([self.filter_input, self.scan_btn], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            # Main Content: Two Columns with Resizable Split
            content_row := ft.Row([
                # Left Column: Devices and Connection Info
                ft.Column([
                    ft.Text("Detected Devices", size=20, weight="bold"),
                    ft.Container(
                        content=ft.Column([self.device_list], scroll=ft.ScrollMode.ALWAYS), 
                        height=300, 
                        border=ft.Border.all(width=1, color="grey800"), 
                        border_radius=10
                    ),
                    ft.Divider(),
                    ft.Text("Connection Information", size=20, weight="bold"),
                    ft.Container(
                        content=ft.Column([
                            self.order_info_text,
                            ft.Row([self.read_char_text, self.write_char_text], spacing=20),
                            ft.Row([self.message_input, self.send_btn], spacing=10),
                        ], spacing=15),
                        padding=10,
                        border=ft.Border.all(width=1, color="grey900"),
                        border_radius=10,
                        expand=True
                    ),
                ], expand=True),
                # Draggable Divider
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.VerticalDivider(width=2, color="grey800"),
                        width=10,
                        bgcolor="transparent",
                    ),
                    on_pan_update=on_pan_update,
                    on_hover=lambda _: setattr(self.page, "cursor", "col-resize") or self.page.update(),
                    mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
                ),
                # Right Column: Activity Logs
                ft.Column([
                    ft.Row([
                        ft.Text("Activity Logs", size=20, weight="bold"),
                        ft.IconButton(
                            icon=ft.icons.Icons.SAVE,
                            tooltip="Auto-Save Logs (to ./logs)", 
                            on_click=self.save_logs_direct
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        content=self.log_display,
                        expand=True,
                        padding=10,
                        bgcolor="black",
                        border=ft.Border.all(width=1, color="grey800"),
                        border_radius=10
                    ),
                ], expand=True),
            ], expand=True, spacing=0),
            # Footer: Status Text
            self.status_text 
        )
        self.page.update()

    def save_logs_direct(self, e):
        """Saves logs directly to a 'logs' folder without FilePicker."""
        import os
        if not self.all_logs:
            self.status_text.value = "Status: No logs to save."
            self.page.update()
            return

        try:
            os.makedirs("logs", exist_ok=True)
            filename = f"logs/ble_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.all_logs))
            
            self.log_message(f"Logs saved to: {os.path.abspath(filename)}", color="green")
            self.status_text.value = f"Status: Saved to {filename}"
        except Exception as ex:
            self.log_message(f"Failed to auto-save logs: {ex}", color="red")
        self.page.update()

    # def on_save_file_result(self, e): ... Removed

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
        self.status_text.value = "Status: Scanning..."
        try:
            self.page.update()
        except Exception:
            return

        self.log_message("Starting BLE Scan...", color="amber")

        while self.is_scanning:
            if not self.page.session:
                break
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
                    
                    # Log to UI
                    self.log_message(f"[SCAN] Found: {name} ({address}) | RSSI: {rssi}", color="amber")
                    if uuids: self.log_message(f"  - UUIDs: {uuids}", color="grey400")
                    if phone: self.log_message(f"  - DECODED PHONE: {phone}", color="green")
                    if card: self.log_message(f"  - DECODED CARD: {card}", color="green")

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
            except RuntimeError as re:
                if "destroyed session" in str(re):
                    self.is_scanning = False
                    break
            except Exception as ex:
                try:
                    self.status_text.value = f"Status: Scan error ({str(ex)})"
                    self.page.update()
                except:
                    break
            
            await asyncio.sleep(1)

    async def toggle_scan(self, e):
        if self.is_scanning:
            self.is_scanning = False
            self.scan_btn.text = "Start Scan"
            self.scan_btn.icon = "play_arrow"
            self.scan_btn.style = ft.ButtonStyle(bgcolor="blue700", color="white")
            self.status_text.value = "Status: Idle"
            self.log_message("Scan Stopped by User.", color="amber")
        else:
            self.scan_btn.text = "Stop Scan"
            self.scan_btn.icon = "stop"
            self.scan_btn.style = ft.ButtonStyle(bgcolor="red700", color="white")
            self.scanning_task = asyncio.create_task(self.run_scan())
        self.page.update()

    async def connect_device(self, address):
        self.log_message(f"[CONNECT] Attempting to connect to {address}...", color="blue")
        self.status_text.value = f"Status: Connecting to {address}..."
        self.page.update()
        
        try:
            client = BleakClient(address)
            await client.connect()
            self.connected_client = client
            self.log_message(f"[CONNECT] Successfully connected to {address}", color="blue")
            self.status_text.value = f"Status: Connected to {address}"
            self.send_btn.disabled = False
            
            # Explore Services and Characteristics
            self.log_message(f"[GATT] Discovering services for {address}...", color="blue")
            services = client.services 
            found_info = False
            self.target_write_char = None
            found_read_char = None
            
            for service in services:
                self.log_message(f"  [Service] {service.uuid} ({service.description})", color="blue")
                for char in service.characteristics:
                    char_uuid = char.uuid.lower()
                    short_uuid = char_uuid.split("-")[0][-4:]
                    self.log_message(f"    [Char] {char.uuid} (Short: {short_uuid}) | Props: {char.properties}", color="grey400")
                    
                    is_system_char = short_uuid in ["2b29", "2b2a", "2a00", "2a01", "2a05"]
                    
                    # --- Priority 1: Strict Match with ble-advertiser spec ---
                    if char_uuid == TARGET_WRITE_UUID:
                        self.target_write_char = char
                        self.write_char_text.value = f"Write Channel: {short_uuid} (Fixed)"
                        self.log_message(f"      -> [MATCH] TARGET WRITE Characteristic found!", color="green")
                    
                    if char_uuid == TARGET_READ_UUID:
                        found_read_char = char
                        self.read_char_text.value = f"Read Channel: {short_uuid} (Fixed)"
                        self.log_message(f"      -> [MATCH] TARGET READ Characteristic found!", color="green")

                    # --- Priority 2: Fallback Logic (if not found yet) ---
                    if not self.target_write_char and not is_system_char:
                        if "write" in char.properties or "write-without-response" in char.properties:
                            self.target_write_char = char
                            self.write_char_text.value = f"Write Channel: {short_uuid}"
                            self.log_message(f"      -> Selected as fallback WRITE target", color="blue")

                    if not found_read_char and "read" in char.properties and not is_system_char:
                        found_read_char = char
                        self.read_char_text.value = f"Read Channel: {short_uuid}"
                        self.log_message(f"      -> Selected as fallback READ target", color="blue")
                            
                        try:
                            # Only try to read if it is explicitly the target READ char or has read property
                            if char == found_read_char:
                                data = await client.read_gatt_char(char.uuid)
                                decoded = data.decode('utf-8', errors='ignore')
                                if decoded.strip():
                                    self.log_message(f"      -> Initial Read Data: {decoded}", color="blue")
                                    self.order_info_text.value = f"Order Information: {decoded}"
                                    found_info = True
                        except Exception as e:
                            self.log_message(f"      -> Read failed: {e}", color="red")
                            continue
            
            if not found_info:
                self.order_info_text.value = "Order Information: No readable data found."
            
            if not self.target_write_char:
                self.log_message("[WARN] No suitable writable application characteristic found.", color="red")
                self.write_char_text.value = "Write Channel: Not found"
                
        except Exception as ex:
            self.log_message(f"[ERROR] Connection failed: {ex}", color="red")
            self.status_text.value = f"Status: Connection failed ({str(ex)})"
        
        self.page.update()

    async def send_data(self, e):
        if not self.connected_client or not self.message_input.value or not self.target_write_char:
            self.status_text.value = "Status: No device connected or message empty."
            self.page.update()
            return
        
        try:
            payload = self.message_input.value
            msg = payload.encode('utf-8')
            char = self.target_write_char
            short_id = char.uuid.split("-")[0][-4:]
            
            self.log_message(f"[SEND] Sending data to {short_id} ({char.uuid})", color="green")
            self.log_message(f"  - Payload: {payload}", color="grey400")
            
            # --- Robust Write Logic ---
            if "write" in char.properties:
                self.log_message(f"  - Method: Write With Response", color="grey400")
                await self.connected_client.write_gatt_char(char.uuid, msg, response=True)
                self.status_text.value = f"Status: Data sent to {short_id} (With Response)"
            elif "write-without-response" in char.properties:
                self.log_message(f"  - Method: Write Without Response", color="grey400")
                await self.connected_client.write_gatt_char(char.uuid, msg, response=False)
                self.status_text.value = f"Status: Data sent to {short_id} (No Response)"
            else:
                self.log_message(f"  - Error: Characteristic not writable.", color="red")
                self.status_text.value = "Status: Target characteristic not writable."
            
            self.log_message(f"  - Result: Sent successfully", color="green")
                
        except Exception as ex:
            err_msg = str(ex)
            short_id = self.target_write_char.uuid.split("-")[0][-4:]
            self.log_message(f"  - Result: FAILED", color="red")
            self.log_message(f"  - Error: {err_msg}", color="red")
            
            if "Access Denied" in err_msg:
                self.status_text.value = f"Status: Failed (Access Denied for {short_id}). Pairing may be required."
            else:
                self.status_text.value = f"Status: Send failed ({err_msg})"
            
        self.page.update()

async def main(page: ft.Page):
    app = BLEScannerApp(page)

if __name__ == "__main__":
    ft.run(main)
