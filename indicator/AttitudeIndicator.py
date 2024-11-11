import os
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPixmap, QTransform

class AttitudeIndicator(QWidget):
    def __init__(self, parent=None):
        super(AttitudeIndicator, self).__init__(parent)
        self.setFixedSize(355, 355)
        self.roll = 0  
        self.pitch = 0  
        current_dir = os.path.dirname(os.path.abspath(__file__))

        self.needle_image = QPixmap(os.path.join(current_dir, "image/background.jpg"))
        self.roll_image = QPixmap(os.path.join(current_dir, "image/roll_cover.png"))
        self.background_image = QPixmap(os.path.join(current_dir, "image/front_cover.png"))

        self.needle_image = self.needle_image.scaled(720, 720, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.roll_image = self.roll_image.scaled(381, 381, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def update_attitude(self, roll=None, pitch=None):
        self.roll = roll * 65 if roll is not None else 0
        self.pitch = pitch * 3 if pitch is not None else 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        size = min(self.width(), self.height())
        center = self.rect().center()
        pitch_offset = self.pitch * (size // 10)
        roll_angle = self.roll

        clip_radius = size // 2
        painter.setClipRegion(QRect(center.x() - clip_radius, center.y() - clip_radius, clip_radius * 2, clip_radius * 2))

        painter.save()
        painter.translate(center.x(), center.y() + pitch_offset)
        combined_transform = QTransform().rotate(-roll_angle)
        rotated_needle = self.needle_image.transformed(combined_transform, Qt.SmoothTransformation)
        painter.drawPixmap(-rotated_needle.width() // 2, -rotated_needle.height() // 2, rotated_needle)
        painter.restore()

        painter.save()
        painter.translate(center.x(), center.y())
        roll_transform = QTransform().rotate(-roll_angle)
        rotated_roll_image = self.roll_image.transformed(roll_transform, Qt.SmoothTransformation)
        painter.drawPixmap(-rotated_roll_image.width() // 2, -rotated_roll_image.height() // 2, rotated_roll_image)
        painter.restore()

        painter.drawPixmap(center.x() - 190.5, center.y() - 190.5, 381, 381, self.background_image)

    def reset_attitude(self):
        self.update_attitude(roll=0, pitch=0)
