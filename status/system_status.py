from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtGui import QPixmap, QPainter, QPen, QPainterPath
from PySide6.QtCore import QTimer, Qt
from dronekit import APIException
import time
import requests

class GPSStatusWidget(QWidget):
    def __init__(self, vehicle=None):
        super().__init__()
        self.vehicle = vehicle
        self.setStyleSheet("background-color: black;")

        self.imageLabel = QLabel(self)
        self.greenPixmap = QPixmap("status/system_image/gps_connect.png").scaled(30, 30)
        self.redPixmap = QPixmap("status/system_image/gps_disconnect.png").scaled(30, 30)
        self.imageLabel.setPixmap(self.redPixmap)
        
        self.satellitesLabel = QLabel("Satellites: Not Connected", self)
        self.satellitesLabel.setStyleSheet("color: red;")

        layout = QVBoxLayout()
        layout.addWidget(self.imageLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.satellitesLabel, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        if not self.vehicle:
            self.set_default_status()
        else:
            self.updateGPSStatus()
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.updateGPSStatus)
            self.timer.start(1000)

    def set_default_status(self):
        self.imageLabel.setPixmap(self.redPixmap)
        self.satellitesLabel.setText("Satellites: Not Connected")
        self.satellitesLabel.setStyleSheet("color: red;")

    def updateGPSStatus(self):
        if not self.vehicle:
            self.set_default_status()
            return

        try:
            satellites_visible = self.vehicle.gps_0.satellites_visible
            fix_type = self.vehicle.gps_0.fix_type
            self.satellitesLabel.setText(f"Satellites: {satellites_visible}")

            if fix_type >= 3 and satellites_visible >= 6:
                self.imageLabel.setPixmap(self.greenPixmap)
                self.satellitesLabel.setStyleSheet("color: white;")  
            else:
                self.imageLabel.setPixmap(self.redPixmap)
                self.satellitesLabel.setStyleSheet("color: red;") 
        except APIException:
            self.set_default_status()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.white, 1)
        painter.setPen(pen)
        
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.drawPath(path)


class BatteryMonitorWidget(QWidget):
    def __init__(self, drone=None):
        super().__init__()
        self.drone = drone
        self.total_capacity = 5000  
        self.remaining_capacity = self.total_capacity
        self.last_update_time = int(time.time() * 1000)
        self.setStyleSheet("background-color: black;")

        self.battery_progress = QProgressBar(self)
        self.battery_progress.setMinimum(0)
        self.battery_progress.setMaximum(100)
        self.battery_progress.setFormat("%p%")
        self.battery_progress.setFixedHeight(15)
        self.battery_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #eee;
                text-align: center;
                font: bold 10px;
                padding: 0px;
                height: 14px;
            }
            QProgressBar::chunk {
                background-color: green;
                border-radius: 3px;
            }
        """)

        self.battery_voltage_label = QLabel("V: N/A", self)
        self.battery_voltage_label.setStyleSheet("color: white;")
        self.battery_current_label = QLabel("A: N/A", self)
        self.battery_current_label.setStyleSheet("color: white;")

        layout = QVBoxLayout()
        layout.addWidget(self.battery_progress, alignment=Qt.AlignCenter)
        layout.addWidget(self.battery_voltage_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.battery_current_label, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        if not self.drone:
            self.set_default_status()
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_battery_info)
            self.timer.start(1000)

    def set_default_status(self):
        self.battery_progress.setValue(0)
        self.battery_voltage_label.setText("V: N/A")
        self.battery_current_label.setText("A: N/A")

    def calculate_battery_level(self, current_draw, elapsed_time_ms, c_rating=40):
        discharged_mAh = current_draw * (elapsed_time_ms / (1000 * 3600)) * 1000
        self.remaining_capacity -= discharged_mAh
        if self.remaining_capacity < 0:
            self.remaining_capacity = 0
        battery_percentage = (self.remaining_capacity / self.total_capacity) * 100
        return int(battery_percentage)

    def update_battery_info(self):
        if not self.drone:
            self.set_default_status()
            return

        battery = self.drone.battery
        current_time_ms = int(time.time() * 1000)
        elapsed_time_ms = current_time_ms - self.last_update_time
        self.last_update_time = current_time_ms

        current_draw = battery.current if battery.current else 0
        battery_percentage = self.calculate_battery_level(current_draw, elapsed_time_ms)

        if battery_percentage > 50:
            color = "green"
        elif 20 <= battery_percentage <= 50:
            color = "orange"
        else:
            color = "red"

        self.battery_progress.setValue(battery_percentage)
        self.battery_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #eee;
                text-align: center;
                font: bold 10px;
                padding: 0px;
                height: 14px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)

        voltage = battery.voltage if battery.voltage else 0
        self.battery_voltage_label.setText(f"V: {voltage:.1f}V" if voltage else "V: N/A")
        self.battery_current_label.setText(f"A: {current_draw:.1f}A" if current_draw else "A: N/A")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.white, 2)
        painter.setPen(pen)
        
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.drawPath(path)


class InternetStatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(30, 30)
        self.status_label = QLabel("Checking connection...")
        self.status_label.setStyleSheet("color: white;")
        
        layout = QVBoxLayout()
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(5000)

        self.check_connection()

    def set_default_status(self):
        self.status_label.setText("Internet: Not Connected")
        self.icon_label.setPixmap(QPixmap("status/system_image/wifi_disconnected(1).png").scaled(30, 30, Qt.KeepAspectRatio))

    def check_connection(self):
        if self.is_connected():
            self.status_label.setText("Internet Connected")
            self.icon_label.setPixmap(QPixmap("status/system_image/wifi_connected(1).png").scaled(30, 30, Qt.KeepAspectRatio))
        else:
            self.set_default_status()

    def is_connected(self):
        try:
            requests.get("http://www.google.com", timeout=2)
            return True
        except requests.ConnectionError:
            return False

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.white, 1)
        painter.setPen(pen)
    
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.drawPath(path)


class SystemStatusPanel(QWidget):
    def __init__(self, vehicle=None):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.setFixedSize(475, 100)
        layout = QHBoxLayout()
        
        self.gps_widget = GPSStatusWidget(vehicle)
        self.battery_widget = BatteryMonitorWidget(vehicle)
        self.internet_widget = InternetStatusWidget()
        
        layout.addWidget(self.gps_widget)
        layout.addWidget(self.battery_widget)
        layout.addWidget(self.internet_widget)
        
        self.setLayout(layout)
