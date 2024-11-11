import os
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPixmap, QTransform

class Altimeter(QWidget):
    def __init__(self, vehicle=None, parent=None):
        super(Altimeter, self).__init__(parent)
        self.vehicle = vehicle 
        self.altitude = 0.0 
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.needle_image = QPixmap(os.path.join(current_dir, "image/needle.png"))
        self.background_image = QPixmap(os.path.join(current_dir, "image/alt_back.png"))

        self.altitude_label = QLabel(self)
        self.altitude_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.altitude_label.setStyleSheet("color: white; font-size: 11px; background-color: transparent; font-weight: bold; padding: 3px;")
        self.altitude_label.setFixedSize(50, 30)
        self.altitude_label.move(40, self.height() - 80)

    def update_altitude(self, altitude=None):
        if altitude is not None:
            self.altitude = round(altitude, 1)
        elif self.vehicle:
            self.altitude = round(self.vehicle.location.global_relative_frame.alt, 1)
        else:
            self.altitude = 0
        self.altitude_label.setText(f"{self.altitude} m")
        self.update()

    def resizeEvent(self, event):
        self.altitude_label.move(40, self.height() - 80)

    def paintEvent(self, event):
        painter = QPainter(self)
        center = self.rect().center()

        bg_size = min(self.width(), self.height())
        painter.drawPixmap(center.x() - bg_size // 2, center.y() - bg_size // 2, bg_size, bg_size, self.background_image)

        painter.save()
        painter.translate(center.x(), center.y())
        angle = self.calculate_angle(self.altitude)
        painter.rotate(angle)  

        fixed_needle_size = 380  
        painter.drawPixmap(-fixed_needle_size // 2, -fixed_needle_size // 2, fixed_needle_size, fixed_needle_size, self.needle_image)
        painter.restore()

    def calculate_angle(self, altitude):
        if altitude <= 0:
            return 0
        elif altitude <= 10:
            return (altitude / 10) * 90 
        elif altitude <= 50:
            return 90 + ((altitude - 10) / 40) * 90  
        elif altitude <= 150:
            return 180 + ((altitude - 50) / 100) * 90 
        else:
            return 270

    def set_vehicle(self, vehicle):
        self.vehicle = vehicle
