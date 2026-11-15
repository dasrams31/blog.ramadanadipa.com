---
title: "Query Agregat SQL: COUNT, SUM, AVG, dan GROUP BY"
description: "Pelajari fungsi agregat SQL dari nol: COUNT, SUM, AVG, GROUP BY, dan HAVING dengan contoh nyata PostgreSQL yang bisa langsung dicoba di database kamu."
cover: /assets/img/covers/query-agregat-sql-count-sum-avg-group-by.jpg
date: 2026-11-15
tags: [PostgreSQL, SQL, database]
faq:
  - Apa itu fungsi agregat di SQL?
  - Fungsi agregat adalah fungsi yang mengambil banyak baris lalu mengembalikan satu nilai ringkasan, misalnya COUNT untuk menghitung baris, SUM untuk menjumlahkan kolom angka, dan AVG untuk menghitung rata-rata.
  - Apa beda WHERE dan HAVING di SQL?
  - WHERE memfilter baris sebelum agregasi, sedangkan HAVING memfilter hasil setelah agregasi. Kalau kondisi kamu memakai COUNT atau SUM, pakainya HAVING, bukan WHERE.
  - Kenapa GROUP BY error di PostgreSQL?
  - PostgreSQL menolak query kalau ada kolom biasa di SELECT yang tidak ada di GROUP BY dan tidak dibungkus fungsi agregat. Solusinya: masukkan semua kolom non-agregat ke GROUP BY atau bungkus dengan fungsi agregat.
  - Kapan pakai COUNT(*) dan kapan COUNT(nama_kolom)?
  - Pakai COUNT(*) untuk menghitung semua baris termasuk yang berisi NULL. Pakai COUNT(nama_kolom) kalau kamu hanya mau menghitung baris yang kolomnya terisi, karena COUNT(nama_kolom) melewatkan NULL.
---

Database jarang dipakai cuma untuk menyimpan data. Cepat atau lambat kamu pasti butuh angka ringkasannya: berapa user yang daftar bulan ini, total penjualan minggu ini, rata-rata rating tiap produk, kategori mana yang paling laku. Semua pertanyaan itu dijawab oleh fungsi agregat SQL. Tanpa fungsi ini, kamu terpaksa menarik ribuan baris ke aplikasi lalu menghitungnya sendiri di PHP atau JavaScript, dan itu lambat sekaligus boros memori.

Artikel ini memakai PostgreSQL, tapi semua query di sini juga jalan di MySQL dengan penyesuaian kecil. Saya pakai contoh toko online sederhana: tabel `products`, `orders`, dan `order_items`. Kalau kamu mau mengikuti langsung, buat dulu tabel dan datanya di akhir artikel, di bagian latihan.

## Fungsi agregat itu apa

Fungsi agregat menerima banyak baris sebagai input dan mengembalikan satu nilai. Lima fungsi yang paling sering dipakai:

- `COUNT()` menghitung jumlah baris
- `SUM()` menjumlahkan nilai numerik
- `AVG()` menghitung rata-rata nilai numerik
- `MIN()` mengambil nilai terkecil
- `MAX()` mengambil nilai terbesar

Satu hal yang wajib diingat: fungsi agregat mengabaikan nilai `NULL`, kecuali `COUNT(*)`. Ini penting karena perilaku ini sering bikin hasil hitungan terlihat salah padahal querynya benar. Saya bahas detailnya di bagian `COUNT` di bawah.

Contoh paling sederhana, hitung total produk dan harga termahal di katalog:

```sql
SELECT
    COUNT(*) AS total_produk,
    MIN(price) AS harga_termurah,
    MAX(price) AS harga_termahal,
    AVG(price) AS harga_rata_rata
FROM products;
```

Hasilnya satu baris berisi empat angka ringkasan. Kamu tidak perlu tahu isi tiap baris, kamu cuma butuh gambar besarnya. Inilah gunanya agregat: mengubah ribuan baris jadi satu jawaban.

## COUNT: menghitung baris dengan benar

`COUNT` punya tiga bentuk dan ketiganya beda hasil. Ini sumber kebingungan paling umum di kalangan pemula, jadi perhatikan baik-baik.

```sql
-- Menghitung semua baris, termasuk yang kolomnya NULL
SELECT COUNT(*) FROM users;

-- Menghitung baris yang kolom email-nya terisi saja
SELECT COUNT(email) FROM users;

-- Menghitung nilai unik, duplikat dihitung sekali
SELECT COUNT(DISTINCT city) FROM users;
```

Bedanya nyata kalau ada data kosong. Misal tabel `users` berisi 100 baris tapi 5 user belum isi email. `COUNT(*)` menghasilkan 100, `COUNT(email)` menghasilkan 95. Kalau kamu mau tahu "berapa user yang sudah verifikasi email", yang benar adalah `COUNT(email)`. Kalau kamu mau tahu "berapa user yang terdaftar", yang benar adalah `COUNT(*)`.

