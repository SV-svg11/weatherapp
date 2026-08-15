import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import re
from collections import deque
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

APP_TITLE = "IoT Weather Monitor"

BAUD_RATE = 9600

MAX_GRAPH_POINTS = 60

TEST_MODE = False


# ============================================================
# COLORS
# ============================================================

BG = "#0b1117"
CARD = "#151d26"
CARD2 = "#1b2632"

TEXT = "#ffffff"
MUTED = "#9aa7b5"

ACCENT = "#38bdf8"
GREEN = "#22c55e"
RED = "#ef4444"
YELLOW = "#facc15"
PURPLE = "#a78bfa"


# ============================================================
# MAIN APPLICATION
# ============================================================

class WeatherMonitor:

    def __init__(self, root):

        self.root = root

        self.root.title(APP_TITLE)

        self.root.geometry("1200x800")

        self.root.minsize(800, 650)

        self.root.configure(bg=BG)

        # ----------------------------------------------------
        # SERIAL
        # ----------------------------------------------------

        self.serial_connection = None

        self.connected = False

        self.stop_thread = False

        self.serial_thread = None

        # ----------------------------------------------------
        # SENSOR VALUES
        # ----------------------------------------------------

        self.temperature = None

        self.humidity = None

        self.light = None

        self.luminous_intensity = None

        self.day_night = "--"

        self.status = "--"

        self.last_update = "--"

        # ----------------------------------------------------
        # GRAPH DATA
        # ----------------------------------------------------

        self.temperature_history = deque(
            maxlen=MAX_GRAPH_POINTS
        )

        self.humidity_history = deque(
            maxlen=MAX_GRAPH_POINTS
        )

        self.light_history = deque(
            maxlen=MAX_GRAPH_POINTS
        )

        # ----------------------------------------------------
        # TEST VALUES
        # ----------------------------------------------------

        self.test_temperature = 30.0

        self.test_humidity = 55.0

        self.test_light = 200

        self.test_direction = 1

        # ----------------------------------------------------
        # CREATE UI
        # ----------------------------------------------------

        self.create_header()

        self.create_connection_panel()

        self.create_sensor_cards()

        self.create_graphs()

        self.create_bottom_status()

        self.refresh_ports()

        self.update_graphs()

        # ----------------------------------------------------
        # CLOSE EVENT
        # ----------------------------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

        # ----------------------------------------------------
        # TEST MODE
        # ----------------------------------------------------

        if TEST_MODE:

            self.run_test_mode()

    # ========================================================
    # HEADER
    # ========================================================

    def create_header(self):

        header = tk.Frame(
            self.root,
            bg=BG
        )

        header.pack(
            fill="x",
            padx=20,
            pady=(15, 5)
        )

        title = tk.Label(
            header,
            text="🌦  IoT WEATHER MONITOR",
            font=("Segoe UI", 24, "bold"),
            bg=BG,
            fg=TEXT
        )

        title.pack(
            side="left"
        )

        self.clock_label = tk.Label(
            header,
            text="",
            font=("Segoe UI", 11),
            bg=BG,
            fg=MUTED
        )

        self.clock_label.pack(
            side="right"
        )

        self.update_clock()

    # ========================================================
    # CLOCK
    # ========================================================

    def update_clock(self):

        current_time = datetime.now().strftime(
            "%d %b %Y   %I:%M:%S %p"
        )

        self.clock_label.config(
            text=current_time
        )

        self.root.after(
            1000,
            self.update_clock
        )

    # ========================================================
    # CONNECTION PANEL
    # ========================================================

    def create_connection_panel(self):

        panel = tk.Frame(
            self.root,
            bg=CARD,
            padx=12,
            pady=10
        )

        panel.pack(
            fill="x",
            padx=20,
            pady=8
        )

        tk.Label(
            panel,
            text="COM Port",
            font=("Segoe UI", 10, "bold"),
            bg=CARD,
            fg=TEXT
        ).pack(
            side="left",
            padx=(5, 8)
        )

        self.port_combo = ttk.Combobox(
            panel,
            width=35,
            state="readonly"
        )

        self.port_combo.pack(
            side="left",
            padx=5
        )

        refresh_button = tk.Button(
            panel,
            text="🔄 Refresh",
            command=self.refresh_ports,
            bg=CARD2,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground=TEXT,
            relief="flat",
            padx=12,
            pady=6
        )

        refresh_button.pack(
            side="left",
            padx=5
        )

        self.connect_button = tk.Button(
            panel,
            text="🔗 Connect",
            command=self.toggle_connection,
            bg=GREEN,
            fg="white",
            activebackground=GREEN,
            relief="flat",
            padx=15,
            pady=6,
            font=("Segoe UI", 10, "bold")
        )

        self.connect_button.pack(
            side="left",
            padx=5
        )

        self.connection_status = tk.Label(
            panel,
            text="● Disconnected",
            font=("Segoe UI", 10, "bold"),
            bg=CARD,
            fg=RED
        )

        self.connection_status.pack(
            side="right",
            padx=10
        )

    # ========================================================
    # SENSOR CARDS
    # ========================================================

    def create_sensor_cards(self):

        container = tk.Frame(
            self.root,
            bg=BG
        )

        container.pack(
            fill="x",
            padx=20,
            pady=8
        )

        for column in range(6):

            container.grid_columnconfigure(
                column,
                weight=1
            )

        self.temperature_card = self.create_sensor_card(
            container,
            "🌡",
            "TEMPERATURE",
            "-- °C",
            0
        )

        self.humidity_card = self.create_sensor_card(
            container,
            "💧",
            "HUMIDITY",
            "-- %",
            1
        )

        self.light_card = self.create_sensor_card(
            container,
            "☀",
            "LIGHT LEVEL",
            "--",
            2
        )

        self.lux_card = self.create_sensor_card(
            container,
            "💡",
            "ESTIMATED LUX",
            "-- lx",
            3
        )

        self.environment_card = self.create_sensor_card(
            container,
            "🌤",
            "ENVIRONMENT",
            "--",
            4
        )

        self.status_card = self.create_sensor_card(
            container,
            "⚡",
            "STATUS",
            "--",
            5
        )

    # ========================================================
    # CREATE SENSOR CARD
    # ========================================================

    def create_sensor_card(
        self,
        parent,
        icon,
        title,
        value,
        column
    ):

        card = tk.Frame(
            parent,
            bg=CARD,
            padx=12,
            pady=12
        )

        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=4
        )

        tk.Label(
            card,
            text=f"{icon}  {title}",
            font=("Segoe UI", 9, "bold"),
            bg=CARD,
            fg=MUTED
        ).pack(
            anchor="w"
        )

        value_label = tk.Label(
            card,
            text=value,
            font=("Segoe UI", 19, "bold"),
            bg=CARD,
            fg=TEXT
        )

        value_label.pack(
            anchor="w",
            pady=(8, 0)
        )

        return value_label

    # ========================================================
    # GRAPHS
    # ========================================================

    def create_graphs(self):

        graph_container = tk.Frame(
            self.root,
            bg=BG
        )

        graph_container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=8
        )

        graph_container.grid_columnconfigure(
            0,
            weight=1
        )

        graph_container.grid_columnconfigure(
            1,
            weight=1
        )

        graph_container.grid_columnconfigure(
            2,
            weight=1
        )

        graph_container.grid_rowconfigure(
            1,
            weight=1
        )

        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        tk.Label(
            graph_container,
            text="🌡 Temperature",
            font=("Segoe UI", 12, "bold"),
            bg=BG,
            fg=TEXT
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=5
        )

        self.temperature_canvas = tk.Canvas(
            graph_container,
            bg=CARD,
            highlightthickness=0
        )

        self.temperature_canvas.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=5,
            pady=5
        )

        # ----------------------------------------------------
        # HUMIDITY
        # ----------------------------------------------------

        tk.Label(
            graph_container,
            text="💧 Humidity",
            font=("Segoe UI", 12, "bold"),
            bg=BG,
            fg=TEXT
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=5
        )

        self.humidity_canvas = tk.Canvas(
            graph_container,
            bg=CARD,
            highlightthickness=0
        )

        self.humidity_canvas.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=5,
            pady=5
        )

        # ----------------------------------------------------
        # LIGHT
        # ----------------------------------------------------

        tk.Label(
            graph_container,
            text="☀ Light Level",
            font=("Segoe UI", 12, "bold"),
            bg=BG,
            fg=TEXT
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=5
        )

        self.light_canvas = tk.Canvas(
            graph_container,
            bg=CARD,
            highlightthickness=0
        )

        self.light_canvas.grid(
            row=1,
            column=2,
            sticky="nsew",
            padx=5,
            pady=5
        )

    # ========================================================
    # BOTTOM STATUS
    # ========================================================

    def create_bottom_status(self):

        bottom = tk.Frame(
            self.root,
            bg=BG
        )

        bottom.pack(
            fill="x",
            padx=20,
            pady=(5, 15)
        )

        self.update_label = tk.Label(
            bottom,
            text="Waiting for sensor data...",
            font=("Segoe UI", 10),
            bg=BG,
            fg=MUTED
        )

        self.update_label.pack(
            side="left"
        )

        self.data_label = tk.Label(
            bottom,
            text="Arduino → HC-05 → PC",
            font=("Segoe UI", 10),
            bg=BG,
            fg=ACCENT
        )

        self.data_label.pack(
            side="right"
        )

    # ========================================================
    # REFRESH PORTS
    # ========================================================

    def refresh_ports(self):

        ports = serial.tools.list_ports.comports()

        port_list = []

        for port in ports:

            description = port.description

            port_list.append(
                f"{port.device} - {description}"
            )

        self.port_combo["values"] = port_list

        if port_list:

            # Prefer COM port containing Bluetooth
            bluetooth_ports = [
                p for p in port_list
                if (
                    "bluetooth" in p.lower()
                    or "hc-05" in p.lower()
                    or "standard serial" in p.lower()
                )
            ]

            if bluetooth_ports:

                self.port_combo.set(
                    bluetooth_ports[0]
                )

            else:

                self.port_combo.current(0)

            self.connection_status.config(
                text=f"● {len(port_list)} COM port(s) found",
                fg=YELLOW
            )

        else:

            self.port_combo.set(
                "No COM ports found"
            )

            self.connection_status.config(
                text="● No COM ports found",
                fg=RED
            )

    # ========================================================
    # TOGGLE CONNECTION
    # ========================================================

    def toggle_connection(self):

        if self.connected:

            self.disconnect()

        else:

            self.connect()

    # ========================================================
    # CONNECT
    # ========================================================

    def connect(self):

        selected = self.port_combo.get()

        if (
            not selected
            or selected == "No COM ports found"
        ):

            messagebox.showwarning(
                "Connection",
                "Select a COM port first."
            )

            return

        match = re.search(
            r"(COM\d+)",
            selected,
            re.IGNORECASE
        )

        if not match:

            messagebox.showerror(
                "Connection",
                "Could not determine the COM port."
            )

            return

        port = match.group(1)

        try:

            self.serial_connection = serial.Serial(
                port=port,
                baudrate=BAUD_RATE,
                timeout=1
            )

            self.connected = True

            self.stop_thread = False

            self.connect_button.config(
                text="⛓ Disconnect",
                bg=RED
            )

            self.connection_status.config(
                text=f"● Connected: {port}",
                fg=GREEN
            )

            self.update_label.config(
                text="Receiving live sensor data..."
            )

            self.serial_thread = threading.Thread(
                target=self.read_serial,
                daemon=True
            )

            self.serial_thread.start()

        except Exception as error:

            self.serial_connection = None

            messagebox.showerror(
                "Connection Error",
                f"Could not connect to {port}.\n\n{error}"
            )

    # ========================================================
    # SERIAL READER
    # ========================================================

    def read_serial(self):

        while (
            self.connected
            and not self.stop_thread
        ):

            try:

                if (
                    self.serial_connection
                    and self.serial_connection.in_waiting
                ):

                    line = (
                        self.serial_connection
                        .readline()
                        .decode(
                            "utf-8",
                            errors="ignore"
                        )
                        .strip()
                    )

                    if line:

                        self.root.after(
                            0,
                            self.process_data,
                            line
                        )

                else:

                    time.sleep(0.02)

            except Exception as error:

                print(
                    "Serial error:",
                    error
                )

                self.root.after(
                    0,
                    self.handle_connection_error,
                    str(error)
                )

                break

    # ========================================================
    # PROCESS DATA
    # ========================================================

    def process_data(self, line):

        print(
            "Received:",
            line
        )

        self.data_label.config(
            text=f"RX: {line}"
        )

        try:

            if ":" not in line:

                return

            key, value = line.split(
                ":",
                1
            )

            key = key.strip().lower()

            value = value.strip()

            # ------------------------------------------------
            # TEMPERATURE
            # ------------------------------------------------

            if key == "temperature":

                number = self.extract_number(
                    value
                )

                if number is not None:

                    self.temperature = number

                    self.temperature_card.config(
                        text=f"{number:.1f} °C"
                    )

                    self.temperature_history.append(
                        number
                    )

            # ------------------------------------------------
            # HUMIDITY
            # ------------------------------------------------

            elif key == "humidity":

                number = self.extract_number(
                    value
                )

                if number is not None:

                    self.humidity = number

                    self.humidity_card.config(
                        text=f"{number:.1f} %"
                    )

                    self.humidity_history.append(
                        number
                    )

            # ------------------------------------------------
            # LIGHT ADC
            # ------------------------------------------------

            elif key == "light":

                number = self.extract_number(
                    value
                )

                if number is not None:

                    self.light = number

                    self.light_card.config(
                        text=f"{number:.0f}"
                    )

                    self.light_history.append(
                        number
                    )

            # ------------------------------------------------
            # LUMINOUS INTENSITY
            # ------------------------------------------------

            elif key in (
                "luminous intensity",
                "luminous"
            ):

                number = self.extract_number(
                    value
                )

                if number is not None:

                    self.luminous_intensity = number

                    self.lux_card.config(
                        text=f"{number:.0f} lx"
                    )

            # ------------------------------------------------
            # DAY / NIGHT
            # ------------------------------------------------

            elif key in (
                "day/night",
                "environment"
            ):

                self.day_night = value

                self.environment_card.config(
                    text=value
                )

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            elif key == "status":

                self.status = value

                self.status_card.config(
                    text=value
                )

            # ------------------------------------------------
            # TIME
            # ------------------------------------------------

            self.last_update = (
                datetime.now().strftime(
                    "%I:%M:%S %p"
                )
            )

            self.update_label.config(
                text=(
                    f"✓ Live data updated at "
                    f"{self.last_update}"
                )
            )

        except Exception as error:

            print(
                "Data processing error:",
                error
            )

    # ========================================================
    # EXTRACT NUMBER
    # ========================================================

    def extract_number(self, text):

        match = re.search(
            r"-?\d+(?:\.\d+)?",
            text
        )

        if match:

            try:

                return float(
                    match.group()
                )

            except ValueError:

                return None

        return None

    # ========================================================
    # UPDATE GRAPHS
    # ========================================================

    def update_graphs(self):

        self.draw_graph(
            self.temperature_canvas,
            self.temperature_history,
            "°C"
        )

        self.draw_graph(
            self.humidity_canvas,
            self.humidity_history,
            "%"
        )

        self.draw_graph(
            self.light_canvas,
            self.light_history,
            "ADC"
        )

        self.root.after(
            500,
            self.update_graphs
        )

    # ========================================================
    # DRAW GRAPH
    # ========================================================

    def draw_graph(
        self,
        canvas,
        data,
        unit
    ):

        canvas.delete("all")

        width = canvas.winfo_width()

        height = canvas.winfo_height()

        if width < 50 or height < 50:

            return

        left = 45

        right = 15

        top = 20

        bottom = 30

        graph_width = (
            width - left - right
        )

        graph_height = (
            height - top - bottom
        )

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        for i in range(5):

            y = (
                top
                + graph_height * i / 4
            )

            canvas.create_line(
                left,
                y,
                width - right,
                y,
                fill="#263442"
            )

        for i in range(6):

            x = (
                left
                + graph_width * i / 5
            )

            canvas.create_line(
                x,
                top,
                x,
                height - bottom,
                fill="#1e2a35"
            )

        if len(data) < 2:

            canvas.create_text(
                width / 2,
                height / 2,
                text="Waiting for data...",
                fill=MUTED,
                font=("Segoe UI", 10)
            )

            return

        values = list(data)

        minimum = min(values)

        maximum = max(values)

        if minimum == maximum:

            minimum -= 1

            maximum += 1

        # ----------------------------------------------------
        # Y SCALE
        # ----------------------------------------------------

        for i in range(5):

            value = (
                maximum
                - (
                    (maximum - minimum)
                    * i
                    / 4
                )
            )

            y = (
                top
                + graph_height * i / 4
            )

            canvas.create_text(
                5,
                y,
                anchor="w",
                text=f"{value:.0f}",
                fill=MUTED,
                font=("Segoe UI", 8)
            )

        # ----------------------------------------------------
        # GRAPH POINTS
        # ----------------------------------------------------

        points = []

        count = len(values)

        for index, value in enumerate(values):

            x = (
                left
                + (
                    index
                    / (count - 1)
                )
                * graph_width
            )

            normalized = (
                value - minimum
            ) / (
                maximum - minimum
            )

            y = (
                top
                + graph_height
                - normalized * graph_height
            )

            points.append(
                (x, y)
            )

        # ----------------------------------------------------
        # GRAPH LINE
        # ----------------------------------------------------

        for i in range(
            len(points) - 1
        ):

            x1, y1 = points[i]

            x2, y2 = points[i + 1]

            canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=ACCENT,
                width=3,
                smooth=True
            )

        # ----------------------------------------------------
        # POINTS
        # ----------------------------------------------------

        for x, y in points:

            canvas.create_oval(
                x - 2,
                y - 2,
                x + 2,
                y + 2,
                fill=ACCENT,
                outline=""
            )

        # ----------------------------------------------------
        # UNIT
        # ----------------------------------------------------

        canvas.create_text(
            width - right,
            top,
            anchor="ne",
            text=unit,
            fill=MUTED,
            font=("Segoe UI", 9)
        )

    # ========================================================
    # TEST MODE
    # ========================================================

    def run_test_mode(self):

        self.test_temperature += (
            0.2 * self.test_direction
        )

        self.test_humidity += (
            0.3 * self.test_direction
        )

        self.test_light += (
            10 * self.test_direction
        )

        if self.test_temperature >= 35:

            self.test_direction = -1

        if self.test_temperature <= 25:

            self.test_direction = 1

        test_data = [
            f"Temperature: {self.test_temperature:.1f} C",
            f"Humidity: {self.test_humidity:.1f} %",
            f"Light: {self.test_light}",
            f"Luminous Intensity: {self.test_light * 1.0:.0f} lux",
            "Day/Night: DAY",
            "Status: NORMAL"
        ]

        for line in test_data:

            self.process_data(line)

        self.root.after(
            1000,
            self.run_test_mode
        )

    # ========================================================
    # DISCONNECT
    # ========================================================

    def disconnect(self):

        self.stop_thread = True

        self.connected = False

        try:

            if self.serial_connection:

                self.serial_connection.close()

        except Exception:
            pass

        self.serial_connection = None

        self.connect_button.config(
            text="🔗 Connect",
            bg=GREEN
        )

        self.connection_status.config(
            text="● Disconnected",
            fg=RED
        )

        self.update_label.config(
            text="Bluetooth disconnected"
        )

    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    def handle_connection_error(
        self,
        error
    ):

        self.disconnect()

        print(
            "Connection error:",
            error
        )

        self.connection_status.config(
            text="● Connection lost",
            fg=RED
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def close_application(self):

        self.stop_thread = True

        self.connected = False

        try:

            if self.serial_connection:

                self.serial_connection.close()

        except Exception:
            pass

        self.root.destroy()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = WeatherMonitor(root)

    root.mainloop()