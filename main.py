import customtkinter as ctk
from ui.login_view import LoginView
from ui.home_view import HomeView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Smart Home Desktop App")
        self.geometry("1000x700")  # Increased size for better display
        self.minsize(800, 600)     # Set minimum window size
        
        # Center window on screen
        self.center_window()
        
        # Configure grid weights for responsive layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # App state
        self.token = None
        self.active_frame = None
        
        # Show login initially
        self.show_login()

    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def clear_frame(self):
        """Clear the current active frame"""
        if self.active_frame:
            self.active_frame.destroy()
            self.active_frame = None

    def show_login(self):
        """Display the login view with optimal settings"""
        self.clear_frame()
        
        # Create login frame with full window coverage
        self.active_frame = LoginView(self, self.on_login_success)
        self.active_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure login frame to expand
        self.active_frame.grid_rowconfigure(0, weight=1)
        self.active_frame.grid_columnconfigure(0, weight=1)

    def show_home_view(self):
        """Display the home view with optimal settings"""
        self.clear_frame()
        
        # Create home frame with proper padding and expansion
        self.active_frame = HomeView(self)
        self.active_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Configure home frame to expand
        self.active_frame.grid_rowconfigure(0, weight=1)
        self.active_frame.grid_columnconfigure(0, weight=1)

    def on_login_success(self, token):
        """Handle successful login"""
        self.token = token
        print(f"Login successful! Token: {token[:10]}...")  # Log first 10 chars for debugging
        self.show_home_view()

    def get_token(self):
        """Get the current authentication token"""
        return self.token

    def logout(self):
        """Handle user logout"""
        self.token = None
        self.show_login()

if __name__ == "__main__":
    # Set CustomTkinter appearance and theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run the application
    app = App()
    app.mainloop()