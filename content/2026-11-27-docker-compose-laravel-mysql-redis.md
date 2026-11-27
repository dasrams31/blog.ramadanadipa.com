---
title: Docker Compose Laravel + MySQL + Redis: Setup Sekali Jalan
description: Satu file docker-compose.yml untuk menjalankan Laravel, MySQL, dan Redis sekaligus. Cocok untuk laptop baru, tim, dan server staging, lengkap dengan contoh.
cover: /assets/img/covers/docker-compose-laravel-mysql-redis.jpg
date: 2026-11-27
tags: [docker-compose, laravel, mysql, redis, devops]
faq:
  - Apa itu Docker Compose dan kenapa developer Laravel memakainya?
  - Docker Compose adalah tool untuk menjalankan banyak container dari satu file YAML. Satu perintah menyalakan Laravel, MySQL, dan Redis sekaligus, jadi semua anggota tim memakai environment yang sama tanpa install satu per satu.
  - Apakah data MySQL hilang kalau container dimatikan?
  - Tidak, selama kamu memakai volume. Data tersimpan di volume Docker dan tetap ada walau container dihapus. Tanpa volume, data hilang begitu container dihapus.
  - Kenapa Laravel tidak bisa konek ke MySQL di Docker?
  - Penyebab paling umum adalah DB_HOST yang masih localhost. Di dalam container, Laravel harus memakai nama service, misalnya mysql, bukan localhost. Cek juga apakah container MySQL sudah sehat sebelum Laravel dijalankan.
  - Bagaimana cara menjalankan queue worker Laravel di Docker Compose?
  - Tambahkan satu service lagi yang menjalankan perintah php artisan queue:work, dengan environment yang sama seperti service app. Worker itu akan memproses job dari Redis tanpa perlu terminal tambahan di laptop.
---

Setiap kali ganti laptop atau onboard anggota tim baru, aku selalu mengulang ritual yang sama: install PHP, install MySQL, install Redis, lalu menghabiskan setengah hari memperbaiki versi yang tidak cocok. Docker Compose mengakhiri ritual itu. Satu file YAML, satu perintah, dan seluruh stack Laravel jalan dengan konfigurasi yang sama di semua mesin.

Artikel ini menjelaskan setup yang kupakai sendiri: Laravel di PHP 8.3, MySQL 8.0, dan Redis 7, lengkap dengan Dockerfile, volume untuk data, dan healthcheck supaya Laravel tidak start sebelum database siap. Semua contoh sudah kutest di Ubuntu dan Windows dengan Docker Desktop.

## Kenapa Docker Compose, bukan install satu per satu

Install langsung di sistem operasi memang terasa ringan, tapi ada tiga masalah yang selalu muncul. Pertama, versi PHP di laptop A dan laptop B berbeda, dan bug muncul hanya di satu mesin. Kedua, MySQL dan Redis yang terinstall di sistem ikut jalan terus dan memakan RAM walau sedang tidak dipakai. Ketiga, membersihkan semuanya saat project selesai itu merepotkan.

Docker Compose menyelesaikan ketiganya. Setiap service jalan di container sendiri, versi dikunci di file, dan semuanya bisa dimatikan dengan satu perintah. Project selesai, jalankan `docker compose down`, dan mesinmu kembali bersih.

## Struktur file yang dipakai

Struktur project Laravel standar, ditambah tiga file di root project.

```text
my-laravel-app/
├── docker-compose.yml
├── Dockerfile
├── .env
├── app/
├── database/
└── ...
```

`docker-compose.yml` mendefinisikan service. `Dockerfile` menjelaskan cara membangun image PHP untuk Laravel. File `.env` tetap file Laravel biasa, hanya nilai host database dan Redis yang berubah.

## Langkah 1: tulis docker-compose.yml

