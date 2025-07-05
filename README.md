# Arabic Kashida Tool

بسم الله الرحمن الرحيم

**Arabic Kashida Tool** adalah aplikasi alat bantu untuk menulis teks Arab dengan dukungan keyboard virtual Arab, Pegon, dan Harakat. Aplikasi ini juga terintegrasi dengan Gemini AI untuk membantu dalam penulisan dan koreksi teks Arab.

## ✨ Fitur Utama

- **Keyboard Virtual Arab**: Keyboard lengkap dengan karakter Arab standar
- **Keyboard Pegon**: Dukungan untuk penulisan Arab Pegon (Arab Jawa)
- **Harakat**: Tanda baca Arab (fathah, kasrah, dhammah, dll.)
- **Integrasi Gemini AI**: Bantuan AI untuk koreksi dan penulisan teks Arab
- **Shortcut Keyboard**: Dukungan shortcut untuk penggunaan yang lebih cepat
- **Copy & Paste**: Fitur copy paste dengan highlight

## 🔧 Persyaratan Sistem

- **Python 3.12+** (disarankan versi terbaru)
- **Windows 10/11** (atau sistem operasi yang mendukung PySide6)
- **Koneksi Internet** (untuk fitur Gemini AI)

## 📦 Instalasi

### 1. Install Python

Download dan install Python dari [python.org](https://www.python.org/downloads/)

- Pastikan mencentang **"Add Python to PATH"** saat instalasi
- Verifikasi instalasi dengan membuka Command Prompt dan ketik:
  ```cmd
  python --version
  ```

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/Arabic-Kashida-Tool.git
cd Arabic-Kashida-Tool
```

Atau download ZIP dari GitHub dan ekstrak ke folder pilihan Anda.

### 3. Install Dependencies

Buka Command Prompt atau PowerShell di folder aplikasi, lalu jalankan:

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi API Key (Opsional)

Jika ingin menggunakan fitur Gemini AI, Anda perlu mendapatkan API Key dari [Google AI Studio](https://aistudio.google.com/).

Setelah mendapatkan API Key, ada dua cara untuk mengaturnya:

**Cara 1: Melalui Aplikasi**
- Jalankan aplikasi
- Klik menu atau tombol konfigurasi API Key
- Masukkan API Key Anda

**Cara 2: Edit File config.json**
```json
{
  "gemini": {
    "api_key": "YOUR_API_KEY_HERE",
    "model": "gemini-2.5-flash",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

## 🚀 Cara Menggunakan

### Menjalankan Aplikasi

**Cara 1: Menggunakan Python**
```bash
python arabic_typing_helper.py
```

**Cara 2: Menggunakan Launcher (Windows)**
```bash
Launcher.bat
```

### Menggunakan Keyboard Virtual

1. **Mode Arab**: Pilih mode "Arabic" untuk menulis teks Arab standar
2. **Mode Pegon**: Pilih mode "Pegon" untuk menulis Arab Pegon (Arab Jawa)
3. **Mode Harakat**: Pilih mode "Harakat" untuk menambahkan tanda baca Arab

### Shortcut Keyboard

- **Ctrl+C**: Copy teks dengan highlight
- **Ctrl+V**: Paste teks
- **Backspace**: Hapus karakter terakhir
- **Delete**: Hapus semua teks
- **Enter**: Baris baru

### Menggunakan Fitur Gemini AI

1. Tulis atau paste teks Arab di area teks
2. Klik tombol "Gemini" atau gunakan menu AI
3. Pilih jenis bantuan yang diinginkan (koreksi, terjemahan, dll.)
4. Tunggu respon dari AI dan review hasilnya

## ⚠️ Penting - Disclaimer

**بارك الله فيكم**

Aplikasi ini adalah **alat bantu** yang menggunakan teknologi AI (Gemini) untuk membantu dalam penulisan dan koreksi teks Arab. Mohon diperhatikan:

### 🔍 Verifikasi Wajib
- **Semua hadits dan ayat Al-Quran yang dihasilkan dari aplikasi ini WAJIB untuk di-crosscheck**
- **Jangan menerima hasil mentah-mentah tanpa verifikasi**
- **Selalu rujuk kepada sumber yang shahih dan terpercaya**

### 📚 Sumber Rujukan yang Disarankan
- **Al-Quran**: Mushaf resmi atau aplikasi Al-Quran terpercaya
- **Hadits**: Kitab hadits shahih (Bukhari, Muslim, dll.) atau aplikasi hadits terpercaya
- **Ulama**: Konsultasi dengan ahli agama yang kompeten

### 🤲 Doa dan Harapan
نسأل الله أن يبارك في هذا العمل وأن ينفع به الأمة

*"Kami memohon kepada Allah agar memberkahi karya ini dan memberikan manfaat kepada umat"*

**Ingatlah**: Teknologi adalah alat, dan kebenaran ilmu agama tetap harus dirujuk kepada sumbernya yang shahih. Semoga aplikasi ini dapat membantu dalam mempermudah belajar dan menulis bahasa Arab, namun tetap dengan kehati-hatian dan verifikasi yang baik.

## 🛠️ Troubleshooting

### Error saat Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Error saat Menjalankan Aplikasi
- Pastikan Python sudah terinstall dengan benar
- Pastikan semua dependencies sudah terinstall
- Coba jalankan dengan: `python -m arabic_typing_helper`

### Masalah dengan Gemini AI
- Pastikan API Key sudah diatur dengan benar
- Pastikan koneksi internet stabil
- Cek quota API Key di Google AI Studio

## 🤝 Kontribusi

Kontribusi selalu welcome! Silakan:
1. Fork repository ini
2. Buat branch baru untuk fitur Anda
3. Commit perubahan Anda
4. Push ke branch
5. Buat Pull Request

## 📄 Lisensi

MIT License - lihat file [LICENSE](LICENSE) untuk detail lengkap.

## 🙏 Penutup

جزاكم الله خيرا

Semoga aplikasi ini bermanfaat untuk memudahkan dalam mempelajari dan menulis bahasa Arab. Mohon maaf jika ada kekurangan, dan jangan lupa untuk selalu memverifikasi konten keagamaan yang dihasilkan.

**Barakallahu fiikum wa jazaakumullahu khairan**

---

*Dibuat dengan ❤️ untuk memudahkan belajar bahasa Arab*