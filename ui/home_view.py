import customtkinter as ctk
from PIL import Image
import os
import requests
import threading
import time

# Set awal theme dan scaling
ctk.set_appearance_mode("dark")  # light / dark / system
ctk.set_default_color_theme("blue")  # optional, bisa "green", "dark-blue", dll

class HomeView(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_room = "Kamar"  # Default room
        
        # LED device mapping berdasarkan ruangan
        self.led_devices = {
            "Kamar": "LED_KAMAR_001",
            "Dapur": "LED_DAPUR_001", 
            "Ruang Tamu": "LED_RUANGTAMU_001"
        }
        
        # API base URL
        self.api_base_url = "http://localhost:8080/api"
        
        # LED status tracking
        self.led_states = {}
        
        # Set up image paths
        self.setup_image_paths()
        
        # Configure scrollable frame
        self.configure(fg_color="transparent")
        
        # Main content frame dengan responsive grid
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid untuk responsive layout
        self.content_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")
        self.content_frame.grid_rowconfigure((2, 3, 4), weight=1)

        # Initialize UI components
        self.create_header()
        self.create_banner()
        self.create_room_selection()
        self.create_dashboard_cards()
        self.create_control_panel()
        self.create_settings_panel()
        
        # Start data fetching after UI is created
        self.after(1000, self.fetch_and_update_sensor_data)
        self.after(2000, self.fetch_led_states)  # Fetch LED states after sensor data

    def setup_image_paths(self):
        """Setup paths untuk gambar"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(os.path.dirname(current_dir), "assets")
        
        self.banner_image_path = os.path.join(self.assets_dir, "banner.png")
        self.home_icon_path = os.path.join(self.assets_dir, "home_icon.png")
        
        os.makedirs(self.assets_dir, exist_ok=True)

    def load_image_safe(self, image_path, size=(100, 100), fallback_text="🏠"):
        """Load image with fallback to emoji if image not found"""
        try:
            if os.path.exists(image_path):
                pil_image = Image.open(image_path)
                return ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
            else:
                return None
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None

    def create_header(self):
        """Membuat header dengan styling yang lebih baik"""
        header_frame = ctk.CTkFrame(self.content_frame, height=60, corner_radius=15)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        header_frame.grid_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🏠 Smart Home Dashboard", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(expand=True)

    def create_banner(self):
        """Membuat banner image yang memanjang"""
        banner_frame = ctk.CTkFrame(self.content_frame, height=120, corner_radius=15)
        banner_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        banner_frame.grid_propagate(False)
        banner_frame.grid_columnconfigure(0, weight=1)
        banner_frame.grid_rowconfigure(0, weight=1)
        
        banner_image = self.load_image_safe(self.banner_image_path, size=(800, 100))
        
        if banner_image:
            banner_label = ctk.CTkLabel(
                banner_frame,
                image=banner_image,
                text=""
            )
            banner_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        else:
            self.create_text_banner(banner_frame)

    def create_text_banner(self, banner_frame):
        """Create text-based banner as fallback"""
        banner_content = ctk.CTkFrame(banner_frame, corner_radius=10)
        banner_content.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        banner_content.grid_columnconfigure(1, weight=1)
        
        # Left side - Icon
        icon_frame = ctk.CTkFrame(banner_content, width=100, corner_radius=10)
        icon_frame.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=10)
        icon_frame.grid_propagate(False)
        
        home_icon = self.load_image_safe(self.home_icon_path, size=(60, 60))
        
        if home_icon:
            icon_label = ctk.CTkLabel(icon_frame, image=home_icon, text="")
            icon_label.pack(expand=True)
        else:
            house_icon = ctk.CTkLabel(
                icon_frame,
                text="🏡",
                font=ctk.CTkFont(size=48)
            )
            house_icon.pack(expand=True)
        
        # Center - Welcome text
        text_frame = ctk.CTkFrame(banner_content, fg_color="transparent")
        text_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)
        
        welcome_label = ctk.CTkLabel(
            text_frame,
            text="Selamat Datang di Rumah Pintar Anda",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        welcome_label.pack(anchor="w", pady=(15, 5))
        
        subtitle_label = ctk.CTkLabel(
            text_frame,
            text="Monitor dan kontrol semua perangkat dengan mudah dari satu tempat",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        subtitle_label.pack(anchor="w")
        
        # Right side - Status indicators
        status_frame = ctk.CTkFrame(banner_content, width=150, corner_radius=10)
        status_frame.grid(row=0, column=2, sticky="ns", padx=(0, 10), pady=10)
        status_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            status_frame,
            text="Status Sistem",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(10, 5))
        
        # Dynamic status indicators
        self.status_online = ctk.CTkLabel(
            status_frame,
            text="🟢 Online",
            font=ctk.CTkFont(size=11),
            text_color="green"
        )
        self.status_online.pack()
        
        self.status_connected = ctk.CTkLabel(
            status_frame,
            text="📡 Terhubung",
            font=ctk.CTkFont(size=11),
            text_color="blue"
        )
        self.status_connected.pack()
        
        self.status_power = ctk.CTkLabel(
            status_frame,
            text="🔋 Normal",
            font=ctk.CTkFont(size=11),
            text_color="orange"
        )
        self.status_power.pack(pady=(0, 10))

    def create_room_selection(self):
        """Membuat panel pemilihan ruangan"""
        room_frame = ctk.CTkFrame(self.content_frame, height=80, corner_radius=15)
        room_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        room_frame.grid_propagate(False)
        room_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        room_title = ctk.CTkLabel(
            room_frame,
            text="🏠 Pilih Ruangan:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        room_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
        
        rooms_data = [
            ("🛏️ Kamar", "Kamar"),
            ("🍳 Dapur", "Dapur"),
            ("🛋️ Ruang Tamu", "Ruang Tamu")
        ]
        
        self.room_buttons = {}
        
        for i, (display_name, room_name) in enumerate(rooms_data, 1):
            btn = ctk.CTkButton(
                room_frame,
                text=display_name,
                height=40,
                corner_radius=20,
                command=lambda r=room_name: self.select_room(r),
                font=ctk.CTkFont(size=14, weight="bold")
            )
            btn.grid(row=0, column=i, padx=10, pady=20, sticky="ew")
            self.room_buttons[room_name] = btn
        
        self.select_room("Kamar")

    def select_room(self, room_name):
        """Handle room selection"""
        self.current_room = room_name
        
        # Update button appearances
        for room, btn in self.room_buttons.items():
            if room == room_name:
                btn.configure(
                    fg_color=("gray75", "gray25"),
                    hover_color=("gray70", "gray30"),
                    text_color=("white", "white")
                )
            else:
                btn.configure(
                    fg_color=("gray90", "gray20"),
                    hover_color=("gray80", "gray25"),
                    text_color=("gray10", "gray90")
                )
        
        # Update control panel title
        if hasattr(self, 'control_title_label'):
            self.control_title_label.configure(text=f"🎛️ Kontrol {self.current_room}")
        
        # Update LED switch state for current room
        self.update_led_switch_for_room(room_name)
        
        # Update room-specific data
        self.update_room_data(room_name)
        print(f"Selected room: {room_name}")

    def update_room_data(self, room_name):
        """Update dashboard data based on selected room"""
        room_data = {
            "Kamar": {"temp": "23°C", "humidity": "55%", "temp_status": "Nyaman", "hum_status": "Optimal"},
            "Dapur": {"temp": "27°C", "humidity": "70%", "temp_status": "Hangat", "hum_status": "Tinggi"},
            "Ruang Tamu": {"temp": "25°C", "humidity": "60%", "temp_status": "Normal", "hum_status": "Baik"}
        }
        
        data = room_data.get(room_name, room_data["Kamar"])
        
        if hasattr(self, 'temp_value_label') and hasattr(self, 'humidity_value_label'):
            self.temp_value_label.configure(text=data["temp"])
            self.humidity_value_label.configure(text=data["humidity"])
            self.temp_status_label.configure(text=f"● {data['temp_status']}")
            self.humidity_status_label.configure(text=f"● {data['hum_status']}")

    def create_dashboard_cards(self):
        """Membuat cards untuk monitoring dengan ukuran yang konsisten"""
        sensor_frame = ctk.CTkFrame(self.content_frame, corner_radius=15)
        sensor_frame.grid(row=3, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        sensor_frame.grid_columnconfigure(0, weight=1)
        sensor_frame.grid_rowconfigure((0, 1, 2), weight=1)
        
        sensor_title = ctk.CTkLabel(
            sensor_frame, 
            text="📊 Monitoring Sensor", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        sensor_title.grid(row=0, column=0, pady=(15, 10))
        
        # Temperature Card
        self.create_sensor_card(
            sensor_frame, "🌡️ Suhu", "23°C", "Nyaman", "green", row=1, 
            value_attr="temp_value_label", status_attr="temp_status_label"
        )
        
        # Humidity Card  
        self.create_sensor_card(
            sensor_frame, "💧 Kelembaban", "55%", "Optimal", "blue", row=2, 
            value_attr="humidity_value_label", status_attr="humidity_status_label"
        )

    def create_control_panel(self):
        """Membuat panel kontrol perangkat"""
        control_frame = ctk.CTkFrame(self.content_frame, corner_radius=15)
        control_frame.grid(row=3, column=1, sticky="nsew", padx=5, pady=(0, 10))
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        
        self.control_title_label = ctk.CTkLabel(
            control_frame, 
            text=f"🎛️ Kontrol {self.current_room}", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.control_title_label.grid(row=0, column=0, pady=(15, 10))
        
        # LED Control dengan API integration
        self.led_control = self.create_led_toggle_card(control_frame, row=1)
        
        # Door Control (Servo)
        self.door_control = self.create_toggle_card(
            control_frame, "🚪 Pintu Otomatis", row=2, icon="🚪"
        )
        
        # Fan Control
        self.fan_control = self.create_fan_card(control_frame, row=3)
        
        # LED Stats mini card
        self.create_led_stats_card(control_frame, row=4)

    def create_settings_panel(self):
        """Membuat panel pengaturan"""
        settings_frame = ctk.CTkFrame(self.content_frame, corner_radius=15)
        settings_frame.grid(row=3, column=2, sticky="nsew", padx=(10, 0), pady=(0, 10))
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        
        settings_title = ctk.CTkLabel(
            settings_frame, 
            text="⚙️ Pengaturan", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_title.grid(row=0, column=0, pady=(15, 10))
        
        # Theme Toggle
        self.theme_frame = ctk.CTkFrame(settings_frame, height=80)
        self.theme_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        self.theme_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            self.theme_frame, 
            text="🎨 Mode Tema", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.theme_button = ctk.CTkButton(
            self.theme_frame, 
            text="🌙 Dark Mode", 
            command=self.toggle_theme,
            height=32,
            corner_radius=20
        )
        self.theme_button.pack(pady=(0, 10))
        
        # Auto Mode Toggle
        self.auto_frame = ctk.CTkFrame(settings_frame, height=80)
        self.auto_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=5)
        self.auto_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            self.auto_frame, 
            text="🤖 Mode Otomatis", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 0))
        
        self.auto_switch = ctk.CTkSwitch(
            self.auto_frame, 
            text="", 
            command=self.toggle_auto_mode
        )
        self.auto_switch.pack(pady=(5, 10))
        
        # LED Location Control
        self.create_location_control_card(settings_frame, row=3)

    def create_led_toggle_card(self, parent, row):
        """Membuat card toggle LED yang terintegrasi dengan API"""
        card_frame = ctk.CTkFrame(parent, height=80, corner_radius=10)
        card_frame.grid(row=row, column=0, sticky="ew", padx=15, pady=5)
        card_frame.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card_frame,
            text="💡 LED Ruangan",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(15, 5))

        # LED switch dengan loading state
        self.led_switch = ctk.CTkSwitch(
            card_frame, 
            text="", 
            command=self.handle_led_toggle
        )
        self.led_switch.pack(pady=(0, 15))

        return self.led_switch

    def create_led_stats_card(self, parent, row):
        """Membuat mini card untuk LED stats"""
        card_frame = ctk.CTkFrame(parent, height=60, corner_radius=10)
        card_frame.grid(row=row, column=0, sticky="ew", padx=15, pady=5)
        card_frame.grid_propagate(False)
        
        self.led_stats_label = ctk.CTkLabel(
            card_frame,
            text="📊 LED: Loading...",
            font=ctk.CTkFont(size=12)
        )
        self.led_stats_label.pack(expand=True)
        
        return card_frame

    def create_location_control_card(self, parent, row):
        """Card untuk kontrol LED berdasarkan lokasi"""
        card_frame = ctk.CTkFrame(parent, height=100, corner_radius=10)
        card_frame.grid(row=row, column=0, sticky="ew", padx=15, pady=5)
        card_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            card_frame,
            text="🏠 Kontrol Lokasi",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        button_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # All ON button
        all_on_btn = ctk.CTkButton(
            button_frame,
            text="🟢 All ON",
            height=25,
            font=ctk.CTkFont(size=11),
            command=lambda: self.control_all_leds_in_location(True)
        )
        all_on_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # All OFF button
        all_off_btn = ctk.CTkButton(
            button_frame,
            text="🔴 All OFF",
            height=25,
            font=ctk.CTkFont(size=11),
            command=lambda: self.control_all_leds_in_location(False)
        )
        all_off_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def create_sensor_card(self, parent, title, value, status, status_color, row, value_attr=None, status_attr=None):
        """Membuat card sensor dengan design yang konsisten"""
        card_frame = ctk.CTkFrame(parent, height=100, corner_radius=10)
        card_frame.grid(row=row, column=0, sticky="ew", padx=15, pady=5)
        card_frame.grid_propagate(False)
        card_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            card_frame, 
            text=title, 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(10, 0))
        
        value_label = ctk.CTkLabel(
            card_frame, 
            text=value, 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        value_label.grid(row=1, column=0, pady=(0, 0))
        
        status_label = ctk.CTkLabel(
            card_frame, 
            text=f"● {status}", 
            font=ctk.CTkFont(size=12),
            text_color=status_color
        )
        status_label.grid(row=2, column=0, pady=(0, 10))
        
        if value_attr:
            setattr(self, value_attr, value_label)
        if status_attr:
            setattr(self, status_attr, status_label)
        
        return value_label

    def create_toggle_card(self, parent, title, row, icon):
        """Membuat card toggle dengan desain yang konsisten"""
        card_frame = ctk.CTkFrame(parent, height=80, corner_radius=10)
        card_frame.grid(row=row, column=0, sticky="ew", padx=15, pady=5)
        card_frame.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(15, 5))

        switch = ctk.CTkSwitch(card_frame, text="")
        switch.pack(pady=(0, 15))
        switch.configure(command=lambda: self.safe_device_toggle(title, switch))

        return switch

    def create_fan_card(self, parent, row):
        """Membuat card kontrol fan dengan design yang lebih baik"""
        card_frame = ctk.CTkFrame(parent, height=120, corner_radius=10)
        card_frame.grid(row=row, column=0, sticky="ew", padx=15, pady=5)
        card_frame.grid_propagate(False)
        
        title_label = ctk.CTkLabel(
            card_frame, 
            text="🌀 Kipas Angin", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        control_container = ctk.CTkFrame(card_frame, fg_color="transparent")
        control_container.pack(pady=(0, 10), padx=10, fill="x")
        control_container.grid_columnconfigure(1, weight=1)
        
        minus_btn = ctk.CTkButton(
            control_container, 
            text="−", 
            width=30, 
            height=30,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.decrease_fan
        )
        minus_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.fan_slider = ctk.CTkSlider(
            control_container, 
            from_=0, 
            to=100, 
            number_of_steps=100, 
            command=self.update_fan_label,
            height=20
        )
        self.fan_slider.grid(row=0, column=1, sticky="ew", padx=5)
        self.fan_slider.set(0)
        
        plus_btn = ctk.CTkButton(
            control_container, 
            text="+", 
            width=30, 
            height=30,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.increase_fan
        )
        plus_btn.grid(row=0, column=2, padx=(5, 0))
        
        self.fan_value_label = ctk.CTkLabel(
            card_frame, 
            text="0%", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.fan_value_label.pack()
        
        return card_frame

    # ========================================
    # API INTEGRATION METHODS FOR LED CONTROL
    # ========================================

    def handle_led_toggle(self):
        """Handle LED toggle dengan API call"""
        if not hasattr(self, 'led_switch'):
            return
            
        try:
            state = self.led_switch.get()
            device_id = self.led_devices.get(self.current_room)
            
            if not device_id:
                print(f"[ERROR] No LED device mapped for room: {self.current_room}")
                return
            
            # Disable switch during API call
            self.led_switch.configure(state="disabled")
            
            # Run API call in thread to avoid blocking UI
            threading.Thread(
                target=self.control_led_api, 
                args=(device_id, state),
                daemon=True
            ).start()
            
        except Exception as e:
            print(f"[ERROR] LED toggle failed: {e}")
            if hasattr(self, 'led_switch'):
                self.led_switch.configure(state="normal")

    def control_led_api(self, device_id, state):
        """Control LED via API call"""
        try:
            # First, try to get current LED to see if it exists
            response = requests.get(
                f"{self.api_base_url}/led/{device_id}", 
                timeout=5
            )
            
            if response.status_code == 404:
                # LED doesn't exist, create it first
                self.create_led_device(device_id, state)
            else:
                # LED exists, control it
                self.update_led_state(device_id, state)
                
        except Exception as e:
            print(f"[ERROR] LED API control failed: {e}")
            # Re-enable switch and reset state on error
            self.after(0, lambda: self.reset_led_switch_on_error())

    def create_led_device(self, device_id, state):
        """Create new LED device via API"""
        payload = {
            "device_id": device_id,
            "state": state,
            "location": self.current_room,
            "led_name": f"LED {self.current_room}",
            "notes": f"Created from Smart Home UI for {self.current_room}"
        }
        
        try:
            response = requests.post(
                f"{self.api_base_url}/led", 
                json=payload, 
                timeout=5
            )
            
            if response.status_code == 201:
                print(f"[API] LED {device_id} created successfully")
                self.after(0, lambda: self.on_led_control_success(device_id, state))
            else:
                print(f"[API ERROR] Failed to create LED: {response.status_code} - {response.text}")
                self.after(0, lambda: self.reset_led_switch_on_error())
                
        except Exception as e:
            print(f"[ERROR] Create LED API call failed: {e}")
            self.after(0, lambda: self.reset_led_switch_on_error())

    def update_led_state(self, device_id, state):
        """Update LED state via control API"""
        payload = {"state": state}
        
        try:
            response = requests.post(
                f"{self.api_base_url}/led/{device_id}/control", 
                json=payload, 
                timeout=5
            )
            
            if response.status_code == 200:
                action = "ON" if state else "OFF"
                print(f"[API] LED {device_id} turned {action}")
                self.after(0, lambda: self.on_led_control_success(device_id, state))
            else:
                print(f"[API ERROR] Failed to control LED: {response.status_code} - {response.text}")
                self.after(0, lambda: self.reset_led_switch_on_error())
                
        except Exception as e:
            print(f"[ERROR] Control LED API call failed: {e}")
            self.after(0, lambda: self.reset_led_switch_on_error())

    def control_all_leds_in_location(self, state):
        """Control all LEDs in current location"""
        try:
            payload = {"state": state}
            response = requests.post(
                f"{self.api_base_url}/led/location/{self.current_room}/control",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                affected_count = data.get('affected_count', 0)
                action = "ON" if state else "OFF"
                print(f"[API] {affected_count} LEDs in {self.current_room} turned {action}")
                
                # Update UI switch if controlling current room
                if hasattr(self, 'led_switch'):
                    if state:
                        self.after(0, lambda: self.led_switch.select())
                    else:
                        self.after(0, lambda: self.led_switch.deselect())
                    self.after(0, lambda: self.led_switch.configure(state="normal"))
                
                # Update LED stats
                self.after(100, self.fetch_led_states)
                
            else:
                print(f"[API ERROR] Failed to control location LEDs: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] Location LED control failed: {e}")

    def on_led_control_success(self, device_id, state):
        """Handle successful LED control"""
        # Update local LED state tracking
        self.led_states[device_id] = state
        
        # Re-enable switch
        if hasattr(self, 'led_switch'):
            self.led_switch.configure(state="normal")
        
        # Update LED stats display
        self.update_led_stats_display()
        
        # Optional: Show success feedback
        action = "ON" if state else "OFF"
        status_text = f"✅ LED {action}"
        if hasattr(self, 'led_stats_label'):
            self.led_stats_label.configure(text=status_text)
            # Reset to normal stats after 2 seconds
            self.after(2000, self.update_led_stats_display)

    def reset_led_switch_on_error(self):
        """Reset LED switch state on API error"""
        if hasattr(self, 'led_switch'):
            # Revert switch state
            current_state = self.led_switch.get()
            if current_state:
                self.led_switch.deselect()
            else:
                self.led_switch.select()
            self.led_switch.configure(state="normal")
            
        if hasattr(self, 'led_stats_label'):
            self.led_stats_label.configure(text="❌ Koneksi Error")

    def fetch_led_states(self):
        """Fetch current LED states from API"""
        try:
            threading.Thread(target=self.fetch_led_states_async, daemon=True).start()
        except Exception as e:
            print(f"[ERROR] Failed to start LED fetch thread: {e}")

    def fetch_led_states_async(self):
        """Async method to fetch LED states"""
        try:
            # Get all LEDs
            response = requests.get(f"{self.api_base_url}/led", timeout=5)
            
            if response.status_code == 200:
                leds_data = response.json()
                
                # Handle both list and dict responses
                if isinstance(leds_data, dict):
                    # If response is wrapped in a data field
                    if 'data' in leds_data:
                        leds_list = leds_data['data']
                    else:
                        leds_list = [leds_data]  # Single LED object
                else:
                    leds_list = leds_data  # Already a list
                
                # Update local LED states
                for led in leds_list:
                    if isinstance(led, dict):
                        device_id = led.get('device_id')
                        state = led.get('state', False)
                        if device_id:
                            self.led_states[device_id] = state
                
                # Update UI on main thread
                self.after(0, lambda: self.update_led_ui_from_api(leds_list))
                
            else:
                print(f"[API ERROR] Failed to fetch LED states: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] Fetch LED states failed: {e}")

    def update_led_ui_from_api(self, leds_data):
        """Update LED UI based on API data"""
        # Update current room LED switch
        current_device_id = self.led_devices.get(self.current_room)
        if current_device_id and hasattr(self, 'led_switch'):
            current_led_state = self.led_states.get(current_device_id, False)
            if current_led_state:
                self.led_switch.select()
            else:
                self.led_switch.deselect()
        
        # Update LED stats
        self.update_led_stats_display()

    def update_led_switch_for_room(self, room_name):
        """Update LED switch state when room changes"""
        device_id = self.led_devices.get(room_name)
        if device_id and hasattr(self, 'led_switch'):
            current_state = self.led_states.get(device_id, False)
            if current_state:
                self.led_switch.select()
            else:
                self.led_switch.deselect()

    def update_led_stats_display(self):
        """Update LED statistics display"""
        if not hasattr(self, 'led_stats_label'):
            return
            
        try:
            total_leds = len(self.led_states)
            active_leds = sum(1 for state in self.led_states.values() if state)
            
            if total_leds > 0:
                stats_text = f"💡 {active_leds}/{total_leds} LED ON"
            else:
                stats_text = "💡 No LEDs found"
                
            self.led_stats_label.configure(text=stats_text)
            
        except Exception as e:
            print(f"[ERROR] Update LED stats failed: {e}")
            self.led_stats_label.configure(text="💡 Stats Error")

    # ========================================
    # DHT11 SENSOR DATA INTEGRATION
    # ========================================

    def fetch_and_update_sensor_data(self):
        """Fetch sensor data from API and update UI"""
        try:
            threading.Thread(target=self.fetch_sensor_data_async, daemon=True).start()
        except Exception as e:
            print(f"[ERROR] Failed to start sensor fetch thread: {e}")

    def fetch_sensor_data_async(self):
        """Async method to fetch sensor data"""
        # Map rooms to sensor device IDs
        sensor_devices = {
            "Kamar": "DHT11_KAMAR_001",
            "Dapur": "DHT11_DAPUR_001", 
            "Ruang Tamu": "DHT11_RUANGTAMU_001"
        }
        
        try:
            for room, device_id in sensor_devices.items():
                try:
                    response = requests.get(
                        f"{self.api_base_url}/dht11/latest/{device_id}", 
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        sensor_data = response.json()
                        
                        # Update UI on main thread
                        self.after(0, lambda r=room, d=sensor_data: self.update_sensor_ui(r, d))
                        
                    else:
                        print(f"[API] No sensor data for {device_id}: {response.status_code}")
                        
                except Exception as e:
                    print(f"[ERROR] Failed to fetch sensor data for {device_id}: {e}")
                    
        except Exception as e:
            print(f"[ERROR] Sensor data fetch failed: {e}")
        
        # Schedule next fetch in 30 seconds
        self.after(30000, self.fetch_and_update_sensor_data)

    def update_sensor_ui(self, room, sensor_data):
        """Update sensor UI with API data"""
        try:
            temperature = sensor_data.get('temperature', 0)
            humidity = sensor_data.get('humidity', 0)
            
            # Store sensor data for room switching
            if not hasattr(self, 'sensor_data_cache'):
                self.sensor_data_cache = {}
            
            self.sensor_data_cache[room] = {
                'temperature': temperature,
                'humidity': humidity,
                'temp_status': self.get_temp_status(temperature),
                'hum_status': self.get_humidity_status(humidity)
            }
            
            # Update UI if this is the current room
            if room == self.current_room:
                self.update_current_room_sensors(temperature, humidity)
                
        except Exception as e:
            print(f"[ERROR] Update sensor UI failed: {e}")

    def update_current_room_sensors(self, temperature, humidity):
        """Update sensor display for current room"""
        try:
            if hasattr(self, 'temp_value_label'):
                self.temp_value_label.configure(text=f"{temperature}°C")
                
            if hasattr(self, 'humidity_value_label'):
                self.humidity_value_label.configure(text=f"{humidity}%")
                
            if hasattr(self, 'temp_status_label'):
                temp_status = self.get_temp_status(temperature)
                temp_color = self.get_temp_color(temperature)
                self.temp_status_label.configure(
                    text=f"● {temp_status}",
                    text_color=temp_color
                )
                
            if hasattr(self, 'humidity_status_label'):
                hum_status = self.get_humidity_status(humidity)
                hum_color = self.get_humidity_color(humidity)
                self.humidity_status_label.configure(
                    text=f"● {hum_status}",
                    text_color=hum_color
                )
                
        except Exception as e:
            print(f"[ERROR] Update current room sensors failed: {e}")

    def get_temp_status(self, temp):
        """Get temperature status description"""
        if temp < 18:
            return "Dingin"
        elif temp < 25:
            return "Nyaman"
        elif temp < 30:
            return "Hangat"
        else:
            return "Panas"

    def get_temp_color(self, temp):
        """Get temperature status color"""
        if temp < 18:
            return "lightblue"
        elif temp < 25:
            return "green"
        elif temp < 30:
            return "orange"
        else:
            return "red"

    def get_humidity_status(self, humidity):
        """Get humidity status description"""
        if humidity < 30:
            return "Kering"
        elif humidity < 60:
            return "Optimal"
        elif humidity < 80:
            return "Tinggi"
        else:
            return "Sangat Tinggi"

    def get_humidity_color(self, humidity):
        """Get humidity status color"""
        if humidity < 30:
            return "orange"
        elif humidity < 60:
            return "green"
        elif humidity < 80:
            return "blue"
        else:
            return "red"

    # ========================================
    # SERVO MOTOR CONTROL INTEGRATION
    # ========================================

    def safe_device_toggle(self, device_name, switch):
        """Safe toggle for devices with error handling"""
        try:
            state = switch.get()
            
            if "Pintu" in device_name:
                self.control_servo_door(state, switch)
            else:
                print(f"[INFO] {device_name} toggled: {state}")
                
        except Exception as e:
            print(f"[ERROR] Device toggle failed for {device_name}: {e}")

    def control_servo_door(self, is_open, switch):
        """Control servo motor for door"""
        try:
            # Disable switch during operation
            switch.configure(state="disabled")
            
            # Map rooms to servo device IDs
            servo_devices = {
                "Kamar": "SERVO_KAMAR_001",
                "Dapur": "SERVO_DAPUR_001",
                "Ruang Tamu": "SERVO_RUANGTAMU_001"
            }
            
            device_id = servo_devices.get(self.current_room, "SERVO_DEFAULT_001")
            position = 90 if is_open else 0  # 90 degrees for open, 0 for closed
            
            # Run servo control in thread
            threading.Thread(
                target=self.control_servo_api,
                args=(device_id, position, switch),
                daemon=True
            ).start()
            
        except Exception as e:
            print(f"[ERROR] Servo control setup failed: {e}")
            switch.configure(state="normal")

    def control_servo_api(self, device_id, position, switch):
        """Control servo via API"""
        try:
            payload = {
                "device_id": device_id,
                "position": position,
                "location": self.current_room,
                "servo_name": f"Door Servo {self.current_room}",
                "notes": f"Door control for {self.current_room}"
            }
            
            # Use the control endpoint
            response = requests.post(
                f"{self.api_base_url}/servo/control",
                json=payload,
                timeout=10  # Servo operations might take longer
            )
            
            if response.status_code == 200:
                action = "opened" if position > 0 else "closed"
                print(f"[API] Door {action} successfully")
                
                # Re-enable switch on success
                self.after(0, lambda: switch.configure(state="normal"))
                
            else:
                print(f"[API ERROR] Servo control failed: {response.status_code} - {response.text}")
                self.after(0, lambda: self.reset_servo_switch(switch))
                
        except Exception as e:
            print(f"[ERROR] Servo API control failed: {e}")
            self.after(0, lambda: self.reset_servo_switch(switch))

    def reset_servo_switch(self, switch):
        """Reset servo switch on error"""
        try:
            current_state = switch.get()
            if current_state:
                switch.deselect()
            else:
                switch.select()
            switch.configure(state="normal")
        except Exception as e:
            print(f"[ERROR] Reset servo switch failed: {e}")

    # ========================================
    # FAN CONTROL AND OTHER UI METHODS
    # ========================================

    def update_fan_label(self, value):
        """Update fan speed label"""
        try:
            if hasattr(self, 'fan_value_label'):
                self.fan_value_label.configure(text=f"{int(value)}%")
        except Exception as e:
            print(f"[ERROR] Update fan label failed: {e}")

    def increase_fan(self):
        """Increase fan speed"""
        try:
            if hasattr(self, 'fan_slider'):
                current = self.fan_slider.get()
                new_value = min(100, current + 10)
                self.fan_slider.set(new_value)
                self.update_fan_label(new_value)
        except Exception as e:
            print(f"[ERROR] Increase fan failed: {e}")

    def decrease_fan(self):
        """Decrease fan speed"""
        try:
            if hasattr(self, 'fan_slider'):
                current = self.fan_slider.get()
                new_value = max(0, current - 10)
                self.fan_slider.set(new_value)
                self.update_fan_label(new_value)
        except Exception as e:
            print(f"[ERROR] Decrease fan failed: {e}")

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        try:
            current_mode = ctk.get_appearance_mode()
            
            if current_mode == "Dark":
                ctk.set_appearance_mode("light")
                self.theme_button.configure(text="☀️ Light Mode")
            else:
                ctk.set_appearance_mode("dark")
                self.theme_button.configure(text="🌙 Dark Mode")
                
        except Exception as e:
            print(f"[ERROR] Theme toggle failed: {e}")

    def toggle_auto_mode(self):
        """Toggle automatic mode"""
        try:
            if hasattr(self, 'auto_switch'):
                auto_enabled = self.auto_switch.get()
                mode_text = "Aktif" if auto_enabled else "Nonaktif"
                print(f"[INFO] Auto mode: {mode_text}")
                
                # Here you could add logic to enable/disable automatic sensor-based controls
                if auto_enabled:
                    self.start_auto_mode()
                else:
                    self.stop_auto_mode()
                    
        except Exception as e:
            print(f"[ERROR] Auto mode toggle failed: {e}")

    def start_auto_mode(self):
        """Start automatic control mode"""
        print("[INFO] Auto mode started - sensors will control devices automatically")
        # You can implement automatic LED/fan control based on sensor readings here
        
    def stop_auto_mode(self):
        """Stop automatic control mode"""
        print("[INFO] Auto mode stopped - manual control only")

    # ========================================
    # ROOM DATA UPDATE ENHANCED
    # ========================================

    def update_room_data(self, room_name):
        """Update dashboard data based on selected room - enhanced with API data"""
        try:
            # Use cached sensor data if available
            if hasattr(self, 'sensor_data_cache') and room_name in self.sensor_data_cache:
                data = self.sensor_data_cache[room_name]
                
                if hasattr(self, 'temp_value_label') and hasattr(self, 'humidity_value_label'):
                    self.temp_value_label.configure(text=f"{data['temperature']}°C")
                    self.humidity_value_label.configure(text=f"{data['humidity']}%")
                    self.temp_status_label.configure(
                        text=f"● {data['temp_status']}",
                        text_color=self.get_temp_color(data['temperature'])
                    )
                    self.humidity_status_label.configure(
                        text=f"● {data['hum_status']}",
                        text_color=self.get_humidity_color(data['humidity'])
                    )
            else:
                # Fallback to default data if no API data available
                room_data = {
                    "Kamar": {"temp": 23, "humidity": 55, "temp_status": "Nyaman", "hum_status": "Optimal"},
                    "Dapur": {"temp": 27, "humidity": 70, "temp_status": "Hangat", "hum_status": "Tinggi"},
                    "Ruang Tamu": {"temp": 25, "humidity": 60, "temp_status": "Normal", "hum_status": "Baik"}
                }
                
                data = room_data.get(room_name, room_data["Kamar"])
                
                if hasattr(self, 'temp_value_label') and hasattr(self, 'humidity_value_label'):
                    self.temp_value_label.configure(text=f"{data['temp']}°C")
                    self.humidity_value_label.configure(text=f"{data['humidity']}%")
                    self.temp_status_label.configure(text=f"● {data['temp_status']}")
                    self.humidity_status_label.configure(text=f"● {data['hum_status']}")
                    
        except Exception as e:
            print(f"[ERROR] Update room data failed: {e}")

    # ========================================
    # CLEANUP AND LIFECYCLE METHODS
    # ========================================

    def on_closing(self):
        """Handle application closing"""
        print("[INFO] Closing Smart Home Dashboard...")
        # Add any cleanup code here if needed
        
    def refresh_all_data(self):
        """Refresh all data from APIs"""
        try:
            print("[INFO] Refreshing all data...")
            self.fetch_and_update_sensor_data()
            self.fetch_led_states()
            
        except Exception as e:
            print(f"[ERROR] Refresh all data failed: {e}")

# ========================================
# ADDITIONAL UTILITY FUNCTIONS
# ========================================

def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%H:%M:%S")
    except:
        return "N/A"

def safe_api_call(func, *args, **kwargs):
    """Wrapper for safe API calls with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[ERROR] API call failed: {e}")
        return None