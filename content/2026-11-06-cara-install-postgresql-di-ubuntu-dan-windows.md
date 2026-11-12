---
title: Cara Install PostgreSQL di Ubuntu dan Windows Lengkap
description: Panduan install PostgreSQL di Ubuntu dan Windows langkah demi langkah, tambah user, buat database pertama, atur password, sampai koneksi ke Laravel dan pgAdmin.
cover: /assets/img/covers/cara-install-postgresql-di-ubuntu-dan-windows.jpg
date: 2026-11-06
tags: [postgresql, database, ubuntu, windows, laravel]
faq:
  - Bagaimana cara cek PostgreSQL sudah terinstall dan jalan?
  - Jalankan `psql --version` untuk cek versi, lalu `sudo systemctl status postgresql` di Ubuntu untuk memastikan servicenya aktif. Kalau muncul `active (running)`, instalasi kamu sudah benar.
  - Kenapa psql menolak login dengan user postgres?
  - Di Ubuntu, user postgres memakai autentikasi peer, jadi kamu harus login lewat akun sistem postgres dengan `sudo -u postgres psql`. Kalau mau login pakai password, ubah dulu passwordnya lalu atur metode autentikasi di `pg_hba.conf`.
  - Berapa port default PostgreSQL?
  - Port default PostgreSQL adalah 5432. Kalau port itu sudah dipakai aplikasi lain, ubah di file `postgresql.conf` lalu restart servicenya.
  - Apakah PostgreSQL gratis untuk project komersial?
  - Ya, PostgreSQL sepenuhnya gratis dan open source dengan lisensi PostgreSQL Licence yang permisif. Kamu bebas memakainya untuk project pribadi maupun komersial tanpa biaya.
---

PostgreSQL adalah database yang aku pakai di hampir semua project Laravel belakangan ini. Alasannya sederhana: gratis, stabil, dan fiturnya lengkap. Masalahnya, langkah installnya sering bikin pemula stuck di hal sepele, misalnya lupa password user postgres, atau psql menolak login tanpa pesan yang jelas.

Artikel ini membahas instalasi PostgreSQL di dua sistem yang paling sering dipakai developer Indonesia: Ubuntu dan Windows. Ikuti sesuai sistem yang kamu pakai, lalu lanjut ke bagian membuat user dan database pertama, karena itu bagian yang paling sering dilewati tutorial lain.

## Sebelum install, siapkan ini dulu

Kamu butuh dua hal sebelum mulai: hak akses admin di komputermu, dan koneksi internet untuk mengunduh paket. Di Ubuntu, pastikan kamu bisa menjalankan `sudo`. Di Windows, jalankan installer dengan klik kanan lalu pilih Run as administrator supaya tidak ada masalah izin saat instalasi.

Satu hal lagi yang perlu diputuskan dari awal: versi PostgreSQL yang mau dipakai. Versi terbaru saat artikel ini ditulis adalah PostgreSQL 17, tapi versi 16 juga masih sangat layak untuk belajar dan project produksi. Yang penting, samakan versi di laptop dan di server supaya tidak ada kejutan saat deploy.

## Install PostgreSQL di Ubuntu

Cara paling gampang di Ubuntu adalah lewat apt, paket manager bawaan. Ubuntu sudah menyediakan PostgreSQL di repository resminya, jadi kamu tidak perlu menambah repository pihak ketiga untuk pemakaian standar.

```bash
# Perbarui daftar paket dulu supaya dapat versi terbaru dari repo
sudo apt update

# Install PostgreSQL beserta tools tambahannya
sudo apt install postgresql postgresql-contrib -y

# Cek versi yang terinstall
psql --version

# Pastikan service PostgreSQL berjalan
sudo systemctl status postgresql
```

Kalau output status menunjukkan `active (running)`, instalasi kamu berhasil. Service ini otomatis jalan setiap kali Ubuntu dinyalakan, jadi kamu tidak perlu menjalankannya manual tiap kali buka laptop.

Satu hal yang membingungkan pemula: setelah install, PostgreSQL membuat akun sistem bernama `postgres` dan user database bernama `postgres`. Keduanya belum punya password. Untuk masuk ke konsol interaktif psql, pakai akun sistem itu:

```bash
# Masuk ke psql sebagai user postgres
sudo -u postgres psql

# Di dalam psql, cek koneksi dan versi
SELECT version();

# Keluar dari psql
\q
```

