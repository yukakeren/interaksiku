# 🥕 Aplikasi Interaktif Sayuran

Aplikasi interaktif yang mendeteksi gerakan tangan untuk berinteraksi dengan gambar sayuran menggunakan OpenCV dan MediaPipe. Dilengkapi dengan sistem kalibrasi presisi, kontrol mouse gesture, dan interface yang user-friendly.

## 📋 Daftar Isi
- [Persyaratan Sistem](#persyaratan-sistem)
- [Fitur Utama](#fitur-utama)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [File yang Diperlukan](#file-yang-diperlukan)
- [Struktur Proyek](#struktur-proyek)
- [Troubleshooting](#troubleshooting)
- [Changelog](#changelog)

## 🖥️ Persyaratan Sistem
- **OS**: Windows 10/11 (dioptimasi untuk Windows)
- **Python**: 3.8 atau lebih tinggi
- **Hardware**: Webcam yang terhubung (built-in atau external)
- **RAM**: Minimal 4GB (direkomendasikan 8GB)
- **Storage**: 500MB untuk dependencies

**Catatan**: Aplikasi dapat mendeteksi dan memilih dari multiple kamera yang terhubung.

## ✨ Fitur Utama

### 🎯 Kalibrasi Presisi
- **Dual Mode Calibration**: GUI drag-&-drop dan OpenCV hand tracking
- **Auto Camera Detection**: Mendeteksi semua kamera yang tersedia
- **Flip Consistency**: Setting flip tersimpan dan konsisten antar aplikasi
- **Small Precision Points**: Titik kalibrasi kecil untuk akurasi tinggi
- **Real-time Preview**: Preview kamera dengan overlay titik kalibrasi

### 🤖 Gesture Recognition
- **MediaPipe Integration**: Deteksi gerakan tangan akurat
- **Multiple Hand Landmarks**: Tracking 21 titik tangan
- **Smoothing Algorithm**: Pergerakan halus dengan anti-jitter
- **Configurable Sensitivity**: Threshold yang dapat disesuaikan

### 🎮 Multiple Applications
1. **Aplikasi Interaktif**: 6 sayuran + background dengan efek hover
2. **Mouse Control**: Kontrol mouse komputer dengan gesture
3. **Test Application**: Simple demo dengan 1 sayuran
4. **GUI Calibrator**: Interface grafis untuk kalibrasi mudah

### 🔧 Advanced Features
- **Perspective Transformation**: Mapping area kalibrasi ke layar penuh
- **Background Integration**: Support gambar background custom
- **RGBA Overlay**: Transparansi untuk objek sayuran
- **Fullscreen Mode**: Mode layar penuh untuk presentasi
- **Multi-camera Support**: Pilihan kamera dengan DirectShow support

## 📦 Instalasi

### Cara 1: Instalasi Otomatis (Rekomendasi)
```batch
# Jalankan sebagai administrator
setup.bat
```

### Cara 2: Instalasi Manual
```bash
# Buat virtual environment (opsional tapi direkomendasikan)
python -m venv venv

# Aktivasi virtual environment
# Windows Command Prompt:
venv\Scripts\activate.bat
# Windows PowerShell:
venv\Scripts\activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Dependencies yang Diinstall
- `opencv-python` - Computer vision dan image processing
- `mediapipe` - Hand tracking dan pose detection  
- `numpy` - Numerical computing
- `pynput` - Mouse dan keyboard control
- `pyautogui` - Screen automation
- `pillow` - Image processing tambahan

## 🚀 Penggunaan

### 1. Kalibrasi Layar (Wajib Dilakukan Pertama Kali)

#### 🖱️ GUI Calibrator (Rekomendasi untuk Pemula)
```batch
# Cara otomatis
run_calibrate_gui.bat

# Cara manual
python calibrate_gui.py
```

**Fitur GUI Calibrator:**
- ✅ **Manual Mode (Default)**: Drag & drop titik dengan mouse
- ✅ **OpenCV Mode**: Deteksi jari otomatis
- ✅ **Camera Selection**: Pilih kamera dari dropdown
- ✅ **Flip Options**: Normal/Mirror mode dengan checkbox
- ✅ **Real-time Preview**: Preview kamera dengan overlay
- ✅ **Load Calibration**: View kalibrasi yang tersimpan

**Langkah-langkah GUI:**
1. Pilih metode kalibrasi (Manual/OpenCV)
2. Pilih kamera dari dropdown
3. Centang "Mirror/Flip horizontal" jika diperlukan
4. Klik "Mulai Kalibrasi"
5. **Manual**: Geser 4 titik berwarna ke sudut area proyeksi
6. **OpenCV**: Arahkan jari ke sudut sesuai petunjuk, tekan SPASI
7. Klik "Simpan Kalibrasi"

#### 💻 Kalibrasi Command Line (untuk Advanced User)
```batch
# Cara otomatis
run_calibration.bat

# Cara manual
python calibrate.py
```

**Langkah-langkah Command Line:**
1. Pilih kamera dari daftar yang terdeteksi
2. Pilih opsi flip (Normal/Mirror)
3. Arahkan jari telunjuk ke sudut layar sesuai petunjuk
4. Tekan SPASI untuk menyimpan setiap titik
5. Ulangi untuk 4 sudut: Kiri Atas → Kanan Atas → Kanan Bawah → Kiri Bawah
6. Tekan ESC untuk membatalkan

### 2. Menjalankan Aplikasi

#### 🥬 Aplikasi Interaktif Utama (6 Sayuran + Background)
```batch
# Cara otomatis
run_interactive.bat

# Cara manual
python interact.py
```

**Fitur Aplikasi Utama:**
- 6 sayuran interaktif: Tomat, Mentimun, Wortel, Terong, Brokoli, Kubis
- Background custom dengan cover-fit scaling
- Efek hover dengan animasi
- Layout grid 3x2 yang responsif
- Mode fullscreen untuk presentasi

#### 🧪 Aplikasi Test (1 Sayuran Simple)
```batch
# Cara otomatis
run_test.bat

# Cara manual
python "interact(test).py"
```

#### 🖱️ Kontrol Mouse dengan Gesture
```batch
# Cara otomatis
run_mouse_control.bat

# Cara manual
python comfis_mouse.py
```

**Fitur Mouse Control:**
- Gerakkan tangan untuk menggerakkan kursor
- Kepalkan tangan untuk klik kiri
- Smoothing untuk pergerakan halus
- Area mapping sesuai kalibrasi
- Visual feedback dengan area kalibrasi

#### 📋 Menu Utama (All-in-One)
```batch
menu.bat
```

### 3. Default Settings (Terbaru)
- **Metode Kalibrasi**: Manual GUI Drag & Drop
- **Flip Mode**: Normal (tidak di-flip)
- **Point Size**: 8px (kecil untuk presisi tinggi)
- **Camera**: Auto-detect dengan pilihan manual

## 📁 File yang Diperlukan

### Untuk Aplikasi Utama (interact.py)
```
📁 Project Root/
├── 🖼️ background.png      # Latar belakang utama
├── 🍅 tomato.png          # Gambar tomat (transparan/RGBA)
├── 🥒 cucumber.png        # Gambar mentimun
├── 🥕 carrot.png          # Gambar wortel  
├── 🍆 eggplant.png        # Gambar terong
├── 🥦 broccoli.png        # Gambar brokoli
└── 🥬 cabbage.png         # Gambar kubis
```

### Untuk Aplikasi Test (interact(test).py)
```
📁 Project Root/
└── 🥬 vegetable.png       # Sayuran tunggal (opsional)
```

### File Kalibrasi (Auto-generated)
```
📁 Project Root/
├── 📊 calibration_points.npy    # Koordinat kalibrasi (4 titik)
├── 📝 calibration_method.txt    # Metode: gui_manual/opencv_hand_tracking
└── ⚙️ calibration_flip.txt      # Setting flip: true/false
```

**Catatan**: 
- Jika file gambar tidak tersedia, aplikasi akan tetap berjalan dengan placeholder
- Format gambar yang didukung: PNG, JPG, JPEG
- Gambar RGBA (dengan transparansi) direkomendasikan untuk efek overlay yang baik

## 📂 Struktur Proyek

```
📁 interaksiku/
├── 🐍 calibrate_gui.py           # GUI calibrator (rekomendasi)
├── 🐍 calibrate.py               # Command line calibrator  
├── 🐍 comfis_mouse.py            # Mouse control dengan gesture
├── 🐍 interact.py                # Aplikasi utama (6 sayuran)
├── 🐍 interact(test).py          # Aplikasi test (1 sayuran)
├── 📦 requirements.txt           # Python dependencies
├── 🎛️ setup.bat                  # Auto installer
├── 🎛️ menu.bat                   # Menu utama
├── 🎛️ run_calibrate_gui.bat      # Launcher GUI calibrator
├── 🎛️ run_calibration.bat        # Launcher command line calibrator
├── 🎛️ run_interactive.bat        # Launcher aplikasi utama
├── 🎛️ run_test.bat               # Launcher aplikasi test
├── 🎛️ run_mouse_control.bat      # Launcher mouse control
├── 📄 README.md                  # Dokumentasi utama
├── 📄 LICENSE                    # MIT License
├── 📄 PERBAIKAN_*.md             # Changelog dan improvement docs
└── 🖼️ *.png                      # Asset gambar sayuran dan background
```

## 🛠️ Troubleshooting

### Masalah Umum

#### ❌ Error: "ModuleNotFoundError: No module named 'mediapipe'"
**Solusi:**
```bash
# Pastikan virtual environment aktif
venv\Scripts\activate

# Install ulang dependencies
pip install -r requirements.txt

# Atau install manual
pip install mediapipe opencv-python numpy
```

#### ❌ Error: "Tidak ada kamera yang ditemukan"
**Solusi:**
1. Pastikan webcam terhubung dan tidak digunakan aplikasi lain
2. Close aplikasi video call (Zoom, Teams, dll.)
3. Restart aplikasi
4. Coba jalankan dengan admin privileges

#### ❌ Error: "File kalibrasi tidak ditemukan"
**Solusi:**
```bash
# Lakukan kalibrasi terlebih dahulu
python calibrate_gui.py
# atau
python calibrate.py
```

#### ❌ Koordinat tidak akurat / tidak sinkron
**Solusi:**
1. Lakukan kalibrasi ulang
2. Pastikan menggunakan setting flip yang sama
3. Gunakan opsi "Gunakan setting dari kalibrasi" di mouse control

#### ❌ Performa lambat / lag
**Solusi:**
1. Close aplikasi lain yang menggunakan CPU/GPU tinggi
2. Kurangi resolusi kamera di `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)`
3. Increase smoothing factor di mouse control

#### ❌ Hand tracking tidak responsif
**Solusi:**
1. Pastikan pencahayaan cukup
2. Gunakan background kontras dengan tangan
3. Adjust threshold di code:
```python
hands = mp_hands.Hands(
    min_detection_confidence=0.5,  # Turunkan untuk lebih sensitif
    min_tracking_confidence=0.5,   # Turunkan untuk lebih sensitif
    max_num_hands=1
)
```

### Error Spesifik Windows

#### ❌ Error: "Access denied" atau permission error
**Solusi:**
1. Jalankan Command Prompt sebagai Administrator
2. Install dependencies dengan `--user` flag:
```bash
pip install --user -r requirements.txt
```

#### ❌ Error: DirectShow camera access
**Solusi:**
- Aplikasi otomatis fallback ke mode non-DirectShow
- Pastikan camera drivers up-to-date

## 📋 Changelog

### ✅ Latest Updates (v2.0)

#### 🎯 Kalibrasi Improvements
- ✅ **GUI Calibrator**: Interface grafis yang user-friendly
- ✅ **Manual Calibration Default**: Drag & drop sebagai default method
- ✅ **Smaller Points**: Titik kalibrasi 8px untuk presisi tinggi
- ✅ **Flip Consistency**: Setting flip tersimpan dan konsisten
- ✅ **Real-time Preview**: Camera preview dengan overlay points

#### 🖱️ Mouse Control Enhancements  
- ✅ **Auto Setting Detection**: Gunakan setting flip dari kalibrasi
- ✅ **Smoothing Algorithm**: Pergerakan mouse yang halus
- ✅ **Visual Feedback**: Area kalibrasi visible saat penggunaan
- ✅ **Gesture Detection**: Kepal tangan untuk klik yang responsif

#### 🔧 Technical Improvements
- ✅ **Requirements Fix**: Hapus tkinter dari requirements (built-in)
- ✅ **Error Handling**: Better error messages dan fallbacks
- ✅ **Multi-camera Support**: Support multiple camera types
- ✅ **Documentation**: Comprehensive README dan changelog

#### 🎨 User Experience
- ✅ **Batch Scripts**: Launcher otomatis untuk semua aplikasi
- ✅ **Menu System**: All-in-one menu dengan menu.bat
- ✅ **Default Settings**: Optimal defaults untuk pemula
- ✅ **Visual Polish**: Smaller UI elements, cleaner interface

### 📝 Previous Versions
- **v1.0**: Basic hand tracking dan vegetable interaction
- **v1.1**: Command line calibration system
- **v1.2**: Mouse control integration
- **v1.3**: Multi-camera support dan flip corrections

## 📜 Lisensi

MIT License - lihat file [LICENSE](LICENSE) untuk detail lengkap.

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan:
1. Fork repository ini
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📞 Support

Jika mengalami masalah atau butuh bantuan:
1. Check [Troubleshooting](#troubleshooting) section
2. Buat issue di GitHub repository
3. Sertakan informasi sistem dan error message lengkap

---

**Happy Coding! 🥕✨**