`COUNT(DISTINCT city)` berguna untuk pertanyaan seperti "dari berapa kota user kita berasal". Tanpa `DISTINCT`, kota yang sama dihitung berkali-kali dan jawabannya jadi jumlah baris, bukan jumlah kota.

Pola yang sering dipakai di dashboard:

```sql
SELECT
    COUNT(*) AS total_order,
    COUNT(DISTINCT user_id) AS pembeli_unik
FROM orders
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);
```

## SUM dan AVG: total dan rata-rata

`SUM` dan `AVG` cuma jalan di kolom numerik. Mencoba menjumlahkan kolom teks akan error, dan itu wajar. Contoh menghitung omzet:

```sql
SELECT SUM(total_amount) AS omzet_bulan_ini
FROM orders
WHERE status = 'paid'
  AND created_at >= DATE_TRUNC('month', CURRENT_DATE);
```

Perhatikan filter `status = 'paid'`. Order yang batal atau belum bayar tidak boleh masuk omzet. Ini kelihatan sepele, tapi di dunia nyata inilah sumber laporan keuangan yang meleset: orang lupa memfilter status sebelum menjumlahkan.

`AVG` menghitung rata-rata, tapi hati-hati dengan pembulatan dan pembagian nol. Rata-rata nilai order:

```sql
SELECT ROUND(AVG(total_amount), 2) AS rata_rata_order
FROM orders
WHERE status = 'paid';
```

`ROUND(..., 2)` membulatkan ke dua desimal supaya hasilnya enak dibaca, misalnya 247500.50 bukan 247500.495312. Rata-rata juga rentan terhadap outlier. Kalau satu order bernilai 50 juta dan sisanya 100 ribu, rata-ratanya akan ketarik naik dan tidak mewakili order tipikal. Untuk kasus seperti itu, hitung juga `MIN`, `MAX`, dan `COUNT` di query yang sama supaya kamu bisa menilai apakah rata-ratanya bisa dipercaya.

```sql
SELECT
    COUNT(*) AS jumlah_order,
    MIN(total_amount) AS order_terkecil,
    MAX(total_amount) AS order_terbesar,
    ROUND(AVG(total_amount), 2) AS rata_rata_order
FROM orders
WHERE status = 'paid';
```

## GROUP BY: agregat per kelompok

Satu angka untuk seluruh tabel kadang tidak cukup. Kamu mau tahu omzet per kategori, jumlah order per kota, atau rata-rata rating per produk. Di sinilah `GROUP BY` bekerja: dia memecah baris jadi kelompok-kelompok, lalu fungsi agregat dihitung per kelompok.

```sql
SELECT
    category,
    COUNT(*) AS jumlah_produk,
    ROUND(AVG(price), 2) AS harga_rata_rata
FROM products
GROUP BY category
ORDER BY jumlah_produk DESC;
```

Hasilnya satu baris per kategori, masing-masing dengan jumlah produk dan harga rata-ratanya. `ORDER BY jumlah_produk DESC` mengurutkan dari kategori terbanyak supaya insight yang paling penting muncul duluan.

Contoh yang lebih nyata, omzet per bulan:

```sql
SELECT
    TO_CHAR(created_at, 'YYYY-MM') AS bulan,
    COUNT(*) AS jumlah_order,
    SUM(total_amount) AS omzet
FROM orders
WHERE status = 'paid'
GROUP BY TO_CHAR(created_at, 'YYYY-MM')
ORDER BY bulan;
```

`TO_CHAR(created_at, 'YYYY-MM')` mengubah timestamp jadi teks seperti `2026-11`, jadi order di bulan yang sama masuk satu kelompok. Pola ini adalah fondasi hampir semua grafik penjualan di dashboard.

Aturan emas `GROUP BY` di PostgreSQL: setiap kolom di `SELECT` harus masuk ke `GROUP BY` atau dibungkus fungsi agregat. Query ini akan ditolak:

```sql
-- ERROR: kolom name tidak ada di GROUP BY
SELECT category, name, COUNT(*)
FROM products
GROUP BY category;
```

PostgreSQL tidak bisa memutuskan nama produk mana yang harus ditampilkan untuk satu kategori yang berisi banyak produk, jadi dia menolak querynya sekalian. MySQL versi lama membiarkan query seperti ini dan diam-diam mengambil nilai sembarangan, itu lebih berbahaya karena hasilnya terlihat benar padahal acak.

`GROUP BY` juga bisa mengelompokkan lebih dari satu kolom. Misalnya jumlah order per kota per status:

```sql
SELECT
    city,
    status,
    COUNT(*) AS jumlah_order
FROM orders
GROUP BY city, status
ORDER BY city, jumlah_order DESC;
```

## HAVING: memfilter hasil agregat