Perintah `sudo -u postgres psql` adalah cara standar di Ubuntu. Jangan coba login langsung dengan `psql -U postgres` dari akun biasa, karena autentikasi defaultnya adalah peer, yang artinya nama user sistem harus sama dengan nama user database. Error `Peer authentication failed for user "postgres"` adalah error yang paling sering ditanyakan soal ini, dan penyebabnya hampir selalu karena perintah di atas tidak dipakai.

### Atur password untuk user postgres

Supaya bisa login pakai password, misalnya dari aplikasi atau dari pgAdmin, atur dulu passwordnya dari dalam psql:

```sql
-- Masih di dalam psql sebagai user postgres
ALTER USER postgres PASSWORD 'ganti-dengan-password-kuat';
```

Setelah itu, ubah metode autentikasi di file `pg_hba.conf`. Cari lokasi filenya dengan perintah berikut:

```bash
sudo -u postgres psql -c "SHOW hba_file;"
```

Buka file tersebut, cari baris yang metode autentikasinya `peer` untuk user postgres, lalu ganti menjadi `scram-sha-256`. Simpan, lalu restart service:

```bash
sudo systemctl restart postgresql
```

Setelah restart, kamu bisa login dengan password:

```bash
psql -U postgres -h localhost
```

## Install PostgreSQL di Windows

Di Windows, cara paling gampang adalah memakai installer resmi dari EnterpriseDB, yang bisa diunduh di postgresql.org/download/windows. Installer ini sudah menyertakan pgAdmin, tool grafis untuk mengelola database, jadi kamu tidak perlu install tool tambahan.

Langkahnya begini:

1. Unduh installer sesuai versi yang kamu mau, pilih yang 64 bit kalau Windows kamu 64 bit.
2. Jalankan installer sebagai administrator.
3. Pilih komponen yang diinstall. Biarkan semua tercentang, termasuk PostgreSQL Server, pgAdmin 4, dan Command Line Tools.
4. Pilih folder instalasi, biarkan default di `C:\Program Files\PostgreSQL\17` kalau kamu tidak punya alasan khusus.
5. Masukkan password untuk user postgres. Catat password ini baik baik, karena kamu akan memakainya setiap kali login lewat pgAdmin atau aplikasi.
6. Biarkan port di 5432, kecuali port itu sudah dipakai aplikasi lain di komputermu.
7. Selesaikan instalasi dan tunggu sampai selesai.

Setelah instalasi selesai, buka pgAdmin 4 dari Start Menu. Saat pertama dibuka, pgAdmin meminta password master, lalu kamu bisa menghubungkan server dengan memasukkan password user postgres yang tadi kamu buat. Kalau koneksi berhasil, kamu akan melihat daftar database bawaan: postgres, template0, dan template1.

### Tambahkan psql ke PATH di Windows

Supaya bisa menjalankan `psql` dari Command Prompt atau PowerShell, tambahkan folder `bin` PostgreSQL ke PATH. Foldernya biasanya `C:\Program Files\PostgreSQL\17\bin`. Caranya: buka System Properties, pilih Environment Variables, edit variabel Path, lalu tambah folder tersebut. Tutup dan buka ulang terminal, lalu tes:

```powershell
psql --version
psql -U postgres -h localhost
```

Kalau `psql` tidak dikenali, kemungkinan besar terminalnya masih memakai PATH lama. Tutup semua jendela terminal dan buka yang baru.

## Buat user dan database pertama

Jangan memakai user postgres untuk project sehari hari. Buat user dan database khusus per project, supaya kalau satu project bermasalah, project lain tidak ikut kena. Ini praktik yang sama seperti di MySQL, hanya sintaksnya sedikit berbeda.

Masuk dulu ke psql sebagai postgres, lalu jalankan perintah berikut. Contoh ini membuat user dan database untuk project toko online:

```sql
-- Buat user baru dengan password
CREATE USER toko_user WITH PASSWORD 'password-kuat-di-sini';

-- Buat database baru yang dimiliki user tersebut
CREATE DATABASE toko_db OWNER toko_user;

-- Beri hak penuh ke user atas database itu
GRANT ALL PRIVILEGES ON DATABASE toko_db TO toko_user;

-- Cek daftar database yang ada
\l

-- Cek daftar user yang ada
\du
```

Untuk menghapus database atau user saat sudah tidak dipakai, perintahnya juga singkat:

```sql
-- Hati hati, perintah ini menghapus database beserta seluruh isinya
DROP DATABASE toko_db;

-- Menghapus user
DROP USER toko_user;
```

