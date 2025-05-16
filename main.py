import cv2
import time
from multiprocessing import Process, Queue
from hand_detector import HandDetector
from controller import drone_controller

gesture_map = {
    (1,1,1,1,1): "takeoff",
    (0,0,0,0,0): "stop",
    (0,1,0,0,0): "forward",
    (0,1,1,0,0): "backward",
    (1,0,0,0,0): "right",
    (0,0,0,0,1): "left",
    (0,1,0,0,1): "up",
    (1,0,0,0,1): "down",
    (1,1,1,1,1): "land"
}

def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    queue = Queue()

    # Start command process
    command_proc = Process(target=drone_controller, args=(queue,))
    command_proc.start()

    lastGestureTime = 0
    cooldown = 1.5

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, _ = detector.findPosition(img)

        if lmList:
            handType = detector.handType(lmList)
            fingers = detector.fingersUp(lmList, handType)
            gesture = gesture_map.get(tuple(fingers), None)
            now = time.time()

            if gesture and now - lastGestureTime > cooldown:
                print("Gesture:", fingers, "→", gesture)
                queue.put(gesture)
                lastGestureTime = now
                cv2.putText(img, gesture.upper(), (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        cv2.imshow("Tello Gesture Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            queue.put("land")
            break

    cap.release()
    cv2.destroyAllWindows()
    command_proc.terminate()

if __name__ == "__main__":
    main()

