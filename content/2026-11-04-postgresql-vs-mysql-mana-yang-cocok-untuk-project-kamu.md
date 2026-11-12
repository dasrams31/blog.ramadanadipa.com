---
title: PostgreSQL vs MySQL: Mana yang Cocok untuk Project Kamu?
description: PostgreSQL atau MySQL untuk project Laravel kamu? Perbandingan jujur soal fitur, JSON, performa, dan kapan masing-masing cocok, plus contoh SQL nyata.
cover: /assets/img/covers/postgresql-vs-mysql-mana-yang-cocok-untuk-project-kamu.jpg
date: 2026-11-04
tags: [postgresql, mysql, database, laravel]
faq:
  - PostgreSQL atau MySQL yang lebih bagus untuk pemula?
  - Keduanya bagus untuk pemula. MySQL terasa lebih mudah di awal karena banyak tutorial hosting murah yang memakainya, sedangkan PostgreSQL memberi fondasi yang lebih kuat untuk tipe data dan fitur lanjutan. Pilih yang dipakai tutorial atau hosting yang kamu ikuti, lalu pahami konsep SQL-nya.
  - Apakah Laravel bisa pindah dari MySQL ke PostgreSQL dengan mudah?
  - Sebagian besar query Eloquent dan migration bisa pindah tanpa banyak perubahan, tetapi query mentah, fungsi tanggal, tipe data JSON, dan auto increment sering perlu disesuaikan. Pindah paling aman di awal project, sebelum query mentah menumpuk.
  - Kapan PostgreSQL lebih cocok daripada MySQL?
  - PostgreSQL lebih cocok saat kamu butuh JSONB, full text search bawaan, tipe data array atau geometri, constraint yang ketat, dan query analitik yang kompleks. Untuk aplikasi CRUD sederhana, perbedaannya sering tidak terasa.
  - Apakah MySQL gratis untuk project komersial?
  - MySQL Community Edition gratis dipakai, termasuk untuk project komersial, dengan lisensi GPL. Kalau kamu tidak mau terikat ketentuan GPL untuk distribusi tertentu, MariaDB adalah alternatif yang kompatibel dan juga gratis.
---

Kalau kamu baru mau mulai project dan bingung memilih database, jawabannya jarang soal mana yang paling cepat. Dua database ini sudah sama sama matang, sama sama gratis, dan sama sama dipakai aplikasi besar. Yang membedakan adalah fitur apa yang kamu butuhkan, seberapa ketat datamu harus dijaga, dan seberapa nyaman kamu dengan ekosistemnya.

Aku memakai keduanya: MySQL untuk setup cepat di hosting murah, PostgreSQL untuk data yang lebih kompleks. Artikel ini membandingkan keduanya dari sisi yang terasa saat coding.

## Jawaban singkatnya

Pilih PostgreSQL kalau kamu membangun aplikasi baru dengan Laravel atau stack modern, butuh JSON yang serius, full text search, atau query yang kompleks. Pilih MySQL atau MariaDB kalau hosting yang kamu pakai sudah menyediakannya, tim sudah terbiasa, atau projectnya aplikasi CRUD dan CMS yang standar.

Kalau masih ragu, pilih PostgreSQL untuk project baru, karena fitur lanjutannya lebih sering kepakai seiring project membesar. Tapi jangan memaksakannya kalau hosting atau tim kamu sudah nyaman dengan MySQL.

## Perbedaan yang paling terasa saat coding

### Tipe data dan aturan yang ketat

PostgreSQL terkenal ketat soal tipe data. Kalau kolomnya integer, kamu tidak bisa memasukkan teks begitu saja. Kedengarannya merepotkan, tapi aturan ini justru menyelamatkanmu dari data sampah yang baru ketahuan berminggu minggu kemudian.

MySQL lebih longgar, terutama pada instalasi lama: ia bisa memotong string yang kepanjangan atau mengubah nilai tidak valid tanpa error yang jelas. Pada instalasi modern dengan strict mode aktif, perilaku ini sudah jauh lebih baik, jadi pastikan strict mode aktif sejak awal.

PostgreSQL juga punya tipe data lebih kaya: array, range, UUID bawaan, inet untuk alamat IP, dan JSONB yang bisa diindeks. MySQL punya JSON juga dan cukup untuk kebutuhan sederhana; bedanya baru terasa saat JSON-nya besar dan sering dicari.

### JSON: JSONB PostgreSQL vs JSON MySQL

Di PostgreSQL, JSONB menyimpan JSON dalam bentuk biner yang sudah diproses, jadi pencarian di dalamnya cepat dan bisa memakai indeks GIN.