Ini file intinya. Tiga service: `app` untuk Laravel, `mysql` untuk database, dan `redis` untuk cache dan queue.

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: laravel_app
    restart: unless-stopped
    working_dir: /var/www/html
    volumes:
      - ./:/var/www/html
    ports:
      - "8000:8000"
    environment:
      DB_HOST: mysql
      DB_PORT: 3306
      DB_DATABASE: laravel_db
      DB_USERNAME: laravel
      DB_PASSWORD: secret123
      REDIS_HOST: redis
      REDIS_PORT: 6379
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    command: php artisan serve --host=0.0.0.0 --port=8000

  mysql:
    image: mysql:8.0
    container_name: laravel_mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: rootsecret123
      MYSQL_DATABASE: laravel_db
      MYSQL_USER: laravel
      MYSQL_PASSWORD: secret123
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-prootsecret123"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    container_name: laravel_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  mysql_data:
  redis_data:
```

Ada beberapa keputusan penting di file ini. Pertama, `DB_HOST` diisi `mysql`, bukan `localhost`. Di dalam jaringan Docker, container saling memanggil lewat nama service. Kalau diisi `localhost`, Laravel akan mencari MySQL di dalam container app sendiri dan gagal.

Kedua, `depends_on` dengan `condition: service_healthy` membuat app menunggu sampai MySQL benar-benar siap menerima koneksi. Tanpa healthcheck, Laravel sering start lebih dulu lalu crash karena database belum siap. Ini kesalahan yang paling sering kualami di awal.

Ketiga, volume `mysql_data` dan `redis_data` menjaga data tetap ada walau container dihapus. Perintah `docker compose down` tidak menghapus volume kecuali kamu menambahkan flag `-v`, jadi data aman.

## Langkah 2: Dockerfile untuk PHP

Image PHP resmi tidak membawa ekstensi yang dibutuhkan Laravel. Dockerfile ini menambahkan ekstensi yang wajib ada, plus Composer.

```dockerfile
FROM php:8.3-fpm

WORKDIR /var/www/html

RUN apt-get update && apt-get install -y \
    git \
    curl \
    zip \
    unzip \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    && docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip \
    && pecl install redis \
    && docker-php-ext-enable redis \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

COPY . /var/www/html

RUN composer install --no-dev --optimize-autoloader
```

Ekstensi `pdo_mysql` adalah yang paling sering terlupa. Tanpa itu, Laravel akan error dengan pesan `could not find driver` dan kamu akan mengira database yang bermasalah. Ekstensi `redis` dari PECL dibutuhkan supaya Laravel bisa memakai driver Redis bawaan. Kalau projectmu memakai queue, tambahkan juga `pcntl`, dan itu sudah ada di daftar di atas.

## Langkah 3: sesuaikan .env Laravel

Sesuaikan nilai di `.env` dengan yang ada di `docker-compose.yml`. Bagian yang berubah hanya koneksi database dan Redis.

```env
APP_NAME="My Laravel App"
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

DB_CONNECTION=mysql
DB_HOST=mysql
DB_PORT=3306
DB_DATABASE=laravel_db
DB_USERNAME=laravel
DB_PASSWORD=secret123

CACHE_STORE=redis
QUEUE_CONNECTION=redis
SESSION_DRIVER=redis
REDIS_HOST=redis
REDIS_PORT=6379
```

Perhatikan bahwa nilai ini juga ditulis di `environment` service app pada `docker-compose.yml`. Nilai environment dari Compose menimpa `.env` saat container berjalan, jadi dua tempat itu harus konsisten. Praktik yang kupakai: `.env` dipakai untuk nilai lokal saat menjalankan `php artisan` di luar Docker, dan environment Compose dipakai saat jalan di container.

Satu hal yang wajib dilakukan: jangan commit password asli ke Git. Untuk project nyata, ganti `secret123` dengan nilai dari file `.env` yang tidak ikut ter-commit, atau pakai Docker secrets. Password di artikel ini hanya contoh untuk development lokal.

## Langkah 4: jalankan dan verifikasi

Dari root project, jalankan perintah ini.

```bash
docker compose up -d --build
```

Flag `-d` menjalankan semuanya di background, dan `--build` membangun ulang image app. Setelah selesai, cek status semua service.

```bash
docker compose ps
```

Semua service harus berstatus `running`, dan MySQL berstatus `healthy`. Kalau ada yang `exited`, lihat lognya.

```bash
docker compose logs app
docker compose logs mysql
```

Kalau app sudah jalan, jalankan migrasi dari dalam container.

```bash
docker compose exec app php artisan migrate
```

Lalu buka `http://localhost:8000` di browser. Kalau halaman Laravel muncul dan `php artisan tinker` bisa membaca tabel, setup selesai.

