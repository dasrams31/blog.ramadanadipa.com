---
title: "Foreign Key dan Relasi Tabel: Konsep Database untuk Pemula"
description: "Pelajari foreign key dan relasi tabel dari nol: one to many, many to many, ON DELETE CASCADE, plus contoh SQL dan migration Laravel yang bisa langsung dicoba."
cover: /assets/img/covers/foreign-key-dan-relasi-tabel-konsep-database-untuk-pemula.jpg
date: 2026-11-13
tags: [PostgreSQL, SQL, database]
faq:
  - Apa itu foreign key dalam database?
  - Foreign key adalah kolom di satu tabel yang menunjuk ke primary key tabel lain. Fungsinya menjaga relasi antar tabel tetap valid, jadi tidak ada data anak yang menunjuk ke data induk yang tidak ada.
  - Apa beda primary key dan foreign key?
  - Primary key adalah identitas unik tiap baris di dalam tabelnya sendiri. Foreign key adalah kolom yang merujuk ke primary key tabel lain untuk menghubungkan dua tabel.
  - Apakah foreign key wajib dipakai di setiap relasi?
  - Tidak wajib secara teknis, tapi sangat disarankan. Tanpa foreign key, database tidak mencegah data yatim dan kamu harus menjaga konsistensi relasi sendiri di kode aplikasi, yang rawan bocor.
  - Apa yang terjadi kalau menghapus data induk yang masih punya anak?
  - Tergantung aturan ON DELETE yang kamu pilih. RESTRICT menolak penghapusan, CASCADE ikut menghapus anaknya, dan SET NULL mengosongkan foreign key di baris anak.
---

Hampir semua aplikasi menyimpan data di banyak tabel yang saling berhubungan. Tabel users menyimpan akun, tabel posts menyimpan tulisan, tabel comments menyimpan komentar. Tanpa relasi yang jelas, ketiga tabel itu cuma kumpulan data lepas yang gampang berantakan. Foreign key adalah mekanisme yang mengikat tabel-tabel itu jadi satu kesatuan yang konsisten.

## Relasi tabel itu apa

Relasi adalah hubungan antar tabel. Ada tiga jenis yang akan kamu temui terus-menerus.

**One to many** adalah relasi paling umum. Satu user punya banyak post, satu post hanya milik satu user. Satu kategori punya banyak produk, satu produk hanya masuk satu kategori.

**Many to many** terjadi saat kedua sisi bisa punya banyak pasangan. Satu post bisa punya banyak tag, satu tag bisa dipakai banyak post. Relasi ini tidak bisa diwakili satu foreign key saja, butuh tabel perantara yang biasanya disebut pivot table.

**One to one** paling jarang. Satu user punya satu profil, satu profil hanya milik satu user. Seringkali ini cuma cara memecah tabel yang terlalu lebar jadi dua bagian.

Kenapa relasi perlu diatur di level database, bukan cuma di kode aplikasi? Karena aplikasi bisa punya bug, tapi database tidak berbohong. Kalau aturannya tertanam di database, data yang tidak konsisten tidak bisa masuk, siapa pun yang menulis datanya.

## Apa itu foreign key

Foreign key adalah kolom di tabel anak yang menunjuk ke primary key tabel induk. Contoh klasik: tabel `posts` punya kolom `user_id` yang menunjuk ke kolom `id` di tabel `users`. Setiap nilai `user_id` di tabel posts harus ada di tabel users. Kalau tidak ada, database menolaknya.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

Sintaks `REFERENCES users(id)` itu adalah foreign key. Sekarang coba masukkan post dengan `user_id` yang tidak ada:

```sql
INSERT INTO posts (user_id, title, body)
VALUES (999, 'Judul Tes', 'Isi tulisan.');
```

PostgreSQL langsung menolak dengan error `violates foreign key constraint`. Inilah yang disebut referential integrity: database menjaga supaya tidak ada data anak yang menunjuk ke induk yang tidak ada. Tanpa foreign key, insert di atas akan berhasil diam-diam, dan nanti saat kamu JOIN, post itu hilang dari hasil karena usernya tidak ketemu. Bug seperti ini sulit dilacak karena datanya terlihat normal sampai ada yang mengeluh.

## Menambah foreign key ke tabel yang sudah ada

Tabel yang sudah terlanjur dibuat tanpa foreign key masih bisa diperbaiki. Pakai `ALTER TABLE` dengan `ADD CONSTRAINT`, dan beri nama constraint yang jelas supaya pesan errornya mudah dibaca.

```sql
ALTER TABLE posts
ADD CONSTRAINT fk_posts_user
FOREIGN KEY (user_id) REFERENCES users(id);
```