Perintah `DROP DATABASE` tidak bisa dibatalkan. Biasakan mengecek nama database dua kali sebelum menekan Enter, terutama di server produksi.

## Hubungkan PostgreSQL ke Laravel

Kalau project kamu Laravel, koneksi ke PostgreSQL tinggal diatur di file `.env`. Pastikan ekstensi `pdo_pgsql` aktif di PHP kamu, lalu ubah konfigurasi database:

```env
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=toko_db
DB_USERNAME=toko_user
DB_PASSWORD=password-kuat-di-sini
```

Setelah itu, tes koneksinya dengan perintah berikut:

```bash
php artisan migrate:status
```

Kalau muncul daftar migration tanpa error, koneksi kamu sudah benar. Kalau muncul error `could not find driver`, berarti ekstensi `pdo_pgsql` belum aktif. Di Ubuntu, install dengan `sudo apt install php-pgsql` lalu restart PHP FPM atau Apache. Di Windows, buka `php.ini`, hapus tanda titik koma di depan `extension=pdo_pgsql`, lalu restart web server kamu.

## Kesalahan umum pemula dan cara menghindarinya

### 1. Lupa password user postgres

Ini kesalahan paling klasik di Windows, karena password dimasukkan sekali saat instalasi lalu tidak pernah dicatat. Solusinya: ubah password lewat pgAdmin tidak bisa kalau kamu tidak bisa login. Cara paling gampang adalah reinstall, atau edit `pg_hba.conf` untuk sementara memakai metode `trust`, ubah password dari psql, lalu kembalikan metodenya ke `scram-sha-256`. Catat password di password manager sejak awal supaya tidak terulang.

### 2. Service PostgreSQL tidak jalan

Di Ubuntu, cek dengan `sudo systemctl status postgresql`. Kalau statusnya mati, nyalakan dengan `sudo systemctl start postgresql`. Di Windows, cek di Services, cari `postgresql-x64-17`, lalu pastikan statusnya Running dan Startup Type-nya Automatic.

### 3. Port 5432 sudah dipakai

Kadang port 5432 sudah dipakai instalasi PostgreSQL lain, atau aplikasi lain. Gejalanya: instalasi gagal di langkah akhir, atau service tidak mau start. Cek pemakaian port dengan `sudo ss -tulpn | grep 5432` di Ubuntu, atau `netstat -ano | findstr 5432` di Windows. Kalau memang bentrok, ubah port di `postgresql.conf` ke angka lain, misalnya 5433, lalu sesuaikan juga di konfigurasi aplikasi kamu.

### 4. Menjalankan query di database yang salah

psql tidak memberi peringatan saat kamu menjalankan `DROP TABLE` di database yang salah. Sebelum menjalankan query destruktif, cek dulu database aktif dengan perintah `\conninfo`. Kebiasaan kecil ini menyelamatkan banyak data.

### 5. Tidak membackup sebelum eksperimen

PostgreSQL punya tool backup bawaan yang sangat mudah dipakai. Sebelum mencoba migration berisiko atau import data besar, backup dulu:

```bash
# Backup satu database ke file .sql
pg_dump -U toko_user -h localhost toko_db > backup-toko.sql

# Restore dari file backup
psql -U toko_user -h localhost toko_db < backup-toko.sql
```

## Langkah praktis yang bisa langsung dicoba

Selesai baca artikel ini, coba lima langkah berikut dalam 15 menit:

1. Install PostgreSQL di sistem kamu, lalu verifikasi dengan `psql --version`.
2. Masuk ke psql dan buat satu user plus satu database untuk project latihan.
3. Buat satu tabel sederhana dan isi dua baris data:

```sql
-- Pindah ke database latihan dulu
\c toko_db

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO customers (name, email) VALUES
    ('Rama', 'rama@example.com'),
    ('Dina', 'dina@example.com');

SELECT * FROM customers;
```

4. Hubungkan database itu ke project Laravel atau ke aplikasi lain yang kamu pakai, lalu jalankan satu query dari aplikasi tersebut.
5. Coba backup database latihanmu dengan `pg_dump`, lalu restore ke database baru untuk memastikan backupnya benar benar bisa dipakai.

Kalau lima langkah itu berhasil, instalasi PostgreSQL kamu sudah siap dipakai project nyata. Langkah berikutnya yang layak dipelajari adalah index supaya query cepat, lalu backup otomatis dengan cron job.
