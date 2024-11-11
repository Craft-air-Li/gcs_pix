from drone_connection import connect_to_drone
from PySide6.QtWidgets import (QLabel, QCheckBox, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QButtonGroup)

class DroneConnectionPanel(QWidget):
    def __init__(self, connect_callback):
        super().__init__()

        self.setFixedSize(480, 150) 

        self.connect_callback = connect_callback

        self.connection_label = QLabel("Connection Type:")

        self.serial_checkbox = QCheckBox("Serial")
        self.tcp_checkbox = QCheckBox("TCP")

        self.connection_group = QButtonGroup(self)
        self.connection_group.addButton(self.serial_checkbox)
        self.connection_group.addButton(self.tcp_checkbox)
        
        self.connection_group.buttonClicked.connect(self.update_connection_input)

        self.port_label = QLabel("Port/IP:")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter port (Serial) or IP (TCP)")

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_drone)

        layout = QVBoxLayout()
        layout.addWidget(self.connection_label)
        
        connection_type_layout = QHBoxLayout()
        connection_type_layout.addWidget(self.serial_checkbox)
        connection_type_layout.addWidget(self.tcp_checkbox)
        layout.addLayout(connection_type_layout)

        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.connect_button)

        layout.addStretch()
        self.setLayout(layout)

    def update_connection_input(self, button):
        if button == self.serial_checkbox:
            self.port_input.setPlaceholderText("Enter COM port (e.g., COM5)")
        elif button == self.tcp_checkbox:
            self.port_input.setPlaceholderText("Enter IP address (e.g., 192.168.0.10)")

    def connect_drone(self):
        connection_type = ""
        connection_value = self.port_input.text()

        if self.serial_checkbox.isChecked():
            connection_type = "Serial"
        elif self.tcp_checkbox.isChecked():
            connection_type = "TCP"
        else:
            print("Please select a connection type.")
            return

        if connection_value:
            vehicle = connect_to_drone(connection_type, connection_value)
            self.connect_callback(vehicle)
        else:
            print("Please enter the required information.")
