import cv2
import serial
import time
import ctypes
import pyautogui
import csv
import os
from datetime import datetime

# --- CONFIGURATION ---
PORT = "COM9"
PASSIVE_TIMEOUT = 60
STUDENT_ID = "S001"  # change per student machine

esp32 = serial.Serial(PORT, 115200, timeout=0.1)
time.sleep(2)
esp32.write(b'S')

# --- CSV SETUP ---
file_name = "data/distraction_log.csv"
os.makedirs("data", exist_ok=True)

if not os.path.exists(file_name):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Student_ID", "Status", "Distraction_Count", "Session_Type", "Archetype"])

def trigger_pop_up():
    ctypes.windll.user32.MessageBoxW(0, "Get Back to Work!", "Distraction Alert", 0x30 | 0x1000)
    esp32.reset_input_buffer()
    esp32.write(b'C')

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(1)

last_mouse_pos = pyautogui.position()
last_motion_time = time.time()
distraction_count = 0

try:
    while cap.isOpened():
        time.sleep(2)

        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        face_visible = len(faces) > 0

        # MOUSE LOGIC
        current_mouse_pos = pyautogui.position()
        if current_mouse_pos != last_mouse_pos:
            last_motion_time = time.time()
            last_mouse_pos = current_mouse_pos

        seconds_since_motion = time.time() - last_motion_time

        # --- REFINED LOGIC ---
        if not face_visible:
            status = "DISTRACTED"
            distraction_type = "NO_FACE"
            esp32.write(b'D')
        elif seconds_since_motion > PASSIVE_TIMEOUT:
            status = "DISTRACTED"
            distraction_type = "PASSIVE"
            esp32.write(b'D')
        else:
            status = "FOCUSED"
            distraction_type = "NONE"
            esp32.write(b'F')

        # Check for Alert Trigger from ESP32
        if esp32.in_waiting > 0:
            line = esp32.readline().decode('utf-8', errors='ignore').strip()
            if "T" in line:
                trigger_pop_up()

        # --- LOG TO CSV ---
        if status == "DISTRACTED":
            distraction_count = min(distraction_count + 1, 10)
        else:
            distraction_count = max(distraction_count - 1, 0)

        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                STUDENT_ID,
                status,
                distraction_count,
                "Live Session",
                "Real Student"
            ])

        # UI Overlay
        color = (0, 255, 0) if status == "FOCUSED" else (0, 0, 255)
        cv2.putText(frame, f"{status} | Idle: {int(seconds_since_motion)}s", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.imshow('Distraction Monitor', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    esp32.write(b'X')
    cap.release()
    cv2.destroyAllWindows()
    esp32.close()
