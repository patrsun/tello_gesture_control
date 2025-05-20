import cv2
import time
from djitellopy import Tello
from hand_detector import HandDetector

# Gesture to command map
gesture_map = {
    (0,0,0,0,0): "stop",
    (0,1,0,0,0): "forward",
    (0,1,1,0,0): "backward",
    (1,0,0,0,0): "right",
    (0,0,0,0,1): "left",
    (0,1,0,0,1): "up",
    (1,0,0,0,1): "down",
}

# Movement speed tuning
x_speed = 20  # forward/backward speed
y_speed = 20  # left/right speed
z_speed = 40  # up/down speed  # left/right speed

def main():
    tello = Tello()
    tello.connect()
    print("Battery:", tello.get_battery())

    tello.streamon()
    frame_read = tello.get_frame_read()

    detector = HandDetector()
    flying = False
    rc = {"x": 0, "y": 0, "z": 0, "yaw": 0}
    current_gesture = ""

    while True:
        img = frame_read.frame
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        # Default to stop motion
        rc = {"x": 0, "y": 0, "z": 0, "yaw": 0}
        current_gesture = ""

        if lmList:
            handType = detector.handType(lmList)
            fingers = detector.fingersUp(lmList, handType)
            gesture = gesture_map.get(tuple(fingers), None)
            current_gesture = gesture if gesture else "unknown"

            if flying and gesture:
                if gesture == "forward":
                    rc["x"] = x_speed
                elif gesture == "backward":
                    rc["x"] = -x_speed
                elif gesture == "right":
                    rc["y"] = y_speed
                elif gesture == "left":
                    rc["y"] = -y_speed
                elif gesture == "up":
                    rc["z"] = z_speed
                elif gesture == "down":
                    rc["z"] = -z_speed
                elif gesture == "stop":
                    rc = {"x": 0, "y": 0, "z": 0, "yaw": 0}

        if flying:
            tello.send_rc_control(rc["y"], rc["x"], rc["z"], rc["yaw"])

        # Draw gesture overlay
        cv2.putText(img, f"Gesture: {current_gesture.upper()}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Tello Gesture Control", img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            if flying:
                tello.land()
            break
        elif key == ord('t'):
            if not flying:
                tello.takeoff()
                time.sleep(2)
                flying = True
        elif key == ord('l'):
            if flying:
                tello.land()
                flying = False

    tello.streamoff()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

