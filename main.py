import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QWidget, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QPen, QPainterPath
sys.path.append(os.path.join(os.path.dirname(__file__), "drone_connect_control"))

from indicator.map import MapWidget
from indicator.alt_bar import AltitudeBar
from indicator.AttitudeIndicator import AttitudeIndicator
from indicator.HeadingIndicator import HeadingIndicator
from indicator.Altimeter import Altimeter
from indicator.Speedometer import GroundSpeedometer, AirSpeedometer
from drone_connect_control.drone_connection_layout import DroneConnectionPanel
from drone_connect_control.drone_control import DroneControlPanel
from status.drone_status import DroneStatusWidget
from status.system_status import SystemStatusPanel
import key_control

class RoundedFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.white, 1)
        painter.setPen(pen)
        
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.drawPath(path)

class GCSMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ground Control Station")
        self.setFixedSize(1400, 850)
        self.setFocusPolicy(Qt.StrongFocus) 
        self.setStyleSheet("background-color: #000001;")
        self.vehicle = None  

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        self.setup_layout(main_layout)
        self.setCentralWidget(main_widget)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gauges)
        self.timer.start(10)

    def setup_layout(self, main_layout):
        self.info_pannel = QFrame()
        self.info_pannel.setMinimumSize(500, 830)
        left_layout = QVBoxLayout(self.info_pannel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)

        self.connection_panel = RoundedFrame()
        connection_layout = QVBoxLayout(self.connection_panel)
        connection_layout.setContentsMargins(0, 0, 0, 0)
        connection_layout.addWidget(DroneConnectionPanel(self.set_vehicle))
        left_layout.addWidget(self.connection_panel)

        self.system_status_panel = SystemStatusPanel(self.vehicle)
        left_layout.addWidget(self.system_status_panel)

        self.drone_control_panel = DroneControlPanel(self.vehicle)  
        self.drone_control_panel.setup_control_buttons(left_layout)
        
        self.drone_status_widget = DroneStatusWidget(self.vehicle)  
        left_layout.addWidget(self.drone_status_widget)  

        spacer_bottom = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        left_layout.addItem(spacer_bottom)
        
        main_layout.addWidget(self.info_pannel, 1)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(0, 0, 0, 0)

        map_container = QFrame()
        map_container.setFixedSize(870, 450)
        map_container.setStyleSheet("background-color: #000001; border: 10px solid #000001; border-radius: 6px;")
        
        map_layout = QHBoxLayout(map_container)
        map_layout.setContentsMargins(0, 0, 0, 0)
        map_layout.setSpacing(10)

        self.map_panel = MapWidget()
        self.map_panel.setMinimumSize(670, 380)
        map_layout.addWidget(self.map_panel)

        self.altitude_bar = AltitudeBar(self.vehicle)
        self.altitude_bar.setFixedWidth(100)
        map_layout.addWidget(self.altitude_bar)

        right_layout.addWidget(map_container)

        self.control_panel = QFrame()
        self.control_panel.setFixedSize(870, 380)
        
        control_layout = QHBoxLayout(self.control_panel)
        control_layout.setSpacing(10)
        control_layout.setContentsMargins(10, 0, 10, 10)

        left_instrument = QVBoxLayout()
        self.altimeter = Altimeter(self)
        self.altimeter.setFixedSize(190, 190)
        left_instrument.addWidget(self.altimeter)

        self.groundSpeedoMeter = GroundSpeedometer(self)
        self.groundSpeedoMeter.setFixedSize(190, 190)
        left_instrument.addWidget(self.groundSpeedoMeter)

        center_instrument = QVBoxLayout()
        self.attitude_widget = AttitudeIndicator(self)
        self.attitude_widget.setFixedSize(380, 380)
        center_instrument.addWidget(self.attitude_widget)

        right_instruments = QVBoxLayout()
        self.heading_widget = HeadingIndicator(self)
        self.heading_widget.setFixedSize(190, 190)
        right_instruments.addWidget(self.heading_widget)

        self.airSpeedoMeter = AirSpeedometer(self)
        self.airSpeedoMeter.setFixedSize(190, 190)
        right_instruments.addWidget(self.airSpeedoMeter)

        control_layout.addLayout(left_instrument)
        control_layout.addLayout(center_instrument)
        control_layout.addLayout(right_instruments)

        right_layout.addWidget(self.control_panel)
        main_layout.addLayout(right_layout, 1)

    def set_vehicle(self, vehicle):
        self.vehicle = vehicle
        self.drone_control_panel.vehicle = self.vehicle

        self.drone_control_panel.mode_selection_widget.vehicle = self.vehicle
        self.drone_control_panel.mode_selection_widget.update_checkboxes()

        self.system_status_panel.gps_widget.vehicle = self.vehicle
        self.system_status_panel.battery_widget.drone = self.vehicle
        self.system_status_panel.gps_widget.updateGPSStatus()
        self.system_status_panel.battery_widget.update_battery_info()
        self.drone_status_widget.vehicle = self.vehicle  

        if self.vehicle:
            self.map_panel.update_vehicle(self.vehicle)
            self.altitude_bar.vehicle = self.vehicle

    def update_gauges(self):
        if not self.vehicle:
            self.attitude_widget.update_attitude(0, 0)
            self.heading_widget.update_heading(0)
            self.altimeter.update_altitude(0)
            self.groundSpeedoMeter.update_speed(0)
            self.airSpeedoMeter.update_speed(0)
            return
        if self.vehicle:
            self.system_status_panel.battery_widget.update_battery_info()
            
        roll = self.vehicle.attitude.roll
        pitch = self.vehicle.attitude.pitch
        heading = self.vehicle.heading
        altitude = self.vehicle.location.global_relative_frame.alt
        groundspeed = self.vehicle.groundspeed
        airspeed = self.vehicle.airspeed

        self.attitude_widget.update_attitude(roll, pitch)
        self.heading_widget.update_heading(heading)
        self.altimeter.update_altitude(altitude)
        self.groundSpeedoMeter.update_speed(groundspeed)
        self.airSpeedoMeter.update_speed(airspeed)
    
    def keyPressEvent(self, event):
        if self.vehicle and self.vehicle.location.global_relative_frame.alt >= 1:
            if self.vehicle.mode.name == "ALT_HOLD":
                key_control.handle_alt_hold_keys(event, self.vehicle)
            elif self.vehicle.mode.name == "GUIDED":
                key_control.handle_guided_keys(event, self.vehicle)
        event.accept()

    def keyReleaseEvent(self, event):
        if self.vehicle:
            if self.vehicle.mode.name == "ALT_HOLD":
                key_control.clear_alt_hold_override(self.vehicle)
            elif self.vehicle.mode.name == "GUIDED":
                key_control.stop_guided_movement(self.vehicle)
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    window = GCSMainWindow()
    window.show()
    app.exec()
