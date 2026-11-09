---
title: "JOIN di SQL: INNER, LEFT, RIGHT dengan Contoh"
description: "Pelajari JOIN di SQL dari nol: INNER JOIN, LEFT JOIN, dan RIGHT JOIN dengan contoh nyata tabel users dan orders di PostgreSQL. Cocok untuk pemula."
date: 2026-11-09
tags: [SQL, PostgreSQL, database]
faq:
  - Kapan harus pakai INNER JOIN dan kapan LEFT JOIN?
  - Pakai INNER JOIN kalau kamu hanya butuh baris yang punya pasangan di kedua tabel. Pakai LEFT JOIN kalau kamu butuh semua baris dari tabel kiri, termasuk yang belum punya pasangan.
  - Apa beda LEFT JOIN dan RIGHT JOIN?
  - Hasilnya sama kalau posisi tabel ditukar. LEFT JOIN mengambil semua baris dari tabel kiri, RIGHT JOIN mengambil semua baris dari tabel kanan. Di praktik, developer hampir selalu pakai LEFT JOIN.
  - Kenapa hasil JOIN saya jadi berlipat ganda?
  - Biasanya karena kolom yang dipakai di ON tidak unik di salah satu tabel. Satu baris di tabel kiri bertemu banyak baris di tabel kanan, jadi hasilnya ikut berlipat.
  - Apakah JOIN lambat kalau datanya besar?
  - JOIN bisa lambat kalau kolom yang di-JOIN tidak punya index. Tambahkan index di foreign key dan kolom yang sering dipakai di klausa ON atau WHERE.
---

Kalau kamu sudah bisa SELECT, WHERE, dan ORDER BY, langkah berikutnya yang wajib dikuasai adalah JOIN. Hampir semua aplikasi nyata menyimpan data di banyak tabel, dan JOIN adalah cara menyatukan data itu dalam satu query. Artikel ini memakai PostgreSQL, tapi sintaksnya sama di MySQL dan database SQL lain.

## Data contoh yang dipakai

Kita pakai dua tabel yang sangat umum di aplikasi nyata: `users` dan `orders`. Satu user bisa punya banyak order, satu order hanya milik satu user.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product VARCHAR(100) NOT NULL,
    total INTEGER NOT NULL
);

INSERT INTO users (name, email) VALUES
    ('Rama', 'rama@mail.com'),
    ('Sinta', 'sinta@mail.com'),
    ('Budi', 'budi@mail.com'),
    ('Dewi', 'dewi@mail.com');

INSERT INTO orders (user_id, product, total) VALUES
    (1, 'Kopi Arabika 250g', 45000),
    (1, 'Gula Aren 500g', 30000),
    (2, 'Teh Melati', 25000);
