# 🚀 Chatbot dengan Dashboard Admin

Sistem ini adalah chatbot berbasis **Flask** dan **PostgreSQL** dengan **Dashboard Admin** untuk mengelola pengguna, antrian, dan pengaduan. Dilengkapi dengan autentikasi berbasis **Role-Based Access Control (RBAC)** serta notifikasi email.

---

## ✨ Fitur Utama

✅ **Autentikasi & RBAC**: Login dan register dengan akses berbeda untuk admin & user.  
✅ **Chatbot**: Respon otomatis untuk interaksi pengguna.  
✅ **Manajemen Antrian**: Mengelola antrian pengguna secara efisien.  
✅ **Pengaduan Pengguna**: Formulir dan sistem tindak lanjut pengaduan.  
✅ **Dashboard Admin**: Panel kontrol untuk mengelola data pengguna.  
✅ **Notifikasi Email**: Menggunakan SMTP untuk mengirim email.

---

## ⚙️ Persyaratan
Sebelum menjalankan proyek, pastikan telah menginstal:
- **Python 3.x**
- **PostgreSQL**
- **Virtual environment** (opsional, tetapi disarankan)

---

## 🚀 Cara Menjalankan Proyek

### 1️⃣ Siapkan Lingkungan Virtual & Install Dependencies
```sh
python -m venv .venv
source .venv/bin/activate   # MacOS/Linux
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 2️⃣ Konfigurasi `.env`
Buat file `.env` di root folder proyek dengan format berikut:
```
EMAIL_USER=your_email 
EMAIL_PASS=your_app_password

DB_NAME=ktp_chatbot
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=your_secret_key
```

#### 🔑 Cara Mendapatkan `EMAIL_PASS` untuk SMTP Gmail
1. Buka [Google Account Security](https://myaccount.google.com/security).
2. Aktifkan **2-Step Verification** jika belum.
3. Pergi ke **App Passwords**.
4. Pilih **Mail** dan **Other (Custom name)**.
5. Klik **Generate** dan gunakan password yang diberikan sebagai `EMAIL_PASS`.

### 3️⃣ Konfigurasi Database & Migrasi
Pastikan PostgreSQL berjalan, lalu buat database yang sesuai dengan konfigurasi di `config.py`.

```sh
python migrate_and_seed.py
```

Admin default yang dibuat:
- **Email:** `admin@example.com`
- **Password:** `admin123`

### 4️⃣ Jalankan Aplikasi
```sh
python app.py
```
Aplikasi berjalan di **`http://127.0.0.1:5000/`**

---

## 📂 Struktur Folder
```
- routes/                  # Routing untuk chatbot, antrian, dan pengaduan
- static/                  # Asset frontend seperti CSS, JS, dan gambar
- templates/               # Tampilan HTML
- .env                     # Konfigurasi environment
- app.py                   # File utama aplikasi
- auth.py                  # Manajemen autentikasi user
- config.py                # Konfigurasi database dan aplikasi
- email_service.py         # Pengiriman email via SMTP
- migrate_and_seed.py      # Migrasi database dan seeding admin
- requirements.txt         # Dependencies Python
```

---

💡 **Proyek ini dikembangkan dengan Flask untuk backend, PostgreSQL sebagai database, dan sistem autentikasi berbasis role. Siap untuk dikembangkan lebih lanjut!** 🚀
