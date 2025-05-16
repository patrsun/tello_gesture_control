from djitellopy import Tello
import time

def drone_controller(queue):
    tello = Tello()
    tello.connect()
    print("Battery:", tello.get_battery())
    flying = False

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
                    tello.move_forward(30)
                elif command == "backward":
                    tello.move_back(30)
                elif command == "left":
                    tello.move_left(30)
                elif command == "right":
                    tello.move_right(30)
                elif command == "up":
                    tello.move_up(30)
                elif command == "down":
                    tello.move_down(30)
                elif command == "stop":
                    tello.send_rc_control(0, 0, 0, 0)

        time.sleep(0.1)