```

Perhatikan: Budi dan Dewi belum pernah order. Detail kecil ini penting, karena di sinilah beda tiap jenis JOIN kelihatan jelas.

## INNER JOIN: hanya yang punya pasangan

INNER JOIN mengambil baris yang punya pasangan di kedua tabel. User tanpa order tidak muncul, order tanpa user juga tidak muncul.

```sql
SELECT users.name, orders.product, orders.total
FROM users
INNER JOIN orders ON orders.user_id = users.id;
```

Hasilnya:

| name | product | total |
|------|---------|-------|
| Rama | Kopi Arabika 250g | 45000 |
| Rama | Gula Aren 500g | 30000 |
| Sinta | Teh Melati | 25000 |

Budi dan Dewi hilang dari hasil karena mereka tidak punya order. Itu bukan bug, itu memang perilaku INNER JOIN. Kata `INNER` boleh dihilangkan, `JOIN` saja sudah berarti INNER JOIN, tapi menuliskannya lengkap bikin query lebih mudah dibaca orang lain.

Pakai INNER JOIN untuk pertanyaan seperti: siapa saja user yang sudah pernah belanja, dan apa yang mereka beli. Kalau kamu mau laporan penjualan, ini jenis JOIN yang paling sering dipakai.

## LEFT JOIN: semua dari tabel kiri, pasangan boleh kosong

LEFT JOIN mengambil semua baris dari tabel kiri, lalu menempelkan data dari tabel kanan kalau ada pasangannya. Kalau tidak ada, kolom dari tabel kanan berisi NULL.

```sql
SELECT users.name, orders.product, orders.total
FROM users
LEFT JOIN orders ON orders.user_id = users.id;
```

Hasilnya:

| name | product | total |
|------|---------|-------|
| Rama | Kopi Arabika 250g | 45000 |
| Rama | Gula Aren 500g | 30000 |
| Sinta | Teh Melati | 25000 |
| Budi | NULL | NULL |
| Dewi | NULL | NULL |

Sekarang Budi dan Dewi muncul, dengan kolom product dan total bernilai NULL. Inilah cara paling umum untuk menjawab pertanyaan: user mana saja yang belum pernah order.

```sql
SELECT users.name, users.email
FROM users
LEFT JOIN orders ON orders.user_id = users.id
WHERE orders.id IS NULL;
```

Pola ini, LEFT JOIN lalu `WHERE ... IS NULL`, adalah salah satu pola SQL yang paling sering dipakai di dunia nyata. Hafalkan. Kegunaannya banyak: cari produk yang belum pernah terjual, cari member yang belum pernah login, cari artikel tanpa komentar.

## RIGHT JOIN: kebalikan dari LEFT JOIN

RIGHT JOIN mengambil semua baris dari tabel kanan. Kalau kita balik posisi tabelnya, hasilnya sama persis dengan LEFT JOIN.

```sql
SELECT users.name, orders.product, orders.total
FROM orders
RIGHT JOIN users ON orders.user_id = users.id;
```

Query di atas menghasilkan tabel yang sama dengan contoh LEFT JOIN sebelumnya. Karena itu, hampir semua developer dan tim yang saya temui memilih untuk selalu menulis LEFT JOIN dan tidak pernah memakai RIGHT JOIN. Konsisten memakai satu arah membuat query lebih mudah dibaca, apalagi kalau JOIN-nya sudah berantai ke tiga atau empat tabel. Kamu cukup tahu RIGHT JOIN itu ada dan cara kerjanya, tidak perlu memakainya sehari-hari.

## FULL JOIN: semua baris dari kedua sisi

Sebagai bonus, PostgreSQL mendukung FULL JOIN, yaitu gabungan LEFT JOIN dan RIGHT JOIN. Semua baris dari kedua tabel muncul, yang tidak punya pasangan diisi NULL.

```sql
SELECT users.name, orders.product, orders.total
FROM users
FULL JOIN orders ON orders.user_id = users.id;
```

Di contoh kita, hasilnya sama dengan LEFT JOIN karena semua order punya user. FULL JOIN baru terasa bedanya kalau ada order yang user_id-nya NULL atau menunjuk user yang sudah dihapus. MySQL tidak punya FULL JOIN bawaan, jadi kalau kamu pindah database, pola ini perlu ditulis dengan UNION.

## JOIN ke tiga tabel atau lebih

Aplikasi nyata jarang berhenti di dua tabel. Misalnya ada tabel `order_items` yang menyimpan tiap barang di dalam satu order, dan tabel `products` untuk detail barang. JOIN tinggal dirangkai satu per satu.

```sql
SELECT
    users.name AS pembeli,
    products.name AS produk,
    order_items.qty,
    order_items.price
