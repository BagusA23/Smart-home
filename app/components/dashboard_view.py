# File: components/dashboard_view.py

import customtkinter as ctk
from components.device_view import DeviceView
from components.led_control_view import LedControlView
from components.setting_view import SettingsView # Pastikan nama file ini benar
from components.admin_panel_view import AdminPanelView

class DashboardView(ctk.CTkFrame):
    # --- Hapus user_role dari init ---
    def __init__(self, parent, api_client, on_logout):
        super().__init__(parent, fg_color="transparent")
        self.api_client = api_client
        self.on_logout = on_logout
        self.user_is_admin = False # Properti baru untuk status admin
        self.current_view = None
        self.buttons = {} 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()

        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#F2F2F2", "#1B1B1B"))
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Tampilkan view default berdasarkan status admin
        if self.user_is_admin:
            self.show_view("admin_panel")
        else:
            self.show_view("dapur")

    def check_admin_access(self):
        """Memeriksa apakah pengguna adalah admin dengan mencoba mengakses endpoint admin."""
        # Panggil API untuk mendapatkan daftar user
        # Jika berhasil, berarti user adalah admin. Jika mengembalikan None, berarti bukan.
        users = self.api_client.get_all_users()
        self.user_is_admin = users is not None
        return self.user_is_admin

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        
        logo_label = ctk.CTkLabel(sidebar, text="🏠 Smart Home", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        button_props = {
            "anchor": "w", "corner_radius": 8, "height": 45, "border_spacing": 10,
            "font": ctk.CTkFont(size=14), "fg_color": "transparent",
            "text_color": ("gray10", "gray90"), "hover_color": ("gray70", "gray30")
        }
        
        # --- LOGIKA BARU UNTUK MEMBUAT TOMBOL ---
        row_num = 1
        
        # Cek hak akses sebelum membuat tombol admin
        if self.check_admin_access():
            self.buttons["admin_panel"] = ctk.CTkButton(sidebar, text="👑 Admin Panel", **button_props, command=lambda: self.show_view("admin_panel"))
            self.buttons["admin_panel"].grid(row=row_num, column=0, sticky="ew", padx=10)
            row_num += 1

        # Tombol-tombol lain tetap dibuat untuk semua user
        self.buttons["dapur"] = ctk.CTkButton(sidebar, text="📊 Dapur", **button_props, command=lambda: self.show_view("dapur"))
        self.buttons["dapur"].grid(row=row_num, column=0, sticky="ew", padx=10)
        row_num += 1
        
        # ... (tombol ruang tamu, kamar, led, settings, seperti sebelumnya) ...
        self.buttons["ruang_tamu"] = ctk.CTkButton(sidebar, text="🛋️ Ruang Tamu", **button_props, command=lambda: self.show_view("ruang_tamu"))
        self.buttons["ruang_tamu"].grid(row=row_num, column=0, sticky="ew", padx=10, pady=5)
        row_num += 1
        
        self.buttons["kamar"] = ctk.CTkButton(sidebar, text="🛏️ Kamar", **button_props, command=lambda: self.show_view("kamar"))
        self.buttons["kamar"].grid(row=row_num, column=0, sticky="ew", padx=10)
        row_num += 1
        
        self.buttons["led_control"] = ctk.CTkButton(sidebar, text="💡 Kontrol LED", **button_props, command=lambda: self.show_view("led_control"))
        self.buttons["led_control"].grid(row=row_num, column=0, sticky="ew", padx=10, pady=5)
        row_num += 1
        
        self.buttons["settings"] = ctk.CTkButton(sidebar, text="⚙️ Pengaturan", **button_props, command=lambda: self.show_view("settings"))
        self.buttons["settings"].grid(row=row_num, column=0, sticky="ew", padx=10)
        row_num += 1

        sidebar.grid_rowconfigure(row_num, weight=1)
        row_num += 1

        logout_button_props = button_props.copy()
        logout_button_props["hover_color"] = ("#c95151", "#a23e3e")
        logout_button = ctk.CTkButton(sidebar, text="🔒 Logout", command=self.on_logout, **logout_button_props)
        logout_button.grid(row=row_num, column=0, sticky="sew", padx=10, pady=(10,5))
        row_num += 1
        
        appearance_menu = ctk.CTkOptionMenu(sidebar, values=["Dark", "Light", "System"], command=ctk.set_appearance_mode, height=35, corner_radius=8)
        appearance_menu.grid(row=row_num, column=0, padx=10, pady=(0, 20), sticky="sew")


    def show_view(self, view_name):
        if self.current_view:
            self.current_view.destroy()
        
        for name, button in self.buttons.items():
            button.configure(fg_color="transparent")
        
        if view_name in self.buttons:
             self.buttons[view_name].configure(fg_color=("gray75", "gray25"))

        # --- Logika show_view tidak perlu tahu role lagi, hanya nama view ---
        if view_name == "admin_panel":
            self.current_view = AdminPanelView(self.content_frame, self.api_client)
        elif view_name in ["dapur", "ruang_tamu", "kamar"]:
            self.current_view = DeviceView(self.content_frame, view_name, self.api_client)
        elif view_name == "led_control":
            self.current_view = LedControlView(self.content_frame, self.api_client)
        elif view_name == "settings":
            self.current_view = SettingsView(self.content_frame, self.api_client)
        
        if self.current_view:
            self.current_view.grid(row=0, column=0, padx=25, pady=25, sticky="nsew")