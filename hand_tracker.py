# core/hand_tracker.py

import cv2
import mediapipe as mp

class HandTracker:
    """
    Simple MediaPipe Hands wrapper.
    """

    def __init__(
        self,
        max_num_hands: int = 1,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.7,
    ) -> None:
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.results = None

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)

    def get_landmarks(self, frame, hand_no: int = 0):
        lm_list = []
        if not self.results or not self.results.multi_hand_landmarks:
            return lm_list

        if hand_no >= len(self.results.multi_hand_landmarks):
            return lm_list

        hand = self.results.multi_hand_landmarks[hand_no]
        h, w, _ = frame.shape

        for idx, lm in enumerate(hand.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append((idx, cx, cy))

        return lm_list
