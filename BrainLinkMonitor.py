import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
from BrainLinkParser import BrainLinkParser # Parser Class from Main Repo: https://github.com/Macrotellect/BrainLinkParser-Python
import threading
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

class EEGMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("BrainLink EEG Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables for storing EEG values
        self.values = {
            'Signal': tk.StringVar(value="0"),
            'Attention': tk.StringVar(value="0"),
            'Meditation': tk.StringVar(value="0"),
            'Delta': tk.StringVar(value="0"),
            'Theta': tk.StringVar(value="0"),
            'LowAlpha': tk.StringVar(value="0"),
            'HighAlpha': tk.StringVar(value="0"),
            'LowBeta': tk.StringVar(value="0"),
            'HighBeta': tk.StringVar(value="0"),
            'LowGamma': tk.StringVar(value="0"),
            'HighGamma': tk.StringVar(value="0")
        }
        
        self.connected = False
        self.serial_port = None
        self.websocket = None
        self.ws_connected = False
        self.setup_ui()

    def setup_ui(self):
        # Create the notebook (tab view)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create the first tab
        self.eeg_setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.eeg_setup_tab, text="EEG Setup")

        # Main frame inside the first tab
        main_frame = ttk.Frame(self.eeg_setup_tab, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="BrainLink EEG Monitor",
            font=('Helvetica', 24, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="10")
        conn_frame.pack(fill=tk.X, pady=(0, 20))

        # Get available COM ports
        ports = [port.device for port in serial.tools.list_ports.comports()]

        # COM port selection
        self.port_var = tk.StringVar(value=ports[0] if ports else "")
        ttk.Label(conn_frame, text="COM Port:").pack(side=tk.LEFT, padx=5)
        self.port_combo = ttk.Combobox(
            conn_frame, 
            textvariable=self.port_var, 
            values=ports,
            width=15
        )
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        # Connect button
        self.connect_btn = ttk.Button(
            conn_frame, 
            text="Connect",
            command=self.toggle_connection
        )
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        # Values frame
        values_frame = ttk.LabelFrame(main_frame, text="EEG Values", padding="10")
        values_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create value displays
        for idx, (key, var) in enumerate(self.values.items()):
            frame = ttk.Frame(values_frame)
            frame.grid(row=idx//2, column=idx%2, padx=10, pady=5, sticky='nsew')
            
            ttk.Label(
                frame, 
                text=f"{key}:",
                font=('Helvetica', 12)
            ).pack(side=tk.LEFT)
            
            value_label = ttk.Label(
                frame, 
                textvariable=var,
                font=('Helvetica', 12, 'bold')
            )
            value_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Configure grid
        values_frame.grid_columnconfigure(0, weight=1)
        values_frame.grid_columnconfigure(1, weight=1)

        # Create the WebSocket tab
        self.websocket_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.websocket_tab, text="WebSocket")

        # WebSocket controls
        ws_frame = ttk.LabelFrame(self.websocket_tab, text="WebSocket Control", padding="10")
        ws_frame.pack(fill=tk.X, padx=10, pady=10)

        self.ws_status_label = ttk.Label(ws_frame, text="Disconnected")
        self.ws_status_label.pack()

    async def send_ws_data(self, data_str):
        await self.websocket.send_text(data_str)

    def run_fastapi(self):
        app = FastAPI()

        @app.websocket("/eeg")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.websocket = websocket
            self.ws_connected = True
            self.root.after(0, self.update_ws_status)
            try:
                while True:
                    await asyncio.sleep(0.1)
            except WebSocketDisconnect:
                self.ws_connected = False
                self.root.after(0, self.update_ws_status)

        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")

    def update_ws_status(self):
        if self.ws_connected:
            self.ws_status_label.config(text="Connected")
        else:
            self.ws_status_label.config(text="Disconnected")

    def read_serial(self):
        parser = BrainLinkParser(self.onEEG)
        while self.connected:
            try:
                data = self.serial_port.read(512)
                parser.parse(data)
            except Exception as e:
                self.connected = False
                self.connect_btn.config(text="Connect")
                messagebox.showerror("Error", f"Lost connection to device: {e}")
                break

    def toggle_connection(self):
        if not self.connected:
            try:
                self.serial_port = serial.Serial(self.port_var.get(), 115200, timeout=2)
                self.connected = True
                self.connect_btn.config(text="Disconnect")
                threading.Thread(target=self.read_serial, daemon=True).start()
            except Exception as e:
                messagebox.showerror("Error", f"Could not connect: {str(e)}")
        else:
            self.connected = False
            if self.serial_port:
                self.serial_port.close()
            self.connect_btn.config(text="Connect")

    def onEEG(self, data):
        self.values['Signal'].set(str(data.signal))
        self.values['Attention'].set(str(data.attention))
        self.values['Meditation'].set(str(data.meditation))
        self.values['Delta'].set(str(data.delta))
        self.values['Theta'].set(str(data.theta))
        self.values['LowAlpha'].set(str(data.lowAlpha))
        self.values['HighAlpha'].set(str(data.highAlpha))
        self.values['LowBeta'].set(str(data.lowBeta))
        self.values['HighBeta'].set(str(data.highBeta))
        self.values['LowGamma'].set(str(data.lowGamma))
        self.values['HighGamma'].set(str(data.highGamma))
        
        if self.websocket and self.ws_connected:
            try:
                eeg_data = {
                    'Signal': data.signal,
                    'Attention': data.attention,
                    'Meditation': data.meditation,
                    'Delta': data.delta,
                    'Theta': data.theta,
                    'LowAlpha': data.lowAlpha,
                    'HighAlpha': data.highAlpha,
                    'LowBeta': data.lowBeta,
                    'HighBeta': data.highBeta,
                    'LowGamma': data.lowGamma,
                    'HighGamma': data.highGamma
                }
                asyncio.run(self.send_ws_data(json.dumps(eeg_data)))
            except Exception as e:
                print(f"WebSocket send error: {str(e)}")
                self.ws_connected = False # Set connection status to false on error
                self.root.after(0, self.update_ws_status) # Update UI to reflect disconnection

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    app = EEGMonitor(root)
    threading.Thread(target=app.run_fastapi, daemon=True).start()
    root.mainloop()