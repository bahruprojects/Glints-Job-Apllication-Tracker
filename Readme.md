# 🚀 Glints Job Application Tracker

Web scraper otomatis untuk mengekstrak data lamaran pekerjaan dari Glints.com ke format CSV.

## 📋 Deskripsi

Program ini secara otomatis mengumpulkan semua data lamaran pekerjaan Anda dari Glints.com (dari semua halaman) dan menyimpannya dalam format CSV yang mudah dianalisis dengan Excel atau Google Sheets.

## ✨ Fitur

- ✅ **Multi-Page Scraping**: Otomatis mengambil data dari ratusan halaman
- ✅ **Auto-Login**: Login otomatis ke akun Glints Anda
- ✅ **Smart Navigation**: 4 strategi berbeda untuk navigasi antar halaman
- ✅ **Duplicate Prevention**: Mencegah data duplikat
- ✅ **Auto-Save Backup**: Backup otomatis setiap 10 halaman
- ✅ **Error Recovery**: Menyimpan data jika terjadi error atau interrupt
- ✅ **Progress Tracking**: Menampilkan progress real-time
- ✅ **CSV Export**: Output dalam format CSV (Excel-friendly)

## 📊 Data yang Dikumpulkan

Program akan mengekstrak informasi berikut:
- **No**: Nomor urut
- **Position**: Nama posisi pekerjaan
- **Company**: Nama perusahaan
- **Submitted Date**: Tanggal pengiriman lamaran
- **Status**: Status lamaran (Dilamar, Ditolak, Dalam Peninjauan, dll.)

## 🛠️ Instalasi

### 1. Install Python
Pastikan Python 3.7 atau lebih tinggi sudah terinstall.
```bash
python --version
```

### 2. Install Dependencies
```bash
pip install selenium
```

### 3. Install ChromeDriver
- Download ChromeDriver sesuai versi Chrome Anda dari: https://chromedriver.chromium.org/downloads
- Extract dan tempatkan di PATH sistem, atau letakkan di folder yang sama dengan script

**Atau gunakan webdriver-manager (Otomatis):**
```bash
pip install webdriver-manager
```

