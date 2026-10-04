---
title: Cara Install Laravel 12 di Windows 11: Panduan Lengkap
description: Panduan lengkap install Laravel 12 di Windows 11: siapkan PHP 8.2+, Composer, dan database, lalu buat project pertama dan jalankan tanpa error.
date: 2026-10-04
tags: [laravel, php, windows, tutorial]
faq:
  - Apa saja syarat install Laravel 12 di Windows?
  - Kamu butuh PHP 8.2 atau lebih baru, Composer, dan database (MySQL/MariaDB atau SQLite). Cara termudah di Windows 11 adalah memakai Laravel Herd yang sudah membundel PHP dan tool lainnya.
  - Apakah Laravel bisa jalan di Windows tanpa XAMPP?
  - Bisa. Laravel Herd dan PHP bawaan (`php artisan serve`) sudah cukup untuk development. XAMPP hanya salah satu opsi, bukan keharusan.
  - Kenapa perintah artisan tidak dikenali setelah install?
  - Biasanya karena Composer belum terdaftar di PATH Windows, atau terminal masih memakai sesi lama. Restart terminal setelah install Composer, lalu cek dengan `composer --version`.
  - Bagaimana cara cek Laravel berhasil terinstall?
  - Jalankan `php artisan serve`, lalu buka `http://localhost:8000` di browser. Kalau halaman welcome Laravel muncul, instalasi berhasil.
---

Menginstall Laravel di Windows sering bikin pemula nyerah sebelum mulai ngoding. Error PHP version, Composer nggak dikenali, database nggak konek — saya sendiri dulu menghabiskan satu sore cuma untuk urusan instalasi.

Artikel ini memangkas semua itu. Ikuti langkahnya berurutan, dan dalam 20 menit kamu punya Laravel 12 yang jalan di Windows 11.

## Pilih Cara Install: Herd vs Manual

Ada dua jalur populer di Windows:

