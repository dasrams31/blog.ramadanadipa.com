---
title: Index di PostgreSQL Bikin Query 100x Lebih Cepat
description: Panduan index di PostgreSQL untuk pemula. Pahami B-tree, GIN, dan BRIN, lihat bukti EXPLAIN ANALYZE, dan hindari kesalahan yang bikin index malah memperlambat database.
cover: /assets/img/covers/index-di-postgresql-bikin-query-100x-lebih-cepat.jpg
date: 2026-11-08
tags: [postgresql, database, index, sql, performance]
faq:
  - Apa itu index di PostgreSQL?
  - Index adalah struktur data tambahan yang membantu PostgreSQL menemukan baris tanpa memindai seluruh tabel. Analoginya seperti daftar isi buku, database langsung lompat ke halaman yang dicari.
  - Kapan saya harus membuat index?
  - Buat index di kolom yang sering muncul di WHERE, JOIN, atau ORDER BY. Jangan membuat index di semua kolom, karena setiap index memperlambat INSERT dan UPDATE serta memakan ruang disk.
  - Apakah index selalu membuat query lebih cepat?
  - Tidak. Di tabel kecil, PostgreSQL lebih memilih sequential scan karena lebih murah. Index juga tidak membantu kalau kondisi WHERE memakai fungsi di kolom, misalnya WHERE LOWER(nama) = 'budi', kecuali kamu membuat index ekspresi.
  - Bagaimana cara cek apakah query saya memakai index?
  - Jalankan EXPLAIN ANALYZE sebelum query kamu. Kalau muncul "Index Scan" atau "Index Only Scan", index sedang dipakai. Kalau muncul "Seq Scan" di tabel besar, kemungkinan index belum ada atau tidak cocok dengan kondisi query.
---

Query yang tadinya butuh 2 detik bisa turun jadi 20 milidetik hanya karena satu baris SQL: `CREATE INDEX`. Aku sudah beberapa kali melihat ini di project Laravel, terutama di tabel yang isinya sudah ratusan ribu baris.

Artikel ini menjelaskan cara kerja index di PostgreSQL, kapan harus membuatnya, jenis index yang tersedia, dan kesalahan yang paling sering dilakukan pemula. Semua contoh bisa langsung dicoba di database kamu sendiri.

## Apa itu index, dan kenapa query lambat tanpa index

Bayangkan kamu mencari satu nama di buku telepon setebal seribu halaman yang tidak punya daftar isi. Satu-satunya cara adalah membaca halaman demi halaman sampai ketemu. Itulah yang dilakukan PostgreSQL tanpa index, namanya sequential scan.

Index bekerja seperti daftar isi. PostgreSQL menyimpan salinan kolom yang di-index dalam struktur yang terurut, lengkap dengan penunjuk ke baris aslinya. Saat kamu mencari `WHERE email = 'budi@gmail.com'`, database tidak lagi membaca seluruh tabel, dia mencari di index yang terurut lalu langsung mengambil baris yang cocok.

Dampaknya terasa kecil di tabel berisi 100 baris, tapi sangat besar di tabel berisi 1 juta baris. Sequential scan di tabel sejuta baris berarti membaca sejuta baris setiap kali query jalan, sementara index scan hanya membaca baris yang cocok.

## Bukti nyata: EXPLAIN ANALYZE sebelum dan sesudah index

PostgreSQL punya alat bawaan untuk melihat rencana eksekusi query, yaitu `EXPLAIN ANALYZE`. Coba di tabel contoh ini:

```sql
-- Buat tabel contoh dengan 500.000 baris
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150),
    city VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO customers (name, email, city)
SELECT 'User ' || i, 'user' || i || '@contoh.com', 'Jakarta'
FROM generate_series(1, 500000) i;
```

Sekarang jalankan query pencarian email tanpa index, dan lihat rencananya:

```sql
EXPLAIN ANALYZE SELECT * FROM customers WHERE email = 'user123456@contoh.com';
```

Hasilnya kurang lebih seperti ini: PostgreSQL memakai `Seq Scan on customers`, membaca 500.000 baris, dan waktu eksekusinya di kisaran ratusan milidetik. Sekarang buat indexnya:

```sql
CREATE INDEX idx_customers_email ON customers (email);
```

Jalankan query yang sama lagi:

```sql
EXPLAIN ANALYZE SELECT * FROM customers WHERE email = 'user123456@contoh.com';
```

Kali ini rencananya berubah menjadi `Index Scan using idx_customers_email`, hanya membaca 1 baris, dan waktunya turun ke kisaran 0,1 sampai 0,5 ms. Itu perbedaan ratusan kali lipat, dan inilah asal klaim "100x lebih cepat" di judul artikel ini.

