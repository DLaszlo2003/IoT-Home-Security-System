import socket
import threading
import time
import tkinter as tk
from tkinter import messagebox

# CONFIGURATION
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000
VALID_PIN = "1234"


class SmartHomeSensor:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Hardware Interface")
        self.root.geometry("400x650")
        self.root.configure(bg="#f0f0f0")

        # HEADER
        tk.Label(root, text="HARDWARE SIMULATOR", font=("Arial", 14, "bold"), bg="#333", fg="white").pack(fill="x")
        self.lbl_status = tk.Label(root, text="Status: Connecting...", fg="orange", bg="#f0f0f0")
        self.lbl_status.pack(pady=5)

        # ZONES
        self.create_zone_frame("Zone 1: Front Door", "Front Door")
        self.create_zone_frame("Zone 2: Kitchen Window", "Kitchen Window")
        self.create_zone_frame("Zone 3: Garage Motion", "Garage")

        # KEYPAD
        self.build_keypad()

        # FEEDBACK
        self.lbl_feedback = tk.Label(root, text="No active commands", font=("Arial", 10), bg="white", relief="sunken",
                                     width=40)
        self.lbl_feedback.pack(side="bottom", pady=10)

        # NETWORK
        self.client = None
        self.connected = False
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def create_zone_frame(self, title, zone_id):
        frame = tk.LabelFrame(self.root, text=title, font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Button(frame, text="OPEN", bg="#ccffcc", width=15,
                  command=lambda: self.send_data(f"ZONE:{zone_id}:OPEN")).pack(side="left", padx=5)

        tk.Button(frame, text="CLOSE", bg="#ffcccc", width=15,
                  command=lambda: self.send_data(f"ZONE:{zone_id}:CLOSED")).pack(side="right", padx=5)

    def build_keypad(self):
        frame = tk.LabelFrame(self.root, text="Physical Security Panel", font=("Arial", 10, "bold"), bg="#ddd", padx=10,
                              pady=10)
        frame.pack(fill="x", padx=10, pady=15)

        tk.Label(frame, text="Enter PIN:", bg="#ddd").pack()
        self.pin_entry = tk.Entry(frame, show="*", justify="center", font=("Arial", 12))
        self.pin_entry.pack(pady=5)

        tk.Button(frame, text="SUBMIT CODE", bg="#007bff", fg="white", command=self.check_pin).pack(fill="x", pady=2)

    def check_pin(self):
        entered_pin = self.pin_entry.get()
        if entered_pin == VALID_PIN:
            print("Keypad: Code Correct -> Sending Disarm")
            self.send_data("AUTH:SUCCESS")
            messagebox.showinfo("Keypad", "Code Accepted. Disarm Signal Sent.")
        else:
            print("Keypad: Code Wrong -> Sending Panic")
            self.send_data("AUTH:FAIL")
            messagebox.showwarning("Keypad", "WRONG CODE! Alarm Triggered!")
        self.pin_entry.delete(0, tk.END)

    def connect_to_server(self):
        while True:
            if not self.connected:
                try:
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client.connect((SERVER_IP, SERVER_PORT))
                    self.connected = True
                    self.root.after(0, lambda: self.lbl_status.config(text="Status: CONNECTED", fg="green"))
                    threading.Thread(target=self.receive_commands, daemon=True).start()
                except:
                    self.root.after(0, lambda: self.lbl_status.config(text="Status: Searching...", fg="orange"))
            time.sleep(3)

    def send_data(self, msg):
        if self.connected and self.client:
            try:
                self.client.send((msg + "\n").encode('utf-8'))
                print(f"Sent: {msg}")
            except:
                self.connected = False
                print("Error sending data")

    def receive_commands(self):
        while self.connected:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if data:
                    print(f"Server Command: {data}")
                    if "ALARM_TRIGGER" in data:
                        self.root.after(0, lambda: self.root.configure(bg="red"))
                        self.root.after(0, lambda: self.lbl_feedback.config(text="!!! SIREN ACTIVATED !!!", bg="red",
                                                                            fg="white"))
                    elif "ALARM_CLEAR" in data:
                        self.root.after(0, lambda: self.root.configure(bg="#f0f0f0"))
                        self.root.after(0,
                                        lambda: self.lbl_feedback.config(text="System Normal", bg="white", fg="black"))
            except:
                self.connected = False
                break


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeSensor(root)
    root.mainloop()