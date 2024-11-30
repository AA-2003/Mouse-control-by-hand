import cv2 
import time 
import HandTrackingModule as htm
from pynput.mouse import Controller, Button
import pyautogui

screenWidth, screenHeight = pyautogui.size()
 
def detect_gesture(img, lms, detector, mouse):
    if len(lms) != 21:
        return None
    
    h, w, c = img.shape
    index_finger_tip = lms[8]
    middle_finger_tip = lms[12]
    index_finger_angle = detector.findAngel(5, 6, 8)
    middle_finger_angle = detector.findAngel(9, 10, 12)
    index_middle_distance = detector.findDistance(8, 12, img)[0]
    thumb_dis = detector.findDistance(4, 5, img)[0]
 
    # move mouse by index finger
    if thumb_dis < 50 and index_finger_angle > 90:
        x = int((index_finger_tip[1]-100)/(w-200) * screenWidth )
        y = int((index_finger_tip[2]-100)/(h-200) * screenHeight )
        mouse.position = (x, y)

    # double click
    elif thumb_dis > 50 and index_finger_angle < 90 and middle_finger_angle < 90 :
        mouse.click(Button.left, 2)
        cv2.putText(img, "double click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # left click
    elif thumb_dis > 50 and index_finger_angle < 90 and middle_finger_angle > 90:
        mouse.press(Button.left)
        time.sleep(0.1)
        mouse.release(Button.left)
        cv2.putText(img, "left click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # right click
    elif thumb_dis > 50 and index_finger_angle > 90 and middle_finger_angle < 90:
        mouse.press(Button.right)
        time.sleep(0.1)
        mouse.release(Button.right)
        cv2.putText(img, "right click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # screenshot
    elif thumb_dis < 50 and index_finger_angle < 90 and middle_finger_angle < 90:
        im1 = pyautogui.screenshot()
        im1.save(f'screenshot.png')
        cv2.putText(img, "Screenshot Taken", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    




def main():
    cap = cv2.VideoCapture(0) 
    detector = htm.handDetector()	
    mouse = Controller()
    pTime = 0
    cTime = 0
    try:
        while cap.isOpened():
            sec , img = cap.read()
            h, w, c = img.shape
            if not sec:
                break
            img = cv2.flip(img, 1)
            cv2.rectangle(img , (100 , 100) , (w-100 , h-100) , (100 , 0 , 0) , 3)

            img = detector.findHands(img , True) 
            lms = detector.findPosition(img) 
            detect_gesture(img, lms, detector, mouse)

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
 
            cv2.putText(img, str(int(fps)), (10, 20), cv2.FONT_HERSHEY_PLAIN, 2,
                        (255, 0, 255), 2)

            cv2.imshow('cam' , img)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    finally:
          cap.release()
          cv2.destroyAllWindows()


if __name__ == "__main__":
    main()