1. **Laravel Herd** (rekomendasi) — aplikasi desktop gratis yang membundel PHP, Composer, dan server lokal. Satu installer, semua beres. Download di [herd.laravel.com](https://herd.laravel.com).
2. **Manual (PHP + XAMPP/Laragon)** — install PHP sendiri, Composer sendiri, web server sendiri. Lebih fleksibel, tapi lebih banyak langkah dan potensi error.

Kalau kamu pemula, pakai Herd. Sisanya di artikel ini mengasumsikan kamu pakai Herd, dengan catatan untuk jalur manual di bagian yang relevan.

## Langkah 1: Install Laravel Herd

1. Download Herd untuk Windows dari herd.laravel.com.
2. Jalankan installer, ikuti wizard sampai selesai.
3. Buka Herd. Secara default ia menyediakan PHP versi terbaru yang kompatibel (8.3/8.4) — sudah memenuhi syarat Laravel 12 (PHP 8.2+).

Verifikasi di PowerShell:

```powershell
php -v
composer --version
```

Keduanya harus menampilkan versi tanpa error. Herd otomatis mendaftarkan PHP dan Composer ke PATH Windows, jadi tidak perlu setting manual.

> **Jalur manual:** kalau tidak pakai Herd, install PHP 8.2+ dari windows.php.net, aktifkan ekstensi yang dibutuhkan Laravel (`mbstring`, `openssl`, `pdo_mysql`/`pdo_sqlite`, `fileinfo`, `tokenizer`, `xml`, `ctype`, `json`, `bcmath`), lalu install Composer dari getcomposer.org.

## Langkah 2: Siapkan Database

Laravel butuh database. Untuk belajar, **SQLite** adalah pilihan paling gampang — tidak perlu install server database sama sekali, datanya disimpan dalam satu file.

Cek dulu ekstensi `pdo_sqlite` aktif:

```powershell
php -m | findstr sqlite
```

Kalau muncul `pdo_sqlite`, kamu siap. Nanti Laravel 12 secara default memakai SQLite, jadi langkah ini praktis tanpa konfigurasi tambahan.

Kalau mau pakai MySQL/MariaDB (misalnya via XAMPP atau Laragon), pastikan servicenya jalan dan catat username, password, serta nama database yang akan dipakai.

## Langkah 3: Buat Project Laravel 12

Buka PowerShell, pindah ke folder tempat kamu menyimpan project (misalnya `C:\laragon\www` atau `D:\projects`), lalu:

```powershell
composer create-project laravel/laravel belajar-laravel
cd belajar-laravel
```

Perintah ini mendownload Laravel 12 beserta semua dependensinya. Tunggu sampai selesai — ukuran downloadnya lumayan, jadi pastikan koneksi stabil.

Cek struktur project yang terbentuk:

```powershell
dir
```

Kamu akan melihat folder `app`, `routes`, `database`, `resources`, dan file penting `.env`.

## Langkah 4: Konfigurasi File .env

File `.env` menyimpan konfigurasi environment: database, nama aplikasi, dan lain-lain. Laravel 12 secara default sudah terkonfigurasi untuk SQLite:

```env
APP_NAME="Belajar Laravel"
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

DB_CONNECTION=sqlite
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_DATABASE=laravel
# DB_USERNAME=root
# DB_PASSWORD=
```

Untuk SQLite, tidak ada yang perlu diubah — file database akan dibuat otomatis saat migration dijalankan.

Kalau memakai MySQL, ubah blok tersebut menjadi:

```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=belajar_laravel
DB_USERNAME=root
DB_PASSWORD=
```

Pastikan database `belajar_laravel` sudah dibuat di MySQL sebelum lanjut.

Generate application key (biasanya sudah otomatis saat `create-project`, tapi amankan dengan perintah ini kalau belum ada):

```powershell
php artisan key:generate
```

## Langkah 5: Jalankan Migration dan Server

Jalankan migration untuk membuat tabel bawaan Laravel (users, sessions, cache):

```powershell
php artisan migrate
```

Untuk SQLite, Laravel akan menanyakan apakah boleh membuat file `database/database.sqlite` — jawab `yes`.

Terakhir, jalankan development server:

```powershell
php artisan serve
```

Buka `http://localhost:8000` di browser. Kalau halaman welcome Laravel 12 muncul, selamat — instalasi berhasil.

> **Catatan Herd:** kalau project-mu disimpan di folder yang dipantau Herd (misalnya `C:\Users\<nama>\Herd`), kamu bisa akses langsung via `http://belajar-laravel.test` tanpa `php artisan serve`.

## Kesalahan Umum Pemula

**"php is not recognized" di PowerShell.** Terjadi kalau PHP belum masuk PATH, atau terminal dibuka sebelum instalasi selesai. Solusi: restart PowerShell (atau restart Windows), lalu cek `php -v` lagi. Pengguna Herd jarang kena ini karena Herd mengatur PATH otomatis.

**Composer error soal ekstensi PHP yang hilang.** Pesan seperti `the requested PHP extension mbstring is missing` berarti ekstensi belum aktif. Di Herd, buka Settings → PHP dan pastikan ekstensi yang dibutuhkan Laravel tercentang. Di instalasi manual, edit `php.ini` dan hapus titik koma di depan baris `extension=mbstring` dan sejenisnya.

**Migration gagal: "could not find driver".** Driver PDO untuk database-mu belum aktif. Untuk SQLite butuh `pdo_sqlite`, untuk MySQL butuh `pdo_mysql`. Cek dengan `php -m` dan aktifkan yang kurang.

**Port 8000 sudah dipakai.** Kalau `php artisan serve` mengeluh port bentrok, jalankan di port lain:

```powershell
php artisan serve --port=8001
```

**Permission error saat Composer install.** Jangan jalankan PowerShell sebagai Administrator kecuali perlu — dan jangan install project di folder sistem seperti `C:\Program Files`. Pakai folder user biasa.

## Checklist Praktis Hari Ini

1. Install Laravel Herd, verifikasi `php -v` dan `composer --version`.
2. Buat project dengan `composer create-project laravel/laravel belajar-laravel`.
3. Sesuaikan `.env`, jalankan `php artisan migrate`.
4. Jalankan `php artisan serve` dan buka di browser.
5. Bonus: buat route pertamamu di `routes/web.php`:

```php
Route::get('/halo', function () {
    return 'Halo, Laravel 12 jalan di Windows 11!';
});
```

Buka `http://localhost:8000/halo` — kalau teksnya muncul, kamu resmi sudah ngoding Laravel.

Langkah berikutnya yang natural: pelajari routing dan Blade, lalu bangun REST API sederhana. Fondasinya sudah beres — tinggal bangun di atasnya.
