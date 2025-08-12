# 🚀 Quick Start Guide - Aplikasi Interaktif Sayuran

Panduan cepat untuk memulai menggunakan aplikasi dalam 5 menit!

## ⚡ Langkah Cepat (5 Menit)

### 1. Install Dependencies (1 menit)
```batch
# Klik kanan "Run as Administrator"
setup.bat
```

### 2. Kalibrasi dengan GUI (2 menit)
```batch
# Double click
run_calibrate_gui.bat
```
- ✅ Pilih "Manual - GUI Drag & Drop"
- ✅ Pilih kamera dari dropdown
- ✅ Klik "Mulai Kalibrasi"
- ✅ Geser 4 titik berwarna ke sudut area proyeksi
- ✅ Klik "Simpan Kalibrasi"

### 3. Jalankan Aplikasi (1 menit)
```batch
# Double click
run_interactive.bat
```

### 4. Kontrol Mouse (1 menit)
```batch
# Double click
run_mouse_control.bat
```
- ✅ Pilih opsi 3 (gunakan setting dari kalibrasi)
- ✅ Gerakkan tangan untuk kontrol mouse
- ✅ Kepalkan tangan untuk klik

## 🎯 Tips Sukses

### Kalibrasi Terbaik
- 📸 **Pencahayaan**: Pastikan ruangan terang
- 🖼️ **Background**: Hindari background rumit
- 📐 **Posisi**: Letakkan kamera di posisi yang stabil
- 🎯 **Presisi**: Geser titik tepat ke sudut area proyeksi

### Hand Tracking Optimal
- ✋ **Kontras**: Tangan kontras dengan background
- 📏 **Jarak**: Jarak 30-50cm dari kamera
- 🤚 **Gesture**: Gunakan jari telunjuk yang jelas
- 🤜 **Klik**: Kepal tangan untuk klik mouse

## 🛠️ Jika Ada Masalah

### Kamera Tidak Terdeteksi
```batch
# 1. Tutup aplikasi video call lain
# 2. Restart aplikasi
# 3. Jalankan sebagai admin
```

### Error Dependencies
```bash
# Install manual jika setup.bat gagal
pip install opencv-python mediapipe numpy pynput pyautogui pillow
```

### Koordinat Tidak Akurat
```batch
# Lakukan kalibrasi ulang
run_calibrate_gui.bat
```

## 📱 Menu Lengkap
```batch
# All-in-one menu
menu.bat
```

---
**Total Waktu Setup: ~5 menit** ⏱️
