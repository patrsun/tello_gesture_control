import cv2
import mediapipe as mp
import time
import numpy as np
from djitellopy import Tello

# Frame size
width, height = 640, 480

# PID parameters
xPID, yPID, zPID = [0.21, 0, 0.1], [0.27, 0, 0.1], [0.0015, 0, 0.05]
xTarget, yTarget, zTarget = width // 2, height // 2, 5000  # zTarget based on hand bounding box area
pTimeX, pTimeY, pTimeZ = 0, 0, 0
pErrorX, pErrorY, pErrorZ = 0, 0, 0

# Hand detection setup
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Drone setup
drone = Tello()
drone.connect()
print("Battery:", drone.get_battery())
drone.streamoff()
drone.streamon()
drone.takeoff()
drone.move_up(80)

def PIDController(PID, target, cVal, pError, pTime, I, limit=[-100, 100]):
    t = time.time() - pTime
    error = target - cVal
    P = PID[0] * error
    I += PID[1] * error * t
    D = PID[2] * (error - pError) / t if t > 0 else 0
    output = P + I + D
    output = int(np.clip(output, limit[0], limit[1]))
    return output, error, time.time(), I

def fingersUp(lmList):
    fingers = []
    if lmList[4][0] > lmList[3][0]:  # Thumb
        fingers.append(1)
    else:
        fingers.append(0)
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        fingers.append(1 if lmList[tip][1] < lmList[pip][1] else 0)
    return fingers

def apply_deadzone(val, threshold=5):
    return val if abs(val) > threshold else 0

# Main loop
while True:
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (width, height))
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    xVal = yVal = zVal = 0

    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]
        lmList = []
        for lm in handLms.landmark:
            h, w, _ = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append((cx, cy))

        fingers = fingersUp(lmList)
        tracking_active = all(f == 1 for f in fingers)

        if tracking_active:
            # Hand center (landmark 9)
            cx, cy = lmList[9]

            # Bounding box area
            x_vals = [pt[0] for pt in lmList]
            y_vals = [pt[1] for pt in lmList]
            x_min, x_max = min(x_vals), max(x_vals)
            y_min, y_max = min(y_vals), max(y_vals)
            area = (x_max - x_min) * (y_max - y_min)

            # Optional visual overlay
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.circle(img, (cx, cy), 6, (255, 255, 0), cv2.FILLED)
            cv2.putText(img, f"Area: {area}", (30, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

            # Ignore invalid areas (noise / hand too close / missing)
            if 1000 < area < 18000:
                xVal, pErrorX, pTimeX, _ = PIDController(xPID, xTarget, cx, pErrorX, pTimeX, 0)
                yVal, pErrorY, pTimeY, _ = PIDController(yPID, yTarget, cy, pErrorY, pTimeY, 0)
                zVal, pErrorZ, pTimeZ, _ = PIDController(zPID, zTarget, area, pErrorZ, pTimeZ, 0, limit=[-20, 20])

                # Apply deadzones to reduce micro-adjustments
                xVal = apply_deadzone(xVal)
                yVal = apply_deadzone(yVal)
                zVal = apply_deadzone(zVal)
            else:
                xVal = yVal = zVal = 0

    drone.send_rc_control(0, zVal, yVal, -xVal)

    # Convert to RGB for display
    imgRGB_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imshow("Drone Hand Tracking", imgRGB_display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break

drone.streamoff()
cv2.destroyAllWindows()