```sql
-- PostgreSQL: cari produk dengan warna merah di kolom JSONB
SELECT id, name, specs
FROM products
WHERE specs @> '{"color": "red"}';

-- Indeks supaya pencarian JSONB tidak scan seluruh tabel
CREATE INDEX idx_products_specs ON products USING GIN (specs);
```

Di MySQL, kolom JSON juga bisa dicari, tapi sintaksnya berbeda dan indeksnya memakai generated column. Untuk JSON kecil, bedanya tidak terasa.

```sql
-- MySQL: cara yang sama dengan fungsi JSON
SELECT id, name, specs
FROM products
WHERE specs ->> '$.color' = 'red';
```

Pelajaran praktisnya: kalau datamu relasional dan rapi, pakai tabel dan foreign key seperti biasa. JSON baru dipakai untuk data yang strukturnya fleksibel, misalnya atribut produk yang berbeda tiap kategori.

### Full text search dan fitur kecil lainnya

PostgreSQL punya full text search bawaan yang cukup kuat untuk search sederhana sampai menengah, tanpa layanan tambahan. MySQL juga punya FULLTEXT index untuk search sederhana. Kalau kebutuhan searchmu berkembang ke typo tolerance dan facet, kamu tetap butuh Meilisearch, Typesense, atau Elasticsearch di kedua database.

Perbedaan kecil lain yang sering kepakai adalah `RETURNING` di PostgreSQL, yang mengambil id baris yang baru dimasukkan dalam satu query, dan sintaks upsert yang berbeda di keduanya:

```sql
-- PostgreSQL: insert lalu langsung dapat id-nya
INSERT INTO users (name, email)
VALUES ('Rama', 'rama@example.com')
RETURNING id;

-- PostgreSQL: upsert berdasarkan email yang unik
INSERT INTO users (email, name)
VALUES ('rama@example.com', 'Rama')
ON CONFLICT (email)
DO UPDATE SET name = EXCLUDED.name;

-- MySQL: upsert dengan sintaks yang berbeda
INSERT INTO users (email, name)
VALUES ('rama@example.com', 'Rama')
ON DUPLICATE KEY UPDATE name = VALUES(name);
```

Perbedaan sintaks ini tidak masalah kalau kamu memakai Eloquent. Ia baru merepotkan saat query mentah tersebar di banyak controller, jadi kumpulkan query mentah di satu tempat, misalnya repository atau scope.

## Performa: jangan percaya klaim sepihak

Di internet kamu akan menemukan klaim bahwa salah satunya jauh lebih cepat. Abaikan klaim seperti itu. Untuk query CRUD biasa dengan indeks yang benar, keduanya cepat. Performa lebih ditentukan oleh desain tabel, indeks, dan query yang kamu tulis daripada merek databasenya.

Yang lebih sering bikin aplikasi lambat adalah query N+1, tabel tanpa indeks di kolom yang sering difilter, dan `SELECT *` di tabel yang kolomnya besar. Sebelum menyalahkan database, jalankan `EXPLAIN` dan lihat apakah querymu memakai indeks.

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 12;
```

Di Laravel, aktifkan query log saat development. Kalau satu halaman memicu puluhan query yang sama, masalahnya ada di kode, bukan di database.

## Kapan pilih PostgreSQL

Pilih PostgreSQL kalau satu atau lebih kondisi ini cocok dengan projectmu: datamu memakai JSON secara serius atau butuh array, UUID, dan tipe data khusus; kamu butuh full text search bawaan untuk tahap awal; kamu butuh constraint yang ketat seperti check constraint dan partial unique index; query analitikmu kompleks, banyak CTE dan window function; atau kamu memakai Supabase, Neon, dan platform modern lain yang menjadikan PostgreSQL sebagai default.

Contoh nyata: aplikasi kasir dengan laporan per cabang dan produk dengan atribut berbeda beda. PostgreSQL memberi ruang gerak lebih luas tanpa menambah layanan lain terlalu cepat.

## Kapan pilih MySQL atau MariaDB

Pilih MySQL atau MariaDB kalau hosting yang kamu pakai hanya menyediakannya dan kamu tidak mau mengurus VPS sendiri, kamu memakai WordPress atau terintegrasi dengan sistem lama yang sudah memakai MySQL, tim sudah terbiasa dengan cara backup dan troubleshootingnya, atau projectnya aplikasi CRUD, company profile, toko online sederhana, atau CMS standar.

MariaDB adalah fork MySQL yang kompatibel dan dipakai banyak distro Linux sebagai penggantinya. Kalau tutorial memakai MySQL, hampir semua langkahnya berlaku juga untuk MariaDB.

## Contoh setup di Laravel

Di Laravel, ganti database semudah mengganti konfigurasi. Jangan menulis password langsung di kode, selalu lewat environment.

```bash
# PostgreSQL
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=nama_database
DB_USERNAME=nama_user
DB_PASSWORD=password_rahasia

