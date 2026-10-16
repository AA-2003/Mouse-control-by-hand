"""Control the mouse with webcam hand gestures."""

import argparse
import time
from datetime import datetime
from pathlib import Path

from gestures import Gesture, GestureLatch, classify_gesture, map_to_screen


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0, help="Camera index (default: 0)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview gestures without desktop actions"
    )
    parser.add_argument(
        "--screenshot-dir",
        type=Path,
        default=Path("screenshots"),
        help="Screenshot output directory (default: screenshots)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    import cv2

    from hand_tracking import HandDetector

    mouse = None
    screen_size = None
    if not args.dry_run:
        import pyautogui
        from pynput.mouse import Button, Controller

        mouse = Controller()
        screen_size = pyautogui.size()

    camera = cv2.VideoCapture(args.camera)
    detector = None
    latch = GestureLatch()
    previous_time = time.monotonic()
    try:
        if not camera.isOpened():
            raise RuntimeError(
                f"Cannot open camera {args.camera}. "
                "Check camera permissions or use --camera 1."
            )
        detector = HandDetector()
        while True:
            success, frame = camera.read()
            if not success or frame is None:
                raise RuntimeError(
                    "Could not read a camera frame. Check the webcam connection."
                )
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            if width <= 200 or height <= 200:
                raise RuntimeError(
                    "Camera resolution must be larger than 200 x 200 pixels."
                )
            cv2.rectangle(
                frame, (100, 100), (width - 100, height - 100), (100, 0, 0), 2
            )
            landmarks = detector.process(frame)
            gesture = None
            if len(landmarks) == 21:
                gesture = classify_gesture(
                    detector.distance(4, 5),
                    detector.angle(5, 6, 8),
                    detector.angle(9, 10, 12),
                )

            now = time.monotonic()
            triggered = latch.should_trigger(gesture, now)
            if not args.dry_run:
                if gesture == Gesture.MOVE:
                    mouse.position = map_to_screen(
                        *landmarks[8][:2], (width, height), screen_size
                    )
                elif triggered:
                    if gesture == Gesture.LEFT_CLICK:
                        mouse.click(Button.left)
                    elif gesture == Gesture.RIGHT_CLICK:
                        mouse.click(Button.right)
                    elif gesture == Gesture.DOUBLE_CLICK:
                        mouse.click(Button.left, 2)
                    elif gesture == Gesture.SCREENSHOT:
                        args.screenshot_dir.mkdir(parents=True, exist_ok=True)
                        filename = datetime.now().strftime(
                            "screenshot_%Y%m%d_%H%M%S_%f.png"
                        )
                        pyautogui.screenshot().save(args.screenshot_dir / filename)

            label = gesture.value if gesture else "No gesture"
            if args.dry_run:
                label = "Preview: " + label
            cv2.putText(
                frame, label, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
            )
            fps = 1 / max(now - previous_time, 1e-6)
            previous_time = now
            cv2.putText(
                frame, f"FPS: {fps:.0f} | Esc: quit", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2,
            )
            cv2.imshow("Hand gesture mouse", frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break
            if cv2.getWindowProperty(
                "Hand gesture mouse", cv2.WND_PROP_VISIBLE
            ) < 1:
                break
    finally:
        camera.release()
        if detector is not None:
            detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except (RuntimeError, ImportError) as error:
        raise SystemExit(str(error)) from None
