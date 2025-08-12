import cv2
import mediapipe as mp
import time
from pynput.mouse import Controller, Button
import pyautogui
import math
import numpy as np
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

def choose_flip_option():
    """Let user choose camera flip option or use saved setting"""
    # Check if we have a saved flip setting from calibration
    saved_flip = None
    if os.path.exists("calibration_flip.txt"):
        with open("calibration_flip.txt", "r") as f:
            flip_setting = f.read().strip()
            saved_flip = flip_setting.lower() == "true"
            print(f"\n💾 Setting flip tersimpan dari kalibrasi: {'Mirror' if saved_flip else 'Normal'}")
    
    print("\n🔄 Opsi Flip Kamera:")
    print("  1. Normal (tidak di-flip)")
    print("  2. Mirror/Flip horizontal (seperti selfie)")
    if saved_flip is not None:
        print(f"  3. Gunakan setting dari kalibrasi ({'Mirror' if saved_flip else 'Normal'}) - Direkomendasikan")
    
    # Check if we can give recommendation based on calibration method
    if os.path.exists("calibration_method.txt"):
        with open("calibration_method.txt", "r") as f:
            method = f.read().strip()
        
        if method == "opencv_hand_tracking":
            print("\n💡 Info: Kalibrasi menggunakan OpenCV hand tracking")
        elif method == "gui_manual":
            print("\n💡 Info: Kalibrasi menggunakan GUI manual")
    
    while True:
        try:
            if saved_flip is not None:
                choice = input("\nPilih opsi flip (1-3, default: 3): ").strip()
            else:
                choice = input("\nPilih opsi flip (1-2, default: 1): ").strip()
                
            if choice == "1":
                print("✅ Menggunakan kamera normal (tidak di-flip)")
                return False
            elif choice == "2":
                print("✅ Menggunakan kamera mirror (flip horizontal)")
                return True
            elif choice == "3" and saved_flip is not None:
                print(f"✅ Menggunakan setting dari kalibrasi ({'Mirror' if saved_flip else 'Normal'})")
                return saved_flip
            elif choice == "" and saved_flip is not None:
                print(f"✅ Menggunakan setting dari kalibrasi ({'Mirror' if saved_flip else 'Normal'})")
                return saved_flip
            elif choice == "" and saved_flip is None:
                print("✅ Menggunakan kamera normal (tidak di-flip)")
                return False
            else:
                valid_options = "1, 2, atau 3" if saved_flip is not None else "1 atau 2"
                print(f"❌ Pilihan tidak valid! Masukkan {valid_options}.")
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

# Inisialisasi MediaPipe dan pynput
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_drawing = mp.solutions.drawing_utils
mouse = Controller()

# Gunakan pyautogui untuk dapatkan ukuran layar
screen_w, screen_h = pyautogui.size()
print(f"Ukuran layar: {screen_w} x {screen_h}")

# Inisialisasi kamera
print("="*60)
print("         KONTROL MOUSE DENGAN GESTURE TANGAN")
print("="*60)

# Pilih kamera yang akan digunakan
selected_camera = choose_camera()

# Pilih opsi flip kamera
use_flip = choose_flip_option()

# Load titik kalibrasi
if not os.path.exists("calibration_points.npy"):
    print("❌ File kalibrasi tidak ditemukan!")
    print("Jalankan 'python calibrate.py' terlebih dahulu untuk kalibrasi.")
    input("Tekan Enter untuk keluar...")
    exit()

cal_points = np.load("calibration_points.npy")

# Check calibration method and flip setting
calibration_method = "unknown"
if os.path.exists("calibration_method.txt"):
    with open("calibration_method.txt", "r") as f:
        calibration_method = f.read().strip()

# Check saved flip setting from calibration
calibration_flip = None
if os.path.exists("calibration_flip.txt"):
    with open("calibration_flip.txt", "r") as f:
        flip_setting = f.read().strip()
        calibration_flip = flip_setting.lower() == "true"

print("✅ Kalibrasi dimuat!")
print("Titik kalibrasi:", cal_points)
print("Metode kalibrasi:", calibration_method)
print("Flip kalibrasi:", "Mirror" if calibration_flip else "Normal" if calibration_flip is not None else "Unknown")
print("Opsi flip kamera:", "Mirror" if use_flip else "Normal")

# Dengan sistem baru, koordinat kalibrasi sudah disesuaikan dengan flip setting
# Jadi kita langsung gunakan koordinat kalibrasi tanpa koreksi
print("✅ Menggunakan koordinat kalibrasi langsung (sudah konsisten)")
cal_points_final = cal_points

print("Titik kalibrasi final untuk transformasi:", cal_points_final)

# Siapkan transformasi perspektif dari area kalibrasi ke layar penuh
screen_corners = np.float32([[0, 0], [screen_w, 0], [screen_w, screen_h], [0, screen_h]])
M = cv2.getPerspectiveTransform(np.float32(cal_points_final), screen_corners)

# Inisialisasi kamera yang dipilih
cap = init_camera(selected_camera)

if cap is None:
    print(f"❌ Gagal membuka kamera {selected_camera}!")
    print("Pastikan kamera tidak digunakan aplikasi lain.")
    input("Tekan Enter untuk keluar...")
    exit()

print("\n📋 Instruksi:")
print("- Gerakkan tangan di area yang sudah dikalibrasi")
print("- Kepalkan tangan untuk klik kiri")
print("- Tekan ESC untuk keluar")
print("="*60)

# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

prev_time = 0

# Variabel untuk melacak status klik
is_clicking = False

