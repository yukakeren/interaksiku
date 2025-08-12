# interact_6_veggies_bg.py
import cv2, mediapipe as mp, numpy as np

# ===== Layar 16:10 + window =====
CANVAS_W, CANVAS_H = 1920, 1200
WINDOW_NAME = "Interactive"
DEBUG_DRAW_BOX = False  # True untuk lihat bounding box

# ===== Background =====
BG_PATH = "background.png"  # pastikan file ini ada di folder yang sama
bg = cv2.imread(BG_PATH)
if bg is None:
    raise FileNotFoundError(f"Background tidak ditemukan: {BG_PATH}")

# cover-fit ke kanvas tanpa distorsi, crop tengah
bh, bw = bg.shape[:2]
scale = max(CANVAS_W / bw, CANVAS_H / bh)
new_w, new_h = int(bw * scale), int(bh * scale)
bg_resized = cv2.resize(bg, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
crop_x = (new_w - CANVAS_W) // 2
crop_y = (new_h - CANVAS_H) // 2
bg_canvas = bg_resized[crop_y:crop_y+CANVAS_H, crop_x:crop_x+CANVAS_W].copy()

# ===== Kalibrasi (TL, TR, BR, BL) -> kanvas =====
cal_points = np.load("calibration_points.npy")
proj_corners = np.float32([[0,0],[CANVAS_W,0],[CANVAS_W,CANVAS_H],[0,CANVAS_H]])
M = cv2.getPerspectiveTransform(np.float32(cal_points), proj_corners)

# ===== MediaPipe Hands =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# ===== 6 sayur (pakai persentase agar gampang diatur) =====
# bbox_pct = (x0, y0, x1, y1) relatif ke kanvas (0..1)
VEGETABLES = [
    {"name":"Tomato",    "img_path":"tomato.png",    "bbox_pct":(0.06, 0.12, 0.30, 0.40)},
    {"name":"Cucumber",  "img_path":"cucumber.png",  "bbox_pct":(0.36, 0.12, 0.64, 0.40)},
    {"name":"Carrot",    "img_path":"carrot.png",    "bbox_pct":(0.70, 0.12, 0.94, 0.40)},
    {"name":"Eggplant",  "img_path":"eggplant.png",  "bbox_pct":(0.06, 0.58, 0.30, 0.86)},
    {"name":"Broccoli",  "img_path":"broccoli.png",  "bbox_pct":(0.36, 0.58, 0.64, 0.86)},
    {"name":"Cabbage",   "img_path":"cabbage.png",   "bbox_pct":(0.70, 0.58, 0.94, 0.86)},
]

def pct_to_px(bbox_pct):
    x0 = int(bbox_pct[0]*CANVAS_W); y0 = int(bbox_pct[1]*CANVAS_H)
    x1 = int(bbox_pct[2]*CANVAS_W); y1 = int(bbox_pct[3]*CANVAS_H)
    return x0, y0, x1, y1

def overlay_rgba(dst, src_rgba, x, y, w, h):
    if src_rgba is None: return
    src = cv2.resize(src_rgba, (w, h), interpolation=cv2.INTER_AREA)
    if src.shape[2] == 3:
        # tanpa alpha → tempel langsung (clip ke ROI)
        x1 = min(x+w, dst.shape[1]); y1 = min(y+h, dst.shape[0])
        x0 = max(x, 0); y0 = max(y, 0)
        if x0>=x1 or y0>=y1: return
        dst[y0:y1, x0:x1] = src[(y0-y):(y1-y), (x0-x):(x1-x)]
        return
    b,g,r,a = cv2.split(src)
    a = a.astype(float)/255.0
    x1 = min(x+w, dst.shape[1]); y1 = min(y+h, dst.shape[0])
    x0 = max(x, 0); y0 = max(y, 0)
    if x0>=x1 or y0>=y1: return
    roi = dst[y0:y1, x0:x1]
    sb = b[(y0-y):(y1-y), (x0-x):(x1-x)]
    sg = g[(y0-y):(y1-y), (x0-x):(x1-x)]
    sr = r[(y0-y):(y1-y), (x0-x):(x1-x)]
    sa = a[(y0-y):(y1-y), (x0-x):(x1-x)]
    for c, ch in enumerate([sb, sg, sr]):
        roi[:,:,c] = (sa*ch + (1-sa)*roi[:,:,c]).astype(np.uint8)
    dst[y0:y1, x0:x1] = roi

# Preload gambar sayur & bbox pixel
for v in VEGETABLES:
    v["img"] = cv2.imread(v["img_path"], cv2.IMREAD_UNCHANGED)
    v["bbox_px"] = pct_to_px(v["bbox_pct"])

# ===== Kamera & fullscreen =====
cap = cv2.VideoCapture(0)
cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

msg = None
msg_timer = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Gagal baca kamera."); break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Mulai dari background yang sudah di-fit
    canvas = bg_canvas.copy()

    # Tampilkan semua sayur
    for v in VEGETABLES:
        x0,y0,x1,y1 = v["bbox_px"]
        overlay_rgba(canvas, v["img"], x0, y0, x1-x0, y1-y0)
        if DEBUG_DRAW_BOX:
            cv2.rectangle(canvas, (x0,y0), (x1,y1), (0,255,0), 2)
            cv2.putText(canvas, v["name"], (x0, y0-6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    # Deteksi jari & cek sentuhan
    touched = None
    if results.multi_hand_landmarks:
        h, w, _ = frame.shape
        for hand in results.multi_hand_landmarks:
            fx = int(hand.landmark[8].x * w)
            fy = int(hand.landmark[8].y * h)
            pt = np.array([[fx, fy]], dtype=np.float32).reshape(-1,1,2)
            warped = cv2.perspectiveTransform(pt, M)[0][0]
            wx, wy = int(warped[0]), int(warped[1])

            # pointer jari
            cv2.circle(canvas, (wx, wy), 12, (0,255,0), -1)

            # cek ke setiap sayur
            for v in VEGETABLES:
                x0,y0,x1,y1 = v["bbox_px"]
                if x0 <= wx <= x1 and y0 <= wy <= y1:
                    touched = v["name"]
                    cv2.rectangle(canvas, (x0,y0), (x1,y1), (255,255,255), 3)
                    break

    if touched:
        msg = f"Yummy {touched}!"
        msg_timer = 20

    if msg_timer > 0 and msg:
        cv2.putText(canvas, msg, (CANVAS_W//2 - 240, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0,0,0), 5)
        cv2.putText(canvas, msg, (CANVAS_W//2 - 240, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0,255,0), 4)
        msg_timer -= 1

    cv2.imshow(WINDOW_NAME, canvas)
    if (cv2.waitKey(1) & 0xFF) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
