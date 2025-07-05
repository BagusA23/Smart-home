# File: components/settings_view.py

import customtkinter as ctk

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, api_client):
        super().__init__(parent, fg_color="transparent")
        self.api_client = api_client
        
        # Konfigurasi grid agar form berada di tengah
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        """Membangun widget untuk form ubah password."""
        
        # Frame pembungkus agar konten tidak menempel ke tepi
        main_frame = ctk.CTkFrame(self, width=500, height=400, corner_radius=15)
        main_frame.grid(row=0, column=0, sticky="")
        main_frame.grid_propagate(False)
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        title = ctk.CTkLabel(main_frame, text="Ubah Kata Sandi", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")
        
        # Form Entries
        self.old_password_entry = ctk.CTkEntry(main_frame, placeholder_text="Kata Sandi Lama", show="*", height=40)
        self.old_password_entry.grid(row=1, column=0, padx=30, pady=5, sticky="ew")

        self.new_password_entry = ctk.CTkEntry(main_frame, placeholder_text="Kata Sandi Baru", show="*", height=40)
        self.new_password_entry.grid(row=2, column=0, padx=30, pady=5, sticky="ew")
        
        self.confirm_password_entry = ctk.CTkEntry(main_frame, placeholder_text="Konfirmasi Kata Sandi Baru", show="*", height=40)
        self.confirm_password_entry.grid(row=3, column=0, padx=30, pady=5, sticky="ew")

        # Tombol Simpan
        self.save_button = ctk.CTkButton(main_frame, text="Simpan Perubahan", height=40, command=self.handle_save)
        self.save_button.grid(row=4, column=0, padx=30, pady=(20, 10), sticky="ew")

        # Label untuk menampilkan status (error atau sukses)
        self.status_label = ctk.CTkLabel(main_frame, text="", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=5, column=0, padx=30, pady=(0, 20), sticky="w")

    def handle_save(self):
        """Menangani validasi input dan memanggil API."""
        old_pass = self.old_password_entry.get()
        new_pass = self.new_password_entry.get()
        confirm_pass = self.confirm_password_entry.get()

        # Validasi Frontend
        if not all([old_pass, new_pass, confirm_pass]):
            self.status_label.configure(text="* Semua kolom harus diisi.", text_color="orange")
            return
        
        if new_pass != confirm_pass:
            self.status_label.configure(text="* Kata sandi baru tidak cocok.", text_color="orange")
            return

        # Panggil API
        success = self.api_client.update_password(old_pass, new_pass)

        if success:
            self.status_label.configure(text="✓ Berhasil disimpan!", text_color="lightgreen")
            # Kosongkan semua field setelah berhasil
            self.old_password_entry.delete(0, 'end')
            self.new_password_entry.delete(0, 'end')
            self.confirm_password_entry.delete(0, 'end')
        else:
             self.status_label.configure(text="* Gagal menyimpan. Periksa kembali input Anda.", text_color="orange")