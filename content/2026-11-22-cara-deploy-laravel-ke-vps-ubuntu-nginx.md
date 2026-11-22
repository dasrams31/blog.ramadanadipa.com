---
title: Deploy Laravel ke VPS Ubuntu dengan Nginx
description: Panduan deploy Laravel ke VPS Ubuntu: install Nginx, PHP 8.3, MySQL, dan SSL gratis sampai aplikasi live. Langkah demi langkah dengan contoh konfigurasi nyata.
cover: /assets/img/covers/cara-deploy-laravel-ke-vps-ubuntu-nginx.jpg
date: 2026-11-22
tags: [laravel, vps, nginx, ubuntu, deploy]
faq:
  - Berapa spesifikasi VPS minimal untuk menjalankan Laravel?
  - VPS 1 vCPU dengan RAM 1 GB sudah cukup untuk aplikasi kecil, tapi 2 GB lebih aman kalau MySQL dan queue worker jalan di server yang sama.
  - Apakah deploy Laravel wajib pakai panel seperti cPanel?
  - Tidak wajib. Nginx, PHP-FPM, dan Composer saja sudah cukup, dan kamu dapat kontrol penuh dengan biaya lebih murah daripada panel berbayar.
  - Kenapa aplikasi Laravel error 500 setelah deploy ke VPS?
  - Penyebab paling umum adalah permission folder storage yang salah, APP_KEY belum di-generate, atau cache config lama. Cek log di storage/logs/laravel.log untuk pesan pastinya.
  - Bagaimana cara update aplikasi Laravel yang sudah live di VPS?
  - Tarik kode terbaru dengan git pull, jalankan composer install dan php artisan migrate, lalu refresh cache dan restart PHP-FPM. Pakai skrip deploy supaya langkahnya konsisten.
---

Deploy pertamaku ke VPS berakhir dengan halaman putih dan error 500 yang tidak jelas. Setelah bolak-balik cek log, ternyata masalahnya sepele: permission folder `storage` salah dan `APP_KEY` belum di-generate. Artikel ini merangkum alur deploy Laravel ke VPS Ubuntu yang sudah kupakai berkali-kali, dari server kosong sampai aplikasi live dengan HTTPS.

Target akhirnya sederhana: aplikasi Laravel jalan di Nginx dengan PHP-FPM, database MySQL, dan sertifikat SSL gratis dari Let's Encrypt. Semua perintah di bawah ini dijalankan di Ubuntu 24.04, tapi caranya sama untuk Ubuntu 22.04.

## Yang kamu butuhkan sebelum mulai

Siapkan tiga hal ini dulu supaya prosesnya tidak terputus di tengah jalan.

1. **VPS Ubuntu** dengan akses root atau user sudo, misalnya dari DigitalOcean, Vultr, atau IDCloudHost. Spesifikasi 1 vCPU dan 2 GB RAM sudah cukup untuk aplikasi kecil sampai menengah.
2. **Domain** yang A record-nya sudah diarahkan ke IP VPS. Tunggu propagasi DNS selesai sebelum mengurus SSL.
3. **Kode Laravel di Git**, misalnya GitHub atau GitLab, lengkap dengan file `.env.example`.

## Langkah 1: install Nginx, PHP, MySQL, dan Composer

Login ke VPS lewat SSH, lalu update paket dan install semua yang dibutuhkan dalam satu perintah.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx mysql-server php8.3-fpm php8.3-cli \
  php8.3-mysql php8.3-mbstring php8.3-xml php8.3-curl php8.3-zip \
  php8.3-bcmath php8.3-intl git unzip curl