Untuk memeriksa koneksi dari dalam container secara langsung, gunakan perintah ini.

```bash
docker compose exec app php artisan tinker --execute="DB::connection()->getPdo(); echo 'Database OK';"
docker compose exec app php artisan tinker --execute="Cache::put('tes', 'ok', 60); echo Cache::get('tes');"
```

## Redis untuk cache dan queue

Dengan `CACHE_STORE=redis` dan `QUEUE_CONNECTION=redis`, Laravel otomatis memakai Redis untuk cache dan antrian. Tambahkan satu service worker supaya job queue diproses tanpa terminal tambahan.

```yaml
  worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: laravel_worker
    restart: unless-stopped
    working_dir: /var/www/html
    volumes:
      - ./:/var/www/html
    environment:
      DB_HOST: mysql
      REDIS_HOST: redis
      QUEUE_CONNECTION: redis
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    command: php artisan queue:work --tries=3
```

Worker ini memakai image yang sama dengan app, jadi tidak perlu Dockerfile kedua. Untuk mencoba, kirim satu job sederhana dari tinker, lalu cek log worker untuk memastikan job diproses.

```bash
docker compose exec app php artisan tinker --execute="dispatch(function () { info('Job dari queue berjalan'); });"
docker compose logs worker
```

## Kesalahan umum pemula

**Port sudah dipakai.** Kalau MySQL lokal di laptopmu sudah memakai port 3306, container MySQL akan gagal start. Solusinya matikan MySQL lokal, atau ubah mapping port kiri menjadi `"3307:3306"`. Ingat, yang diubah hanya angka kiri. Angka kanan adalah port di dalam container dan harus tetap 3306.

**Permission folder storage dan bootstrap/cache.** Laravel butuh akses tulis ke `storage` dan `bootstrap/cache`. Kalau muncul error permission, jalankan ini dari dalam container.

```bash
docker compose exec app chown -R www-data:www-data storage bootstrap/cache
docker compose exec app chmod -R 775 storage bootstrap/cache
```

**Mengubah .env tapi tidak restart.** Laravel membaca `.env` saat proses start. Setelah mengubah `.env`, restart service app supaya nilai baru terbaca.

```bash
docker compose restart app
```

**Lupa rebuild setelah mengubah Dockerfile.** Perubahan di Dockerfile tidak berlaku hanya dengan `up`. Selalu sertakan `--build` setelah mengubah Dockerfile.

```bash
docker compose up -d --build
```

**Data hilang setelah `down -v`.** Flag `-v` menghapus volume, termasuk `mysql_data`. Jangan pernah memakai `down -v` di environment yang datanya masih dibutuhkan. Untuk sekadar mematikan, cukup `docker compose down`.

## Perintah harian yang wajib dihafal

Enam perintah ini menutupi hampir semua kebutuhan sehari-hari.

```bash
docker compose up -d          # nyalakan semua service
docker compose down           # matikan semua service, data tetap aman
docker compose ps             # lihat status service
docker compose logs -f app    # ikuti log app secara live
docker compose exec app bash  # masuk ke dalam container app
docker compose exec app php artisan migrate  # jalankan migrasi
```

## Langkah praktis hari ini

Kalau kamu belum pernah memakai Docker Compose, coba langsung di project Laravel yang sedang kamu kerjakan. Salin file `docker-compose.yml` dan `Dockerfile` di atas, sesuaikan nama database dan password, lalu jalankan `docker compose up -d --build`. Begitu halaman Laravel muncul di `localhost:8000` dan migrasi berhasil, kamu sudah punya environment yang bisa dibagikan ke siapa pun lewat Git tanpa instruksi install yang panjang.

Langkah berikutnya yang layak dicoba: tambahkan service `nginx` sebagai reverse proxy di depan app, dan service `mailpit` untuk menangkap email keluar saat development. Keduanya mengikuti pola yang sama seperti service di atas, dan aku akan membahasnya di artikel berikutnya.
