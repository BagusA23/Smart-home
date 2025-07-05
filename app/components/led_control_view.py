# components/led_control_view.py
import customtkinter as ctk

class LedControlView(ctk.CTkFrame):
    def __init__(self, parent, api_client):
        super().__init__(parent, fg_color="transparent")
        self.api_client = api_client
        
        # Konfigurasi grid untuk konten
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Agar frame kartu bisa expand
        
        self._create_widgets()
        self.load_leds()

    def _create_widgets(self):
        """Membangun widget utama di dalam frame."""
        self.title_label = ctk.CTkLabel(self, text="💡 Kontrol Lampu LED", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Gunakan ScrollableFrame untuk menangani banyak LED
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) # 4 kolom kartu

    def load_leds(self):
        """Memuat status LED dari API dan membuat kartu kontrol."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        states = self.api_client.get_all_led_states() #
        
        if not states:
            ctk.CTkLabel(self.scrollable_frame, text="Tidak ada LED yang terdaftar di server.", font=ctk.CTkFont(size=14)).grid(row=0, column=0, columnspan=4, pady=20)
            return

        for i, state in enumerate(states):
            row = i // 4
            col = i % 4
            self.create_led_card(state['pin'], state['state'], row, col)

    def create_led_card(self, pin, current_state, row, col):
        """Membuat satu kartu untuk mengontrol satu LED."""
        card = ctk.CTkFrame(self.scrollable_frame, corner_radius=15, border_width=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1) # Agar tombol menempel di bawah

        # Header Kartu (Nama dan Pin)
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header_frame, text=f"Lampu Pin {pin}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w")
        
        # Status Label
        status_text = f"Status: {current_state.title()}" #
        status_color = "#33FF57" if current_state == "ON" else ("#FF5733" if current_state == "OFF" else "#33B5FF")
        status_label = ctk.CTkLabel(card, text=status_text, font=ctk.CTkFont(size=12), text_color=status_color)
        status_label.grid(row=1, column=0, padx=15, pady=5, sticky="w")
        
        # Tombol Kontrol
        new_state_to_set = "ON" if current_state == "OFF" else "OFF"
        button_text = "Nyalakan" if current_state == "OFF" else "Matikan"
        
        toggle_button = ctk.CTkButton(
            card,
            text=button_text,
            height=35,
            command=lambda p=pin, ns=new_state_to_set: self.change_led_state(p, ns)
        )
        toggle_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    def change_led_state(self, pin, new_state):
        """Mengirim perintah perubahan status LED dan memuat ulang UI."""
        print(f"Mengubah status LED pin {pin} menjadi {new_state}")
        result = self.api_client.set_led_state(pin, new_state) #
        if result:
            self.load_leds() # Muat ulang semua kartu untuk merefleksikan perubahan