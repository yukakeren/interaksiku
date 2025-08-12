# interact_6_veggies_bg.py
import cv2, mediapipe as mp, numpy as np
import os

# Set environment variables for Windows compatibility
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

def detect_cameras():
    """Detect available cameras and return list of working camera indices"""
    available_cameras = []
    print("🔍 Mendeteksi kamera yang tersedia...")
    
    for i in range(10):  # Check first 10 camera indices
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
                print(f"✅ Kamera {i}: Tersedia")
            else:
                print(f"❌ Kamera {i}: Tidak dapat membaca frame")
            cap.release()
        else:
            # Try without DirectShow for this index
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(i)
                    print(f"✅ Kamera {i}: Tersedia (tanpa DirectShow)")
                cap.release()
    
    return available_cameras

def choose_camera():
    """Let user choose which camera to use"""
    cameras = detect_cameras()
    
    if not cameras:
        print("❌ Tidak ada kamera yang terdeteksi!")
        print("Pastikan kamera terhubung dengan baik.")
        input("Tekan Enter untuk keluar...")
        exit()
    
    if len(cameras) == 1:
        print(f"📷 Menggunakan kamera {cameras[0]} (satu-satunya yang tersedia)")
        return cameras[0]
    
    print("\n📷 Kamera yang tersedia:")
    for i, cam_idx in enumerate(cameras):
        print(f"  {i + 1}. Kamera {cam_idx}")
    
    while True:
        try:
            choice = input(f"\nPilih kamera (1-{len(cameras)}): ").strip()
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(cameras):
                    selected_camera = cameras[choice_idx]
                    print(f"✅ Menggunakan kamera {selected_camera}")
                    return selected_camera
                else:
                    print("❌ Pilihan tidak valid!")
            else:
                print("❌ Masukkan angka yang valid!")
        except KeyboardInterrupt:
            print("\n❌ Dibatalkan oleh pengguna.")
            exit()
        except Exception as e:
            print(f"❌ Error: {e}")

def init_camera(camera_index):
    """Initialize camera with given index"""
    # Try with DirectShow first
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, _ = cap.read()
        if ret:
            print(f"✅ Kamera {camera_index} berhasil dibuka dengan DirectShow!")
            return cap
        cap.release()
    
    # Try without DirectShow
    cap = cv2.VideoCapture(camera_index)
    if cap.isOpened():
        ret, _ = cap.read()
        if ret:
            print(f"✅ Kamera {camera_index} berhasil dibuka!")
            return cap
        cap.release()
    
    return None

# ===== Layar 16:10 + window =====
CANVAS_W, CANVAS_H = 1920, 1200
WINDOW_NAME = "Interactive"
DEBUG_DRAW_BOX = False  # True untuk lihat bounding box

# ===== Background =====
BG_PATH = "background.png"  # pastikan file ini ada di folder yang sama
if not os.path.exists(BG_PATH):
    print(f"❌ File background tidak ditemukan: {BG_PATH}")
    print("Pastikan file background.png ada di folder yang sama dengan script.")
    input("Tekan Enter untuk keluar...")
    exit()

bg = cv2.imread(BG_PATH)
if bg is None:
    print(f"❌ Gagal memuat background: {BG_PATH}")
    input("Tekan Enter untuk keluar...")
    exit()

# cover-fit ke kanvas tanpa distorsi, crop tengah
bh, bw = bg.shape[:2]
scale = max(CANVAS_W / bw, CANVAS_H / bh)
new_w, new_h = int(bw * scale), int(bh * scale)
bg_resized = cv2.resize(bg, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
crop_x = (new_w - CANVAS_W) // 2
crop_y = (new_h - CANVAS_H) // 2
bg_canvas = bg_resized[crop_y:crop_y+CANVAS_H, crop_x:crop_x+CANVAS_W].copy()

# ===== Kalibrasi (TL, TR, BR, BL) -> kanvas =====
if not os.path.exists("calibration_points.npy"):
    print("❌ File kalibrasi tidak ditemukan!")
    print("Jalankan 'python calibrate.py' terlebih dahulu untuk kalibrasi.")
    input("Tekan Enter untuk keluar...")
    exit()

cal_points = np.load("calibration_points.npy")

# Check calibration method to determine if correction is needed
calibration_method = "unknown"
if os.path.exists("calibration_method.txt"):
    with open("calibration_method.txt", "r") as f:
        calibration_method = f.read().strip()

# Apply correction only for OpenCV hand tracking (because it uses flipped coordinates)
if calibration_method == "opencv_hand_tracking":
    frame_width = 640  # Asumsi lebar frame kamera
    cal_points_corrected = cal_points.copy()
    for i in range(len(cal_points_corrected)):
        cal_points_corrected[i][0] = frame_width - cal_points_corrected[i][0]
    cal_points_final = cal_points_corrected
else:
    cal_points_final = cal_points

proj_corners = np.float32([[0,0],[CANVAS_W,0],[CANVAS_W,CANVAS_H],[0,CANVAS_H]])
M = cv2.getPerspectiveTransform(np.float32(cal_points_final), proj_corners)

# ===== MediaPipe Hands =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.7,
    max_num_hands=1  # Only detect one hand for better performance
)

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
missing_files = []
for v in VEGETABLES:
    if not os.path.exists(v["img_path"]):
        missing_files.append(v["img_path"])
        v["img"] = None
    else:
        v["img"] = cv2.imread(v["img_path"], cv2.IMREAD_UNCHANGED)
    v["bbox_px"] = pct_to_px(v["bbox_pct"])

if missing_files:
    print("⚠️  File gambar sayur tidak ditemukan:")
    for file in missing_files:
        print(f"   - {file}")
    print("Aplikasi akan tetap berjalan tanpa gambar yang hilang.")
    input("Tekan Enter untuk melanjutkan...")

# ===== Kamera & fullscreen =====
print("="*60)
print("           APLIKASI INTERAKTIF SAYURAN")
print("="*60)

# Pilih kamera yang akan digunakan
selected_camera = choose_camera()

# Inisialisasi kamera yang dipilih
cap = init_camera(selected_camera)

if cap is None:
    print(f"❌ Gagal membuka kamera {selected_camera}!")
    print("Pastikan kamera tidak digunakan aplikasi lain.")
    input("Tekan Enter untuk keluar...")
    exit()

print("\n📋 Tekan ESC untuk keluar dari aplikasi.")
print("="*60)

# Set camera properties for better performance
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

msg = None
msg_timer = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Gagal membaca frame dari kamera.")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Mulai dari background yang sudah di-fit
    canvas = bg_canvas.copy()

    # Tampilkan semua sayur
    for v in VEGETABLES:
        if v["img"] is not None:  # Only display if image exists
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
                if v["img"] is not None:  # Only check if image exists
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
