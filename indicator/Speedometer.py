import os
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QTransform

class Speedometer(QWidget):
    def __init__(self, speed_type="Ground Speed", vehicle=None, parent=None):
        super(Speedometer, self).__init__(parent)
        self.vehicle = vehicle
        self.speed = 0.0
        self.speed_type = speed_type
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.needle_image = QPixmap(os.path.join(current_dir, "image/needle.png"))
        self.background_image = QPixmap(os.path.join(current_dir, "image/speed_back.png"))

        self.speed_label = QLabel(self)
        self.speed_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.speed_label.setStyleSheet("color: white; font-size: 11px; background-color: transparent; font-weight: bold; padding: 3px;")
        self.speed_label.setFixedSize(50, 30)
        self.speed_label.move(40, self.height() - 80)
        
        self.type_label = QLabel(self)
        self.type_label.setText("Ground" if self.speed_type == "Ground Speed" else "Air")
        self.type_label.setAlignment(Qt.AlignCenter)
        self.type_label.setStyleSheet("color: white; font-size: 14px; background-color: transparent; font-weight: bold;")
        self.type_label.setFixedSize(60, 20)
        self.type_label.move(self.width() // 2 - 30, self.height() // 2 - 60)  

    def update_speed(self, speed=None):
        if speed is not None:
            self.speed = round(speed, 1)
        elif self.vehicle:
            self.speed = round(self.vehicle.groundspeed if self.speed_type == "Ground Speed" else self.vehicle.airspeed, 1)
        else:
            self.speed = 0 
        self.speed_label.setText(f"{self.speed} m/s")
        self.update()

    def resizeEvent(self, event):
        self.speed_label.move(40, self.height() - 80)
        self.type_label.move(self.width() // 2 - 30, self.height() // 2 - 60)

    def paintEvent(self, event):
        painter = QPainter(self)
        center = self.rect().center()

        bg_size = min(self.width(), self.height())
        painter.drawPixmap(center.x() - bg_size // 2, center.y() - bg_size // 2, bg_size, bg_size, self.background_image)

        painter.save()
        painter.translate(center.x(), center.y())
        angle = self.calculate_angle(self.speed)
        painter.rotate(angle)
        
        fixed_needle_size = 380  
        painter.drawPixmap(-fixed_needle_size // 2, -fixed_needle_size // 2, fixed_needle_size, fixed_needle_size, self.needle_image)
        painter.restore()

    def calculate_angle(self, speed):
        max_speed = 45
        if speed <= 0:
            return 0
        elif speed >= max_speed:
            return 270
        else:
            return (speed / max_speed) * 270

    def set_vehicle(self, vehicle):
        self.vehicle = vehicle

class GroundSpeedometer(Speedometer):
    def __init__(self, vehicle=None, parent=None):
        super().__init__("Ground Speed", vehicle, parent)

class AirSpeedometer(Speedometer):
    def __init__(self, vehicle=None, parent=None):
        super().__init__("Air Speed", vehicle, parent)
