from PySide6.QtWidgets import QDial, QWidget, QVBoxLayout, QLabel, QApplication
from PySide6.QtCore import Signal, Qt


class EncoderDial(QDial):
    """A QDial that behaves like a rotary encoder.
    
    Emits stepped(+1) on clockwise turn, stepped(-1) on counter-clockwise.
    The dial wraps and has no absolute position — only relative steps matter.
    """
    # stepped = Signal(int)  # +1 or -1

    def __init__(self, steps_per_rev=24, parent=None, servicer = None, controller_id:int = 0):
        super().__init__(parent)
        self._steps_per_rev = steps_per_rev
        self._last_value = None
        self._controller_id = controller_id
        self._servicer = servicer

        # Use a large range centered at 0 to avoid hitting min/max
        self.setRange(0, steps_per_rev - 1)
        self.setWrapping(True)
        self.setSingleStep(1)
        self.setPageStep(1)
        self.setValue(0)

        self._last_value = self.value()
        self.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self, new_val):
        if self._last_value is None:
            self._last_value = new_val
            return

        half = self._steps_per_rev // 2
        delta = new_val - self._last_value

        # Handle wrap-around
        if delta > half:
            delta -= self._steps_per_rev
        elif delta < -half:
            delta += self._steps_per_rev

        if delta != 0:
            self._servicer.emit_relative_event(self._controller_id, 1 if delta > 0 else -1)
            # self.stepped.emit(1 if delta > 0 else -1)

        self._last_value = new_val


# --- Demo ---
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = QWidget()
    layout = QVBoxLayout(window)

    label = QLabel("Position: 0")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    dial = EncoderDial(steps_per_rev=24)

    position = [0]

    def on_step(delta):
        position[0] += delta
        label.setText(f"Position: {position[0]}  (delta: {'+' if delta > 0 else ''}{delta})")

    dial.stepped.connect(on_step)

    layout.addWidget(dial)
    layout.addWidget(label)
    window.setWindowTitle("Encoder Dial Demo")
    window.show()
    sys.exit(app.exec_())
