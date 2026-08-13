import re
import threading
import time
from collections import deque
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import (
    Color,
    Line,
    RoundedRectangle,
    Ellipse
)
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget


# ============================================================
# CONFIGURATION
# ============================================================

APP_TITLE = "IoT Weather Monitor"

BAUD_RATE = 9600

MAX_GRAPH_POINTS = 60

HC05_UUID = "00001101-0000-1000-8000-00805F9B34FB"


# ============================================================
# COLORS
# ============================================================

BG = (0.043, 0.067, 0.090, 1)
CARD = (0.082, 0.114, 0.149, 1)
CARD2 = (0.106, 0.149, 0.196, 1)

TEXT = (1, 1, 1, 1)
MUTED = (0.60, 0.65, 0.71, 1)

ACCENT = (0.22, 0.74, 0.97, 1)
GREEN = (0.13, 0.77, 0.36, 1)
RED = (0.94, 0.27, 0.27, 1)
YELLOW = (0.98, 0.79, 0.08, 1)
PURPLE = (0.65, 0.55, 0.98, 1)


# ============================================================
# ROUNDED PANEL
# ============================================================

class RoundedPanel(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        with self.canvas.before:

            Color(*CARD)

            self.background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

    def update_background(self, *args):

        self.background.pos = self.pos
        self.background.size = self.size


# ============================================================
# ICON BADGE
# ============================================================

class IconBadge(Widget):

    def __init__(
        self,
        symbol="T",
        icon_color=ACCENT,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.symbol = symbol
        self.icon_color = icon_color

        self.size_hint = (None, None)
        self.size = (dp(42), dp(42))

        with self.canvas:

            Color(
                icon_color[0],
                icon_color[1],
                icon_color[2],
                0.16
            )

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )

            Color(*icon_color)

            self.border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(10)
                ),
                width=1.3
            )

        self.bind(
            pos=self.update_graphics,
            size=self.update_graphics
        )

    def update_graphics(self, *args):

        self.bg.pos = self.pos
        self.bg.size = self.size

        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(10)
        )

        self.canvas.after.clear()

        with self.canvas.after:

            Color(*self.icon_color)

            # Simple graphical icon instead of emoji
            if self.symbol == "T":

                # thermometer style
                Line(
                    points=[
                        self.center_x,
                        self.y + dp(11),
                        self.center_x,
                        self.y + dp(29)
                    ],
                    width=2.5
                )

                Ellipse(
                    pos=(
                        self.center_x - dp(7),
                        self.y + dp(5)
                    ),
                    size=(dp(14), dp(14))
                )

            elif self.symbol == "H":

                # droplet style
                Line(
                    points=[
                        self.center_x,
                        self.y + dp(7),
                        self.center_x - dp(8),
                        self.y + dp(20),
                        self.center_x,
                        self.y + dp(33),
                        self.center_x + dp(8),
                        self.y + dp(20),
                        self.center_x,
                        self.y + dp(7)
                    ],
                    width=2
                )

            elif self.symbol == "L":

                # light rays
                Ellipse(
                    pos=(
                        self.center_x - dp(7),
                        self.center_y - dp(7)
                    ),
                    size=(dp(14), dp(14))
                )

                for angle in range(0, 360, 45):

                    import math

                    a = math.radians(angle)

                    x1 = self.center_x + math.cos(a) * dp(11)
                    y1 = self.center_y + math.sin(a) * dp(11)

                    x2 = self.center_x + math.cos(a) * dp(16)
                    y2 = self.center_y + math.sin(a) * dp(16)

                    Line(
                        points=[x1, y1, x2, y2],
                        width=1.8
                    )

            elif self.symbol == "LX":

                # light bulb
                Ellipse(
                    pos=(
                        self.center_x - dp(8),
                        self.center_y - dp(9)
                    ),
                    size=(dp(16), dp(18))
                )

                Line(
                    points=[
                        self.center_x - dp(5),
                        self.center_y - dp(11),
                        self.center_x + dp(5),
                        self.center_y - dp(11)
                    ],
                    width=2
                )

            elif self.symbol == "E":

                # environment / cloud style
                Line(
                    points=[
                        self.x + dp(8),
                        self.center_y - dp(4),
                        self.x + dp(15),
                        self.center_y + dp(5),
                        self.x + dp(25),
                        self.center_y + dp(5),
                        self.x + dp(32),
                        self.center_y - dp(4),
                        self.x + dp(28),
                        self.center_y - dp(10),
                        self.x + dp(12),
                        self.center_y - dp(10),
                        self.x + dp(8),
                        self.center_y - dp(4)
                    ],
                    width=2
                )

            elif self.symbol == "S":

                # status lightning
                Line(
                    points=[
                        self.center_x + dp(4),
                        self.y + dp(34),
                        self.center_x - dp(7),
                        self.center_y,
                        self.center_x + dp(2),
                        self.center_y,
                        self.center_x - dp(5),
                        self.y + dp(7)
                    ],
                    width=2.5
                )


