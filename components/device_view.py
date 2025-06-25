# components/device_view.py
import customtkinter as ctk

class DeviceView(ctk.CTkFrame):
    def __init__(self, parent, device_id, api_client):
        super().__init__(parent, fg_color="transparent")
        self.device_id = device_id
        self.api_client = api_client
        self.history_rows = []
        
        # Konfigurasi grid utama untuk layout yang seimbang dan responsif
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self._create_widgets()
        self.update_data()

    def _create_widgets(self):
        """Membangun semua widget di dalam frame."""
        # === Header ===
        self.title_label = ctk.CTkLabel(self, text=f"Status: {self.device_id.replace('_', ' ').title()}", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # === Area Kiri: Kartu Data & Kontrol ===
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 15))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.temp_card = self._create_data_card(cards_frame, "🌡️ Suhu", "N/A", 0, 0)
        self.humidity_card = self._create_data_card(cards_frame, "💧 Kelembapan", "N/A", 0, 1)
        self.door_card = self._create_data_card(cards_frame, "🚪 Pintu", "N/A", 0, 2)
        
        self.gas_card = self._create_data_card(cards_frame, "💨 Gas", "N/A", 1, 0)
        self.flame_card = self._create_data_card(cards_frame, "🔥 Api", "N/A", 1, 1)
        self.fan_status_card = self._create_data_card(cards_frame, "💨 Kipas", "N/A", 1, 2)

        self._create_fan_control_card(cards_frame, 2, 0)
        
        refresh_button = ctk.CTkButton(cards_frame, text="🔄 Refresh Data", command=self.update_data, height=40)
        refresh_button.grid(row=3, column=0, columnspan=3, pady=(15, 0), sticky="ew")

        # === Area Kanan: Tabel Riwayat ===
        history_frame = ctk.CTkFrame(self)
        history_frame.grid(row=1, column=1, sticky="nsew", padx=(15, 0))
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=1) 
        
        ctk.CTkLabel(history_frame, text="📋 Riwayat Terbaru", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        self.history_scrollable = ctk.CTkScrollableFrame(history_frame, fg_color="transparent")
        self.history_scrollable.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        self.history_scrollable.grid_columnconfigure(0, weight=3)
        self.history_scrollable.grid_columnconfigure(1, weight=2)
        self.history_scrollable.grid_columnconfigure(2, weight=2)
        self.history_scrollable.grid_columnconfigure(3, weight=2)
        self.history_scrollable.grid_columnconfigure(4, weight=2)
        self.history_scrollable.grid_columnconfigure(5, weight=2)
        
        headers = ["Waktu", "Suhu", "Lembap", "Pintu", "Gas", "Api"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.history_scrollable, text=header, font=ctk.CTkFont(size=12, weight="bold"), text_color=("gray10", "gray90"))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        ctk.CTkFrame(self.history_scrollable, height=1, fg_color=("gray80", "gray25")).grid(row=1, column=0, columnspan=6, sticky="ew", pady=(0, 5))

    def _create_data_card(self, parent, title, initial_value, row, col):
        """Membuat satu kartu untuk menampilkan data sensor."""
        card = ctk.CTkFrame(parent, corner_radius=12, height=120)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        card.grid_propagate(False)
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=15, pady=(10, 0), sticky="w")
        value_label = ctk.CTkLabel(card, text=initial_value, font=ctk.CTkFont(size=26, weight="bold"))
        value_label.grid(row=1, column=0, padx=15, pady=(0, 10))
        
        return value_label

    def _create_fan_control_card(self, parent, row, col):
        """Membuat kartu untuk kontrol kipas."""
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=row, column=col, columnspan=3, padx=5, pady=5, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(card, text="⚙️ Kontrol Kipas", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.fan_switch_var = ctk.StringVar(value="off")
        fan_switch = ctk.CTkSwitch(
            card, text="Otomatis / Manual", variable=self.fan_switch_var,
            onvalue="on", offvalue="off", command=self.toggle_fan_override
        )
        fan_switch.grid(row=0, column=1, padx=20, pady=15, sticky="e")
    
    def _populate_history(self):
        """Mengisi tabel riwayat dengan data dari API."""
        for row_widget_list in self.history_rows:
            for widget in row_widget_list:
                widget.destroy()
        self.history_rows.clear()
        
        data = self.api_client.get_device_readings(self.device_id, limit=15) or []
        
        for i, reading in enumerate(data):
            # --- PENYESUAIAN --- Menggunakan kunci 'created_at' dan 'door_status'
            timestamp_str = reading.get('created_at', 'N/A')
            if timestamp_str != 'N/A':
                timestamp_str = timestamp_str[:16].replace("T", " ")

            row_data = [
                timestamp_str,
                f"{reading.get('temperature', 0):.1f}°C",
                f"{reading.get('humidity', 0):.1f}%",
                reading.get('door_status', 'N/A'),
                "Terdeteksi" if reading.get('gas_value', -1) == 1 else "Aman",
                "Terdeteksi" if reading.get('flame_value', -1) == 0 else "Aman"
            ]
            row_widgets = []
            for j, cell_data in enumerate(row_data):
                cell = ctk.CTkLabel(self.history_scrollable, text=cell_data, font=ctk.CTkFont(size=12), anchor="w")
                cell.grid(row=i+2, column=j, padx=5, pady=3, sticky="w")
                if "Terdeteksi" in str(cell_data) or "OPEN" in str(cell_data):
                    cell.configure(text_color=("#B22222", "#FF6347"))
                row_widgets.append(cell)
            self.history_rows.append(row_widgets)

    def update_data(self):
        """Mengambil data terbaru dari API dan memperbarui semua elemen UI."""
        data = self.api_client.get_device_readings(self.device_id, limit=1)
        if data:
            latest = data[0]
            # Update kartu data
            self.temp_card.configure(text=f"{latest.get('temperature', 0):.1f}°C")
            self.humidity_card.configure(text=f"{latest.get('humidity', 0):.1f}%")
            
            # --- PENYESUAIAN --- Menggunakan kunci 'door_status'
            door = latest.get('door_status', 'N/A')
            self.door_card.configure(text=door)
            self.door_card.master.configure(fg_color=("#FFE5E5", "#8B0000") if door == "OPEN" else ("#FFFFFF", "#2B2B2B"))

            # Kode untuk gas dan api tetap menggunakan .get() agar tidak error jika tidak ada di JSON
            gas = latest.get('gas_value', -1)
            self.gas_card.configure(text="Terdeteksi" if gas == 1 else "Aman")
            self.gas_card.master.configure(fg_color=("#FFE5E5", "#8B0000") if gas == 1 else ("#FFFFFF", "#2B2B2B"))
            
            flame = latest.get('flame_value', -1)
            self.flame_card.configure(text="Terdeteksi" if flame == 0 else "Aman")
            self.flame_card.master.configure(fg_color=("#FFE5E5", "#8B0000") if flame == 0 else ("#FFFFFF", "#2B2B2B"))
            
            # --- PENYESUAIAN --- Menggunakan kunci 'fan_status'
            fan = latest.get('fan_status', 'N/A')
            self.fan_status_card.configure(text=fan.title())
        
        self._populate_history()
        self.after(30000, self.update_data)
        
    def toggle_fan_override(self):
        """Mengirim perintah override kipas ke API."""
        is_override = self.fan_switch_var.get() == "on"
        self.api_client.set_fan_override(self.device_id, is_override)