# core/gestures.py

from typing import List, Tuple, Dict

# Mediapipe indices
THUMB_TIP = 4
THUMB_IP  = 3
INDEX_TIP = 8
INDEX_PIP = 6
MIDDLE_TIP = 12
MIDDLE_PIP = 10
RING_TIP = 16
RING_PIP = 14
PINKY_TIP = 20
PINKY_PIP = 18

FINGER_GROUPS = {
    "index": (INDEX_TIP, INDEX_PIP),
    "middle": (MIDDLE_TIP, MIDDLE_PIP),
    "ring": (RING_TIP, RING_PIP),
    "pinky": (PINKY_TIP, PINKY_PIP),
    # thumb is weird, we can ignore or add simple check
}

def _map_landmarks(lm_list: List[Tuple[int, int, int]]) -> Dict[int, Tuple[int, int]]:
    return {idx: (x, y) for idx, x, y in lm_list}

def count_fingers_up(lm_list: List[Tuple[int, int, int]]) -> int:
    """
    Count how many fingers (index, middle, ring, pinky) are 'up'.
    Used for palm-wipe eraser: if >= 3, treat as open hand.
    """
    if not lm_list:
        return 0

    lm_map = _map_landmarks(lm_list)
    count = 0

    for tip, pip in FINGER_GROUPS.values():
        if tip in lm_map and pip in lm_map:
            _, tip_y = lm_map[tip]
            _, pip_y = lm_map[pip]
            if tip_y < pip_y:  # tip above pip
                count += 1

    return count
