import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch


class TrackingTests(unittest.TestCase):
    def setUp(self):
        self.cv2 = MagicMock()
        self.mp = MagicMock()
        spec = importlib.util.spec_from_file_location(
            "tracking_under_test", Path(__file__).resolve().parents[1] / "hand_tracking.py"
        )
        module = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"cv2": self.cv2, "mediapipe": self.mp}):
            spec.loader.exec_module(module)
        self.detector = module.HandDetector()

    def test_angle_wraps_across_negative_and_positive_180_degrees(self):
        self.detector.landmarks = [(-100, 10, 0), (0, 0, 0), (-100, -10, 0)]
        self.assertAlmostEqual(self.detector.angle(0, 1, 2), 11.421186, places=5)

    def test_original_depth_heuristic_is_preserved(self):
        self.detector.landmarks = [(0, 0, -0.01), (3, 4, 0)]
        self.assertEqual(self.detector.distance(0, 1), 10)
        self.detector.landmarks[0] = (0, 0, -0.1)
        self.assertEqual(self.detector.distance(0, 1), 5)

    def test_lost_hand_clears_landmarks_from_previous_frame(self):
        self.detector.landmarks = [(1, 2, 3)] * 21
        self.detector._hands.process.return_value = SimpleNamespace(
            multi_hand_landmarks=None
        )
        self.assertEqual(self.detector.process(SimpleNamespace(shape=(480, 640, 3))), [])


if __name__ == "__main__":
    unittest.main()
