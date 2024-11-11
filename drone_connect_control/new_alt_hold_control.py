from PySide6.QtCore import QTimer
from dronekit import VehicleMode
import time

class AltHoldTakeoffController:
    def __init__(self, vehicle, target_throttle=1700, hover_throttle=1500, duration=3):
        self.vehicle = vehicle
        self.target_throttle = target_throttle
        self.hover_throttle = hover_throttle
        self.duration = duration
        self.elapsed_time = 0
        self.takeoff_timer = QTimer()
        self.takeoff_timer.timeout.connect(self.update_throttle)
        
    def start_takeoff(self):
        self.vehicle.mode = VehicleMode("ALT_HOLD")
        self.vehicle.armed = True

        while not self.vehicle.armed:
            print("Waiting for drone to be armed...")
            time.sleep(1)

        print("ALT_HOLD mode: Taking off...")
        self.elapsed_time = 0
        self.takeoff_timer.start(15000) 
    def update_throttle(self):

        if self.elapsed_time < self.duration * 1000:  
            self.vehicle.channels.overrides['3'] = self.target_throttle
            self.elapsed_time += 100
        else:
            self.vehicle.channels.overrides['3'] = self.hover_throttle
            print("Hovering at target altitude")
            self.takeoff_timer.stop()

def alt_hold_takeoff(vehicle):
    takeoff_controller = AltHoldTakeoffController(vehicle)
    takeoff_controller.start_takeoff()
