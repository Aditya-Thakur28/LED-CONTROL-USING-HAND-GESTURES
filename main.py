import cv2
import mediapipe as mp
import serial
import time

# Initialize Serial Communication with Arduino
arduino = serial.Serial('COM7', 9600, timeout=1)
  # Change COM port as needed
time.sleep(2)  # Give some time for the connection to establish

# Initialize Mediapipe Hand module
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Define the finger tips landmarks
FINGER_TIPS = [4, 8, 12, 16, 20]

# Start capturing video from webcam
cap = cv2.VideoCapture(0)
last_sent_time = time.time()
finger_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    new_finger_count = 0

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = hand_landmarks.landmark
            fingers_up = []

            for tip in FINGER_TIPS:
                if tip == 4:  # Thumb special case
                    if landmarks[tip].x < landmarks[tip - 1].x:
                        fingers_up.append(1)
                    else:
                        fingers_up.append(0)
                else:
                    if landmarks[tip].y < landmarks[tip - 2].y:
                        fingers_up.append(1)
                    else:
                        fingers_up.append(0)

            new_finger_count = sum(fingers_up)

    # Update finger count and send to Arduino every second
    if time.time() - last_sent_time >= 1:
        finger_count = new_finger_count
        arduino.write(f'{finger_count}\n'.encode())
        last_sent_time = time.time()

    # Display finger count
    cv2.putText(frame, f'Fingers: {finger_count}', (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("Finger Counter", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()