Satu catatan: jalankan `ANALYZE customers;` setelah mengisi data, supaya planner punya statistik akurat untuk memilih rencana eksekusi terbaik.

## Jenis index di PostgreSQL: jangan cuma tahu B-tree

PostgreSQL menyediakan beberapa jenis index, dan memilih yang salah bisa membuat index tidak terpakai. Ini empat yang paling sering kamu butuhkan:

### B-tree: default untuk hampir semua kasus

B-tree adalah jenis index default. Cocok untuk pencarian sama dengan (`=`), rentang (`<`, `>`, `BETWEEN`), dan pengurutan (`ORDER BY`). Kalau kamu ragu mau pakai jenis apa, pakai B-tree.

```sql
CREATE INDEX idx_orders_created_at ON orders (created_at);
CREATE INDEX idx_users_email ON users (email);
```

### Hash: hanya untuk pencarian sama dengan

Hash index hanya berguna untuk perbandingan `=`, tidak bisa dipakai untuk rentang atau pengurutan. Performanya kurang lebih setara B-tree, jadi jarang ada alasan memilih hash.

### GIN: untuk kolom JSONB dan pencarian teks

GIN (Generalized Inverted Index) dibuat untuk kolom yang berisi banyak nilai di dalam satu baris, misalnya kolom JSONB atau array. Kalau kamu menyimpan data JSONB dan sering mencari di dalamnya, GIN adalah jawabannya.

```sql
-- Index untuk pencarian di dalam kolom JSONB
CREATE INDEX idx_products_meta ON products USING GIN (meta);

-- Sekarang query seperti ini memakai index
SELECT * FROM products WHERE meta @> '{"warna": "merah"}';
```

GIN juga dipakai di balik fitur full text search PostgreSQL, lewat `to_tsvector`.

### BRIN: untuk tabel raksasa yang datanya terurut

BRIN (Block Range Index) menyimpan ringkasan nilai minimum dan maksimum per blok data. Ukurannya sangat kecil, cocok untuk tabel jutaan baris yang datanya masuk secara berurutan, misalnya tabel log dengan kolom `created_at`. Jangan pakai BRIN di kolom yang nilainya acak.

```sql
CREATE INDEX idx_logs_created_at ON logs USING BRIN (created_at);
```

## Cara membuat index yang benar

Sintaks dasarnya sederhana, tapi ada beberapa variasi yang penting di project nyata:

```sql
-- Index biasa di satu kolom
CREATE INDEX idx_users_city ON users (city);

-- Index di beberapa kolom, berguna kalau query sering memfilter dua kolom sekaligus
CREATE INDEX idx_orders_user_status ON orders (user_id, status);

-- Index unik, sekaligus mencegah data duplikat
CREATE UNIQUE INDEX idx_users_email_unique ON users (email);

-- Partial index, hanya untuk baris yang memenuhi kondisi, ukurannya jauh lebih kecil
CREATE INDEX idx_orders_pending ON orders (created_at) WHERE status = 'pending';

-- Index ekspresi, untuk query yang memakai fungsi di kolom
CREATE INDEX idx_users_lower_email ON users (LOWER(email));
```

Perhatikan urutan kolom di index multi-kolom: kolom yang paling sering difilter sebaiknya di depan. Index `(user_id, status)` membantu query `WHERE user_id = 5 AND status = 'paid'`, tapi tidak membantu query yang hanya memfilter `status` saja.

### Membuat index di tabel produksi tanpa mengunci

`CREATE INDEX` biasa mengunci tabel untuk tulis selama proses pembuatan. Di tabel besar, ini bisa menghentikan aplikasi kamu beberapa menit. Solusinya adalah `CONCURRENTLY`:

```sql
CREATE INDEX CONCURRENTLY idx_customers_email ON customers (email);
```

Perintah ini tidak mengunci tabel untuk tulis, jadi aplikasi tetap jalan. Kekurangannya, prosesnya lebih lambat dan memakan CPU lebih banyak. Di Laravel, kamu bisa memakainya di migration seperti ini:

```php
// Di dalam migration, pakai raw statement supaya bisa CONCURRENTLY
DB::statement('CREATE INDEX CONCURRENTLY idx_customers_email ON customers (email)');
```

Satu jebakan: `CREATE INDEX CONCURRENTLY` tidak bisa dijalankan di dalam transaksi. Kalau migration Laravel kamu membungkus semuanya dalam transaksi, perintah ini akan gagal. Jalankan secara manual lewat psql atau migration terpisah tanpa transaksi.

## Kapan index tidak membantu

