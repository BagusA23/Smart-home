# login_view.py

import customtkinter as ctk
import requests
import threading
from tkinter import messagebox

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.on_login_success = on_login_success
        
        # Konfigurasi grid untuk layout tengah yang responsif
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.is_loading = False
        
        self.build_ui()
    
    def build_ui(self):
        """Membangun komponen UI utama dalam sebuah kartu terpusat."""
        
        # Kartu login utama sebagai pusat dari semua elemen
        login_card = ctk.CTkFrame(
            self, 
            width=450,
            corner_radius=20, 
            border_width=1,
            border_color=("gray75", "gray25")
        )
        login_card.grid(row=0, column=0, sticky="") # Tidak sticky agar tetap di tengah
        
        login_card.grid_columnconfigure(0, weight=1)
        
        # --- Header ---
        header_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="ew")

        title = ctk.CTkLabel(header_frame, text="Selamat Datang!", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack()
        subtitle = ctk.CTkLabel(header_frame, text="Masuk untuk mengakses dasbor Anda", font=ctk.CTkFont(size=14), text_color=("gray50", "gray40"))
        subtitle.pack()
        
        # --- Form ---
        form_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        form_frame.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)

        self.username_entry = ctk.CTkEntry(form_frame, placeholder_text="Nama Pengguna", height=45, corner_radius=10)
        self.username_entry.grid(row=0, column=0, sticky="ew", pady=(5, 10))

        self.password_entry = ctk.CTkEntry(form_frame, placeholder_text="Kata Sandi", show="*", height=45, corner_radius=10)
        self.password_entry.grid(row=1, column=0, sticky="ew", pady=(5, 15))

        self.login_button = ctk.CTkButton(form_frame, text="Masuk", height=45, font=ctk.CTkFont(size=14, weight="bold"), corner_radius=10, command=self.handle_login)
        self.login_button.grid(row=2, column=0, sticky="ew")
        
        # --- Footer di dalam kartu ---
        footer_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        footer_frame.grid(row=2, column=0, padx=40, pady=(20, 30), sticky="ew")
        footer_frame.grid_columnconfigure(0, weight=1)

        self.remember_checkbox = ctk.CTkCheckBox(footer_frame, text="Ingat saya", font=ctk.CTkFont(size=12))
        self.remember_checkbox.grid(row=0, column=0, sticky="w")
        
        forgot_button = ctk.CTkButton(
            footer_frame, text="Lupa Kata Sandi?", font=ctk.CTkFont(size=12, underline=True),
            fg_color="transparent", hover=False, text_color=("gray50", "gray40"),
            command=self.handle_forgot_password
        )
        forgot_button.grid(row=0, column=1, sticky="e")

        # Bindings untuk tombol Enter
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
    
    def handle_login(self):
        """Menangani proses login dan validasi input."""
        if self.is_loading:
            return
            
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Gagal Masuk", "Nama pengguna dan kata sandi wajib diisi.")
            return
        
        self.set_loading_state(True)
        thread = threading.Thread(target=self.authenticate_user, args=(username, password), daemon=True)
        thread.start()
    
    def authenticate_user(self, username, password):
        """Mengautentikasi pengguna melalui API."""
        try:
            response = requests.post(
                "http://localhost:8080/login",
                json={"username": username, "password": password},
                timeout=10
            )
            self.parent.after(0, self.handle_auth_response, response)
        except requests.exceptions.Timeout:
            self.parent.after(0, self.handle_auth_error, "Koneksi timeout. Silakan coba lagi.")
        except requests.exceptions.ConnectionError:
            self.parent.after(0, self.handle_auth_error, "Tidak dapat terhubung ke server.")
        except requests.exceptions.RequestException as e:
            self.parent.after(0, self.handle_auth_error, f"Autentikasi gagal.\n{str(e)}")
    
    def handle_auth_response(self, response):
        """Menangani respons dari server setelah upaya login."""
        self.set_loading_state(False)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                messagebox.showinfo("Berhasil", "Login berhasil! Mengalihkan ke dasbor...")
                self.on_login_success(token)
            else:
                messagebox.showerror("Gagal Masuk", "Token autentikasi tidak ditemukan dari server.")
        else:
            messagebox.showerror("Gagal Masuk", "Nama pengguna atau kata sandi tidak valid.")
            self.password_entry.delete(0, 'end')
    
    def handle_auth_response(self, response):
        """Menangani respons dari server setelah upaya login."""
        self.set_loading_state(False)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            
            # --- TAMBAHKAN PRINT DI SINI ---
            print(f"1. [LoginView] Token diterima dari server: {token}") 
            
            if token:
                # ... (messagebox.showinfo) ...
                self.on_login_success(token)
    
    def handle_forgot_password(self):
        """Menampilkan pesan informasi untuk fitur lupa kata sandi."""
        messagebox.showinfo("Lupa Kata Sandi", "Silakan hubungi administrator sistem untuk mereset kata sandi Anda.")
    
    def set_loading_state(self, loading):
        """Mengatur status UI saat proses login sedang berjalan."""
        self.is_loading = loading
        state = "disabled" if loading else "normal"
        text = "Memproses..." if loading else "Masuk"
        
        self.login_button.configure(text=text, state=state)
        self.username_entry.configure(state=state)
        self.password_entry.configure(state=state)