Kalau tabel sudah berisi data yang melanggar relasi, perintah di atas gagal. Cari dulu baris bermasalahnya:

```sql
SELECT posts.id, posts.user_id
FROM posts
LEFT JOIN users ON users.id = posts.user_id
WHERE users.id IS NULL;
```

Perbaiki atau hapus baris itu dulu, baru jalankan `ALTER TABLE` lagi. Pola ini juga berguna saat kamu mengambil alih project lama yang tabelnya tidak punya foreign key sama sekali. Jangan langsung menambah constraint tanpa mengecek data lama.

Untuk menghapus foreign key, pakai nama constraintnya:

```sql
ALTER TABLE posts DROP CONSTRAINT fk_posts_user;
```

Inilah alasan memberi nama constraint secara eksplisit lebih baik daripada membiarkan database membuat nama otomatis seperti `posts_user_id_fkey`. Nama yang jelas bikin maintenance jauh lebih mudah.

## Relasi many to many dengan pivot table

Satu post bisa punya banyak tag, dan satu tag dipakai banyak post. Foreign key tunggal tidak bisa mewakili ini, jadi buat tabel ketiga yang hanya berisi dua foreign key.

```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE post_tag (
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);
```

Primary key gabungan `(post_id, tag_id)` mencegah pasangan yang sama dimasukkan dua kali. Query untuk mengambil semua tag milik satu post jadi sederhana:

```sql
SELECT tags.name
FROM tags
JOIN post_tag ON post_tag.tag_id = tags.id
WHERE post_tag.post_id = 1;
```

Pola pivot table ini muncul di mana-mana: produk dan kategori, user dan role, siswa dan mata pelajaran. Begitu kamu hafal polanya, kamu tidak perlu berpikir ulang tiap kali menemukannya.

## ON DELETE dan ON UPDATE: pilih perilakunya

Saat baris induk dihapus atau diubah, database harus tahu apa yang dilakukan ke baris anak. Ada empat pilihan, dan memilih yang salah bisa menghapus data yang tidak seharusnya hilang.

**RESTRICT** adalah perilaku default. Database menolak penghapusan induk selama masih ada anak yang menunjuk ke sana. Aman, tapi kamu harus menghapus anaknya dulu secara manual.

**CASCADE** ikut menghapus semua baris anak saat induk dihapus. Cocok untuk data yang memang tidak ada artinya tanpa induknya, seperti komentar milik sebuah post. Hapus post, komentarnya ikut terhapus.

**SET NULL** mengosongkan foreign key di baris anak, jadi anaknya tetap ada tapi kehilangan induk. Kolom foreign key harus boleh NULL kalau pakai opsi ini. Cocok untuk kasus seperti post yang penulisnya dihapus, tapi tulisannya tetap ingin dipertahankan.

**SET DEFAULT** mengisi foreign key dengan nilai default yang kamu tentukan, misalnya user sistem dengan id 0 sebagai pemilik pengganti.

Contoh penerapannya:

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    body TEXT NOT NULL
);
```

Di contoh ini, menghapus user tidak menghapus tulisannya, tapi menghapus post ikut menghapus komentarnya. Dua keputusan yang berbeda untuk dua relasi yang berbeda, dan keduanya ditulis eksplisit di skema, bukan disembunyikan di kode aplikasi. Kalau ada developer baru bergabung ke tim, dia bisa membaca aturan ini langsung dari struktur tabel.

`ON UPDATE CASCADE` bekerja dengan cara yang sama untuk perubahan primary key. Praktiknya jarang dipakai karena primary key sebaiknya tidak pernah berubah setelah dibuat. Kalau kamu sering mengubah id, itu tanda desain tabelnya perlu dipikirkan ulang.

## Foreign key di Laravel migration

Di Laravel, foreign key ditulis di migration dan Eloquent memakainya untuk relasi antar model. Contoh migration untuk tabel posts:

```php
Schema::create('posts', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->nullOnDelete();
    $table->string('title');
    $table->text('body');
    $table->timestamps();
});
```

`foreignId('user_id')->constrained()` membuat kolom `user_id` plus foreign key ke tabel users secara otomatis. `nullOnDelete()` setara dengan `ON DELETE SET NULL`. Alternatifnya, `cascadeOnDelete()` setara dengan `ON DELETE CASCADE`.

Relasi di model Eloquent tinggal dideklarasikan:

```php
// app/Models/User.php
public function posts()
{
    return $this->hasMany(Post::class);
}

// app/Models/Post.php
public function user()
{
    return $this->belongsTo(User::class);
}