Index bukan obat mujarab. Ada situasi di mana PostgreSQL sengaja mengabaikan index kamu, dan itu keputusan yang benar.

**Tabel kecil.** Di tabel berisi 100 baris, membaca seluruh tabel lebih cepat daripada membaca index lalu mengambil barisnya satu per satu. Planner PostgreSQL tahu ini, jadi jangan heran kalau `EXPLAIN` tetap menunjukkan Seq Scan.

**Kolom dengan sedikit variasi nilai.** Index di kolom `status` yang isinya cuma `active` dan `inactive` hampir tidak membantu, karena separuh tabel tetap harus dibaca. Index paling efektif di kolom yang nilainya beragam, misalnya email atau ID.

**Fungsi di kolom tanpa index ekspresi.** Query `WHERE LOWER(email) = 'budi@gmail.com'` tidak bisa memakai index biasa di kolom `email`, karena nilai yang dicari sudah diubah oleh fungsi. Solusinya adalah index ekspresi seperti contoh di atas, atau ubah query-nya.

**Kondisi LIKE dengan wildcard di depan.** `WHERE name LIKE '%budi%'` tidak bisa memakai B-tree, karena pencarian dimulai dari tengah string. Untuk kebutuhan ini, pakai ekstensi `pg_trgm` dengan index GIN:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_users_name_trgm ON users USING GIN (name gin_trgm_ops);

-- Sekarang pencarian LIKE '%budi%' memakai index
SELECT * FROM users WHERE name LIKE '%budi%';
```

## Kesalahan umum pemula dan cara menghindarinya

**Membuat index di semua kolom.** Setiap index memperlambat INSERT, UPDATE, dan DELETE, karena PostgreSQL harus memperbarui semua index setiap kali data berubah. Tabel dengan 10 index bisa membuat proses insert dua sampai tiga kali lebih lambat.

**Lupa mengukur sebelum dan sesudah.** Jangan membuat index lalu berasumsi query jadi cepat. Selalu jalankan `EXPLAIN ANALYZE` sebelum dan sesudah, dan bandingkan waktunya. Kalau tidak ada perbaikan, hapus index itu, karena dia cuma membebani tulis dan memakan disk.

**Tidak pernah membersihkan index yang tidak terpakai.** Index yang tidak pernah dipakai tetap memakan ruang dan memperlambat tulis. Cek index yang tidak terpakai dengan query ini:

```sql
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

Kalau ada index dengan `idx_scan = 0` dan ukurannya besar, pertimbangkan untuk menghapusnya:

```sql
DROP INDEX idx_yang_tidak_terpakai;
```

**Membuat index duplikat.** Index `(email)` dan index `(email, status)` itu tumpang tindih, karena index kedua sudah mencakup pencarian di kolom email. Cek index yang sudah ada dengan `\d nama_tabel` di psql sebelum membuat yang baru.

## Langkah praktis yang bisa langsung dicoba

Ini urutan kerja yang aku pakai setiap kali ada query lambat di project Laravel:

1. Aktifkan query log di Laravel atau cek slow query di PostgreSQL dengan mengaktifkan `log_min_duration_statement = 200` di `postgresql.conf`. Angka 200 berarti query yang lebih lambat dari 200 ms akan dicatat.
2. Ambil query paling lambat, lalu jalankan `EXPLAIN ANALYZE` di psql atau di tool seperti DBeaver.
3. Cari baris `Seq Scan` di tabel yang besar, lalu lihat kolom apa yang dipakai di `Filter` atau kondisi WHERE.
4. Buat index di kolom itu, lalu jalankan `EXPLAIN ANALYZE` lagi untuk memastikan rencananya berubah jadi `Index Scan` dan waktunya turun.
5. Kalau query sudah cepat tapi tabel makin lambat saat insert, cek jumlah index dengan `\d nama_tabel` dan hapus yang tidak terpakai.

Di Laravel, kamu juga bisa menambahkan index lewat migration dengan cara standar:

```php
Schema::table('customers', function (Blueprint $table) {
    $table->index('email');
    $table->index(['user_id', 'status']);
});
```

## Penutup

Index adalah alat paling murah untuk mempercepat database: satu baris SQL bisa mengubah query dari ratusan milidetik jadi di bawah satu milidetik. Tapi buatlah berdasarkan bukti dari `EXPLAIN ANALYZE`, pilih jenis yang sesuai pola query kamu, dan bersihkan index yang tidak terpakai secara berkala.

Mulai dari satu query paling lambat di project kamu hari ini: jalankan `EXPLAIN ANALYZE`, cari Seq Scan di tabel besar, dan buat satu index untuk mengatasinya.
