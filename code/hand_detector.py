import cv2
import time
import math
import mediapipe as mp
from djitellopy import Tello

# Hand detector class
class HandDetector:
    def __init__(self, maxHands=1, detectionCon=0.8, trackCon=0.5):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            max_num_hands=maxHands,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        xList, yList = [], []
        bbox = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            h, w, _ = img.shape
            for id, lm in enumerate(myHand.landmark):
                px, py = int(lm.x * w), int(lm.y * h)
                lmList.append((id, px, py))
                xList.append(px)
                yList.append(py)
                if draw:
                    cv2.circle(img, (px, py), 5, (255, 0, 255), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = (xmin, ymin, xmax - xmin, ymax - ymin)
            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)
        return lmList, bbox

    def fingersUp(self, lmList, handType="Right"):
        fingers = []
        tipIds = [4, 8, 12, 16, 20]

        if handType == "Right":
            fingers.append(1 if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1] else 0)
        else:
            fingers.append(1 if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1] else 0)

        for id in range(1, 5):
            fingers.append(1 if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2] else 0)

        return fingers

    def handType(self, lmList):
        if len(lmList) < 18:
            return "Unknown"
        return "Right" if lmList[17][1] < lmList[5][1] else "Left"

# Main recognition loop with drone integration
def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    tello = Tello()
    tello.connect()
    print("Battery:", tello.get_battery())

    flying = False
    lastGestureTime = 0
    cooldown = 1.5

    gestureActions = {
        (1,1,1,1,1): "takeoff_or_land",
        (0,0,0,0,0): "stop",
        (0,1,0,0,0): "forward",
        (0,1,1,0,0): "backward",
        (1,0,0,0,0): "right",
        (0,0,0,0,1): "left",
        (0,1,0,0,1): "up",
        (1,0,0,0,1): "down"
    }

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        if lmList:
            handType = detector.handType(lmList)
            fingers = detector.fingersUp(lmList, handType)
            fingerTuple = tuple(fingers)
            action = gestureActions.get(fingerTuple, "Unknown")

            currentTime = time.time()
            if currentTime - lastGestureTime > cooldown:
                if action != "Unknown":
                    print("Gesture:", fingers, "→", action)

                    if action == "takeoff_or_land":
                        if not flying:
                            tello.takeoff()
                            flying = True
                        else:
                            tello.land()
                            flying = False

                    elif flying:
                        if action == "forward":
                            tello.move_forward(30)
                        elif action == "backward":
                            tello.move_back(30)
                        elif action == "right":
                            tello.move_right(30)
                        elif action == "left":
                            tello.move_left(30)
                        elif action == "up":
                            tello.move_up(30)
                        elif action == "down":
                            tello.move_down(30)
                        elif action == "stop":
                            tello.send_rc_control(0, 0, 0, 0)

                    lastGestureTime = currentTime

            cv2.putText(img, action.upper(), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        cv2.imshow("Gesture Drone Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if flying:
                tello.land()
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
