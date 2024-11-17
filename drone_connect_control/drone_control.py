from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QWidget, QFrame
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from dronekit import VehicleMode
from drone_mode_selection import DroneModeSelectionWidget
import time

class DroneControlPanel(QWidget):
    def __init__(self, vehicle):
        super().__init__()
        self.vehicle = vehicle

        self.status_label = QLabel("Disarmed")
        self.status_label.setFixedSize(140, 90)
        self.status_label.setFont(QFont("Extra Bold"))
        self.status_label.setStyleSheet("font-size: 20px; font-weight: 900; border: 1px solid white")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.update_status_color("Disarmed")

        self.mode_label = QLabel("Mode: Unknown")
        self.mode_label.setFixedSize(140, 90)
        self.mode_label.setFont(QFont("Extra Bold"))
        self.mode_label.setStyleSheet("font-size: 20px; font-weight: 900; border: 1px solid white")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.update_mode_color("Unknown")

        self.mode_selection_widget = DroneModeSelectionWidget(self.vehicle)
        self.mode_selection_widget.setFixedSize(140, 90)  

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(100)

        layout = QVBoxLayout(self)
        self.setup_control_buttons(layout)

    def setup_control_buttons(self, layout):
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.mode_label)
        status_layout.addWidget(self.mode_selection_widget)  
        layout.addLayout(status_layout)

        arm_disarm_layout = QHBoxLayout()
        self.arm_button = QPushButton("Arm")
        self.arm_button.setFixedSize(100, 50)
        self.arm_button.setStyleSheet("border: 1px solid white; border-radius: 6px;")  
        self.arm_button.clicked.connect(self.arm_drone)

        self.disarm_button = QPushButton("Disarm")
        self.disarm_button.setFixedSize(100, 50)
        self.disarm_button.setStyleSheet("border: 1px solid white; border-radius: 6px;")  
        self.disarm_button.clicked.connect(self.disarm_drone)

        self.takeoff_button = QPushButton("Takeoff")
        self.takeoff_button.setFixedSize(100, 50)
        self.takeoff_button.setStyleSheet("border: 1px solid white; border-radius: 6px;")
        self.takeoff_button.clicked.connect(self.takeoff_drone)

        self.land_button = QPushButton("Land")
        self.land_button.setFixedSize(100, 50)
        self.land_button.setStyleSheet("border: 1px solid white; border-radius: 6px;")
        self.land_button.clicked.connect(self.land_drone)
        
        arm_disarm_layout.addWidget(self.arm_button)
        arm_disarm_layout.addWidget(self.disarm_button)
        arm_disarm_layout.addWidget(self.takeoff_button)
        arm_disarm_layout.addWidget(self.land_button)
        layout.addLayout(arm_disarm_layout)
        layout.addStretch()

    def update_status(self):
        if self.vehicle:
            status = "Armed" if self.vehicle.armed else "Disarmed"
            mode = self.vehicle.mode.name if self.vehicle.mode else "Unknown"
            self.status_label.setText(status)
            self.update_status_color(status)

            self.mode_label.setText(f"{mode}")
            self.update_mode_color(mode)

            if mode == "STABILIZE":
                self.takeoff_button.setText("Unable")
                self.takeoff_button.setEnabled(False)
                self.land_button.setText("Unable")
                self.land_button.setEnabled(False)
            else:
                self.takeoff_button.setText("Takeoff")
                self.takeoff_button.setEnabled(True)
                self.land_button.setText("Land")
                self.land_button.setEnabled(True)
        else:
            self.status_label.setText("Not Connected")
            self.update_status_color("Not Connected")
            self.mode_label.setText("Mode: N/A")
            self.update_mode_color("N/A")

    def update_status_color(self, status):
        color = "#00FF00" if status == "Armed" else "#800080" if status == "Disarmed" else "#808080"
        self.status_label.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px; border: 1px solid white;")

    def update_mode_color(self, mode):
        color_map = {
            "GUIDED": "#0000FF",  
            "LAND": "#FF0000",    
            "LOITER": "#FFFF00",  
            "AUTO": "#00FFFF",    
            "Unknown": "#808080"  
        }
        color = color_map.get(mode, "#808080")
        self.mode_label.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px; border: 1px solid white;")

    def arm_drone(self):
        if self.vehicle:
            self.vehicle.armed = True
            print("Drone armed.")

    def disarm_drone(self):
        if self.vehicle:
            self.vehicle.armed = False
            print("Drone disarmed.")

    def takeoff_drone(self):
        if not self.vehicle:
            print("No vehicle connected.")
            return

        current_mode = self.vehicle.mode.name
        if current_mode == "STABILIZE":
            print("Takeoff is not allowed in STABILIZE mode.")
            return

        if current_mode == "ALT_HOLD":
            self.alt_hold_takeoff()
        elif current_mode == "GUIDED":
            self.guided_takeoff()
        elif current_mode == "LAND":
            print("Takeoff is not allowed in LAND mode.")
            return

    def alt_hold_takeoff(self):
        target_altitude = 2  
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        while not self.vehicle.armed:
            print("Waiting for drone to be armed...")
            time.sleep(1)
    
        self.vehicle.channels.overrides['3'] = 1700  
        self.alt_hold_timer = QTimer()
        self.alt_hold_timer.timeout.connect(lambda: self.altitude_control(target_altitude))
        self.alt_hold_timer.start(500)

    def altitude_control(self, target_altitude):
        if self.vehicle.mode.name not in ["ALT_HOLD"] or not self.vehicle.armed:
            self.alt_hold_timer.stop()
            return

        current_altitude = self.vehicle.location.global_relative_frame.alt
        if self.vehicle.mode.name == "ALT_HOLD":
            if current_altitude >= target_altitude - 0.05:
                self.vehicle.channels.overrides['3'] = 1500 
            else:
                self.vehicle.channels.overrides['3'] = 1700

    def guided_takeoff(self):
        target_altitude = 2       
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.simple_takeoff(target_altitude)

    def land_drone(self):
        if self.vehicle:
            self.vehicle.mode = VehicleMode("LAND")
            self.vehicle.channels.overrides.clear()