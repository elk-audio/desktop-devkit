"""Main Qt window with hardcoded PCB layout controls."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QGroupBox,
    QGridLayout,
    QDial,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from .encoder import EncoderDial
import base64

from grpc_server import servicer
from grpc_server.servicer import PinProxyServicer


class MainWindow(QMainWindow):
    """Main application window with hardcoded PCB layout."""

    display_write_signal = Signal(str)
    led_update_signal = Signal(int, bool)

    def __init__(
        self, servicer: PinProxyServicer, host: str = "0.0.0.0", port: int = 50051
    ):
        super().__init__()
        self.servicer = servicer
        self.led_indicators = {}  # Dictionary to store LED indicators by ID

        # Connect signals
        self.display_write_signal.connect(self._on_display_write)
        self.led_update_signal.connect(self._on_led_update)

        self.setWindowTitle("Mock Events GUI - TOPO DevKit")
        self.setMinimumSize(1000, 900)  # Increased to accommodate larger dials

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Create UI sections matching PCB layout
        self._create_display_section(main_layout)
        self._create_red_led_section(main_layout)
        self._create_encoder_section(main_layout)
        self._create_potentiometer_section(main_layout)
        self._create_rgb_led_section(main_layout)
        self._create_switch_section(main_layout)
        self._create_rotary_section(main_layout)

        # Add status label
        self.status_label = QLabel(f"gRPC Server: {host}:{port}")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch()

        # Register callbacks with servicer
        self.servicer.set_display_update_callback(
            lambda msg: self.display_write_signal.emit(msg)
        )
        self.servicer.set_led_update_callback(
            lambda led_id, active: self.led_update_signal.emit(led_id, active)
        )

    def _create_display_section(self, parent_layout: QVBoxLayout):
        """Create OLED display section."""
        display_group = QGroupBox("OLED Display")
        display_layout = QVBoxLayout()
        display_group.setLayout(display_layout)

        self.display = QLabel()
        self.display.setStyleSheet("border: none; background-color: black;")
        #self.display.setFixedSize(128, 64)
        self.display.setFixedSize(256, 128)
        display_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_layout.addWidget(self.display, alignment=Qt.AlignmentFlag.AlignCenter)

        parent_layout.addWidget(display_group)

    def _create_red_led_section(self, parent_layout: QVBoxLayout):
        """Create section with 4 red LEDs."""
        led_group = QGroupBox("Red LEDs")
        led_group.setMaximumHeight(70)  # Keep LED section compact
        led_layout = QHBoxLayout()
        led_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins to prevent clipping
        led_layout.setSpacing(5)  # Reduce spacing between LEDs
        led_group.setLayout(led_layout)

        # Add 4 red LEDs (IDs 50-53)
        for i in range(4):
            led_id = 13 + i
            led_widget = self._create_led_indicator(led_id, f"LED{i + 1}", "red")
            led_layout.addWidget(led_widget)

        parent_layout.addWidget(led_group)

    def _create_encoder_section(self, parent_layout: QVBoxLayout):
        """Create encoder section with 4 encoders."""
        encoder_group = QGroupBox("Encoders")
        encoder_group.setMinimumHeight(150)  # Height for dial + label + switch button
        encoder_layout = QHBoxLayout()
        encoder_group.setLayout(encoder_layout)

        # Add all 4 encoders horizontally
        encoder_layout.addWidget(self._create_encoder_dial(33, "ENC1"))
        encoder_layout.addWidget(self._create_encoder_dial(34, "ENC2"))
        encoder_layout.addWidget(self._create_encoder_dial(35, "ENC3"))
        encoder_layout.addWidget(self._create_encoder_dial(36, "ENC4"))

        parent_layout.addWidget(encoder_group)

    def _create_potentiometer_section(self, parent_layout: QVBoxLayout):
        """Create potentiometer section (8 pots in 2x4 grid)."""
        pot_group = QGroupBox("Potentiometers")
        pot_group.setMinimumHeight(240)  # 2x encoder section height
        pot_layout = QGridLayout()
        pot_group.setLayout(pot_layout)

        # Row 0 (Top row on PCB)
        pot_layout.addWidget(self._create_pot(21, "POT1"), 0, 0)
        pot_layout.addWidget(self._create_pot(22, "POT2"), 0, 1)
        pot_layout.addWidget(self._create_pot(23, "POT3"), 0, 2)
        pot_layout.addWidget(self._create_pot(24, "POT4"), 0, 3)

        # Row 1 (Bottom row on PCB)
        pot_layout.addWidget(self._create_pot(25, "POT5"), 1, 0)
        pot_layout.addWidget(self._create_pot(26, "POT6"), 1, 1)
        pot_layout.addWidget(self._create_pot(27, "POT7"), 1, 2)
        pot_layout.addWidget(self._create_pot(28, "POT8"), 1, 3)

        parent_layout.addWidget(pot_group)

    def _create_rgb_led_section(self, parent_layout: QVBoxLayout):
        """Create section with 4 RGB LED placeholders."""
        led_group = QGroupBox("RGB LEDs (Placeholder)")
        led_group.setMaximumHeight(70)  # Keep LED section compact
        led_layout = QHBoxLayout()
        led_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins to prevent clipping
        led_layout.setSpacing(5)  # Reduce spacing between LEDs
        led_group.setLayout(led_layout)

        # Add 4 RGB LED placeholders
        for i in range(4):
            led_widget = self._create_rgb_led_placeholder(f"RGB{i + 1}")
            led_layout.addWidget(led_widget)

        parent_layout.addWidget(led_group)

    def _create_switch_section(self, parent_layout: QVBoxLayout):
        """Create switch section (4 switches)."""
        switch_group = QGroupBox("Switches")
        switch_layout = QHBoxLayout()
        switch_group.setLayout(switch_layout)

        switch_layout.addWidget(self._create_switch(17, "SW1"))
        switch_layout.addWidget(self._create_switch(18, "SW2"))
        switch_layout.addWidget(self._create_switch(19, "SW3"))
        switch_layout.addWidget(self._create_switch(20, "SW4"))

        parent_layout.addWidget(switch_group)

    def _create_rotary_section(self, parent_layout: QVBoxLayout):
        """Create rotary switch section (4-position)."""
        rotary_group = QGroupBox("Rotary Switch")
        rotary_layout = QHBoxLayout()
        rotary_group.setLayout(rotary_layout)

        rotary_layout.addWidget(QLabel("S1 (4-Position):"))
        rotary_layout.addWidget(self._create_rotary_switch(40, "S1"))

        parent_layout.addWidget(rotary_group)

    def _create_pot(self, controller_id: int, label: str) -> QWidget:
        """Create a potentiometer control (analog dial)."""
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Label
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_widget)

        # Dial for potentiometer (no wrapping - limited rotation)
        dial = QDial()
        dial.setMinimum(0)
        dial.setMaximum(100)  # 0.0-1.0 in 0.01 steps
        dial.setValue(0)
        dial.setWrapping(False)  # Limited rotation like a real pot
        dial.setNotchesVisible(True)
        dial.setMinimumSize(50, 50)  # Prevent shrinking on large screens

        # Value display
        value_label = QLabel("0.00")
        value_label.setAlignment(Qt.AlignCenter)

        def on_dial_change(value: int):
            actual_value = value / 100.0
            value_label.setText(f"{actual_value:.2f}")
            self.servicer.emit_analog_event(controller_id, actual_value)

        dial.valueChanged.connect(on_dial_change)

        layout.addWidget(dial)
        layout.addWidget(value_label)

        # Register state with servicer
        self.servicer.register_pot_state(controller_id, label, "GUI", 0.0)

        return container

    def _create_encoder_dial(self, controller_id: int, label: str) -> QWidget:
        """Create an encoder control (QDial for relative events)."""
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Label
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_widget)

        # QDial for encoder
        dial = EncoderDial(steps_per_rev=24, parent=self, servicer=self.servicer, controller_id=controller_id)
        dial.setFixedSize(50, 50)

        layout.addWidget(dial, alignment=Qt.AlignCenter)

        s = self._create_switch(controller_id - 4, label + 'S')
        s.setFixedWidth(70)
        s.setStyleSheet("margin-top: 8px;")
        layout.addWidget(s, alignment=Qt.AlignCenter)
        # Register state with servicer
        self.servicer.register_encoder_state(controller_id, label, "GUI")

        return container

    def _create_switch(self, controller_id: int, label: str) -> QPushButton:
        """Create a switch control (toggle button)."""
        button = QPushButton(label)
        button.setCheckable(True)
        button.setMinimumWidth(80)

        def on_button_toggle(checked: bool):
            self.servicer.emit_toggle_event(controller_id, checked)

        button.toggled.connect(on_button_toggle)

        # Register state with servicer
        self.servicer.register_switch_state(controller_id, label, "GUI", False)

        return button

    def _create_rotary_switch(self, controller_id: int, label: str) -> QWidget:
        """Create a 4-position rotary switch (range event)."""
        container = QWidget()
        layout = QHBoxLayout()
        container.setLayout(layout)

        # Slider for 4 positions
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(4)
        slider.setValue(1)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(1)

        # Value display
        value_label = QLabel("1")

        def on_slider_change(value: int):
            value_label.setText(str(value))
            self.servicer.emit_range_event(controller_id, value)

        slider.valueChanged.connect(on_slider_change)

        layout.addWidget(slider)
        layout.addWidget(value_label)

        # Register state with servicer
        self.servicer.register_rotary_state(controller_id, label, "GUI", 1)

        return container

    def _create_led_indicator(self, led_id: int, label: str, color: str) -> QWidget:
        """Create an LED indicator that can be controlled via gRPC."""
        container = QWidget()
        layout = QHBoxLayout()  # Changed to horizontal layout
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(5)  # Small spacing between LED and label
        container.setLayout(layout)

        # LED indicator (circle using QLabel)
        led = QLabel()
        led.setFixedSize(20, 20)
        led.setAlignment(Qt.AlignCenter)

        # Set initial off state
        self._update_led_style(led, color, False)

        # Store reference for updates
        self.led_indicators[led_id] = (led, color)

        # Initialize LED state in servicer
        with self.servicer._state_lock:
            self.servicer._led_states[led_id] = False

        # Add LED first, then label
        layout.addWidget(led)

        # Label
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(label_widget)

        return container

    def _create_rgb_led_placeholder(self, label: str) -> QWidget:
        """Create an RGB LED placeholder (non-functional)."""
        container = QWidget()
        layout = QHBoxLayout()  # Changed to horizontal layout
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(5)  # Small spacing between LED and label
        container.setLayout(layout)

        # RGB LED indicator (shows rainbow gradient)
        led = QLabel()
        led.setFixedSize(20, 20)
        led.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 red, stop:0.33 green, stop:0.66 blue, stop:1 red); "
            "border-radius: 10px; border: 1px solid gray;"
        )
        layout.addWidget(led)

        # Label
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(label_widget)

        return container

    def _update_led_style(self, led_widget: QLabel, color: str, active: bool):
        """Update LED style based on state."""
        if active:
            led_widget.setStyleSheet(
                f"background-color: {color}; "
                f"border-radius: 10px; border: 1px solid darkgray;"
            )
        else:
            led_widget.setStyleSheet(
                f"background-color: #333; border-radius: 10px; border: 1px solid gray;"
            )

    def _on_led_update(self, led_id: int, active: bool):
        """Handle LED update signal (called in Qt thread via signal)."""
        if led_id in self.led_indicators:
            led_widget, color = self.led_indicators[led_id]
            self._update_led_style(led_widget, color, active)

    def _on_display_write(self, message: str):
        """Handle display write signal (called in Qt thread via signal)."""
        png_data = base64.b64decode(message)
        pixmap = QPixmap()
        pixmap.loadFromData(png_data)
        self.display.setPixmap(pixmap.scaled(self.display.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
