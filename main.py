# main.py

import cv2

from core.hand_tracker import HandTracker
from core.drawing_engine import DrawingEngine
from core.gestures import count_fingers_up
from ui.overlay import (
    draw_top_bar,
    hit_test_tool,
    hit_test_color,
    draw_camera_preview,
)
from ui.config import (
    WINDOW_NAME,
    MAX_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    CURSOR_COLOR,
    CURSOR_RADIUS,
    CURSOR_THICKNESS,
    TOOL_ITEMS,
    COLOR_ITEMS,
    TOP_BAR_HEIGHT,
)

def get_index_tip_point(lm_list):
    for idx, x, y in lm_list:
        if idx == 8:
            return x, y
    return None

def main():
    cap = cv2.VideoCapture(0)

    # ↓ reduce resolution = less lag
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ok, frame = cap.read()
    if not ok:
        print("Error: Cannot access camera.")
        return

    h, w, _ = frame.shape

    hand_tracker = HandTracker(
        max_num_hands=MAX_HANDS,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    )
    drawing_engine = DrawingEngine(h, w)

    selected_tool_idx = 0        # Pen
    selected_color_idx = 0       # Black
    current_tool = TOOL_ITEMS[selected_tool_idx]
    current_color_name, current_color_bgr = COLOR_ITEMS[selected_color_idx]
    is_eraser_tool = (current_tool == "Eraser")
    drawing_engine.set_color(current_color_bgr, eraser=is_eraser_tool)

    # shapes
    shape_active = False
    shape_start = None
    last_shape_end = None

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)

        # ---- Hand tracking ----
        hand_tracker.process(frame)
        lm_list = hand_tracker.get_landmarks(frame, hand_no=0)
        index_point = get_index_tip_point(lm_list)

        fingers_up = count_fingers_up(lm_list)
        palm_eraser = fingers_up >= 3   # open hand = wipe

        # ---- Selection (top bar) ----
        if index_point is not None:
            x, y = index_point

            # top bar: just selection, never draw here
            if y <= TOP_BAR_HEIGHT:
                tool_idx = hit_test_tool(x, y, w)
                color_idx = hit_test_color(x, y, w)

                if tool_idx is not None:
                    selected_tool_idx = tool_idx
                    current_tool = TOOL_ITEMS[selected_tool_idx]
                    is_eraser_tool = (current_tool == "Eraser")
                    drawing_engine.set_color(current_color_bgr, eraser=is_eraser_tool)
                    shape_active = False
                    shape_start = None
                    last_shape_end = None

                if color_idx is not None:
                    selected_color_idx = color_idx
                    current_color_name, current_color_bgr = COLOR_ITEMS[selected_color_idx]
                    if not is_eraser_tool:
                        drawing_engine.set_color(current_color_bgr, eraser=False)

        # ---- Drawing area ----
        drawing_area_flag = False
        if index_point is not None:
            _, y = index_point
            if y > TOP_BAR_HEIGHT:
                drawing_area_flag = True

        # 1) Palm wipe = big eraser, overrides everything
        if palm_eraser and drawing_area_flag:
            drawing_engine.draw_freehand_step(index_point, True, use_eraser=True)
            shape_active = False
            shape_start = None
            last_shape_end = None

        else:
            # 2) Freehand tools: Pen / Eraser
            if current_tool in ("Pen", "Eraser"):
                drawing_engine.draw_freehand_step(
                    index_point,
                    drawing_area_flag,
                    use_eraser=is_eraser_tool,
                )
                shape_active = False
                shape_start = None
                last_shape_end = None

            # 3) Shape tools
            else:
                if drawing_area_flag and index_point is not None:
                    if not shape_active:
                        shape_active = True
                        shape_start = index_point
                    last_shape_end = index_point
                else:
                    if shape_active and shape_start is not None and last_shape_end is not None:
                        sx, sy = shape_start
                        ex, ey = last_shape_end
                        # Don't draw if started in top bar
                        if sy > TOP_BAR_HEIGHT and ey > TOP_BAR_HEIGHT:
                            drawing_engine.set_color(current_color_bgr, eraser=is_eraser_tool)
                            if current_tool == "Line":
                                drawing_engine.draw_line(shape_start, last_shape_end)
                            elif current_tool == "Rect":
                                drawing_engine.draw_rect(shape_start, last_shape_end)
                            elif current_tool == "Circle":
                                drawing_engine.draw_circle(shape_start, last_shape_end)
                    shape_active = False
                    shape_start = None
                    last_shape_end = None

        # ---- Build final board ----
        base = drawing_engine.get_canvas()
        board = base.copy()

        draw_top_bar(board, selected_tool_idx, selected_color_idx)

        # Shape preview
        if shape_active and shape_start is not None and last_shape_end is not None:
            sx, sy = shape_start
            ex, ey = last_shape_end
            if sy > TOP_BAR_HEIGHT and ey > TOP_BAR_HEIGHT:
                preview_color = current_color_bgr
                if current_tool == "Line":
                    cv2.line(board, (sx, sy), (ex, ey), preview_color, 1)
                elif current_tool == "Rect":
                    cv2.rectangle(board, (sx, sy), (ex, ey), preview_color, 1)
                elif current_tool == "Circle":
                    r = int(((sx - ex) ** 2 + (sy - ey) ** 2) ** 0.5)
                    cv2.circle(board, (sx, sy), r, preview_color, 1)

        # Camera preview
        draw_camera_preview(board, frame)

        # Cursor
        if index_point is not None:
            x, y = index_point
            cv2.circle(board, (x, y), CURSOR_RADIUS, CURSOR_COLOR, CURSOR_THICKNESS)

        cv2.imshow(WINDOW_NAME, board)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            drawing_engine.clear()
        elif key == ord('s'):
            cv2.imwrite("air_board_output.png", drawing_engine.get_canvas())
            print("Saved as air_board_output.png")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
