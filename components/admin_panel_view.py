# File: components/admin_panel_view.py

import customtkinter as ctk
from tkinter import messagebox

class AdminPanelView(ctk.CTkFrame):
    def __init__(self, parent, api_client):
        super().__init__(parent, fg_color="transparent")
        self.api_client = api_client
        self.user_widgets = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header_frame, text="Manajemen Pengguna", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header_frame, text="🔄 Refresh", width=100, command=self.load_users).grid(row=0, column=1, sticky="e")

        # Scrollable Frame untuk daftar user
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.load_users()

    def load_users(self):
        """Mengambil data user dari API dan membuat widgetnya."""
        # Hapus widget lama
        for widgets in self.user_widgets:
            widgets['frame'].destroy()
        self.user_widgets.clear()

        users = self.api_client.get_all_users()
        if not users:
            ctk.CTkLabel(self.scroll_frame, text="Tidak ada pengguna yang ditemukan.").pack()
            return

        # Buat header tabel
        self.create_table_header()

        # Buat baris untuk setiap pengguna
        for user in users:
            self.create_user_row(user)

    def create_table_header(self):
        header = ctk.CTkFrame(self.scroll_frame, fg_color=("gray85", "gray20"))
        header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        header.grid_columnconfigure((1, 2), weight=2)
        header.grid_columnconfigure(3, weight=1)
        header.grid_columnconfigure(4, weight=2)
        
        ctk.CTkLabel(header, text="ID", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkLabel(header, text="Username", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(header, text="Email", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkLabel(header, text="Role", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=5)
        ctk.CTkLabel(header, text="Aksi", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=10, pady=5, sticky="e")

    def create_user_row(self, user_data):
        user_id = user_data.get('id')
        row_frame = ctk.CTkFrame(self.scroll_frame, border_width=1, border_color=("gray80", "gray25"))
        row_frame.grid(row=len(self.user_widgets) + 1, column=0, sticky="ew", pady=2)
        row_frame.grid_columnconfigure((1, 2), weight=2)
        row_frame.grid_columnconfigure(3, weight=1)
        row_frame.grid_columnconfigure(4, weight=2)

        # Info Pengguna
        ctk.CTkLabel(row_frame, text=user_data.get('id')).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(row_frame, text=user_data.get('username')).grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(row_frame, text=user_data.get('email')).grid(row=0, column=2, padx=10, sticky="w")

        # Tombol Aksi
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=4, padx=10, pady=5, sticky="e")
        actions_frame.grid_columnconfigure(1, weight=1)

        # Dropdown untuk Role
        role_var = ctk.StringVar(value=user_data.get('role'))
        role_menu = ctk.CTkOptionMenu(
            row_frame,
            values=["user", "admin"],
            variable=role_var,
            width=120,
            command=lambda new_role, uid=user_id: self.update_role(uid, new_role)
        )
        role_menu.grid(row=0, column=3, padx=10)

        # Tombol Hapus
        delete_button = ctk.CTkButton(
            actions_frame, text="Hapus", width=80,
            fg_color="#D22B2B", hover_color="#AA2222",
            command=lambda uid=user_id: self.delete_user(uid)
        )
        delete_button.grid(row=0, column=0, padx=5)
        
        # Simpan referensi
        self.user_widgets.append({'id': user_id, 'frame': row_frame})

    def update_role(self, user_id, new_role):
        success = self.api_client.update_user_role(user_id, new_role)
        if success:
            messagebox.showinfo("Berhasil", f"Role untuk user ID {user_id} telah diubah menjadi {new_role}.")
        else:
            messagebox.showerror("Gagal", "Gagal mengubah role.")
        self.load_users() # Refresh list

    def delete_user(self, user_id):
        # Minta konfirmasi sebelum menghapus
        answer = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus pengguna dengan ID {user_id}? Tindakan ini tidak dapat dibatalkan."
        )
        if answer:
            success = self.api_client.delete_user(user_id)
            if success:
                self.load_users() # Refresh list jika berhasil