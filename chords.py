from collections import deque
import cv2
import mediapipe as mp


class ChordDetector:

    def __init__(self):

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,  # Reduced from 0.7 for faster detection
            min_tracking_confidence=0.5,   # Reduced from 0.7 for faster detection
        )

        self.current_chord = "None"
        self.last_seen = "None"
        self.frame_count = 0
        self.ready = True
        self.chord_history = deque(maxlen=2)  # For faster stabilization

    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        chord = "None"

        if results.multi_hand_landmarks:

            hand = results.multi_hand_landmarks[0]

            self.mp_draw.draw_landmarks(
                frame, hand, self.mp_hands.HAND_CONNECTIONS
            )

            lm = hand.landmark

            # Using more reliable finger detection
            thumb = lm[4].x < lm[3].x
            index = lm[8].y < lm[6].y
            middle = lm[12].y < lm[10].y
            ring = lm[16].y < lm[14].y
            pinky = lm[20].y < lm[18].y

            gesture = (thumb, index, middle, ring, pinky)

            if gesture == (False, True, False, False, False):
                chord = "G"

            elif gesture == (False, True, True, False, False):
                chord = "D"

            elif gesture == (False, True, True, True, False):
                chord = "E"

            elif gesture == (False, True, True, True, True):
                chord = "C"

            elif gesture == (True, True, True, True, True):
                chord = "Em"

            elif gesture == (True, True, False, False, False):
                chord = "F"

            elif gesture == (True, False, False, False, True):
                chord = "Am"
                
            elif gesture == (False, True, False, False, True):
                chord = "Bm"
                
            elif gesture == (False, False, True, True, True):
                chord = "B"
                
            elif gesture == (False, False, False, True, True):
                chord = "Dm"

        # -------------------------
        # Faster Chord Stabilization
        # -------------------------
        # Keep history of last 2 detections
        self.chord_history.append(chord)
        
        # If we have 2 consistent detections, update chord immediately
        if len(self.chord_history) == 2 and self.chord_history[0] == self.chord_history[1]:
            previous_chord = self.current_chord
            self.current_chord = chord
            
            # Determine if we should play sound
            if self.current_chord != "None" and (self.current_chord != previous_chord or self.ready):
                play_sound = True
                self.ready = False
            else:
                play_sound = False
        else:
            play_sound = False

        # Reset ready state when no chord is detected
        if self.current_chord == "None":
            self.ready = True

        cv2.putText(
            frame,
            f"Chord: {self.current_chord}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        return frame, self.current_chord, play_sound
