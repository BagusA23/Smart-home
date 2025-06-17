import customtkinter as ctk
import requests
import threading
from tkinter import messagebox

# Set appearance theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LoginView(ctk.CTkScrollableFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        
        # Configure scrollable frame
        self.configure(fg_color="transparent")
        
        # Main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Configure grid for responsive layout
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=2)
        self.content_frame.grid_columnconfigure(2, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)
        
        # Loading state
        self.is_loading = False
        
        # Build UI components
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI components"""
        # Header section
        self.create_header()
        
        # Main login section
        self.create_login_section()
        
        # Footer section
        self.create_footer()
    
    def create_header(self):
        """Create header with branding"""
        header_frame = ctk.CTkFrame(self.content_frame, height=120, corner_radius=20)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 30))
        header_frame.grid_propagate(False)
        
        # Logo and title container
        logo_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_container.pack(expand=True, fill="both")
        
        # Logo icon
        logo_label = ctk.CTkLabel(
            logo_container,
            text="🏠",
            font=ctk.CTkFont(size=48)
        )
        logo_label.pack(pady=(20, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            logo_container,
            text="Smart Home System",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            logo_container,
            text="Secure Access to Your Connected Home",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        subtitle_label.pack(pady=(5, 0))
    
    def create_login_section(self):
        """Create main login form section"""
        # Left spacer
        left_spacer = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        left_spacer.grid(row=1, column=0, sticky="nsew")
        
        # Main login card
        login_card = ctk.CTkFrame(self.content_frame, corner_radius=25)
        login_card.grid(row=1, column=1, sticky="nsew", padx=20)
        
        # Configure login card grid
        login_card.grid_columnconfigure(0, weight=1)
        login_card.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)
        login_card.grid_rowconfigure(7, weight=1)
        
        # Card header
        self.create_card_header(login_card)
        
        # Login form
        self.create_login_form(login_card)
        
        # Alternative login options
        self.create_alternative_login(login_card)
        
        # Right spacer
        right_spacer = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        right_spacer.grid(row=1, column=2, sticky="nsew")
    
    def create_card_header(self, parent):
        """Create login card header"""
        header_container = ctk.CTkFrame(parent, fg_color="transparent", height=100)
        header_container.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        header_container.grid_propagate(False)
        
        # Welcome back text
        welcome_label = ctk.CTkLabel(
            header_container,
            text="Welcome Back!",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        welcome_label.pack(pady=(10, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_container,
            text="Sign in to access your smart home dashboard",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40")
        )
        subtitle_label.pack()
    
    def create_login_form(self, parent):
        """Create the login form"""
        form_container = ctk.CTkFrame(parent, fg_color="transparent")
        form_container.grid(row=1, column=0, sticky="ew", padx=40, pady=20)
        form_container.grid_columnconfigure(0, weight=1)
        
        # Username section
        username_label = ctk.CTkLabel(
            form_container,
            text="Username",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        username_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Enter your username",
            height=50,
            font=ctk.CTkFont(size=14),
            corner_radius=15
        )
        self.username_entry.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Password section
        password_label = ctk.CTkLabel(
            form_container,
            text="Password",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        password_label.grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Enter your password",
            show="*",
            height=50,
            font=ctk.CTkFont(size=14),
            corner_radius=15
        )
        self.password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        # Remember me and forgot password
        options_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        options_frame.grid(row=4, column=0, sticky="ew", pady=(0, 30))
        options_frame.grid_columnconfigure(1, weight=1)
        
        self.remember_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Remember me",
            font=ctk.CTkFont(size=12)
        )
        self.remember_checkbox.grid(row=0, column=0, sticky="w")
        
        forgot_button = ctk.CTkButton(
            options_frame,
            text="Forgot Password?",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color=("gray60", "gray40"),
            hover_color=("gray80", "gray30"),
            command=self.handle_forgot_password
        )
        forgot_button.grid(row=0, column=1, sticky="e")
        
        # Login button
        self.login_button = ctk.CTkButton(
            form_container,
            text="Sign In",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=15,
            command=self.handle_login
        )
        self.login_button.grid(row=5, column=0, sticky="ew", pady=(0, 20))
        
        # Bind Enter key
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
    
    def create_alternative_login(self, parent):
        """Create alternative login options"""
        alt_container = ctk.CTkFrame(parent, fg_color="transparent")
        alt_container.grid(row=2, column=0, sticky="ew", padx=40, pady=20)
        alt_container.grid_columnconfigure(0, weight=1)
        
        # Divider
        divider_frame = ctk.CTkFrame(alt_container, fg_color="transparent")
        divider_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        divider_frame.grid_columnconfigure((0, 2), weight=1)
        
        # Left line
        left_line = ctk.CTkFrame(divider_frame, height=1, fg_color=("gray70", "gray30"))
        left_line.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Or text
        or_label = ctk.CTkLabel(
            divider_frame,
            text="or",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        or_label.grid(row=0, column=1)
        
        # Right line
        right_line = ctk.CTkFrame(divider_frame, height=1, fg_color=("gray70", "gray30"))
        right_line.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        
        # Biometric login button
        biometric_button = ctk.CTkButton(
            alt_container,
            text="🔐 Use Biometric Login",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=15,
            fg_color=("gray80", "gray20"),
            hover_color=("gray70", "gray30"),
            command=self.handle_biometric_login
        )
        biometric_button.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Quick login options
        quick_login_frame = ctk.CTkFrame(alt_container, fg_color="transparent")
        quick_login_frame.grid(row=2, column=0, sticky="ew")
        quick_login_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Demo login button
        demo_button = ctk.CTkButton(
            quick_login_frame,
            text="🎯 Demo Login",
            height=40,
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            fg_color=("orange", "darkorange"),
            hover_color=("darkorange", "orange"),
            command=self.handle_demo_login
        )
        demo_button.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Guest access button
        guest_button = ctk.CTkButton(
            quick_login_frame,
            text="👤 Guest Access",
            height=40,
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            fg_color=("gray", "dimgray"),
            hover_color=("dimgray", "gray"),
            command=self.handle_guest_access
        )
        guest_button.grid(row=0, column=1, sticky="ew", padx=(10, 0))
    
    def create_footer(self):
        """Create footer section"""
        footer_frame = ctk.CTkFrame(self.content_frame, height=80, corner_radius=15)
        footer_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(30, 0))
        footer_frame.grid_propagate(False)
        
        # Footer content
        footer_content = ctk.CTkFrame(footer_frame, fg_color="transparent")
        footer_content.pack(expand=True, fill="both")
        
        # Copyright text
        copyright_label = ctk.CTkLabel(
            footer_content,
            text="© 2025 Smart Home System. All rights reserved.",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        copyright_label.pack(pady=(20, 5))
        
        # Version info
        version_label = ctk.CTkLabel(
            footer_content,
            text="Version 2.0.1 | Build 2025.06.14",
            font=ctk.CTkFont(size=10),
            text_color=("gray70", "gray50")
        )
        version_label.pack()
    
    def handle_login(self):
        """Handle login process"""
        if self.is_loading:
            return
            
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.show_error_dialog("Login Failed", "Username and password are required.")
            return
        
        # Start login process in background thread
        self.set_loading_state(True)
        thread = threading.Thread(target=self.authenticate_user, args=(username, password))
        thread.daemon = True
        thread.start()
    
    def authenticate_user(self, username, password):
        """Authenticate user with API"""
        try:
            response = requests.post(
                "http://localhost:8080/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            # Schedule UI update on main thread
            self.parent.after(0, lambda: self.handle_auth_response(response))
            
        except requests.exceptions.Timeout:
            self.parent.after(0, lambda: self.handle_auth_error("Connection timeout. Please try again."))
        except requests.exceptions.ConnectionError:
            self.parent.after(0, lambda: self.handle_auth_error("Cannot connect to server."))
        except requests.exceptions.RequestException as e:
            self.parent.after(0, lambda: self.handle_auth_error(f"Authentication failed.\n{str(e)}"))
    
    def handle_auth_response(self, response):
        """Handle authentication response"""
        self.set_loading_state(False)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            
            if token:
                self.show_success_dialog("Login successful! Redirecting to dashboard...")
                # Delay before calling success callback
                self.parent.after(1500, lambda: self.on_login_success(token))
            else:
                self.show_error_dialog("Login Failed", "Authentication token not found.")
        else:
            self.show_error_dialog("Login Failed", "Invalid username or password.")
    
    def handle_auth_error(self, error_message):
        """Handle authentication error"""
        self.set_loading_state(False)
        self.show_error_dialog("Connection Error", error_message)
        # Clear password field
        self.password_entry.delete(0, 'end')
    
    def handle_forgot_password(self):
        """Handle forgot password"""
        self.show_info_dialog("Forgot Password", "Please contact your system administrator to reset your password.")
    
    def handle_biometric_login(self):
        """Handle biometric login"""
        self.show_info_dialog("Biometric Login", "Biometric authentication is not yet implemented. Please use username and password.")
    
    def handle_demo_login(self):
        """Handle demo login"""
        self.username_entry.delete(0, 'end')
        self.username_entry.insert(0, "demo")
        self.password_entry.delete(0, 'end')
        self.password_entry.insert(0, "demo123")
        self.show_info_dialog("Demo Login", "Demo credentials have been filled in. Click 'Sign In' to continue.")
    
    def handle_guest_access(self):
        """Handle guest access"""
        self.show_info_dialog("Guest Access", "Guest access provides limited functionality. Some features may be restricted.")
        # Simulate guest login
        self.parent.after(1000, lambda: self.on_login_success("guest_token"))
    
    def set_loading_state(self, loading):
        """Set loading state for UI elements"""
        self.is_loading = loading
        
        if loading:
            self.login_button.configure(text="Signing In...", state="disabled")
            self.username_entry.configure(state="disabled")
            self.password_entry.configure(state="disabled")
        else:
            self.login_button.configure(text="Sign In", state="normal")
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
    
    def show_error_dialog(self, title, message):
        """Show error dialog"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Content
        content_frame = ctk.CTkFrame(dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Error icon
        error_label = ctk.CTkLabel(
            content_frame,
            text="⚠️",
            font=ctk.CTkFont(size=40)
        )
        error_label.pack(pady=(20, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=350
        )
        message_label.pack(pady=(0, 20))
        
        # OK button
        ok_button = ctk.CTkButton(
            content_frame,
            text="OK",
            command=dialog.destroy,
            width=100
        )
        ok_button.pack(pady=(0, 10))
        
        # Focus on OK button
        ok_button.focus()
    
    def show_success_dialog(self, message):
        """Show success dialog"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Success")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Content
        content_frame = ctk.CTkFrame(dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Success icon
        success_label = ctk.CTkLabel(
            content_frame,
            text="✅",
            font=ctk.CTkFont(size=40)
        )
        success_label.pack(pady=(20, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=300
        )
        message_label.pack(pady=(0, 20))
        
        # Auto close after 2 seconds
        dialog.after(2000, dialog.destroy)
    
    def show_info_dialog(self, title, message):
        """Show info dialog"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Content
        content_frame = ctk.CTkFrame(dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Info icon
        info_label = ctk.CTkLabel(
            content_frame,
            text="ℹ️",
            font=ctk.CTkFont(size=40)
        )
        info_label.pack(pady=(20, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=350
        )
        message_label.pack(pady=(0, 20))
        
        # OK button
        ok_button = ctk.CTkButton(
            content_frame,
            text="OK",
            command=dialog.destroy,
            width=100
        )
        ok_button.pack(pady=(0, 10))


def create_login_window():
    """Create desktop login window"""
    root = ctk.CTk()
    root.title("Smart Home Login")
    root.geometry("1000x700")
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1000 // 2)
    y = (root.winfo_screenheight() // 2) - (700 // 2)
    root.geometry(f"1000x700+{x}+{y}")
    
    def on_login_success(token):
        print(f"Login successful! Token: {token}")
        messagebox.showinfo("Success", "Redirecting to dashboard...")
        root.destroy()
    
    login_view = LoginView(root, on_login_success)
    login_view.pack(fill="both", expand=True)
    
    return root

# # Example usage
# if __name__ == "__main__":
#     app = create_login_window()
#     app.mainloop()