Setelah dikelompokkan, kadang kamu cuma mau melihat kelompok yang memenuhi syarat, misalnya kategori yang produknya lebih dari 10, atau pelanggan yang total belanjanya di atas 5 juta. Filter seperti ini tidak bisa pakai `WHERE`, karena `WHERE` jalan sebelum agregasi dan belum tahu hasil hitungannya. Pakainya `HAVING`.

```sql
SELECT
    user_id,
    COUNT(*) AS jumlah_order,
    SUM(total_amount) AS total_belanja
FROM orders
WHERE status = 'paid'
GROUP BY user_id
HAVING SUM(total_amount) > 5000000
ORDER BY total_belanja DESC;
```

Urutan eksekusi logisnya: `WHERE` dulu memfilter order yang sudah dibayar, lalu `GROUP BY` mengelompokkan per user, lalu `HAVING` membuang user yang total belanjanya di bawah 5 juta. Query ini adalah cara standar mencari pelanggan VIP.

Kesalahan klasik pemula adalah menulis kondisi agregat di `WHERE`:

```sql
-- ERROR: fungsi agregat tidak boleh di WHERE
SELECT user_id, COUNT(*)
FROM orders
WHERE COUNT(*) > 5
GROUP BY user_id;
```

PostgreSQL menolak ini karena `WHERE` dievaluasi per baris, sebelum ada kelompok yang bisa dihitung. Begitu kamu butuh kondisi atas hasil `COUNT`, `SUM`, atau `AVG`, pindah ke `HAVING`.

Kamu bisa memakai alias di `HAVING` di PostgreSQL, jadi query di atas bisa ditulis lebih ringkas:

```sql
SELECT
    user_id,
    COUNT(*) AS jumlah_order,
    SUM(total_amount) AS total_belanja
FROM orders
WHERE status = 'paid'
GROUP BY user_id
HAVING total_belanja > 5000000
ORDER BY total_belanja DESC;
```

## Kesalahan umum pemula dan cara menghindarinya

**Pertama, memakai SELECT * bersama GROUP BY.** `SELECT *` menarik semua kolom, dan hampir pasti ada kolom yang tidak masuk `GROUP BY`. Biasakan menulis kolom yang kamu butuhkan saja, satu per satu. Query jadi lebih jelas dan error seperti ini hilang sendiri.

**Kedua, lupa memfilter sebelum agregat.** Menjumlahkan semua order tanpa `status = 'paid'` membuat omzet terlihat lebih besar dari aslinya. Selalu tanya dulu: baris mana yang boleh masuk hitungan, baru tulis querynya.

**Ketiga, mengira AVG menghitung NULL sebagai nol.** `AVG` melewatkan `NULL` sepenuhnya. Kalau ada 4 nilai yaitu 100, 200, 300, dan NULL, rata-ratanya adalah 200, bukan 150. Kalau kamu memang mau NULL dihitung sebagai nol, bungkus kolomnya dulu dengan `COALESCE(nama_kolom, 0)`.

**Keempat, memakai COUNT(nama_kolom) saat maksudnya COUNT(*).** Kalau kolomnya boleh NULL, hasil keduanya beda dan kamu bisa salah baca jumlah data. Pakai `COUNT(*)` sebagai default, dan pakai `COUNT(nama_kolom)` hanya saat kamu memang sengaja mau melewatkan NULL.

**Kelima, mengurutkan hasil GROUP BY tanpa ORDER BY.** Urutan baris hasil `GROUP BY` tidak dijamin. Kalau urutan penting buat kamu, selalu tambahkan `ORDER BY` yang eksplisit.

## Latihan praktis: coba langsung

Buat tabel dan data contoh berikut di database latihanmu, lalu jalankan query-query di artikel ini satu per satu dan perhatikan hasilnya.

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price NUMERIC(12, 2) NOT NULL
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    city VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO products (name, category, price) VALUES
    ('Keyboard Mekanikal', 'Elektronik', 850000),
    ('Mouse Wireless', 'Elektronik', 350000),
    ('Kursi Gaming', 'Furniture', 2500000),
    ('Meja Lipat', 'Furniture', 450000),
    ('Buku SQL Dasar', 'Buku', 120000);

INSERT INTO orders (user_id, city, status, total_amount) VALUES
    (1, 'Jakarta', 'paid', 850000),
    (1, 'Jakarta', 'paid', 350000),
    (2, 'Bandung', 'paid', 2500000),
    (3, 'Jakarta', 'cancelled', 120000),
    (2, 'Bandung', 'pending', 450000);
```

Setelah data masuk, coba jawab tiga pertanyaan ini dengan satu query masing-masing:

1. Berapa omzet dari order yang sudah dibayar saja?
2. Kota mana yang menghasilkan omzet terbesar?
3. User mana saja yang total belanjanya di atas 1 juta?

Kalau kamu bisa menjawab ketiganya tanpa menarik data ke aplikasi, kamu sudah paham inti fungsi agregat. Selanjutnya, coba gabungkan dengan `JOIN` untuk menampilkan nama kategori atau nama user di hasil akhirnya.
