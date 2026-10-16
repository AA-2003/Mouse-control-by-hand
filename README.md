# Mouse Control by Hand

Control the pointer, click, and take screenshots using webcam hand gestures.

## Setup

Requires a webcam and 64-bit Python 3.11 or 3.12.

```bash
git clone https://github.com/AA-2003/Mouse-control-by-hand.git
cd Mouse-control-by-hand
python -m venv .venv
```

Activate with `.\.venv\Scripts\Activate.ps1` on Windows, or
`source .venv/bin/activate` on macOS / Linux (X11).

```bash
python -m pip install -r requirements.txt
python main.py --dry-run
```

Preview mode shows gestures without performing desktop actions. Run
`python main.py` to enable mouse control. Press **Esc**, close the camera
window, or press **Ctrl+C** to quit.

Options: `--camera 1` selects another webcam;
`--screenshot-dir captures` changes the screenshot directory.

MediaPipe is pinned to 0.10.21 for the legacy Hands API. Linux Wayland
is not supported.

## Gestures

| Action | Thumb near index knuckle | Index finger | Middle finger |
| --- | --- | --- | --- |
| Move pointer | Yes | Extended | Any |
| Left click | No | Bent | Extended |
| Right click | No | Extended | Bent |
| Double click | No | Bent | Bent |
| Screenshot | Yes | Bent | Bent |

Move the index fingertip inside the rectangle. Clicks and screenshots fire
once per held gesture, with a 0.5-second cooldown. Release the gesture before
repeating it. Screenshots are saved in `screenshots/`.

## Tests

```bash
python -m unittest discover -s tests -v
```

CI checks Windows with Python 3.11 and 3.12. Webcam tracking and desktop
actions need manual testing.
