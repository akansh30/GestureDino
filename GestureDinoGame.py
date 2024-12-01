import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Initialize Mediapipe and camera
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

# Helper function to check if fingers are up
def fingers_up(hand_landmarks):
    fingers = []
    landmarks = hand_landmarks.landmark
    tips = [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP,
            mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP,
            mp_hands.HandLandmark.PINKY_TIP]

    for i, tip in enumerate(tips):
        if i == 0:  # Thumb
            fingers.append(landmarks[tip].x < landmarks[mp_hands.HandLandmark.THUMB_IP].x)  # Adjust for hand orientation
        else:  # Other fingers
            fingers.append(landmarks[tip].y < landmarks[tip - 2].y)  # Compare tip with pip
    return fingers

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get fingers up
            fingers = fingers_up(hand_landmarks)

            # Check for pinch gesture
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            pinch_distance = abs(thumb_tip.x - index_tip.x) + abs(thumb_tip.y - index_tip.y)
            if pinch_distance < 0.05:  # Pinch detected
                pyautogui.press("space")  # Simulate spacebar press for jumping
                cv2.putText(frame, "Pinch - Jump!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Check for higher jump with 5 fingers
            elif all(fingers):  # All fingers are up
                pyautogui.keyDown("up")  # Simulate higher jump
                cv2.putText(frame, "Five Fingers - Higher Jump!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            # Check for duck with index finger only
            elif fingers == [False, True, False, False, False]:  # Only index finger is up
                pyautogui.keyDown("down")  # Simulate duck
                cv2.putText(frame, "Index Finger - Duck!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the video feed
    cv2.putText(frame, "Pinch: Jump | 5 Fingers: Higher Jump | Index: Duck", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.imshow("Gesture Controlled Dino Game", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
