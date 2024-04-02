import socket
from threading import Thread
from config.settings import load_config

class MUDConnection:
    def __init__(self, on_message=None):
        config = load_config()
        self.host = config.get('Network', 'host')
        self.port = config.getint('Network', 'port')
        self.quit_command = config.get('Network', 'quit_command')
        self.user = config.get('Credentials', 'USER')
        self.password = config.get('Credentials', 'PASS')
        self.on_message = on_message
        self.socket = None
        self.connected = False
        self.login_attempted = False  # Flag to ensure login happens only once

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.connected = True
        Thread(target=self.receive_data, daemon=True).start()

    def send(self, data):
        if self.connected:
            self.socket.sendall(f"{data}\r\n".encode())

    def receive_data(self):
        try:
            while self.connected:
                data = self.socket.recv(4096).decode('utf-8', errors='replace')
                if data and self.on_message:
                    self.on_message(data)
                # Check for the login trigger if login hasn't been attempted yet
                if not self.login_attempted and "Enter your name," in data:
                    self.login_attempted = True  # Prevent further login attempts
                    self.send(self.user)  # Send the username
                    self.send(self.password)  # Send the password
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False

    def close(self):
        if self.connected:
            self.send(self.quit_command)
            self.socket.close()
            self.connected = False