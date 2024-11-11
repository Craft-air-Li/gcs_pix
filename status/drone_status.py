from PySide6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QTextEdit, QFrame
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QPainter, QPen, QPainterPath
import logging
from dronekit import connect

class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.append(msg)
        self.text_widget.verticalScrollBar().setValue(self.text_widget.verticalScrollBar().maximum())

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

class DroneStatusWidget(QWidget):
    def __init__(self, vehicle):
        super().__init__()

        self.vehicle = vehicle
        self.init_ui()

        self.setup_logging()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)

    def init_ui(self):
        self.setWindowTitle("Drone Status and Log Checker")
        self.setFixedSize(475, 400)
        
        self.status_container = RoundedFrame()
        status_layout = QGridLayout(self.status_container)

        self.gps_status_label = QLabel("GPS Status: Not Acquired")
        self.gps_status_num = QLabel("Satellites: Unknown")
        self.ins_label = QLabel("INS Status: Unknown")
        self.mag_label = QLabel("MAG Status: Unknown")
        self.ahrs_label = QLabel("AHRS Status: Unknown")
        self.ekf_label = QLabel("EKF Status: Unknown")
        self.fen_label = QLabel("Failsafe: Unknown")
        self.rc_status_label = QLabel("RC Status: Unknown")
        self.pwr_label = QLabel("Power Status: Unknown")
        self.link_label = QLabel("Link Status: Unknown")

        labels = [
            self.gps_status_label, self.gps_status_num,
            self.ins_label, self.mag_label,
            self.ahrs_label, self.ekf_label,
            self.fen_label, self.rc_status_label,
            self.pwr_label, self.link_label
        ]

        for label in labels:
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setFont(QFont("Arial", 8))
            label.setStyleSheet("padding: 5px; margin: 2px;") 

        positions = [
            (0, 0), (0, 1), (1, 0), (1, 1),
            (2, 0), (2, 1), (3, 0), (3, 1),
            (4, 0), (4, 1)
        ]

        for position, label in zip(positions, labels):
            status_layout.addWidget(label, *position)

        self.guide_mode_label = self.create_mode_label("Guide Mode: Not Available", "darkgreen")
        self.alt_hold_mode_label = self.create_mode_label("Alt Hold Mode: Not Available", "darkblue")
        self.land_mode_label = self.create_mode_label("Land Mode: Not Available", "darkred")
        self.stabilize_mode_label = self.create_mode_label("Stabilize Mode: Not Available", "purple")
        self.pre_label = self.create_mode_label("Flight Preparedness: Unknown", "orange")

        mode_layout = QVBoxLayout()
        mode_layout.addWidget(self.guide_mode_label)
        mode_layout.addWidget(self.alt_hold_mode_label)
        mode_layout.addWidget(self.land_mode_label)
        mode_layout.addWidget(self.stabilize_mode_label)
        mode_layout.addWidget(self.pre_label)

        status_layout_container = QHBoxLayout()
        status_layout_container.addWidget(self.status_container)
        status_layout_container.addLayout(mode_layout)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFixedSize(455, 150)
        self.log_text_edit.setStyleSheet("background-color: #222222; color: #00FF00; font-family: Consolas;")

        main_layout = QVBoxLayout()
        main_layout.addLayout(status_layout_container)
        main_layout.addWidget(QLabel("Log Messages:"))
        main_layout.addWidget(self.log_text_edit)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def create_mode_label(self, text, color):
        label = QLabel(text)
        label.setFixedSize(150, 28)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 6, QFont.Bold))
        label.setStyleSheet(f"""
            background-color: {color};
            color: white;
            font-weight: bold;
            border: 1px solid white;
            border-radius: 4px;
        """)
        return label

    def setup_logging(self):
        log_handler = LogHandler(self.log_text_edit)
        log_handler.setLevel(logging.INFO)  
        log_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.INFO)  

    def update_status(self):
        if not self.vehicle:
            self.gps_status_label.setText("GPS Status: Not Acquired")
            self.gps_status_num.setText("Satellites: Unknown")
            self.ins_label.setText("INS Status: Unknown")
            self.mag_label.setText("MAG Status: Unknown")
            self.ahrs_label.setText("AHRS Status: Unknown")
            self.ekf_label.setText("EKF Status: Unknown")
            self.fen_label.setText("Failsafe: Unknown")
            self.rc_status_label.setText("RC Status: Unknown")
            self.pwr_label.setText("Power Status: Unknown")
            self.link_label.setText("Link Status: Unknown")
            self.pre_label.setText("Flight Preparedness: Not Ready")
            return

        satellites_visible = self.vehicle.gps_0.satellites_visible
        if self.vehicle.gps_0.fix_type >= 3:
            self.gps_status_label.setText("GPS Status: Acquired")
            self.gps_status_num.setText(f"Satellites: {satellites_visible}")
            self.gps_status_label.setStyleSheet("color: green;")
            self.gps_status_num.setStyleSheet("color: green;")
        else:
            self.gps_status_label.setText(f"GPS Status: Not Acquired, Satellites: {satellites_visible}")
            self.gps_status_num.setText(f"Satellites: {satellites_visible}")
            self.gps_status_label.setStyleSheet("color: red;")
            self.gps_status_num.setStyleSheet("color: red;")

        if self.vehicle.attitude and self.vehicle.velocity and self.vehicle.location.global_relative_frame:
            self.ins_label.setText("INS Status: Active")
            self.ins_label.setStyleSheet("color: green;")
        else:
            self.ins_label.setText("INS Status: Inactive")
            self.ins_label.setStyleSheet("color: red;")

        if self.vehicle.heading is not None:
            self.mag_label.setText("MAG Status: Active")
            self.mag_label.setStyleSheet("color: green;")
        else:
            self.mag_label.setText("MAG Status: Inactive")
            self.mag_label.setStyleSheet("color: red;")

        if self.vehicle.ekf_ok:
            self.ekf_label.setText("EKF Status: Stable")
            self.ekf_label.setStyleSheet("color: green;")
        else:
            self.ekf_label.setText("EKF Status: Unstable")
            self.ekf_label.setStyleSheet("color: red;")

        if self.vehicle.ekf_ok and self.vehicle.attitude:
            self.ahrs_label.setText("AHRS Status: Active")
            self.ahrs_label.setStyleSheet("color: green;")
        else:
            self.ahrs_label.setText("AHRS Status: Inactive")
            self.ahrs_label.setStyleSheet("color: red;")

        if self.vehicle.system_status.state in ['CRITICAL', 'EMERGENCY']:
            self.fen_label.setText("Failsafe: Active")
            self.fen_label.setStyleSheet("color: red;")
        else:
            self.fen_label.setText("Failsafe: Inactive")
            self.fen_label.setStyleSheet("color: green;")

        last_heartbeat = self.vehicle.last_heartbeat
        if last_heartbeat < 1:
            self.link_label.setText("Link Status: OK")
            self.link_label.setStyleSheet("color: green;")
        else:
            self.link_label.setText("Link Status: Inactive")
            self.link_label.setStyleSheet("color: red;")

        if self.vehicle.channels:
            self.rc_status_label.setText("RC Status: Connected")
            self.rc_status_label.setStyleSheet("color: green;")
        else:
            self.rc_status_label.setText("RC Status: Disconnected")
            self.rc_status_label.setStyleSheet("color: red;")

        self.pwr_label.setText("Power Status: OK" if self.vehicle.battery.voltage > 10 else "Power Status: Low")
        self.pwr_label.setStyleSheet("color: green;" if self.vehicle.battery.voltage > 10 else "color: red;")

        if self.vehicle.gps_0.fix_type >= 3 and self.vehicle.battery.voltage > 10 and self.vehicle.ekf_ok:
            self.pre_label.setText("Flight Preparedness: Ready")
            self.pre_label.setStyleSheet("color: green; background-color: orange; border: 1px solid white; border-radius: 4px;")
            self.pre_label.setFont(QFont("Arial", 8, QFont.Bold))

        else:
            self.pre_label.setText("Flight Preparedness: Not Ready")
            self.pre_label.setStyleSheet("color: red; background-color: orange; border: 1px solid white; border-radius: 4px;")
            self.pre_label.setFont(QFont("Arial", 8, QFont.Bold))

        self.update_mode_availability()

    def update_mode_availability(self):
        if self.vehicle.gps_0.fix_type >= 3 and self.vehicle.ekf_ok:
            self.guide_mode_label.setText("Guide Mode: Available")
            self.guide_mode_label.setStyleSheet("background-color: darkgreen; color: white; border: 1px solid white; border-radius: 4px;")
            self.guide_mode_label.setFont(QFont("Arial", 8, QFont.Bold))
        else:
            self.guide_mode_label.setText("Guide Mode: Not Available")
            self.guide_mode_label.setStyleSheet("background-color: darkred; color: white; border: 1px solid white; border-radius: 4px;")
            self.guide_mode_label.setFont(QFont("Arial", 8, QFont.Bold))

        if self.vehicle.ekf_ok and self.vehicle.battery.voltage >= 5.0:
            self.alt_hold_mode_label.setText("Alt Hold Mode: Available")
            self.alt_hold_mode_label.setStyleSheet("background-color: darkblue; color: white; border: 1px solid white; border-radius: 4px;")
            self.alt_hold_mode_label.setFont(QFont("Arial", 8, QFont.Bold))
        else:
            self.alt_hold_mode_label.setText("Alt Hold Mode: Not Available")
            self.alt_hold_mode_label.setStyleSheet("background-color: darkred; color: white; border: 1px solid white; border-radius: 4px;")
            self.alt_hold_mode_label.setFont(QFont("Arial", 8, QFont.Bold))

        if self.vehicle.ekf_ok and self.vehicle.channels:
            self.land_mode_label.setText("Land Mode: Available")
            self.land_mode_label.setStyleSheet("background-color: darkred; color: white; border: 1px solid white; border-radius: 4px;")
            self.land_mode_label.setFont(QFont("Arial", 8, QFont.Bold))
        else:
            self.land_mode_label.setText("Land Mode: Not Available")
            self.land_mode_label.setStyleSheet("background-color: darkred; color: white; border: 1px solid white; border-radius: 4px;")
            self.land_mode_label.setFont(QFont("Arial", 8, QFont.Bold))

        if self.vehicle.battery.voltage >= 5.0:
            self.stabilize_mode_label.setText("Stabilize Mode: Available")
            self.stabilize_mode_label.setStyleSheet("background-color: purple; color: white; border: 1px solid white; border-radius: 4px;")
            self.stabilize_mode_label.setFont(QFont("Arial", 8, QFont.Bold))
        else:
            self.stabilize_mode_label.setText("Stabilize Mode: Not Available")
            self.stabilize_mode_label.setStyleSheet("background-color: darkred; color: white; border: 1px solid white; border-radius: 4px;")
            self.stabilize_mode_label.setFont(QFont("Arial", 8, QFont.Bold))