public function comments()
{
    return $this->hasMany(Comment::class);
}
```

Dengan deklarasi itu, `$user->posts` mengambil semua tulisan milik user, dan `$post->user` mengambil penulisnya. Perhatikan bahwa Eloquent hanya membaca relasi, sedangkan aturan konsistensinya tetap dipegang foreign key di database. Keduanya saling melengkapi: Eloquent bikin kodenya enak dibaca, foreign key bikin datanya tidak bisa rusak.

Satu hal penting: jalankan migration dalam urutan yang benar. Tabel induk harus dibuat dulu sebelum tabel anak yang merujuk ke sana. Laravel mengurutkan migration berdasarkan timestamp di nama file, jadi buat migration users sebelum posts.

## Kesalahan umum pemula

### 1. Tidak memakai foreign key sama sekali

Ini kesalahan paling umum. Alasannya macam-macam: malas, tidak tahu, atau merasa cukup menjaga relasi di kode aplikasi. Akibatnya data yatim menumpuk diam-diam dan baru ketahuan saat laporan atau fitur tertentu menampilkan hasil aneh. Selalu pasang foreign key, kecuali ada alasan teknis yang sangat spesifik.

### 2. Tipe data foreign key tidak cocok dengan primary key

Primary key `SERIAL` adalah integer 32 bit, sedangkan `BIGSERIAL` adalah bigint 64 bit. Kalau primary key tabel users memakai `id()` di Laravel yang menghasilkan bigint, foreign key harus `foreignId` atau `unsignedBigInteger`, bukan integer biasa. Tipe yang tidak cocok bikin pembuatan foreign key gagal, atau lebih buruk, berperilaku aneh di database tertentu.

### 3. CASCADE di semua relasi tanpa berpikir

`ON DELETE CASCADE` itu praktis, tapi berbahaya kalau dipasang sembarangan. Menghapus satu kategori tidak seharusnya menghapus semua produk di dalamnya. Menghapus satu user tidak seharusnya menghapus semua order dan riwayat pembayarannya. Pilih CASCADE hanya untuk data yang memang tidak bermakna tanpa induknya, seperti komentar pada post atau item pada order.

### 4. Lupa index di kolom foreign key

Di PostgreSQL, foreign key tidak otomatis dibuatkan index seperti primary key. Kalau tabel anak punya jutaan baris, query JOIN dan pengecekan foreign key jadi lambat. Tambahkan index sendiri:

```sql
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);
```

Di Laravel, `foreignId` sudah membuat index otomatis, jadi masalah ini lebih sering muncul di project yang skemanya ditulis manual.

### 5. Menghapus data induk langsung dari database tanpa cek anak

Menghapus baris lewat SQL manual atau tool database tanpa memperhatikan relasi bisa gagal karena RESTRICT, atau menghapus lebih banyak dari yang kamu kira karena CASCADE. Sebelum menghapus data induk, selalu cek dulu berapa baris anak yang terpengaruh:

```sql
SELECT COUNT(*) FROM posts WHERE user_id = 5;
SELECT COUNT(*) FROM comments WHERE user_id = 5;
```

Dua detik mengecek bisa menyelamatkanmu dari kehilangan data yang tidak bisa dikembalikan.

## Langkah praktis yang bisa langsung dicoba

Pertama, buat database latihan dan jalankan skema users, posts, dan comments di atas. Kedua, coba masukkan post dengan `user_id` yang tidak ada dan lihat sendiri error foreign key-nya. Ketiga, coba hapus satu user yang masih punya post, lalu amati bedanya RESTRICT, CASCADE, dan SET NULL dengan mengubah aturan ON DELETE-nya. Keempat, buat pivot table post_tag dan tulis query untuk mengambil semua tag dari satu post. Kelima, kalau kamu pakai Laravel, buat migration yang sama dengan `foreignId` dan deklarasikan relasi `hasMany` dan `belongsTo` di model, lalu coba `$user->posts` di tinker.

## Penutup

Ringkasan singkatnya: foreign key adalah kolom yang menunjuk ke primary key tabel lain, dan fungsinya menjaga relasi tetap valid di level database. One to many diwakili satu foreign key di tabel anak, many to many butuh pivot table, dan one to one adalah kasus khusus yang jarang dipakai. Pilih perilaku ON DELETE dengan sengaja, RESTRICT untuk keamanan, CASCADE untuk data yang ikut mati bersama induknya, SET NULL untuk data yang harus bertahan. Pasang index di foreign key, samakan tipe datanya dengan primary key, dan biasakan mengecek baris anak sebelum menghapus induk. Kuasai ini, dan skema database kamu sudah lebih rapi dari sebagian besar project pemula. Langkah berikutnya yang nyambung: pelajari JOIN untuk membaca data lintas tabel, karena relasi yang sudah kamu bangun di sini adalah fondasi semua query JOIN.
