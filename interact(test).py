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

# Konfigurasi 16:10``
CANVAS_WIDTH  = 1920   
CANVAS_HEIGHT = 1200  

# Load titik kalibrasi & siapkan transform ke kanvas 16:10
if not os.path.exists("calibration_points.npy"):
    print("❌ File kalibrasi tidak ditemukan!")
    print("Jalankan 'python calibrate.py' terlebih dahulu untuk kalibrasi.")
    input("Tekan Enter untuk keluar...")
    exit()

cal_points = np.load("calibration_points.npy")  # urutan: TL, TR, BR, BL

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

proj_corners = np.float32([[0,0],
                           [CANVAS_WIDTH,0],
                           [CANVAS_WIDTH,CANVAS_HEIGHT],
                           [0,CANVAS_HEIGHT]])
M = cv2.getPerspectiveTransform(np.float32(cal_points_final), proj_corners)

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.7,
    max_num_hands=1  # Only detect one hand for better performance
)

# Gambar sayur
if not os.path.exists("vegetable.png"):
    print("⚠️  File vegetable.png tidak ditemukan!")
    print("Aplikasi akan tetap berjalan dengan kotak hitam.")
    veg_img = None
else:
    veg_img = cv2.imread("vegetable.png", cv2.IMREAD_UNCHANGED)
    if veg_img is None:
        print("⚠️  Gagal memuat vegetable.png!")
        
veg_w, veg_h = 220, 220
veg_x, veg_y = (CANVAS_WIDTH - veg_w)//2, (CANVAS_HEIGHT - veg_h)//2  # center

# Kamera (ganti index kalau perlu)
print("="*60)
print("         APLIKASI INTERAKTIF TEST")
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

# Buat jendela fullscreen
window_name = "Interactive"
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Gagal membaca frame dari kamera.")
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
    else:
        # Draw a placeholder rectangle if no image
        cv2.rectangle(canvas, (veg_x, veg_y), (veg_x+veg_w, veg_y+veg_h), (100, 100, 100), -1)
        cv2.putText(canvas, "NO IMAGE", (veg_x+50, veg_y+veg_h//2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

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