```

Perhatikan paket `php8.3-fpm`, bukan `libapache2-mod-php`. Nginx tidak bisa menjalankan PHP sendiri, ia meneruskan request PHP ke PHP-FPM lewat socket. Ekstensi di atas mencakup kebutuhan umum Laravel: `mbstring`, `xml`, `curl`, `zip`, dan `bcmath`.

Selanjutnya install Composer secara global.

```bash
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
composer --version
```

Terakhir, amankan instalasi MySQL dan buat database beserta user khusus aplikasi. Jangan pernah memakai user root MySQL untuk aplikasi.

```bash
sudo mysql_secure_installation
sudo mysql -e "CREATE DATABASE myapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER 'myapp'@'localhost' IDENTIFIED BY 'password-yang-kuat';"
sudo mysql -e "GRANT ALL PRIVILEGES ON myapp.* TO 'myapp'@'localhost';"
```

## Langkah 2: clone project dan install dependency

Simpan kode aplikasi di `/var/www`, lokasi standar untuk web di Ubuntu. Clone repo, lalu install dependency PHP tanpa paket development.

```bash
cd /var/www
sudo git clone https://github.com/username/myapp.git
cd myapp
sudo composer install --no-dev --optimize-autoloader
```

Flag `--no-dev` penting di production: paket seperti PHPUnit dan Laravel Debugbar tidak ikut terinstall, jadi folder `vendor` lebih kecil dan permukaan serangan lebih sempit.

## Langkah 3: konfigurasi file .env

Salin `.env.example` menjadi `.env`, lalu isi kredensial database dan APP_KEY. Jangan pernah menyalin file `.env` dari laptop ke server lewat cara yang tidak aman, dan jangan commit `.env` ke Git.

```bash
cp .env.example .env
nano .env
```

Isi bagian pentingnya seperti ini, sesuaikan nama database dan password dengan yang kamu buat di langkah 1.

```ini
APP_NAME="MyApp"
APP_ENV=production
APP_DEBUG=false
APP_URL=https://myapp.example.com

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=myapp
DB_USERNAME=myapp
DB_PASSWORD=password-yang-kuat
```

`APP_DEBUG=false` wajib di production. Kalau debug menyala, halaman error Laravel menampilkan potongan konfigurasi, query, dan path file ke siapa pun yang memicu error. Setelah `.env` selesai, generate key dan jalankan migrasi.

```bash
php artisan key:generate
php artisan migrate --force
php artisan storage:link
```

## Langkah 4: konfigurasi Nginx

Ini bagian yang paling sering salah. Buat file konfigurasi baru untuk domain kamu, lalu isi dengan server block berikut.

```bash
sudo nano /etc/nginx/sites-available/myapp
```

```nginx
server {
    listen 80;
    server_name myapp.example.com;
    root /var/www/myapp/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.3-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

Tiga detail di konfigurasi ini sering terlewat. Pertama, `root` harus mengarah ke folder `public`, bukan ke root project Laravel. Kalau root mengarah ke folder project, file `.env` bisa diakses lewat browser. Kedua, blok `location /` memakai `try_files` dengan fallback ke `index.php`, supaya routing Laravel yang cantik tetap jalan tanpa `index.php` di URL. Ketiga, `fastcgi_pass` harus cocok dengan versi PHP yang terinstall. Cek nama socket yang benar dengan `ls /var/run/php/`.

Aktifkan konfigurasi dan reload Nginx.

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Perintah `nginx -t` menguji sintaks sebelum reload. Kalau ada typo, Nginx menolak reload dan konfigurasi lama tetap jalan, jadi situs tidak ikut mati.

## Langkah 5: permission dan cache

Laravel butuh akses tulis ke folder `storage` dan `bootstrap/cache`. Beri kepemilikan ke user web server `www-data`, lalu kunci permission file dan folder dengan angka yang aman.

```bash
sudo chown -R www-data:www-data /var/www/myapp/storage /var/www/myapp/bootstrap/cache
sudo find /var/www/myapp -type f -exec chmod 644 {} \;
sudo find /var/www/myapp -type d -exec chmod 755 {} \;
sudo chmod -R 775 /var/www/myapp/storage /var/www/myapp/bootstrap/cache
```

Terakhir, aktifkan cache konfigurasi, route, dan view supaya request lebih cepat dan `.env` tidak dibaca ulang setiap request.

```bash
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

Ingat satu aturan: setiap kali kamu mengubah `.env` di server, jalankan `php artisan config:cache` lagi. Kalau tidak, aplikasi tetap memakai konfigurasi lama dari cache dan perubahanmu seolah tidak berpengaruh.

## Langkah 6: HTTPS gratis dengan Certbot

SSL dari Let's Encrypt gratis dan cukup untuk hampir semua aplikasi. Install Certbot, lalu biarkan plugin Nginx mengurus sertifikat dan redirect HTTP ke HTTPS otomatis.

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d myapp.example.com
```

Certbot menambahkan blok SSL ke konfigurasi Nginx dan memasang timer systemd untuk perpanjangan otomatis. Verifikasi timernya jalan dengan perintah berikut.

```bash
sudo systemctl list-timers | grep certbot
```

Sampai di sini aplikasi kamu sudah live di `https://myapp.example.com`. Coba buka di browser, lalu cek halaman login atau halaman utama untuk memastikan tidak ada error 500.

## Kesalahan umum pemula dan cara menghindarinya

**Root Nginx mengarah ke folder project, bukan `public`.** Ini kesalahan paling berbahaya karena file `.env` dan `composer.json` bisa diunduh lewat browser. Selalu arahkan `root` ke `/var/www/myapp/public`.

**APP_DEBUG masih true di production.** Halaman error Laravel menampilkan stack trace lengkap. Matikan debug dan cek log di `storage/logs/laravel.log` kalau ada error, jangan menebak dari halaman putih.

**Permission folder storage 777.** Memberi 777 memang menyelesaikan error permission, tapi siapa pun di server bisa menulis ke folder itu. Gunakan kepemilikan `www-data` dan permission 775 seperti di langkah 5.

**Lupa menjalankan migrasi setelah deploy.** Aplikasi jalan tapi halaman error karena tabel belum ada. Selalu jalankan `php artisan migrate --force` sebagai bagian dari proses deploy, bukan sebagai langkah yang diingat belakangan.

**Cache config tidak di-refresh setelah ubah .env.** Ini jebakan klasik: kamu mengubah password database, tapi aplikasi tetap memakai yang lama. Biasakan menjalankan `config:cache` ulang setiap kali `.env` berubah.

## Skrip deploy sekali jalan

Supaya deploy berikutnya tidak manual dan tidak ada langkah yang tertinggal, simpan skrip ini sebagai `deploy.sh` di repo, lalu jalankan setiap kali ada update.

```bash
#!/bin/bash
set -e
cd /var/www/myapp

git pull origin main
composer install --no-dev --optimize-autoloader
php artisan migrate --force
php artisan config:cache
php artisan route:cache
php artisan view:cache
sudo systemctl reload php8.3-fpm
echo "Deploy selesai."
```

Flag `set -e` membuat skrip berhenti di perintah pertama yang gagal, jadi deploy yang rusak tidak dilanjutkan setengah jalan. Satu catatan: perintah `systemctl reload` butuh sudo tanpa password untuk user deploy, atau jalankan skrip ini sebagai root.

Dengan alur ini, deploy berikutnya tinggal satu perintah: `bash deploy.sh`. Kalau nanti aplikasimu butuh queue worker atau scheduler, tambahkan Supervisor untuk worker dan cron entry `php artisan schedule:run` per menit. Tapi untuk aplikasi pertama yang live, enam langkah di atas sudah cukup.

Selamat, Laravel kamu sekarang jalan di VPS sendiri, bukan lagi di shared hosting dengan batasan yang tidak jelas.
