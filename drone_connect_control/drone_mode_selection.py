from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPen, QPainterPath, QFont
from dronekit import VehicleMode

class DroneModeSelectionWidget(QWidget):
    def __init__(self, vehicle):
        super().__init__()
        self.vehicle = vehicle
        self.setWindowTitle("Drone Mode Selection")
        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        checkbox_style = """
            QCheckBox {
                font-size: 10px;  
                padding: 1px;    
            }
            QCheckBox::indicator {
                width: 12px;      
                height: 12px;     
            }
        """

        self.stabilize_checkbox = QCheckBox("Stabilize")
        self.stabilize_checkbox.setStyleSheet(checkbox_style)

        self.alt_hold_checkbox = QCheckBox("Alt Hold")
        self.alt_hold_checkbox.setStyleSheet(checkbox_style)

        self.guided_checkbox = QCheckBox("Guided")
        self.guided_checkbox.setStyleSheet(checkbox_style)

        self.land_checkbox = QCheckBox("Land")
        self.land_checkbox.setStyleSheet(checkbox_style)

        layout.addWidget(self.stabilize_checkbox)
        layout.addWidget(self.alt_hold_checkbox)
        layout.addWidget(self.guided_checkbox)
        layout.addWidget(self.land_checkbox)

        self.current_mode = "STABILIZE"
        self.stabilize_checkbox.setChecked(True)
        self.update_checkboxes()  

        self.stabilize_checkbox.stateChanged.connect(lambda: self.on_checkbox_checked("STABILIZE"))
        self.alt_hold_checkbox.stateChanged.connect(lambda: self.on_checkbox_checked("ALT_HOLD"))
        self.guided_checkbox.stateChanged.connect(lambda: self.on_checkbox_checked("GUIDED"))
        self.land_checkbox.stateChanged.connect(lambda: self.on_checkbox_checked("LAND"))

        self.setLayout(layout)

        self.mode_sync_timer = QTimer(self)
        self.mode_sync_timer.timeout.connect(self.sync_mode)
        self.mode_sync_timer.start(500)  

    def update_checkboxes(self):
        is_connected = self.vehicle is not None
        self.stabilize_checkbox.setEnabled(is_connected)
        self.alt_hold_checkbox.setEnabled(is_connected)
        self.guided_checkbox.setEnabled(is_connected)
        self.land_checkbox.setEnabled(is_connected)

    def on_checkbox_checked(self, mode):
        if self.vehicle is None:
            self.update_checkboxes()
            return

        if mode == "STABILIZE" and self.stabilize_checkbox.isChecked():
            self.alt_hold_checkbox.setChecked(False)
            self.guided_checkbox.setChecked(False)
            self.land_checkbox.setChecked(False)
        elif mode == "ALT_HOLD" and self.alt_hold_checkbox.isChecked():
            self.stabilize_checkbox.setChecked(False)
            self.guided_checkbox.setChecked(False)
            self.land_checkbox.setChecked(False)
        elif mode == "GUIDED" and self.guided_checkbox.isChecked():
            self.stabilize_checkbox.setChecked(False)
            self.alt_hold_checkbox.setChecked(False)
            self.land_checkbox.setChecked(False)
        elif mode == "LAND" and self.land_checkbox.isChecked():
            self.stabilize_checkbox.setChecked(False)
            self.alt_hold_checkbox.setChecked(False)
            self.guided_checkbox.setChecked(False)

        if self.set_drone_mode(mode):
            self.current_mode = mode

    def set_drone_mode(self, mode):
        if self.vehicle:
            self.vehicle.mode = VehicleMode(mode)
            if self.vehicle.mode.name == mode:
                return True
        return False

    def sync_mode(self):
        if self.vehicle is not None:
            vehicle_mode = self.vehicle.mode.name
            if vehicle_mode != self.current_mode:
                self.current_mode = vehicle_mode
                self.restore_current_mode()

    def restore_current_mode(self):
        self.stabilize_checkbox.blockSignals(True)
        self.alt_hold_checkbox.blockSignals(True)
        self.guided_checkbox.blockSignals(True)
        self.land_checkbox.blockSignals(True)

        if self.current_mode == "STABILIZE":
            self.stabilize_checkbox.setChecked(True)
            self.alt_hold_checkbox.setChecked(False)
            self.guided_checkbox.setChecked(False)
            self.land_checkbox.setChecked(False)
        elif self.current_mode == "ALT_HOLD":
            self.stabilize_checkbox.setChecked(False)
            self.alt_hold_checkbox.setChecked(True)
            self.guided_checkbox.setChecked(False)
            self.land_checkbox.setChecked(False)
        elif self.current_mode == "GUIDED":
            self.stabilize_checkbox.setChecked(False)
            self.alt_hold_checkbox.setChecked(False)
            self.guided_checkbox.setChecked(True)
            self.land_checkbox.setChecked(False)
        elif self.current_mode == "LAND":
            self.stabilize_checkbox.setChecked(False)
            self.alt_hold_checkbox.setChecked(False)
            self.guided_checkbox.setChecked(False)
            self.land_checkbox.setChecked(True)

        self.stabilize_checkbox.blockSignals(False)
        self.alt_hold_checkbox.blockSignals(False)
        self.guided_checkbox.blockSignals(False)
        self.land_checkbox.blockSignals(False)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.white, 1)
        painter.setPen(pen)

        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)
        painter.drawPath(path)