# MySQL, ganti blok di atas dengan blok ini
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=nama_database
DB_USERNAME=nama_user
DB_PASSWORD=password_rahasia
```

Migration yang sama biasanya jalan di keduanya, selama kamu tidak memakai tipe data khusus. Perhatikan `$table->json()`: di PostgreSQL ia dibuat sebagai `jsonb`, di MySQL sebagai `json`.

## Kesalahan umum pemula dan cara menghindarinya

### 1. Memilih database karena ikut ikutan

Kesalahan paling umum adalah memilih database karena ramai dibicarakan, lalu kesulitan saat hosting atau tutorial yang diikuti memakai database lain. Cek dulu hosting dan tutorial yang akan kamu pakai, lalu ikuti database yang dipakai di sana.

### 2. Tidak memakai indeks di kolom yang sering dicari

Tabel kecil terasa cepat tanpa indeks, masalah baru muncul saat datanya puluhan ribu. Beri indeks pada foreign key dan kolom yang sering dipakai di `WHERE` dan `ORDER BY`, tapi jangan ke semua kolom, karena setiap indeks memperlambat insert dan update.

### 3. Menyimpan semua data sebagai JSON

Data yang sering dicari, diurutkan, atau dipakai join sebaiknya tetap jadi kolom biasa. JSON dipakai untuk data yang memang tidak punya struktur tetap. Kalau query JSON-mu rumit untuk kebutuhan dasar, itu tanda datanya seharusnya jadi tabel relasional.

### 4. Tidak pernah backup sebelum mengubah skema

Migration yang gagal bisa meninggalkan tabel dalam kondisi setengah jadi. Sebelum migration besar di production, backup dulu: `pg_dump` untuk PostgreSQL, `mysqldump` untuk MySQL. Simpan backup di luar server yang sama.

```bash
# Backup PostgreSQL ke file
pg_dump -U nama_user -h 127.0.0.1 nama_database > backup-2026-11-04.sql

# Backup MySQL ke file
mysqldump -u nama_user -p nama_database > backup-2026-11-04.sql
```

### 5. Password database tersebar di kode

Jangan menulis password database di kode atau commit Git. Pakai `.env` dan pastikan `.env` masuk `.gitignore`. Untuk production, pakai user khusus aplikasi dengan hak seminimal mungkin, bukan user root.

## Langkah praktis: coba keduanya dalam 30 menit

Cara tercepat memahami perbedaannya adalah menjalankan keduanya berdampingan lewat Docker, tanpa menginstal apa pun di sistem utama.

```yaml
# docker-compose.yml: PostgreSQL dan MySQL berdampingan
services:
  pgsql:
    image: postgres:16
    environment:
      POSTGRES_DB: coba_db
      POSTGRES_USER: coba
      POSTGRES_PASSWORD: rahasia
    ports:
      - "5432:5432"
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: coba_db
      MYSQL_USER: coba
      MYSQL_PASSWORD: rahasia
      MYSQL_ROOT_PASSWORD: rahasia_root
    ports:
      - "3306:3306"
```

Jalankan dengan `docker compose up -d`, buat satu tabel yang sama di keduanya, dan jalankan contoh query JSON di atas. Perhatikan sintaks yang berbeda dan kecepatan query setelah indeks ditambahkan. Setelah itu, pakai satu database secara konsisten sampai project selesai.

## Penutup

PostgreSQL dan MySQL sama sama pilihan yang bagus. PostgreSQL unggul di fitur lanjutan, tipe data, dan keketatan aturan. MySQL unggul di kemudahan setup, ketersediaan di hosting murah, dan keakraban tim yang sudah lama memakainya. Untuk project baru yang dibangun dari nol dengan Laravel dan stack modern, PostgreSQL adalah pilihan default yang aman. Untuk project yang sudah terikat ekosistem MySQL, tetap di MySQL adalah keputusan yang masuk akal.

Yang paling penting bukan mereknya, tapi kebiasaanmu: pakai indeks dengan benar, hindari query N+1, backup sebelum mengubah skema, dan jangan menyimpan password di kode.
