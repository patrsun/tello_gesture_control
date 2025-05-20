import time
from djitellopy import Tello

def drone_controller(queue):
    tello = Tello()
    tello.connect()
    print("Battery:", tello.get_battery())
    flying = False
    rc = {"x": 0, "y": 0, "z": 0, "yaw": 0}

    while True:
        if not queue.empty():
            command = queue.get()
            print("Received command:", command)

            if command == "takeoff" and not flying:
                tello.takeoff()
                flying = True

            elif command == "land" and flying:
                tello.land()
                flying = False

            elif flying:
                if command == "forward":
                    rc["x"] = 40
                elif command == "backward":
                    rc["x"] = -40
                elif command == "left":
                    rc["y"] = -40
                elif command == "right":
                    rc["y"] = 40
                elif command == "up":
                    rc["z"] = 40
                elif command == "down":
                    rc["z"] = -40
                elif command == "stop":
                    rc = {"x": 0, "y": 0, "z": 0, "yaw": 0}

        if flying:
            tello.send_rc_control(rc["y"], rc["x"], rc["z"], rc["yaw"])

        time.sleep(0.1)

