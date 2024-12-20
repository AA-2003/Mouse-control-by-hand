import cv2
import mediapipe as mp
import time
import math
import numpy as np 

class handDetector():
    def __init__(self, mode=False, maxHands=1, complexity = 1 , detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.complexity = complexity 
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.complexity , 
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None
 
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
 
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img
 
    def findPosition(self, img, handNo=0, draw=True):
        # if not self.results:
        #     img = self.findHands(img)
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                radius = int(lm.z)*2
                self.lmList.append([id, cx, cy, lm.z])

                if draw:
                    cv2.circle(img, (cx, cy), radius, (255, 0, 0), cv2.FILLED)
 
        return self.lmList

    def findDistance(self, p1, p2, img, draw=True):
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        z = self.lmList[p1][3]
        # radius = int(self.lmList[p1][0])*2
        # if draw:
        #     cv2.circle(img, (x1, y1), radius, (255, 0, 255), cv2.FILLED)
        #     cv2.circle(img, (x2, y2), radius, (255, 0, 255), cv2.FILLED)
        #     cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        #     cv2.circle(img, (cx, cy), radius, (255, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1) 
        if abs(z) < 0.05 :
            length *= 2

        return length, img, [x1, y1, x2, y2, cx, cy]
    def findAngel(self, p1, p2, p3):
        a = [self.lmList[p1][1], self.lmList[p1][2]]
        b = [self.lmList[p2][1], self.lmList[p2][2]]
        c = [self.lmList[p3][1], self.lmList[p3][2]]
        
        radians = np.arctan2(c[1]-b[1], c[0] - b[0]) - np.arctan2(a[1]-b[1],a[0]-b[0])
        angel = np.abs(np.degrees(radians))
        return angel

 
def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])
 
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
 
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
 
        cv2.imshow("Image", img)
        if cv2.waitKey(5) & 0xFF == 27:
            break
 
if __name__ == "__main__":
    main()
