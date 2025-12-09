# ui/config.py

"""
Clean minimal configuration for Air Draw Studio v3 – tuned for responsiveness.
"""

# ---------- WINDOW / BOARD ----------

WINDOW_NAME = "Air Draw Studio"

BOARD_BACKGROUND = (255, 255, 255)  # pure white

TOP_BAR_HEIGHT = 60   # tools + colors
BOTTOM_MARGIN = 10    # bottom safe area

# ---------- TOOLS & COLORS ----------

TOOL_ITEMS = [
    "Pen",
    "Eraser",
    "Line",
    "Rect",
    "Circle",
]

COLOR_ITEMS = [
    ("Black",  (0, 0, 0)),
    ("Blue",   (255, 0, 0)),
    ("Green",  (0, 255, 0)),
    ("Red",    (0, 0, 255)),
    ("Purple", (255, 0, 255)),
]

PEN_THICKNESS = 4
ERASER_THICKNESS = 40
SHAPE_THICKNESS = 3

# ---------- HAND / GESTURES ----------

MAX_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# ⚠️ More responsive writing:
SMOOTHING_ALPHA = 0.2      # small = less lag
MIN_DRAW_DISTANCE = 0      # draw even tiny movements

# ---------- UI LOOK ----------

FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE_SMALL = 0.5
FONT_THICKNESS = 1
FONT_THICKNESS_BOLD = 2

TOP_BAR_BG = (25, 25, 25)
TOP_BAR_SPLIT_COLOR = (60, 60, 60)

CURSOR_COLOR = (0, 200, 255)
CURSOR_RADIUS = 9
CURSOR_THICKNESS = 2

# ---------- CAMERA PREVIEW ----------

CAM_PREVIEW_SCALE = 0.2      # % of board width
CAM_PREVIEW_MARGIN = 12
CAM_PREVIEW_BORDER_COLOR = (60, 60, 60)
CAM_PREVIEW_BORDER_THICKNESS = 2