FROM users
JOIN orders ON orders.user_id = users.id
JOIN order_items ON order_items.order_id = orders.id
JOIN products ON products.id = order_items.product_id
WHERE orders.id = 1;
```

Aturan praktisnya: urutkan JOIN mengikuti relasi datanya, dan beri alias yang jelas kalau nama kolom bentrok. Di query di atas saya pakai `AS pembeli` dan `AS produk` supaya hasil query langsung enak dibaca di aplikasi, tanpa perlu rename di kode PHP atau JavaScript.

Kalau satu query JOIN lima tabel dan hasilnya mulai sulit dipahami, itu sinyal untuk berhenti sejenak. Cek apakah semua relasi memang dibutuhkan di satu query, atau lebih baik dipecah jadi dua query yang lebih kecil. Query yang benar tapi tidak bisa dibaca tim adalah utang teknis.

## Kesalahan umum pemula

### 1. Lupa klausa ON

```sql
-- Salah: tanpa ON, hasilnya cross join
SELECT * FROM users JOIN orders;
```

Tanpa ON, database memasangkan setiap user dengan setiap order. Empat user dikali tiga order jadi dua belas baris, dan angkanya makin gila seiring data bertambah. PostgreSQL bahkan menolak query `JOIN` tanpa ON, tapi tetap waspada saat menulis query panjang.

### 2. JOIN di kolom yang salah

Pastikan kolom di ON memang pasangan foreign key dan primary key. JOIN `orders.id = users.id` secara sintaks sah, tapi hasilnya ngawur: order nomor 1 dipasangkan dengan user nomor 1 hanya karena angkanya kebetulan sama. Selalu cek relasinya, bukan sekadar tipe datanya sama-sama integer.

### 3. SELECT * di query JOIN

`SELECT *` di query JOIN mengembalikan semua kolom dari semua tabel, termasuk kolom id yang duplikat dan kolom yang tidak kamu pakai. Selain boros bandwidth, hasilnya rawan bentrok di kode aplikasi karena ada dua kolom bernama `id`. Sebutkan kolom yang kamu butuhkan saja, dan beri alias kalau namanya sama.

### 4. Mengira NULL itu nol atau string kosong

Baris hasil LEFT JOIN yang tidak punya pasangan berisi NULL, bukan 0 dan bukan string kosong. `WHERE total = 0` tidak akan menangkapnya, harus `WHERE total IS NULL`. Kesalahan ini sering bikin laporan "user belum belanja" menampilkan angka kosong padahal datanya ada.

### 5. JOIN tanpa index di foreign key

Kalau tabel orders punya jutaan baris dan `user_id` tidak punya index, database harus memindai seluruh tabel untuk tiap JOIN. Di PostgreSQL, foreign key tidak otomatis dibuatkan index seperti primary key. Tambahkan sendiri:

```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

Satu baris ini bisa mengubah query yang tadinya butuh belasan detik jadi hitungan milidetik. Cek dengan `EXPLAIN ANALYZE` sebelum dan sesudah menambahkan index, supaya kamu melihat sendiri bedanya.

## Langkah praktis yang bisa langsung dicoba

Pertama, buat database latihan dan isi dengan tabel users dan orders di atas. Kedua, jalankan ketiga query INNER, LEFT, dan RIGHT JOIN, lalu bandingkan hasilnya baris demi baris. Ketiga, tulis query untuk pertanyaan nyata: siapa user yang total belanjanya paling besar, dan siapa user yang belum pernah belanja sama sekali. Keempat, tambahkan index di `user_id` lalu jalankan `EXPLAIN ANALYZE` untuk melihat rencana eksekusinya.

Kalau kamu membangun aplikasi Laravel, semua pola di artikel ini punya padanannya di Eloquent. `User::has('orders')->get()` untuk INNER JOIN, dan `User::doesntHave('orders')->get()` untuk pola LEFT JOIN plus `WHERE ... IS NULL`. Tapi memahami SQL mentahnya dulu membuatmu jauh lebih cepat saat debugging query yang dihasilkan framework.

## Penutup

Ringkasan singkatnya: INNER JOIN untuk baris yang punya pasangan di kedua tabel, LEFT JOIN untuk semua baris tabel kiri plus pasangan kalau ada, RIGHT JOIN kebalikan dari LEFT JOIN yang jarang dipakai, dan FULL JOIN untuk semua baris dari kedua sisi. Kuasai empat ini plus pola LEFT JOIN dengan `WHERE ... IS NULL`, dan kamu sudah bisa menjawab sebagian besar pertanyaan data di aplikasi nyata. Latihan terbaik adalah memakai data project kamu sendiri, bukan data contoh, karena di situlah kesalahan dan pola yang aneh baru kelihatan.
