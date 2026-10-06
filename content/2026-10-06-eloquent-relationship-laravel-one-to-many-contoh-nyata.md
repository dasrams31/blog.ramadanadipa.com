---
title: Eloquent One to Many Laravel: Contoh Relasi yang Nyata
description: Pelajari relasi Eloquent one to many di Laravel dengan contoh nyata: setup migrasi, definisi belongsTo dan hasMany, eager loading, plus kesalahan umum pemula.
date: 2026-10-06
tags: [laravel, php, eloquent, database]
faq:
  - Apa itu relasi one to many di Laravel Eloquent?
  - Relasi di mana satu baris di tabel A bisa terhubung ke banyak baris di tabel B, seperti satu penulis punya banyak artikel. Di Eloquent, sisi "banyak" pakai hasMany() dan sisi "satu" pakai belongsTo().
  - Kapan pakai hasMany dan kapan pakai belongsTo?
  - Pakai hasMany() di model yang "memiliki" banyak item (misal User punya banyak Post), dan belongsTo() di model "anak" yang menunjuk ke pemiliknya (Post dimiliki satu User).
  - Kenapa query Eloquent saya lambat saat menampilkan relasi?
  - Biasanya karena N+1 query problem: setiap baris relasi memicu query baru. Atasi dengan eager loading memakai with(), misalnya User::with('posts')->get().
  - Bagaimana cara menyimpan data anak yang otomatis terhubung ke induk?
  - Gunakan method relasinya, misalnya $user->posts()->create([...]). Laravel otomatis mengisi foreign key, jadi tidak perlu menulis user_id secara manual.
---

Relasi database adalah bagian yang paling sering bikin pemula Laravel nyerah setengah jalan. Padahal konsepnya sederhana: artikel ini pakai satu contoh nyata yang kamu pasti kenal — **satu penulis punya banyak artikel** — dan kita bangun sampai bisa jalan.

## Skenario Nyatanya

Bayangkan aplikasi blog. Ada dua tabel:

- `users` — penulis
- `posts` — artikel

Satu user bisa menulis banyak post. Satu post hanya dimiliki satu user. Ini pola klasik **one to many**, dan pola yang sama berlaku untuk: satu kategori punya banyak produk, satu order punya banyak item, satu sekolah punya banyak siswa.

## Langkah 1: Siapkan Migrasi

Post butuh kolom `user_id` sebagai foreign key yang menunjuk ke `users.id`:

```php
// database/migrations/xxxx_create_posts_table.php

Schema::create('posts', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->cascadeOnDelete();
    $table->string('title');
    $table->text('body');
    $table->timestamps();
});
```

`constrained()` otomatis membuat foreign key ke tabel `users`. `cascadeOnDelete()` artinya kalau user dihapus, semua post-nya ikut terhapus — masuk akal untuk contoh ini, tapi pikir dua kali kalau datanya penting.

Jalankan:

```bash
php artisan migrate
```

## Langkah 2: Definisi Relasi di Model

Di sisi "banyak" (`User`), pakai `hasMany`:

```php
// app/Models/User.php

public function posts(): HasMany
{
    return $this->hasMany(Post::class);
}
```

Di sisi "satu" (`Post`), pakai `belongsTo`:

```php
// app/Models/Post.php

public function user(): BelongsTo
{
    return $this->belongsTo(User::class);
}
```

Sudah. Itu seluruh definisi relasinya. Laravel menebak nama foreign key (`user_id`) dan tabel dari konvensi penamaan — selama kamu mengikuti konvensi, tidak perlu konfigurasi tambahan.

## Langkah 3: Pakai Relasinya

Mengambil semua post milik seorang user:

```php
$user = User::find(1);

foreach ($user->posts as $post) {
    echo $post->title;
}
```

Mengambil pemilik sebuah post:

```php
$post = Post::find(5);
echo $post->user->name;
```

Menyimpan post baru yang otomatis terhubung ke user:

```php
$user->posts()->create([
    'title' => 'Belajar Eloquent',
    'body' => 'Isi artikelnya...',
]);
```

Perhatikan bedanya: `$user->posts` (tanpa kurung) mengembalikan **collection** hasil, sedangkan `$user->posts()` (dengan kurung) mengembalikan **query builder relasi** yang bisa dilanjut dengan `create()`, `where()`, atau `count()`.

### Filtering Lewat Relasi

Mau post milik user yang judulnya mengandung kata tertentu?

```php
$posts = $user->posts()->where('title', 'like', '%Laravel%')->get();
```

Atau cari user yang punya minimal satu post:

```php
$users = User::has('posts')->get();
```

## Langkah 4: Hindari N+1 Query dengan Eager Loading