Lalu ubah baris ini di script:
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Ganti di __init__:
service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=chrome_options)
```

## 📁 Struktur File

```
project-folder/
│
├── Glints-Job-Application-Tracker.py    # Script utama
├── README.md                             # File ini
├── my_glints_applications_complete.csv  # Output utama
├── glints_backup_page_10.csv            # Auto-backup (opsional)
└── glints_interrupted.csv               # Recovery file (jika ada)
```

## 🚀 Cara Menggunakan

### 1. Konfigurasi Kredensial

Buka file `Glints-Job-Application-Tracker.py` dan edit bagian ini:

```python
# LOGIN - GANTI INI!
EMAIL = "email_anda@example.com"      # ⚠️ Ganti dengan email Glints Anda
PASSWORD = "password_anda"             # ⚠️ Ganti dengan password Glints Anda
```

### 2. Jalankan Program

**Windows:**
```bash
python Glints-Job-Application-Tracker.py
```

**Mac/Linux:**
```bash
python3 Glints-Job-Application-Tracker.py
```

### 3. Proses Berjalan

Program akan:
1. ✅ Login ke akun Glints Anda
2. 🔄 Membuka halaman "My Applications"
3. 📄 Scraping data dari setiap halaman
4. ⏭️ Navigasi otomatis ke halaman berikutnya
5. 💾 Menyimpan hasil ke CSV

### 4. Output

File CSV akan tersimpan di folder yang sama dengan script:
- `my_glints_applications_complete.csv` - File utama (semua data)
- `glints_backup_page_X.csv` - Backup setiap 10 halaman
- `glints_interrupted.csv` - Jika proses di-interrupt (Ctrl+C)
- `glints_error_recovery.csv` - Jika terjadi error

## ⚙️ Konfigurasi Lanjutan

### Mode Headless (Background)
Untuk menjalankan browser di background (tidak terlihat):
```python
# Uncomment baris ini di __init__:
chrome_options.add_argument('--headless')
```

### Limit Halaman
Untuk membatasi jumlah halaman maksimal:
```python
# Edit di scrape_all_pages():
max_pages = 100  # Default: 500
```

### Auto-save Interval
Untuk mengubah frekuensi auto-save:
```python
# Edit di scrape_all_pages():
if page_number % 10 == 0:  # Ganti 10 dengan angka lain
```

## 🐛 Troubleshooting

### Error: ChromeDriver not found
**Solusi**: Install webdriver-manager atau download ChromeDriver manual

### Login gagal
**Solusi**: 
- Pastikan email dan password benar
- Coba login manual di browser terlebih dahulu
- Glints mungkin memerlukan verifikasi (2FA)

### Stuck di halaman tertentu
**Solusi**:
- Periksa koneksi internet
- Refresh halaman manual saat browser terbuka
- Periksa apakah Glints mengubah struktur website

### Data tidak lengkap
**Solusi**:
- Jalankan ulang program (duplicate akan di-skip)
- Periksa file backup: `glints_backup_page_X.csv`
- Tambahkan delay lebih lama (edit `time.sleep()`)

### Browser crash
**Solusi**:
- Tutup aplikasi Chrome lain
- Restart komputer
- Update Chrome dan ChromeDriver ke versi terbaru

## ⚠️ Catatan Penting

1. **Legal & Ethical**:
   - Program ini hanya untuk data pribadi Anda sendiri
   - Jangan gunakan untuk scraping data orang lain
   - Patuhi Terms of Service Glints

2. **Rate Limiting**:
   - Program sudah include delay untuk menghindari rate limiting
   - Jangan modifikasi delay menjadi terlalu cepat

3. **Data Privacy**:
   - File CSV berisi data pribadi Anda
   - Jangan share file CSV ke public
   - Simpan dengan aman

4. **Website Changes**:
   - Jika Glints update website, program mungkin perlu update
   - Report issue jika program tidak berjalan

## 📈 Tips Penggunaan

### Untuk Lamaran Banyak (Ribuan)
- Waktu estimasi: 1-2 jam untuk ribuan lamaran
- Jangan minimize browser saat proses berjalan
- Pastikan laptop tidak sleep/hibernate
- Gunakan koneksi internet stabil

### Menghentikan Proses
Tekan `Ctrl + C` di terminal. Data yang sudah terkumpul akan otomatis disimpan ke `glints_interrupted.csv`

### Melanjutkan Scraping
Program akan skip data duplikat, jadi aman untuk dijalankan ulang.

## 📊 Contoh Output CSV

```csv
no,position,company,submitted_date,status
1,DATA ANALYST,Pt. Bhinneka Sangkuriang Transport,Agustus 10 2025 7:10 malam,Dilamar
2,Junior Data Analyst,Fleetify.id,November 4 2025 3:19 pm,Applied
3,Data Specialist,PT. Tech Indonesia,Oktober 15 2025 2:30 pm,Ditolak
```

## 🔄 Update & Maintenance

### Check for Updates
Periksa versi terbaru di repository ini

### Version History
- **v2.0** (2024): Multi-strategy navigation, auto-backup
- **v1.0** (2024): Initial release

## 🤝 Kontribusi

Jika menemukan bug atau ingin menambah fitur:
1. Fork repository ini
2. Buat branch baru (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📞 Support

Jika mengalami masalah:
1. Periksa bagian Troubleshooting di atas
2. Pastikan dependencies sudah terinstall dengan benar
3. Periksa versi Chrome dan ChromeDriver compatible
4. Report issue dengan detail error message

## 📜 License

Program ini untuk penggunaan personal. Tidak untuk distribusi komersial.

## ⚡ Quick Start

```bash
# 1. Clone/download script
# 2. Install dependencies
pip install selenium

# 3. Edit kredensial di script
nano Glints-Job-Application-Tracker.py

# 4. Jalankan
python Glints-Job-Application-Tracker.py

# 5. Tunggu sampai selesai
# 6. Buka my_glints_applications_complete.csv
```

## 🎯 FAQ

**Q: Berapa lama waktu yang dibutuhkan?**
A: Tergantung jumlah lamaran. Rata-rata 10-20 detik per halaman.

**Q: Apakah bisa dijalankan di Mac/Linux?**
A: Ya, pastikan ChromeDriver untuk sistem operasi yang sesuai.

**Q: Apakah perlu Chrome browser?**
A: Ya, program menggunakan Selenium dengan Chrome.

**Q: Bisa menggunakan Firefox?**
A: Bisa, tapi perlu modifikasi code untuk menggunakan GeckoDriver.

**Q: Data aman?**
A: Ya, semua data disimpan lokal di komputer Anda.

**Q: Apakah melanggar ToS Glints?**
A: Program ini hanya mengakses data pribadi Anda sendiri, sama seperti membuka browser manual.

---

**Made with ❤️ for Job Seekers**

*Semoga membantu dalam tracking lamaran pekerjaan Anda! Good luck! 🍀*