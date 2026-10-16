"""Small wrapper around MediaPipe's legacy Hands solution."""

import math

import cv2
import mediapipe as mp


class HandDetector:
    """Track one hand and expose its pixel coordinates and joint angles."""

    def __init__(self):
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarks = []

    def process(self, frame):
        """Draw the detected hand and return its 21 landmarks, or an empty list."""
        result = self._hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.landmarks = []
        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            height, width = frame.shape[:2]
            self.landmarks = [
                (int(point.x * width), int(point.y * height), point.z)
                for point in hand.landmark
            ]
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand, mp.solutions.hands.HAND_CONNECTIONS
            )
        return self.landmarks

    def distance(self, first, second):
        """Return pixel distance using the original project's depth heuristic."""
        x1, y1, depth = self.landmarks[first]
        x2, y2, _ = self.landmarks[second]
        distance = math.hypot(x2 - x1, y2 - y1)
        return distance * 2 if abs(depth) < 0.05 else distance

    def angle(self, first, joint, last):
        """Return the smaller joint angle in degrees (0 through 180)."""
        ax, ay, _ = self.landmarks[first]
        bx, by, _ = self.landmarks[joint]
        cx, cy, _ = self.landmarks[last]
        radians = math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx)
        degrees = abs(math.degrees(radians)) % 360
        return min(degrees, 360 - degrees)

    def close(self):
        self._hands.close()
