from enum import Enum


class Gesture(Enum):
    MOVE = "Move pointer"
    LEFT_CLICK = "Left click"
    RIGHT_CLICK = "Right click"
    DOUBLE_CLICK = "Double click"
    SCREENSHOT = "Screenshot"


def classify_gesture(thumb_distance, index_angle, middle_angle):
    if thumb_distance < 50 and index_angle > 90:
        return Gesture.MOVE
    if thumb_distance > 50:
        if index_angle < 90 and middle_angle < 90:
            return Gesture.DOUBLE_CLICK
        if index_angle < 90 and middle_angle > 90:
            return Gesture.LEFT_CLICK
        if index_angle > 90 and middle_angle < 90:
            return Gesture.RIGHT_CLICK
    if thumb_distance < 50 and index_angle < 90 and middle_angle < 90:
        return Gesture.SCREENSHOT
    return None


class GestureLatch:
    """Trigger once per held gesture, subject to cooldown."""

    def __init__(self, cooldown=0.5):
        if cooldown < 0:
            raise ValueError("Cooldown must be non-negative.")
        self.cooldown = cooldown
        self._active = None
        self._last_trigger = float("-inf")

    def should_trigger(self, gesture, now):
        if gesture in (None, Gesture.MOVE):
            self._active = gesture
            return False
        if gesture == self._active or now - self._last_trigger < self.cooldown:
            return False
        self._active = gesture
        self._last_trigger = now
        return True


def map_to_screen(x, y, frame_size, screen_size, margin=100):
    width, height = frame_size
    screen_width, screen_height = screen_size
    if width <= 2 * margin or height <= 2 * margin:
        raise ValueError("Camera frame is too small for the tracking area.")
    screen_x = round((x - margin) / (width - 2 * margin) * (screen_width - 1))
    screen_y = round((y - margin) / (height - 2 * margin) * (screen_height - 1))
    return (
        max(0, min(screen_width - 1, screen_x)),
        max(0, min(screen_height - 1, screen_y)),
    )
