from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import main


@contextmanager
def fake_camera(opened=True, readable=True, size=(480, 640, 3)):
    cv2 = MagicMock()
    camera = cv2.VideoCapture.return_value
    camera.isOpened.return_value = opened
    frame = SimpleNamespace(shape=size)
    camera.read.return_value = (readable, frame if readable else None)
    cv2.flip.side_effect = lambda image, _: image
    cv2.waitKey.side_effect = [-1, 27]
    cv2.getWindowProperty.return_value = 1
    tracking = MagicMock()
    detector = tracking.HandDetector.return_value
    detector.process.return_value = [(200, 200, 0)] * 21
    detector.distance.return_value = 60
    detector.angle.side_effect = lambda *points: 60 if points[0] == 5 else 120
    with patch.dict("sys.modules", {"cv2": cv2, "hand_tracking": tracking}):
        yield cv2, camera, detector, tracking


class CameraLoopTests(unittest.TestCase):
    def test_unavailable_camera_reports_error_and_releases_resources(self):
        with fake_camera(opened=False) as (cv2, camera, _, tracking):
            with self.assertRaisesRegex(RuntimeError, "Cannot open camera 2"):
                main.main(["--dry-run", "--camera", "2"])
            tracking.HandDetector.assert_not_called()
            camera.release.assert_called_once()
            cv2.destroyAllWindows.assert_called_once()

    def test_failed_frame_is_checked_before_accessing_its_shape(self):
        with fake_camera(readable=False) as (cv2, camera, detector, _):
            with self.assertRaisesRegex(RuntimeError, "Could not read a camera frame"):
                main.main(["--dry-run"])
            camera.release.assert_called_once()
            detector.close.assert_called_once()
            cv2.destroyAllWindows.assert_called_once()

    def test_preview_does_not_import_or_use_desktop_controllers(self):
        with fake_camera() as (_, camera, detector, _):
            with patch.dict("sys.modules", {"pyautogui": None, "pynput": None}):
                main.main(["--dry-run"])
            self.assertEqual(detector.process.call_count, 2)
            camera.release.assert_called_once()

    def test_held_gesture_clicks_only_once_across_frames(self):
        desktop = MagicMock()
        desktop.size.return_value = (1920, 1080)
        mouse_module = MagicMock()
        modules = {
            "pyautogui": desktop,
            "pynput": MagicMock(),
            "pynput.mouse": mouse_module,
        }
        with fake_camera(), patch.dict("sys.modules", modules):
            main.main([])
        mouse_module.Controller.return_value.click.assert_called_once_with(
            mouse_module.Button.left
        )
        desktop.screenshot.assert_not_called()

    def test_small_frames_release_the_camera_and_tracker(self):
        with fake_camera(size=(100, 100, 3)) as (_, camera, detector, _):
            with self.assertRaisesRegex(RuntimeError, "resolution"):
                main.main(["--dry-run"])
            camera.release.assert_called_once()
            detector.close.assert_called_once()

    def test_window_close_exits_without_waiting_for_escape(self):
        with fake_camera() as (cv2, _, detector, _):
            cv2.getWindowProperty.return_value = 0
            main.main(["--dry-run"])
            detector.process.assert_called_once()

    def test_cli_accepts_custom_screenshot_directory(self):
        args = main.parse_args(["--screenshot-dir", "captures", "--camera", "1"])
        self.assertEqual(args.screenshot_dir, Path("captures"))
        self.assertEqual(args.camera, 1)


if __name__ == "__main__":
    unittest.main()
