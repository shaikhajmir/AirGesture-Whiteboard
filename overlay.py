# ui/overlay.py

import cv2
from ui.config import (
    TOP_BAR_HEIGHT,
    TOOL_ITEMS,
    COLOR_ITEMS,
    TOP_BAR_BG,
    TOP_BAR_SPLIT_COLOR,
    FONT,
    FONT_SCALE_SMALL,
    FONT_THICKNESS,
    FONT_THICKNESS_BOLD,
    CAM_PREVIEW_SCALE,
    CAM_PREVIEW_MARGIN,
    CAM_PREVIEW_BORDER_COLOR,
    CAM_PREVIEW_BORDER_THICKNESS,
)

def draw_top_bar(board, selected_tool_idx: int, selected_color_idx: int):
    """
    Single slim top bar with tools on left and colors on right.
    """
    h, w, _ = board.shape

    # Background bar
    cv2.rectangle(board, (0, 0), (w, TOP_BAR_HEIGHT), TOP_BAR_BG, cv2.FILLED)

    # Split: left = tools, right = colors
    split_x = int(w * 0.55)  # 55% for tools, 45% for colors
    cv2.line(board, (split_x, 0), (split_x, TOP_BAR_HEIGHT), TOP_BAR_SPLIT_COLOR, 1)

    # ---- Tools (left) ----
    tool_area_width = split_x
    tool_item_width = tool_area_width // len(TOOL_ITEMS)

    for i, name in enumerate(TOOL_ITEMS):
        x1 = i * tool_item_width
        x2 = (i + 1) * tool_item_width

        if i == selected_tool_idx:
            bg = (55, 55, 90)
            thickness = FONT_THICKNESS_BOLD
        else:
            bg = (45, 45, 45)
            thickness = FONT_THICKNESS

        cv2.rectangle(board, (x1, 0), (x2, TOP_BAR_HEIGHT), bg, cv2.FILLED)

        text_size, _ = cv2.getTextSize(name, FONT, FONT_SCALE_SMALL, thickness)
        text_w, text_h = text_size
        text_x = x1 + (tool_item_width - text_w) // 2
        text_y = TOP_BAR_HEIGHT // 2 + text_h // 2

        cv2.putText(
            board,
            name,
            (text_x, text_y),
            FONT,
            FONT_SCALE_SMALL,
            (255, 255, 255),
            thickness,
        )

    # ---- Colors (right) ----
    color_area_width = w - split_x
    color_item_width = color_area_width // len(COLOR_ITEMS)

    for i, (name, bgr) in enumerate(COLOR_ITEMS):
        cx_center = split_x + i * color_item_width + color_item_width // 2
        cy_center = TOP_BAR_HEIGHT // 2

        radius = min(color_item_width, TOP_BAR_HEIGHT) // 3

        if i == selected_color_idx:
            # Outer ring highlight
            cv2.circle(board, (cx_center, cy_center), radius + 6, (255, 255, 255), 2)

        cv2.circle(board, (cx_center, cy_center), radius, bgr, cv2.FILLED)

def hit_test_tool(x: int, y: int, width: int):
    """
    If (x, y) is inside tools area, return tool index else None.
    """
    if y < 0 or y > TOP_BAR_HEIGHT:
        return None

    split_x = int(width * 0.55)
    if x >= split_x:
        return None

    tool_area_width = split_x
    item_width = tool_area_width // len(TOOL_ITEMS)
    idx = x // item_width
    if 0 <= idx < len(TOOL_ITEMS):
        return idx
    return None

def hit_test_color(x: int, y: int, width: int):
    """
    If (x, y) is inside colors area, return color index else None.
    """
    if y < 0 or y > TOP_BAR_HEIGHT:
        return None

    split_x = int(width * 0.55)
    if x < split_x:
        return None

    color_area_width = width - split_x
    item_width = color_area_width // len(COLOR_ITEMS)
    idx = (x - split_x) // item_width
    if 0 <= idx < len(COLOR_ITEMS):
        return idx
    return None

def draw_camera_preview(board, cam_frame):
    """
    Draw a small camera preview in bottom-right corner.
    """
    if cam_frame is None:
        return

    h, w, _ = board.shape
    ch, cw, _ = cam_frame.shape

    target_w = int(w * CAM_PREVIEW_SCALE)
    if target_w <= 0:
        return

    scale = target_w / cw
    target_h = int(ch * scale)

    x2 = w - CAM_PREVIEW_MARGIN
    x1 = x2 - target_w
    y2 = h - CAM_PREVIEW_MARGIN
    y1 = y2 - target_h

    cam_resized = cv2.resize(cam_frame, (target_w, target_h))

    cv2.rectangle(
        board,
        (x1 - 2, y1 - 2),
        (x2 + 2, y2 + 2),
        CAM_PREVIEW_BORDER_COLOR,
        CAM_PREVIEW_BORDER_THICKNESS,
    )

    board[y1:y2, x1:x2] = cam_resized