Ini jebakan terbesar pemula. Kode ini terlihat normal:

```php
// ❌ JANGAN: memicu N+1 query
$users = User::all();

foreach ($users as $user) {
    echo $user->name . ': ' . $user->posts->count() . ' artikel';
}
```

Kalau ada 100 user, Laravel menjalankan **1 query untuk user + 100 query untuk post masing-masing user** = 101 query. Solusinya, eager loading:

```php
// ✅ BENAR: hanya 2 query
$users = User::with('posts')->get();

foreach ($users as $user) {
    echo $user->name . ': ' . $user->posts->count() . ' artikel';
}
```

`with('posts')` membuat Laravel mengambil semua post terkait dalam satu query tambahan, lalu memasangkannya ke user masing-masing di memori.

Bahkan ada cara lebih hemat kalau cuma butuh hitungan:

```php
$users = User::withCount('posts')->get();

foreach ($users as $user) {
    echo $user->posts_count; // kolom virtual, tanpa query tambahan
}
```

## Kesalahan Umum Pemula

### 1. Nama Method Relasi Salah Kaprah

Laravel menebak foreign key dari nama method. Method `user()` menebak `user_id`. Kalau method-nya dinamai `author()` tapi kolomnya tetap `user_id`, relasinya gagal diam-diam. Solusinya: samakan nama, atau sebutkan eksplisit:

```php
public function author(): BelongsTo
{
    return $this->belongsTo(User::class, 'user_id');
}
```

### 2. Lupa Eager Loading di Halaman Daftar

Halaman index yang menampilkan 20 post beserta nama penulisnya tanpa `with('user')` = 21 query. Di local terasa cepat, di production dengan traffic nyata jadi lambat. Biasakan: **setiap kali loop mengakses relasi, pasang `with()`**.

### 3. Mengisi Foreign Key Manual

Pemula sering menulis:

```php
// ❌ Bisa jalan, tapi rawan salah
Post::create(['user_id' => $user->id, 'title' => '...']);
```

Lebih aman dan lebih jelas lewat relasi: `$user->posts()->create([...])`. Foreign key terisi otomatis dan tidak mungkin salah menunjuk user lain.

### 4. Foreign Key Tanpa Index

`foreignId()->constrained()` sudah membuat index otomatis. Tapi kalau kamu bikin kolom foreign key manual dengan `$table->unsignedBigInteger('user_id')` tanpa `->index()` atau `->constrained()`, query join-nya akan lambat saat data membesar. Selalu pakai `foreignId()->constrained()` kecuali ada alasan kuat.

## Nested Eager Loading: Relasi Bertingkat

Relasi bisa dirantai. Misal setiap post punya banyak komentar (`Post hasMany Comment`), dan kamu mau menampilkan user beserta post dan komentarnya sekaligus:

```php
$users = User::with('posts.comments')->get();
```

Satu panggilan `with('posts.comments')` mengambil tiga tabel sekaligus — user, post, dan komentar — tanpa N+1 di level mana pun. Aturan praktisnya: **setiap titik di rantai properti relasi di dalam loop harus sudah di-`with()`**.

Satu catatan penting soal mass assignment: `create()` lewat relasi tetap tunduk pada `$fillable` di model. Jadi pastikan model `Post` mengizinkan kolom yang kamu isi:

```php
// app/Models/Post.php

protected $fillable = ['title', 'body'];
```

Tidak perlu memasukkan `user_id` ke `$fillable` — Laravel mengisinya sendiri lewat relasi, dan justru lebih aman begitu karena user tidak bisa memalsukan pemilik post lewat input form.

## Coba Sekarang (5 Menit)

1. Buat migrasi post dengan `foreignId('user_id')->constrained()`, jalankan `php artisan migrate`.
2. Tambahkan method `posts()` di model `User` dan `user()` di model `Post`.
3. Di `php artisan tinker`, buat satu user dan tiga post lewat `$user->posts()->create([...])`.
4. Ambil user dengan `User::with('posts')->find(1)` dan cek `$user->posts->count()`.

Kalau empat langkah itu jalan tanpa error, kamu sudah paham 80% relasi Eloquent yang dipakai di project nyata. Sisanya — many to many, polymorphic — tinggal pengembangan pola yang sama.

## Kapan Tidak Pakai Relasi Eloquent?

Jujur saja: untuk laporan agregat berat (misal rekap penjualan per bulan dari jutaan baris), query builder mentah atau SQL view sering lebih cepat dan lebih jelas daripada memaksa relasi Eloquent. Eloquent unggul untuk CRUD dan logika domain; untuk reporting skala besar, jangan ragu pakai `DB::table()`.
