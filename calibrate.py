# calibrate.py
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

def choose_flip_option():
    """Let user choose camera flip option"""
    print("\n🔄 Opsi Flip Kamera:")
    print("  1. Normal (tidak di-flip) - Default")
    print("  2. Mirror/Flip horizontal (seperti selfie)")
    print("\n💡 Rekomendasi: Pilih opsi 1 (Normal) untuk konsistensi dengan GUI manual")
    
    while True:
        try:
            choice = input("\nPilih opsi flip (1-2, default: 1): ").strip()
            if choice == "1" or choice == "":
                print("✅ Menggunakan kamera normal (tidak di-flip)")
                return False
            elif choice == "2":
                print("✅ Menggunakan kamera mirror (flip horizontal)")
                return True
            else:
                print("❌ Pilihan tidak valid! Masukkan 1 atau 2.")
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

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.7,
    max_num_hands=1  # Only detect one hand for better performance
)

print("="*60)
print("           KALIBRASI LAYAR INTERAKTIF")
print("="*60)

# Pilih kamera yang akan digunakan
selected_camera = choose_camera()

# Pilih opsi flip kamera
use_flip = choose_flip_option()

# Inisialisasi kamera yang dipilih
cap = init_camera(selected_camera)

if cap is None:
    print(f"❌ Gagal membuka kamera {selected_camera}!")
    print("Pastikan kamera tidak digunakan aplikasi lain.")
    input("Tekan Enter untuk keluar...")
    exit()

# Set resolusi kamera untuk performa yang lebih baik
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS to 30 for better performance

points = []

# Urutan pojok (searah jarum jam)
corner_names = ["Kiri Atas", "Kanan Atas", "Kanan Bawah", "Kiri Bawah"]

print("\n📋 Instruksi:")
print("1. Arahkan jari telunjuk ke sudut layar sesuai petunjuk")
print("2. Tekan SPASI untuk menyimpan titik")
print("3. Tekan ESC untuk membatalkan")
print("4. Pastikan jari terdeteksi (lingkaran hijau) sebelum menyimpan")
print("="*60)

# Create window
cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Calibration", 800, 600)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Gagal membaca frame dari kamera.")
        break
    
    # Flip horizontal untuk konsistensi dengan comfis_mouse.py
    if use_flip:
        frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Tulis instruksi pojok
    if len(points) < len(corner_names):
        instruksi = f"Arahkan jari ke: {corner_names[len(points)]} - Tekan SPASI"
        cv2.putText(frame, instruksi, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    # Tampilkan progress
    progress = f"Progress: {len(points)}/4"
    cv2.putText(frame, progress, (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Tampilkan camera yang digunakan
    cv2.putText(frame, f'Camera: {selected_camera}', (30, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Tampilkan status flip
    flip_status = "Mirror" if use_flip else "Normal"
    cv2.putText(frame, f'Flip: {flip_status}', (30, 140),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            h, w, _ = frame.shape
            x = int(hand.landmark[8].x * w)
            y = int(hand.landmark[8].y * h)
            cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
            
            # Tampilkan koordinat jari
            cv2.putText(frame, f"({x}, {y})", (x+15, y-15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Cek tombol spasi untuk menyimpan titik
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' ') and results.multi_hand_landmarks and len(points) < 4:
        for hand in results.multi_hand_landmarks:
            h, w, _ = frame.shape
            x = int(hand.landmark[8].x * w)
            y = int(hand.landmark[8].y * h)
            points.append([x, y])
            print(f"{corner_names[len(points)-1]}: ({x}, {y})")
            break  # Hanya ambil satu tangan

    cv2.imshow("Calibration", frame)

    if len(points) == 4:
        np.save("calibration_points.npy", np.array(points))
        
        # Save metadata to indicate this is from OpenCV hand tracking
        with open("calibration_method.txt", "w") as f:
            f.write("opencv_hand_tracking")
        
        # Save flip setting
        with open("calibration_flip.txt", "w") as f:
            f.write("true" if use_flip else "false")
            
        print("\n" + "="*50)
        print("✅ KALIBRASI BERHASIL!")
        print("File tersimpan: calibration_points.npy")
        print(f"Flip setting: {'Mirror' if use_flip else 'Normal'}")
        print("Titik kalibrasi:")
        for i, point in enumerate(points):
            print(f"  {corner_names[i]}: {point}")
        print("="*50)
        print("Tekan Enter untuk melanjutkan ke aplikasi interaktif...")
        input()
        break

    if key == 27:  # Esc keluar
        print("\n❌ Kalibrasi dibatalkan oleh pengguna.")
        break

cap.release()
cv2.destroyAllWindows()
