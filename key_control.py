from dronekit import VehicleMode
from pymavlink import mavutil
from PySide6.QtCore import Qt

def handle_alt_hold_keys(event, vehicle):
    pitch = 1500
    roll = 1500
    throttle = 1550  
    yaw = 1500

    if event.key() == Qt.Key_W:
        pitch = 1300  
    elif event.key() == Qt.Key_S:
        pitch = 1700  
    elif event.key() == Qt.Key_A:
        roll = 1300  
    elif event.key() == Qt.Key_D:
        roll = 1700  
    elif event.key() == Qt.Key_Q:
        throttle = 1800  
    elif event.key() == Qt.Key_E:
        throttle = 1350  
    elif event.key() == Qt.Key_F:
        yaw = 1600  
    elif event.key() == Qt.Key_R:
        yaw = 1400  

    throttle = max(1500, min(throttle, 1700))

    vehicle.channels.overrides = {
        '1': roll,        
        '2': pitch,       
        '3': throttle,    
        '4': yaw          
    }

def clear_alt_hold_override(vehicle):
    vehicle.channels.overrides = {
        '1': 1500,  
        '2': 1500,  
        '3': 1550,  
        '4': 1500  
    }

def send_ned_velocity(vehicle, vx, vy, vz):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,
        0, 0,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0,
        0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()

def handle_guided_keys(event, vehicle):
    vx, vy, vz = 0, 0, 0
    if event.key() == Qt.Key_W:
        vx = 2
    elif event.key() == Qt.Key_S:
        vx = -2
    elif event.key() == Qt.Key_A:
        vy = -2
    elif event.key() == Qt.Key_D:
        vy = 2
    elif event.key() == Qt.Key_Q:
        vz = -2
    elif event.key() == Qt.Key_E:
        vz = 2
    send_ned_velocity(vehicle, vx, vy, vz)

def stop_guided_movement(vehicle):
    send_ned_velocity(vehicle, 0, 0, 0)
