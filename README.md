# Chatbot dengan Dashboard Admin

Proyek ini adalah sistem chatbot dengan dashboard admin berbasis Flask dan PostgreSQL. Sistem ini mencakup fitur login dan register dengan role-based access control, serta berbagai endpoint untuk mengelola antrian dan pengaduan.

## Fitur Utama

- **Autentikasi**: Login dan register dengan perbedaan akses antara admin dan user.
- **Chatbot**: Sistem chatbot untuk berinteraksi dengan pengguna.
- **Manajemen Antrian**: Mengelola antrian pengguna.
- **Pengaduan**: Fitur untuk menangani pengaduan pengguna.
- **Dashboard Admin**: Tampilan admin untuk mengelola data pengguna.
- **Email Notifikasi**: Menggunakan SMTP untuk mengirim email.

## Persyaratan

Sebelum menjalankan proyek, pastikan Anda telah menginstal:

- Python 3.x
- PostgreSQL
- Virtual environment (opsional tapi disarankan)

## Cara Menjalankan Proyek

### 1. Siapkan Lingkungan Virtual & Install Dependencies

```sh
python -m venv venv
source venv/bin/activate   # Untuk MacOS/Linux
venv\Scripts\activate    # Untuk Windows
pip install -r requirements.txt
```

### 2. Buat File `.env`

Karena file `.env` tidak disertakan dalam ZIP, Anda perlu membuatnya secara manual di root folder proyek dengan format berikut:

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

#### Cara Mendapatkan `EMAIL_PASS` untuk SMTP
Jika Anda menggunakan Gmail, Anda perlu menggunakan **App Password** karena Google tidak mengizinkan penggunaan kata sandi biasa untuk SMTP. Ikuti langkah-langkah berikut:

1. Buka [Google Account Security](https://myaccount.google.com/security).
2. Aktifkan **2-Step Verification** jika belum diaktifkan.
3. Pergi ke bagian **App Passwords**.
4. Pilih aplikasi **Mail** dan perangkat **Other (Custom name)**.
5. Klik **Generate** dan salin password yang diberikan.
6. Gunakan password tersebut sebagai `EMAIL_PASS` di file `.env` Anda.

### 3. Konfigurasi Database & Migrasi

Pastikan PostgreSQL berjalan, lalu buat database yang sesuai dengan konfigurasi dalam `config.py`.

Jalankan perintah berikut untuk membuat tabel yang diperlukan dan menambahkan admin:

```sh
python migrate_and_seed.py
```

Admin default yang dibuat:

- **Email:** `admin@example.com`
- **Password:** `admin123`

### 4. Jalankan Aplikasi

```sh
python app.py
```

Aplikasi akan berjalan di `http://127.0.0.1:5000/`

## Struktur Folder

```
- routes/                  # Berisi file routing untuk chatbot, antrian, dan pengaduan
- static/                  # Folder untuk asset frontend seperti CSS, JS, dan gambar
- templates/               # Folder untuk tampilan HTML
- .env                     # File konfigurasi environment
- app.py                   # File utama untuk menjalankan aplikasi
- auth.py                  # Manajemen autentikasi user
- config.py                # Konfigurasi database dan aplikasi
- email_service.py         # File untuk pengiriman email via SMTP
- migrate_and_seed.py      # File untuk migrasi database dan seeding admin
- requirements.txt         # Daftar dependencies Python
```
