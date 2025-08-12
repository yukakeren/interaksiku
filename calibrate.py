# calibrate.py
import cv2, mediapipe as mp, numpy as np

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)  # ganti index kalau perlu
points = []

# Urutan pojok (searah jarum jam)
corner_names = ["Kiri Atas", "Kanan Atas", "Kanan Bawah", "Kiri Bawah"]

while True:
    ret, frame = cap.read()
    if not ret:
        print("Tidak bisa membuka kamera.")
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Tulis instruksi pojok
    if len(points) < len(corner_names):
        instruksi = f"{corner_names[len(points)]}"
        cv2.putText(frame, instruksi, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            h, w, _ = frame.shape
            x = int(hand.landmark[8].x * w)
            y = int(hand.landmark[8].y * h)
            cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)

            # Simpan titik saat spasi ditekan
            if cv2.waitKey(1) & 0xFF == ord(' '):
                points.append([x, y])
                print(f"{corner_names[len(points)-1]}: {x}, {y}")

    cv2.imshow("Calibration", frame)

    if len(points) == 4:
        np.save("calibration_points.npy", np.array(points))
        print("Kalibrasi selesai & disimpan.")
        break

    if cv2.waitKey(1) & 0xFF == 27:  # Esc keluar
        break

cap.release()
cv2.destroyAllWindows()
