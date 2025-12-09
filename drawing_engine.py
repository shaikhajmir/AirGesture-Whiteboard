# core/drawing_engine.py

import numpy as np
import cv2
from typing import Optional, Tuple

from ui.config import (
    BOARD_BACKGROUND,
    TOP_BAR_HEIGHT,
    BOTTOM_MARGIN,
    SMOOTHING_ALPHA,
    MIN_DRAW_DISTANCE,
    PEN_THICKNESS,
    ERASER_THICKNESS,
    SHAPE_THICKNESS,
)

class DrawingEngine:
    """
    White canvas drawing engine with Pen, Eraser, and simple shapes.
    """

    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.canvas = np.full((height, width, 3), BOARD_BACKGROUND, dtype=np.uint8)

        self.prev_point: Optional[Tuple[int, int]] = None
        self.current_color = (0, 0, 0)
        self.eraser_mode = False

    def set_color(self, color: Tuple[int, int, int], eraser: bool = False):
        self.current_color = color
        self.eraser_mode = eraser

    def clear(self):
        self.canvas[:] = BOARD_BACKGROUND
        self.prev_point = None

    def _smooth_point(self, current: Tuple[int, int]) -> Tuple[int, int]:
        if self.prev_point is None:
            return current
        x, y = current
        px, py = self.prev_point
        sx = int(SMOOTHING_ALPHA * x + (1.0 - SMOOTHING_ALPHA) * px)
        sy = int(SMOOTHING_ALPHA * y + (1.0 - SMOOTHING_ALPHA) * py)
        return sx, sy

    def _distance(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    def _in_drawing_area(self, y: int) -> bool:
        return TOP_BAR_HEIGHT < y < (self.height - BOTTOM_MARGIN)

    def draw_freehand_step(self, point: Optional[Tuple[int, int]], drawing: bool, use_eraser: bool):
        """
        Freehand drawing for Pen and Eraser (or palm wipe).
        """
        if point is None or not drawing:
            self.prev_point = None
            return

        x, y = point
        if not self._in_drawing_area(y):
            self.prev_point = None
            return

        smoothed = self._smooth_point((x, y))

        if self.prev_point is None:
            self.prev_point = smoothed
            return

        if MIN_DRAW_DISTANCE > 0 and self._distance(smoothed, self.prev_point) < MIN_DRAW_DISTANCE:
            return

        px, py = self.prev_point
        cx, cy = smoothed

        if use_eraser or self.eraser_mode:
            color = BOARD_BACKGROUND
            thickness = ERASER_THICKNESS
        else:
            color = self.current_color
            thickness = PEN_THICKNESS

        cv2.line(self.canvas, (px, py), (cx, cy), color, thickness)
        self.prev_point = (cx, cy)

    # ---- Shapes ----

    def draw_line(self, start: Tuple[int, int], end: Tuple[int, int]):
        color = BOARD_BACKGROUND if self.eraser_mode else self.current_color
        cv2.line(self.canvas, start, end, color, SHAPE_THICKNESS)

    def draw_rect(self, start: Tuple[int, int], end: Tuple[int, int]):
        color = BOARD_BACKGROUND if self.eraser_mode else self.current_color
        cv2.rectangle(self.canvas, start, end, color, SHAPE_THICKNESS)

    def draw_circle(self, start: Tuple[int, int], end: Tuple[int, int]):
        color = BOARD_BACKGROUND if self.eraser_mode else self.current_color
        r = int(self._distance(start, end))
        cv2.circle(self.canvas, start, r, color, SHAPE_THICKNESS)

    def get_canvas(self):
        return self.canvas
