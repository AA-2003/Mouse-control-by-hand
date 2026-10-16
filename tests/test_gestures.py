import unittest

from gestures import Gesture, GestureLatch, classify_gesture, map_to_screen


class GestureTests(unittest.TestCase):
    def test_supported_gestures(self):
        examples = [
            ((40, 120, 120), Gesture.MOVE),
            ((40, 120, 60), Gesture.MOVE),
            ((60, 60, 120), Gesture.LEFT_CLICK),
            ((60, 120, 60), Gesture.RIGHT_CLICK),
            ((60, 60, 60), Gesture.DOUBLE_CLICK),
            ((40, 60, 60), Gesture.SCREENSHOT),
            ((60, 120, 120), None),
        ]
        for measurements, expected in examples:
            with self.subTest(measurements=measurements):
                self.assertEqual(classify_gesture(*measurements), expected)

    def test_ambiguous_thresholds_are_neutral(self):
        for measurements in [(50, 60, 60), (60, 90, 60), (60, 60, 90)]:
            with self.subTest(measurements=measurements):
                self.assertIsNone(classify_gesture(*measurements))

    def test_held_click_and_screenshot_never_repeat(self):
        for gesture in [Gesture.LEFT_CLICK, Gesture.SCREENSHOT]:
            with self.subTest(gesture=gesture):
                latch = GestureLatch()
                self.assertTrue(latch.should_trigger(gesture, 0))
                for now in [0.01, 0.6, 10]:
                    self.assertFalse(latch.should_trigger(gesture, now))

    def test_release_rearms_action_but_keeps_cooldown(self):
        latch = GestureLatch()
        self.assertTrue(latch.should_trigger(Gesture.LEFT_CLICK, 0))
        self.assertFalse(latch.should_trigger(None, 0.1))
        self.assertFalse(latch.should_trigger(Gesture.LEFT_CLICK, 0.2))
        self.assertTrue(latch.should_trigger(Gesture.LEFT_CLICK, 0.5))

    def test_movement_rearms_and_changed_action_waits_for_cooldown(self):
        latch = GestureLatch()
        self.assertTrue(latch.should_trigger(Gesture.SCREENSHOT, 0))
        self.assertFalse(latch.should_trigger(Gesture.RIGHT_CLICK, 0.1))
        self.assertTrue(latch.should_trigger(Gesture.RIGHT_CLICK, 0.5))
        self.assertFalse(latch.should_trigger(Gesture.MOVE, 0.6))
        self.assertTrue(latch.should_trigger(Gesture.RIGHT_CLICK, 1))

    def test_screen_mapping_clamps_points_outside_camera_rectangle(self):
        frame, screen = (640, 480), (1920, 1080)
        self.assertEqual(map_to_screen(-100, -100, frame, screen), (0, 0))
        self.assertEqual(map_to_screen(1000, 1000, frame, screen), (1919, 1079))
        x, y = map_to_screen(320, 240, frame, screen)
        self.assertLessEqual(abs(x - 960), 1)
        self.assertLessEqual(abs(y - 540), 1)

    def test_tiny_camera_frames_are_rejected(self):
        with self.assertRaises(ValueError):
            map_to_screen(0, 0, (200, 480), (1920, 1080))


if __name__ == "__main__":
    unittest.main()
