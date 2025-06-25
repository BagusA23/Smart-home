# File: main.py

import customtkinter as ctk
# Hapus: import jwt
from login_view import LoginView
from components.dashboard_view import DashboardView
from components.api_client import ApiClient

# Hapus: JWT_SECRET_KEY

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart Home Control Panel V2")
        self.geometry("1280x768")
        self.minsize(1024, 700)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.api_client = ApiClient()
        self.current_frame = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.show_login_view()

    def show_login_view(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.login_view = LoginView(self, on_login_success=self.on_login_success)
        self.login_view.grid(row=0, column=0, sticky="nsew")
        self.current_frame = self.login_view

    def on_login_success(self, token):
        """Callback setelah login, sekarang jauh lebih sederhana."""
        print(f"2. [MainApp] Menerima token untuk di-set: {token}")
        self.api_client.set_token(token)
        print(f"Login berhasil! Token diterima.")
        print(f"Login berhasil! Token telah di-set di ApiClient.")

        if self.current_frame:
            self.current_frame.destroy()
            
        # --- TIDAK PERLU LAGI MENERUSKAN ROLE ---
        self.dashboard = DashboardView(
            self,
            api_client=self.api_client,
            on_logout=self.on_logout
        )
        self.dashboard.grid(row=0, column=0, sticky="nsew")
        self.current_frame = self.dashboard

    def on_logout(self):
        self.api_client.set_token(None)
        self.show_login_view()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()