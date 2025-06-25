import requests
import json
from tkinter import messagebox

class ApiClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.token = None

    def set_token(self, token):
        """Menyimpan token JWT setelah login berhasil."""
        self.token = token

    def _get_headers(self):
        """Mempersiapkan header untuk request yang memerlukan otentikasi."""
        # --- TAMBAHKAN PRINT DI SINI ---
        print(f"3. [ApiClient] Mempersiapkan header dengan token: {self.token}")
        
        if not self.token:
            # Ini seharusnya tidak terjadi dalam alur normal setelah login
            raise Exception("Token otentikasi tidak ditemukan.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _handle_request_error(self, response, success_code=200):
        """Menangani respons HTTP yang tidak berhasil."""
        if response.status_code != success_code:
            try:
                error_data = response.json()
                message = error_data.get("error", "Terjadi kesalahan yang tidak diketahui")
            except json.JSONDecodeError:
                message = f"Gagal memproses respons dari server (Status: {response.status_code})."
            
            messagebox.showerror("Error API", message)
            return None
        return response.json()

    def get_device_readings(self, device_id, limit=1):
        """Mengambil pembacaan sensor terakhir dari perangkat tertentu."""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.base_url}/api/devices/{device_id}?limit={limit}",
                headers=headers,
                timeout=5
            )
            # Mengharapkan array, bahkan untuk limit=1
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return [] # Mengembalikan array kosong jika tidak ada data
            else:
                self._handle_request_error(response)
                return None

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error Koneksi", f"Tidak dapat terhubung ke server: {e}")
            return None

    def set_fan_override(self, device_id, override_status):
        """Mengatur mode override kipas untuk perangkat."""
        try:
            headers = self._get_headers()
            payload = {"override": override_status}
            response = requests.post(
                f"{self.base_url}/api/devices/{device_id}/fan-override",
                json=payload,
                headers=headers,
                timeout=5
            )
            return self._handle_request_error(response)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error Koneksi", f"Tidak dapat mengubah mode kipas: {e}")
            return None

    def get_all_led_states(self):
        """Mengambil status semua LED dari endpoint publik."""
        try:
            # Endpoint ini bersifat publik sesuai dengan route.go
            response = requests.get(f"{self.base_url}/leds/states", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                self._handle_request_error(response)
                return []
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error Koneksi", f"Tidak dapat mengambil status LED: {e}")
            return []

    def set_led_state(self, pin, state):
        """Mengatur status LED tertentu."""
        try:
            headers = self._get_headers()
            payload = {"state": state} # State harus "ON", "OFF", atau "BLINKING"
            response = requests.post(
                f"{self.base_url}/api/leds/{pin}/state",
                json=payload,
                headers=headers,
                timeout=5
            )
            return self._handle_request_error(response)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error Koneksi", f"Tidak dapat mengubah status LED: {e}")
            return None
        
    def update_password(self, old_password, new_password):
        """Mengirim permintaan untuk mengubah password pengguna."""
        try:
            headers = self._get_headers()
            payload = {
                "old_password": old_password,
                "new_password": new_password
            }
            response = requests.put(
                f"{self.base_url}/api/user/password",
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                messagebox.showinfo("Berhasil", "Password berhasil diperbarui.")
                return True
            else:
                # Coba dapatkan pesan error dari server
                try:
                    error_msg = response.json().get("error", "Terjadi kesalahan.")
                except:
                    error_msg = f"Gagal memperbarui password (Status: {response.status_code})"
                messagebox.showerror("Gagal", error_msg)
                return False

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error Koneksi", f"Tidak dapat terhubung ke server: {e}")
            return False
        

    # File: components/api_client.py
# (Tambahkan metode-metode ini di dalam kelas ApiClient)

    def get_all_users(self):
        """Mengambil daftar semua pengguna. Mengembalikan None jika gagal atau tidak diizinkan."""
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.base_url}/api/admin/users", headers=headers, timeout=5)
            
            # Jika berhasil, kembalikan data JSON
            if response.status_code == 200:
                return response.json()
            # Jika dilarang (bukan admin), kembalikan None tanpa menampilkan error
            elif response.status_code == 403:
                print("Akses ditolak (bukan admin). Ini normal.")
                return None
            # Untuk error lainnya, tampilkan popup
            else:
                self._handle_request_error(response)
                return None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error Koneksi", f"Gagal mengambil data pengguna: {e}")
            return None

    def update_user_role(self, user_id, new_role):
        """Mengubah role pengguna tertentu. Memerlukan hak admin."""
        try:
            headers = self._get_headers()
            payload = {"role": new_role}
            response = requests.put(f"{self.base_url}/api/admin/users/{user_id}/role", json=payload, headers=headers, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error Koneksi", f"Gagal mengubah role: {e}")
            return False

    def delete_user(self, user_id):
        """Menghapus pengguna tertentu. Memerlukan hak admin."""
        try:
            headers = self._get_headers()
            response = requests.delete(f"{self.base_url}/api/admin/users/{user_id}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                messagebox.showinfo("Berhasil", "Pengguna berhasil dihapus.")
                return True
            else:
                # Coba dapatkan pesan error dari server
                try:
                    error_msg = response.json().get("error", "Terjadi kesalahan.")
                except:
                    error_msg = f"Gagal menghapus pengguna (Status: {response.status_code})"
                messagebox.showerror("Gagal", error_msg)
                return False

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error Koneksi", f"Gagal menghapus pengguna: {e}")
            return False