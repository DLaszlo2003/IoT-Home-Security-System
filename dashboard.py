import tkinter as tk
from tkinter import messagebox, Menu
import socket
import threading
import urllib.request
import datetime

SERVER_PORT = 5000
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

system_armed = False
connected_clients = []


class SecurityDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Central Security Command Center")
        self.root.geometry("700x500")

        # 1. LOGIN SCREEN
        self.login_frame = tk.Frame(root)
        self.build_login_screen()

        # 2. MAIN DASHBOARD
        self.main_frame = tk.Frame(root)
        self.build_dashboard()

        self.login_frame.pack(fill="both", expand=True)

    # --- GUI ---
    def build_login_screen(self):
        tk.Label(self.login_frame, text="SECURE SYSTEM LOGIN", font=("Arial", 20, "bold"), fg="#333").pack(pady=40)
        tk.Label(self.login_frame, text="Operator ID:").pack()
        self.entry_user = tk.Entry(self.login_frame);
        self.entry_user.pack(pady=5)
        tk.Label(self.login_frame, text="Password:").pack()
        self.entry_pass = tk.Entry(self.login_frame, show="*");
        self.entry_pass.pack(pady=5)
        tk.Button(self.login_frame, text="AUTHENTICATE", bg="#0052cc", fg="white", command=self.perform_login).pack(
            pady=20)

    def build_dashboard(self):
        menubar = Menu(self.root)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Log Off", command=self.logout)
        menubar.add_cascade(label="System", menu=file_menu)
        self.root.config(menu=menubar)


        btn_logout = tk.Button(self.main_frame, text="LOG OFF", font=("Arial", 10, "bold"),
                               bg="#d9534f", fg="white", command=self.logout)
        btn_logout.place(relx=0.12, rely=0.9, anchor="ne")

        # Status
        self.lbl_main_status = tk.Label(self.main_frame, text="SYSTEM DISARMED", font=("Arial", 28, "bold"), fg="white",
                                        bg="gray", width=20)
        self.lbl_main_status.pack(pady=40)

        # Arm/Disarm Button
        self.btn_toggle = tk.Button(self.main_frame, text="ARM SYSTEM", font=("Arial", 14), bg="green", fg="white",
                                    command=self.toggle_arm_state)
        self.btn_toggle.pack(pady=10)

        # Log
        tk.Label(self.main_frame, text="Real-time Event Log:", anchor="w").pack(fill="x", padx=20)
        self.listbox_log = tk.Listbox(self.main_frame, height=10)
        self.listbox_log.pack(fill="both", padx=20, pady=10)

        # Internet Status
        self.lbl_net_status = tk.Label(self.main_frame, text="Checking Internet...", anchor="e", fg="blue")
        self.lbl_net_status.pack(side="bottom", fill="x", padx=10)

    # --- ACTIONS ---
    def perform_login(self):
        if self.entry_user.get() == ADMIN_USER and self.entry_pass.get() == ADMIN_PASS:
            self.login_frame.pack_forget()
            self.main_frame.pack(fill="both", expand=True)
            self.log_event("Admin logged in.")
            threading.Thread(target=self.start_server, daemon=True).start()
            threading.Thread(target=self.check_internet, daemon=True).start()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    def logout(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.root.config(menu="")
        self.entry_pass.delete(0, tk.END)

    def toggle_arm_state(self):
        global system_armed
        system_armed = not system_armed

        if system_armed:
            self.lbl_main_status.config(text="SYSTEM ARMED", bg="green")
            self.btn_toggle.config(text="DISARM SYSTEM", bg="red")
            self.log_event("System Manual Override: ARMED")
        else:
            self.lbl_main_status.config(text="SYSTEM DISARMED", bg="gray")
            self.btn_toggle.config(text="ARM SYSTEM", bg="green")
            self.log_event("System Manual Override: DISARMED")
            self.broadcast_command("ALARM_CLEAR")

    def force_disarm(self):
        # Used by the keypad to force disarm
        global system_armed
        if system_armed:
            self.toggle_arm_state()

    def log_event(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.listbox_log.insert(tk.END, f"[{timestamp}] {message}")
        self.listbox_log.see(tk.END)

    def check_internet(self):
        try:
            urllib.request.urlopen('http://google.com', timeout=2)
            self.root.after(0, lambda: self.lbl_net_status.config(text="Cloud Uplink: ACTIVE", fg="green"))
        except:
            self.root.after(0, lambda: self.lbl_net_status.config(text="Cloud Uplink: OFFLINE", fg="red"))

    # --- NETWORKING ---
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', SERVER_PORT))
        server.listen(5)
        self.root.after(0, lambda: self.log_event(f"Server ready on port {SERVER_PORT}"))

        while True:
            client, addr = server.accept()
            connected_clients.append(client)
            self.root.after(0, lambda: self.log_event(f"Sensor connected: {addr}"))
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

    def handle_client(self, conn):
        global system_armed
        while True:
            try:
                raw_data = conn.recv(1024).decode('utf-8')
                if not raw_data: break

                messages = raw_data.split('\n')

                for data in messages:
                    data = data.strip()
                    if not data: continue

                    print(data)

                    # 1. ZONE DATA
                    if data.startswith("ZONE"):
                        parts = data.split(":")
                        zone = parts[1]
                        state = parts[2]

                        self.root.after(0, lambda z=zone, s=state: self.log_event(f"SENSOR: {z} -> {s}"))

                        if state == "OPEN" and system_armed:
                            self.root.after(0, self.trigger_alarm_gui)
                            self.broadcast_command("ALARM_TRIGGER")

                    # 2. KEYPAD: SUCCESS (Disarm)
                    elif data == "AUTH:SUCCESS":
                        self.root.after(0, lambda: self.log_event("KEYPAD: Valid PIN. Disarming..."))
                        self.root.after(0, self.force_disarm)
                        self.broadcast_command("ALARM_CLEAR")

                    # 3. KEYPAD: FAIL (Panic)
                    elif data == "AUTH:FAIL":
                        self.root.after(0, lambda: self.log_event("KEYPAD: !!! INVALID PIN !!!"))
                        self.root.after(0, self.trigger_alarm_gui)
                        self.broadcast_command("ALARM_TRIGGER")

            except ConnectionResetError:
                break

        if conn in connected_clients:
            connected_clients.remove(conn)

    def broadcast_command(self, cmd):
        for client in connected_clients:
            try:
                client.send(cmd.encode('utf-8'))
            except:
                pass

    def trigger_alarm_gui(self):
        self.lbl_main_status.config(text="!!! INTRUDER ALERT !!!", bg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityDashboard(root)
    root.mainloop()