# ============================================================
# SENSOR CARD
# ============================================================

class SensorCard(RoundedPanel):

    def __init__(
        self,
        symbol,
        title,
        value="--",
        icon_color=ACCENT,
        **kwargs
    ):

        super().__init__(
            orientation="horizontal",
            padding=[dp(12), dp(10)],
            spacing=dp(10),
            **kwargs
        )

        self.size_hint_y = None
        self.height = dp(105)

        icon = IconBadge(
            symbol=symbol,
            icon_color=icon_color
        )

        self.add_widget(icon)

        text_box = BoxLayout(
            orientation="vertical",
            spacing=dp(2)
        )

        title_label = Label(
            text=title,
            color=MUTED,
            font_size=dp(11),
            bold=True,
            halign="left",
            valign="middle"
        )

        title_label.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        self.value_label = Label(
            text=value,
            color=TEXT,
            font_size=dp(21),
            bold=True,
            halign="left",
            valign="middle"
        )

        self.value_label.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        text_box.add_widget(title_label)
        text_box.add_widget(self.value_label)

        self.add_widget(text_box)

    def set_value(self, value):

        self.value_label.text = value


# ============================================================
# GRAPH
# ============================================================

class GraphWidget(Widget):

    def __init__(
        self,
        data,
        unit,
        graph_color=ACCENT,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.data = data
        self.unit = unit
        self.graph_color = graph_color

        self.bind(
            pos=self.redraw,
            size=self.redraw
        )

        Clock.schedule_interval(
            lambda dt: self.redraw(),
            0.5
        )

    def redraw(self, *args):

        self.canvas.clear()

        width = self.width
        height = self.height

        if width < dp(80) or height < dp(80):
            return

        left = dp(35)
        right = dp(10)
        top = dp(15)
        bottom = dp(25)

        graph_width = width - left - right
        graph_height = height - top - bottom

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        with self.canvas:

            Color(
                0.15,
                0.20,
                0.25,
                1
            )

            for i in range(5):

                y = (
                    self.y
                    + bottom
                    + graph_height * i / 4
                )

                Line(
                    points=[
                        self.x + left,
                        y,
                        self.x + width - right,
                        y
                    ],
                    width=0.7
                )

            for i in range(6):

                x = (
                    self.x
                    + left
                    + graph_width * i / 5
                )

                Line(
                    points=[
                        x,
                        self.y + bottom,
                        x,
                        self.y + height - top
                    ],
                    width=0.5
                )

        values = list(self.data)

        if len(values) < 2:

            return

        minimum = min(values)
        maximum = max(values)

        if minimum == maximum:

            minimum -= 1
            maximum += 1

        points = []

        count = len(values)

        for index, value in enumerate(values):

            x = (
                self.x
                + left
                + (
                    index / (count - 1)
                ) * graph_width
            )

            normalized = (
                value - minimum
            ) / (
                maximum - minimum
            )

            y = (
                self.y
                + bottom
                + normalized * graph_height
            )

            points.extend([x, y])

        with self.canvas:

            Color(*self.graph_color)

            Line(
                points=points,
                width=2.2,
                joint="round"
            )

            # latest point

            x = points[-2]
            y = points[-1]

            Ellipse(
                pos=(
                    x - dp(3),
                    y - dp(3)
                ),
                size=(
                    dp(6),
                    dp(6)
                )
            )


# ============================================================
# MAIN APP
# ============================================================

class WeatherApp(App):

    def build(self):

        self.title = APP_TITLE

        # ----------------------------------------------------
        # SENSOR DATA
        # ----------------------------------------------------

        self.temperature = None
        self.humidity = None
        self.light = None
        self.luminous_intensity = None
        self.day_night = "--"
        self.status = "--"

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
        # BLUETOOTH
        # ----------------------------------------------------

        self.bluetooth_socket = None
        self.connected = False
        self.stop_thread = False
        self.serial_thread = None

        # ----------------------------------------------------
        # ROOT
        # ----------------------------------------------------

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        # FIXED BACKGROUND
        with root.canvas.before:

            Color(*BG)

            self.bg = RoundedRectangle(
                pos=root.pos,
                size=root.size
            )

        root.bind(
            pos=self.update_bg,
            size=self.update_bg
        )

        self.root_widget = root

        # ----------------------------------------------------
        # SCROLL
        # ----------------------------------------------------

        scroll = ScrollView(
            do_scroll_x=False
        )

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        content.bind(
            minimum_height=content.setter(
                "height"
            )
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = BoxLayout(
            size_hint_y=None,
            height=dp(65)
        )

        title_box = BoxLayout(
            orientation="vertical"
        )

        title_box.add_widget(
            Label(
                text="IOT WEATHER MONITOR",
                font_size=dp(24),
                bold=True,
                color=TEXT,
                halign="left",
                valign="middle"
            )
        )

        self.clock_label = Label(
            text="",
            font_size=dp(11),
            color=MUTED,
            halign="left"
        )

        title_box.add_widget(
            self.clock_label
        )

        header.add_widget(title_box)

        self.connection_status = Label(
            text="● Bluetooth Disconnected",
            color=RED,
            font_size=dp(12),
            bold=True,
            halign="right",
            valign="middle"
        )

        header.add_widget(
            self.connection_status
        )

        content.add_widget(header)

        # ====================================================
        # BLUETOOTH PANEL
        # ====================================================

        bluetooth_panel = RoundedPanel(
            orientation="horizontal",
            padding=dp(10),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(60)
        )

        self.device_spinner = Spinner(
            text="Select Bluetooth Device",
            values=[],
            background_color=CARD2,
            color=TEXT,
            size_hint_x=0.45
        )

        bluetooth_panel.add_widget(
            self.device_spinner
        )

        refresh_button = Button(
            text="REFRESH",
            background_color=CARD2,
            color=TEXT,
            size_hint_x=0.18
        )

        refresh_button.bind(
            on_press=lambda x:
            self.refresh_bluetooth()
        )

        bluetooth_panel.add_widget(
            refresh_button
        )

        self.connect_button = Button(
            text="CONNECT",
            background_color=GREEN,
            color=TEXT,
            bold=True,
            size_hint_x=0.22
        )

        self.connect_button.bind(
            on_press=lambda x:
            self.toggle_bluetooth()
        )

        bluetooth_panel.add_widget(
            self.connect_button
        )

        content.add_widget(
            bluetooth_panel
        )

        # ====================================================
        # SENSOR CARDS
        # ====================================================

        cards = GridLayout(
            cols=3,
            spacing=dp(8),
            size_hint_y=None
        )

        cards.bind(
            minimum_height=cards.setter(
                "height"
            )
        )

        self.temperature_card = SensorCard(
            "T",
            "TEMPERATURE",
            "-- °C",
            ACCENT
        )

        self.humidity_card = SensorCard(
            "H",
            "HUMIDITY",
            "-- %",
            ACCENT
        )

        self.light_card = SensorCard(
            "L",
            "LIGHT LEVEL",
            "--",
            YELLOW
        )

        self.lux_card = SensorCard(
            "LX",
            "LUMINOUS INTENSITY",
            "-- lx",
            PURPLE
        )

        self.environment_card = SensorCard(
            "E",
            "DAY / NIGHT",
            "--",
            YELLOW
        )

        self.status_card = SensorCard(
            "S",
            "STATUS",
            "--",
            GREEN
        )

        cards.add_widget(
            self.temperature_card
        )

        cards.add_widget(
            self.humidity_card
        )

        cards.add_widget(
            self.light_card
        )

        cards.add_widget(
            self.lux_card
        )

        cards.add_widget(
            self.environment_card
        )

        cards.add_widget(
            self.status_card
        )

        content.add_widget(cards)

        # ====================================================
        # GRAPH TITLE
        # ====================================================

        content.add_widget(
            Label(
                text="LIVE SENSOR DATA",
                color=TEXT,
                font_size=dp(18),
                bold=True,
                size_hint_y=None,
                height=dp(38),
                halign="left"
            )
        )

        # ====================================================
        # THREE GRAPHS SIDE BY SIDE
        # ====================================================

        graphs = GridLayout(
            cols=3,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(245)
        )

        # ----------------------------------------------------
        # TEMPERATURE GRAPH
        # ----------------------------------------------------

        temp_column = BoxLayout(
            orientation="vertical",
            spacing=dp(5)
        )

        temp_column.add_widget(
            Label(
                text="Temperature",
                color=TEXT,
                font_size=dp(13),
                bold=True,
                size_hint_y=None,
                height=dp(25),
                halign="left"
            )
        )

        temp_panel = RoundedPanel()

        self.temperature_graph = GraphWidget(
            self.temperature_history,
            "C",
            ACCENT
        )

        temp_panel.add_widget(
            self.temperature_graph
        )

        temp_column.add_widget(
            temp_panel
        )

        graphs.add_widget(
            temp_column
        )

        # ----------------------------------------------------
        # HUMIDITY GRAPH
        # ----------------------------------------------------

        humidity_column = BoxLayout(
            orientation="vertical",
            spacing=dp(5)
        )

        humidity_column.add_widget(
            Label(
                text="Humidity",
                color=TEXT,
                font_size=dp(13),
                bold=True,
                size_hint_y=None,
                height=dp(25),
                halign="left"
            )
        )

        humidity_panel = RoundedPanel()

        self.humidity_graph = GraphWidget(
            self.humidity_history,
            "%",
            ACCENT
        )

        humidity_panel.add_widget(
            self.humidity_graph
        )

        humidity_column.add_widget(
            humidity_panel
        )

        graphs.add_widget(
            humidity_column
        )

        # ----------------------------------------------------
        # LIGHT GRAPH
        # ----------------------------------------------------

        light_column = BoxLayout(
            orientation="vertical",
            spacing=dp(5)
        )

        light_column.add_widget(
            Label(
                text="Light Level",
                color=TEXT,
                font_size=dp(13),
                bold=True,
                size_hint_y=None,
                height=dp(25),
                halign="left"
            )
        )

        light_panel = RoundedPanel()

        self.light_graph = GraphWidget(
            self.light_history,
            "ADC",
            YELLOW
        )

        light_panel.add_widget(
            self.light_graph
        )

        light_column.add_widget(
            light_panel
        )

        graphs.add_widget(
            light_column
        )

        content.add_widget(graphs)

        # ====================================================
        # CURRENT READINGS
        # ====================================================

        content.add_widget(
            Label(
                text="CURRENT READINGS",
                color=TEXT,
                font_size=dp(18),
                bold=True,
                size_hint_y=None,
                height=dp(40),
                halign="left"
            )
        )

        self.data_label = Label(
            text="Waiting for sensor data...",
            color=MUTED,
            font_size=dp(12),
            size_hint_y=None,
            height=dp(55),
            halign="left",
            valign="middle"
        )

        self.data_label.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        content.add_widget(
            self.data_label
        )

        # ====================================================
        # CONTROLS
        # ====================================================

        controls = RoundedPanel(
            orientation="horizontal",
            padding=dp(10),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(60)
        )

        refresh = Button(
            text="REFRESH BLUETOOTH",
            background_color=CARD2,
            color=TEXT
        )

        refresh.bind(
            on_press=lambda x:
            self.refresh_bluetooth()
        )

        controls.add_widget(refresh)

        disconnect = Button(
            text="DISCONNECT",
            background_color=RED,
            color=TEXT
        )

        disconnect.bind(
            on_press=lambda x:
            self.disconnect()
        )

        controls.add_widget(disconnect)

        content.add_widget(controls)

        # ====================================================
        # FOOTER
        # ====================================================

        content.add_widget(
            Label(
                text="Arduino  ->  HC-05  ->  Android  ->  IoT Weather Monitor",
                color=ACCENT,
                font_size=dp(11),
                size_hint_y=None,
                height=dp(40)
            )
        )

        scroll.add_widget(content)

        root.add_widget(scroll)

        # ====================================================
        # CLOCK
        # ====================================================

        Clock.schedule_interval(
            self.update_clock,
            1
        )

        # ====================================================
        # BLUETOOTH REFRESH
        # ====================================================

        Clock.schedule_once(
            lambda dt:
            self.refresh_bluetooth(),
            1
        )

        return root

    # ========================================================
    # BACKGROUND
    # ========================================================

    def update_bg(self, *args):

        self.bg.pos = self.root_widget.pos
        self.bg.size = self.root_widget.size

    # ========================================================
    # CLOCK
    # ========================================================

    def update_clock(self, dt=None):

        self.clock_label.text = datetime.now().strftime(
            "%d %b %Y    %I:%M:%S %p"
        )

    # ========================================================
    # BLUETOOTH REFRESH
    # ========================================================

    def refresh_bluetooth(self):

        try:

            from jnius import autoclass

            BluetoothAdapter = autoclass(
                "android.bluetooth.BluetoothAdapter"
            )

            adapter = BluetoothAdapter.getDefaultAdapter()

            if adapter is None:

                self.device_spinner.text = (
                    "Bluetooth unavailable"
                )

                self.connection_status.text = (
                    "● Bluetooth unavailable"
                )

                self.connection_status.color = RED

                return

            if not adapter.isEnabled():

                self.device_spinner.text = (
                    "Turn Bluetooth ON"
                )

                self.connection_status.text = (
                    "● Turn Bluetooth ON"
                )

                self.connection_status.color = YELLOW

                return

            paired_devices = adapter.getBondedDevices()

            iterator = paired_devices.iterator()

            devices = []

            while iterator.hasNext():

                device = iterator.next()

                name = device.getName()

                address = device.getAddress()

                devices.append(
                    f"{name} | {address}"
                )

            if devices:

                self.device_spinner.values = devices

                hc05 = [
                    device
                    for device in devices
                    if "HC-05" in device.upper()
                ]

                if hc05:

                    self.device_spinner.text = hc05[0]

                else:

                    self.device_spinner.text = devices[0]

                self.connection_status.text = (
                    f"● {len(devices)} device(s) found"
                )

                self.connection_status.color = YELLOW

            else:

                self.device_spinner.values = []

                self.device_spinner.text = (
                    "No paired devices"
                )

                self.connection_status.text = (
                    "● No paired Bluetooth devices"
                )

                self.connection_status.color = RED

        except Exception as error:

            print(
                "Bluetooth refresh error:",
                error
            )

            self.device_spinner.text = (
                "Bluetooth unavailable on PC"
            )

            self.connection_status.text = (
                "● Android Bluetooth only"
            )

            self.connection_status.color = YELLOW

    # ========================================================
    # TOGGLE BLUETOOTH
    # ========================================================

    def toggle_bluetooth(self):

        if self.connected:

            self.disconnect()

        else:

            self.connect_bluetooth()

    # ========================================================
    # CONNECT BLUETOOTH
    # ========================================================

    def connect_bluetooth(self):

        selected = self.device_spinner.text

        if selected in (
            "Select Bluetooth Device",
            "No paired devices",
            "Bluetooth unavailable",
            "Turn Bluetooth ON",
            "Bluetooth error",
            "Bluetooth unavailable on PC"
        ):

            self.data_label.text = (
                "Please pair and select HC-05 first."
            )

            return

        match = re.search(
            r"([0-9A-F]{2}(?::[0-9A-F]{2}){5})",
            selected,
            re.IGNORECASE
        )

        if not match:

            self.data_label.text = (
                "Could not determine Bluetooth address."
            )

            return

        address = match.group(1)

        try:

            from jnius import autoclass

            BluetoothAdapter = autoclass(
                "android.bluetooth.BluetoothAdapter"
            )

            UUID = autoclass(
                "java.util.UUID"
            )

            adapter = BluetoothAdapter.getDefaultAdapter()

            device = adapter.getRemoteDevice(
                address
            )

            uuid = UUID.fromString(
                HC05_UUID
            )

            self.bluetooth_socket = (
                device.createRfcommSocketToServiceRecord(
                    uuid
                )
            )

            adapter.cancelDiscovery()

            self.data_label.text = (
                "Connecting to HC-05..."
            )

            self.bluetooth_socket.connect()

            self.connected = True
            self.stop_thread = False

            self.connect_button.text = (
                "DISCONNECT"
            )

            self.connect_button.background_color = RED

            device_name = selected.split(
                "|"
            )[0].strip()

            self.connection_status.text = (
                f"● Connected: {device_name}"
            )

            self.connection_status.color = GREEN

            self.data_label.text = (
                "✓ Receiving live sensor data..."
            )

            self.serial_thread = threading.Thread(
                target=self.read_bluetooth,
                daemon=True
            )

            self.serial_thread.start()

        except Exception as error:

            print(
                "Bluetooth connection error:",
                error
            )

            self.bluetooth_socket = None
            self.connected = False

            self.connection_status.text = (
                "● Connection failed"
            )

            self.connection_status.color = RED

            self.data_label.text = (
                f"Connection error: {error}"
            )

    # ========================================================
    # BLUETOOTH READER
    # ========================================================

    def read_bluetooth(self):

        buffer = ""

        stream = None

        try:

            stream = (
                self.bluetooth_socket
                .getInputStream()
            )

        except Exception as error:

            print(error)
            return

        while (
            self.connected
            and not self.stop_thread
        ):

            try:

                byte_value = stream.read()

                if byte_value == -1:

                    time.sleep(0.02)
                    continue

                char = chr(byte_value)

                if char in ("\n", "\r"):

                    if buffer.strip():

                        line = buffer.strip()

                        Clock.schedule_once(
                            lambda dt,
                            line=line:
                            self.process_data(line)
                        )

                    buffer = ""

                else:

                    buffer += char

            except Exception as error:

                print(
                    "Bluetooth read error:",
                    error
                )

                Clock.schedule_once(
                    lambda dt:
                    self.handle_connection_error()
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

                    self.temperature_card.set_value(
                        f"{number:.1f} °C"
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

                    self.humidity_card.set_value(
                        f"{number:.1f} %"
                    )

                    self.humidity_history.append(
                        number
                    )

            # ------------------------------------------------
            # LIGHT
            # ------------------------------------------------

            elif key == "light":

                number = self.extract_number(
                    value
                )

                if number is not None:

                    self.light = number

                    self.light_card.set_value(
                        f"{number:.0f}"
                    )

                    self.light_history.append(
                        number
                    )

            # ------------------------------------------------
            # LUX
            # ------------------------------------------------

            elif key in (
                "luminous intensity",
                "luminous",
                "lux"
            ):

                number = self.extract_number(
                    value
                )

                if number is not None:

                    self.luminous_intensity = number

                    self.lux_card.set_value(
                        f"{number:.0f} lx"
                    )

            # ------------------------------------------------
            # DAY / NIGHT
            # ------------------------------------------------

            elif key in (
                "day/night",
                "environment"
            ):

                self.day_night = value

                self.environment_card.set_value(
                    value.upper()
                )

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            elif key == "status":

                self.status = value

                self.status_card.set_value(
                    value.upper()
                )

            # ------------------------------------------------
            # UPDATE
            # ------------------------------------------------

            current_time = datetime.now().strftime(
                "%I:%M:%S %p"
            )

            self.data_label.text = (
                f"Live data updated at {current_time}\n"
                f"RX: {line}"
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
    # DISCONNECT
    # ========================================================

    def disconnect(self):

        self.stop_thread = True
        self.connected = False

        try:

            if self.bluetooth_socket:

                self.bluetooth_socket.close()

        except Exception:
            pass

        self.bluetooth_socket = None

        self.connect_button.text = (
            "CONNECT"
        )

        self.connect_button.background_color = GREEN

        self.connection_status.text = (
            "● Bluetooth Disconnected"
        )

        self.connection_status.color = RED

        self.data_label.text = (
            "Bluetooth disconnected"
        )

    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    def handle_connection_error(self):

        self.disconnect()

        self.connection_status.text = (
            "● Connection lost"
        )

        self.connection_status.color = RED

    # ========================================================
    # STOP
    # ========================================================

    def on_stop(self):

        self.disconnect()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    WeatherApp().run()