# Variabel untuk smoothing pergerakan mouse
smoothing_factor = 5  # Kurangi untuk respon lebih cepat
prev_positions_x = []
prev_positions_y = []

# Tambahan untuk visualisasi area kalibrasi
def draw_calibration_area(frame, cal_points):
    """Menggambar area kalibrasi di frame"""
    points = cal_points.astype(np.int32)
    cv2.polylines(frame, [points], True, (0, 255, 255), 2)
    
    # Label sudut
    corner_names = ["TL", "TR", "BR", "BL"]
    for i, point in enumerate(points):
        cv2.circle(frame, tuple(point), 8, (0, 255, 255), -1)
        cv2.putText(frame, corner_names[i], (point[0]+10, point[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Mirror frame berdasarkan opsi flip & konversi ke RGB
    if use_flip:
        frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Dengan sistem baru, koordinat kalibrasi sudah sesuai dengan setting flip
    # Jadi kita langsung gunakan koordinat kalibrasi untuk tampilan
    cal_points_display = cal_points
    
    # Gambar area kalibrasi dengan koordinat yang sesuai tampilan
    draw_calibration_area(frame, cal_points_display)
    
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_rgb.flags.writeable = False

    results = hands.process(img_rgb)
    img_rgb.flags.writeable = True
    frame = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Ambil titik MCP middle finger (landmark 9) untuk posisi mouse
            lm9 = hand_landmarks.landmark[9]  # Pangkal jari tengah
            lm12 = hand_landmarks.landmark[12]  # Ujung jari tengah
            
            # Konversi ke koordinat kamera
            cx, cy = int(lm9.x * w), int(lm9.y * h)

            # Transform titik tangan ke koordinat layar menggunakan kalibrasi
            hand_point = np.array([[cx, cy]], dtype=np.float32).reshape(-1, 1, 2)
            transformed_point = cv2.perspectiveTransform(hand_point, M)[0][0]
            mapped_x, mapped_y = int(transformed_point[0]), int(transformed_point[1])
            
            # Batasi koordinat agar tidak keluar layar
            mapped_x = max(0, min(screen_w - 1, mapped_x))
            mapped_y = max(0, min(screen_h - 1, mapped_y))

            # Hitung jarak antara pangkal dan ujung jari tengah untuk deteksi kepalan
            distance = math.sqrt((lm12.x - lm9.x)**2 + (lm12.y - lm9.y)**2)
            
            # Threshold untuk mendeteksi kepalan tangan
            threshold = 0.08  # Sesuaikan nilai ini berdasarkan pengujian
            
            # Deteksi apakah tangan mengepal atau terbuka
            hand_closed = distance < threshold
            
            # Tampilkan status tangan
            status_text = "Mengepal" if hand_closed else "Terbuka"
            status_color = (0, 0, 255) if hand_closed else (0, 255, 0)
            cv2.putText(frame, status_text, (cx+10, cy-30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            # Kontrol klik mouse
            if hand_closed and not is_clicking:
                mouse.press(Button.left)
                is_clicking = True
            elif not hand_closed and is_clicking:
                mouse.release(Button.left)
                is_clicking = False
            
            # Tampilkan titik di layar kamera
            circle_color = (0, 0, 255) if hand_closed else (0, 255, 0)
            cv2.circle(frame, (cx, cy), 12, circle_color, -1)
            cv2.putText(frame, f'Cam: {cx},{cy}', (cx+10, cy-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Tambahkan posisi yang sudah di-transform ke daftar untuk smoothing
            prev_positions_x.append(mapped_x)
            prev_positions_y.append(mapped_y)
            
            # Batasi jumlah posisi sebelumnya sesuai smoothing_factor
            if len(prev_positions_x) > smoothing_factor:
                prev_positions_x.pop(0)
                prev_positions_y.pop(0)
            
            # Hitung posisi rata-rata untuk smoothing
            if len(prev_positions_x) > 0:
                smoothed_x = int(sum(prev_positions_x) / len(prev_positions_x))
                smoothed_y = int(sum(prev_positions_y) / len(prev_positions_y))
                
                # Kontrol mouse dengan posisi yang sudah di-smoothing
                mouse.position = (smoothed_x, smoothed_y)
                
                # Tampilkan info mapping
                cv2.putText(frame, f'Screen: {smoothed_x},{smoothed_y}', (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    else:
        # Jika tangan tidak terdeteksi dan masih dalam status klik, lepaskan klik
        if is_clicking:
            mouse.release(Button.left)
            is_clicking = False
        
        # Reset daftar posisi saat tangan tidak terdeteksi
        prev_positions_x = []
        prev_positions_y = []

    # Hitung FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
    prev_time = curr_time

    # Tampilkan informasi di layar
    cv2.putText(frame, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Tampilkan status klik
    if is_clicking:
        cv2.putText(frame, "KLIK AKTIF", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    # Tampilkan ukuran layar
    cv2.putText(frame, f'Screen: {screen_w}x{screen_h}', (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Tampilkan camera yang digunakan
    cv2.putText(frame, f'Camera: {selected_camera}', (w-150, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Tampilkan status flip
    flip_status = "Mirror" if use_flip else "Normal"
    cv2.putText(frame, f'Flip: {flip_status}', (w-150, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Instruksi
    cv2.putText(frame, "ESC: Keluar", (w-120, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Hand Gesture Mouse Control (Calibrated)", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

# Pastikan melepaskan klik jika program ditutup saat sedang klik
if is_clicking:
    mouse.release(Button.left)

cap.release()
cv2.destroyAllWindows()