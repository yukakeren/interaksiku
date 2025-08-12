import cv2, mediapipe as mp, numpy as np

# Konfigurasi 16:10``
CANVAS_WIDTH  = 1920   
CANVAS_HEIGHT = 1200  

# Load titik kalibrasi & siapkan transform ke kanvas 16:10
cal_points = np.load("calibration_points.npy")  # urutan: TL, TR, BR, BL
proj_corners = np.float32([[0,0],
                           [CANVAS_WIDTH,0],
                           [CANVAS_WIDTH,CANVAS_HEIGHT],
                           [0,CANVAS_HEIGHT]])
M = cv2.getPerspectiveTransform(np.float32(cal_points), proj_corners)

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Gambar sayur
veg_img = cv2.imread("vegetable.png", cv2.IMREAD_UNCHANGED)
veg_w, veg_h = 220, 220
veg_x, veg_y = (CANVAS_WIDTH - veg_w)//2, (CANVAS_HEIGHT - veg_h)//2  # center

# Kamera (ganti index kalau perlu)
cap = cv2.VideoCapture(0)

# Buat jendela fullscreen
window_name = "Interactive"
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Gagal baca kamera.")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Kanvas 16:10
    canvas = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)

    # Tempel sayur (support alpha kalau ada)
    if veg_img is not None:
        resized = cv2.resize(veg_img, (veg_w, veg_h))
        if resized.shape[2] == 4:  # BGRA
            b, g, r, a = cv2.split(resized)
            roi = canvas[veg_y:veg_y+veg_h, veg_x:veg_x+veg_w]
            alpha = a.astype(float)/255.0
            for c, ch in enumerate([b, g, r]):
                roi[:,:,c] = (alpha*ch + (1-alpha)*roi[:,:,c]).astype(np.uint8)
            canvas[veg_y:veg_y+veg_h, veg_x:veg_x+veg_w] = roi
        else:
            canvas[veg_y:veg_y+veg_h, veg_x:veg_x+veg_w] = cv2.resize(veg_img[:,:,:3], (veg_w, veg_h))

    # Deteksi jari dan mapping ke koordinat kanvas 16:10
    if results.multi_hand_landmarks:
        h, w, _ = frame.shape
        for hand in results.multi_hand_landmarks:
            x = int(hand.landmark[8].x * w)
            y = int(hand.landmark[8].y * h)

            # Warp titik jari ke ruang proyeksi (kanvas 16:10)
            pt = np.array([[x, y]], dtype=np.float32).reshape(-1,1,2)
            warped_pt = cv2.perspectiveTransform(pt, M)[0][0]
            wx, wy = int(warped_pt[0]), int(warped_pt[1])

            # Gambar titik jari di kanvas
            cv2.circle(canvas, (wx, wy), 10, (0,255,0), -1)

            # Cek sentuh sayur
            if veg_x <= wx <= veg_x+veg_w and veg_y <= wy <= veg_y+veg_h:
                cv2.putText(canvas, "Yummy!", (CANVAS_WIDTH//2 - 120, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 4)

    cv2.imshow(window_name, canvas)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
