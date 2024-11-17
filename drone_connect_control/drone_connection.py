from dronekit import connect

def connect_to_drone(connection_type, connection_value, wait_ready=True):
    connection_string = ""

    if connection_type == "Serial":
        connection_string = connection_value
        try:
            vehicle = connect(connection_string, wait_ready=wait_ready, baud=57600, timeout=60)
            print("Drone connected successfully!")
            return vehicle
        except Exception as e:
            print(f"Error connecting to drone: {e}")
            return None  
    elif connection_type == "TCP":
        connection_string = f"{connection_value}:14550"
        try:
            vehicle = connect(connection_string, wait_ready=wait_ready)
            print("Drone connected successfully!")
            return vehicle
        except Exception as e:
            print(f"Error connecting to drone: {e}")
            return None 

    
