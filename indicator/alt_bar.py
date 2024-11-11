from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QFont

MAX_ALTITUDE = 150.0
BAR_WIDTH = 50  
BAR_HEIGHT_PX = 400  

class AltitudeBar(QWidget):
    def __init__(self, vehicle=None):
        super().__init__()
        self.vehicle = vehicle 
        self.altitude = 0  
        self.setFixedSize(BAR_WIDTH, BAR_HEIGHT_PX)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_altitude)
        self.timer.start(500)

    def update_altitude(self):
        if self.vehicle and self.vehicle.location.global_relative_frame:
            altitude = self.vehicle.location.global_relative_frame.alt
            self.altitude = altitude if altitude is not None else 0
        else:
            self.altitude = 0
        self.update()

    def paintEvent(self, event):
        bar_height = min((self.altitude / MAX_ALTITUDE) * BAR_HEIGHT_PX, BAR_HEIGHT_PX)
        color_intensity = min(1, self.altitude / MAX_ALTITUDE)
        color = QColor(color_intensity * 255, 0, (1 - color_intensity) * 255)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
    
        painter.setBrush(color)
        painter.drawRect(0, BAR_HEIGHT_PX - bar_height, BAR_WIDTH - 10, bar_height)

        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        text_y_position = BAR_HEIGHT_PX - bar_height - 20
        text_y_position = max(10, text_y_position)
        painter.drawText(5, text_y_position, f"{self.altitude:.1f} m")

        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 5))
        offset = 10
        for i in range(0, int(MAX_ALTITUDE) + 10, 10):
            y_position = BAR_HEIGHT_PX - (i / MAX_ALTITUDE) * BAR_HEIGHT_PX
            painter.drawText(BAR_WIDTH + offset, y_position, f"{i} m")
            painter.drawLine(BAR_WIDTH + offset - 5, y_position, BAR_WIDTH + offset, y_position)

    def set_vehicle(self, vehicle):
        self.vehicle = vehicle

