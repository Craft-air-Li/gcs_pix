import os
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QTransform

class HeadingIndicator(QWidget):
    def __init__(self, parent=None):
        super(HeadingIndicator, self).__init__(parent)
        self.heading = 0  

        current_dir = os.path.dirname(os.path.abspath(__file__))
        needle_image_path = os.path.join(current_dir, "image/com_needle.png")
        background_image_path = os.path.join(current_dir, "image/com_back.png")

        self.needle_image = QPixmap(needle_image_path)
        self.background_image = QPixmap(background_image_path)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.heading_label = QLabel(self)
        self.heading_label.setAlignment(Qt.AlignCenter)
        self.heading_label.setStyleSheet("color: white; font-size: 10px; background-color: transparent; font-weight: bold;")
        self.heading_label.setFixedSize(30, 30)
        self.update_heading(0)  

    def update_heading(self, heading=None):
        self.heading = int(heading) if heading is not None else 0
        self.heading_label.setText(f"{self.heading}*")
        self.update()

    def resizeEvent(self, event):
        self.heading_label.move(self.width() // 2 - self.heading_label.width() // 2, self.height() // 2 - self.heading_label.height() // 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        center = self.rect().center()

        bg_size = min(self.width(), self.height())
        painter.drawPixmap(center.x() - bg_size // 2, center.y() - bg_size // 2, bg_size, bg_size, self.background_image)

        painter.save()
        painter.translate(center.x(), center.y())
        painter.rotate(self.heading)
        needle_size = 380  
        painter.drawPixmap(-needle_size // 2, -needle_size // 2, needle_size, needle_size, self.needle_image)
        painter.restore()

    def reset_heading(self):
        self.update_heading(0)
