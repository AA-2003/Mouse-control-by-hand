import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

prev_time = 0 
curr_time = 0
maxi = 0
while True:
    sec, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handlms in results.multi_hand_landmarks:
            for id, lm in enumerate(handlms.landmark):
                print(img.shape)
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                print(id, cx, cy)
                if id == 0 or id == 4:
                    cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
                

            mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    maxi = max(maxi, int(fps))
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 
                3, (255, 0, 0), 3)


    cv2.imshow("webcam", img)
    if cv2.waitKey(5) & 0xFF == 27:
        break

print(fps)