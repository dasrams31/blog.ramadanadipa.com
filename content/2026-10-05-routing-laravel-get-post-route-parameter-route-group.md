---
title: Routing Laravel: GET, POST, Parameter & Route Group
description: Panduan routing Laravel: bedakan GET dan POST, pakai route parameter dan route group, plus cara umum yang bikin error dan cara memperbaikinya.
date: 2026-10-05
tags: [laravel, php, routing, tutorial]
faq:
  - Apa beda route GET dan POST di Laravel?
  - Route GET dipakai untuk menampilkan halaman atau data, sedangkan POST dipakai untuk menerima kiriman data seperti form. Laravel memisahkan keduanya karena HTTP memperlakukan GET sebagai operasi baca yang aman diulang.
  - Bagaimana cara mengambil parameter dari URL di Laravel?
  - Tuliskan `{nama}` di path route, lalu tangkap sebagai argumen closure atau controller method dengan nama yang sama. Tambahkan `whereNumber()` atau regex untuk membatasi formatnya.
  - Apa itu route group di Laravel?
  - Cara mengelompokkan beberapa route yang berbagi prefix URL, middleware, atau namespace. Berguna untuk merapikan `routes/web.php` yang sudah berisi puluhan route.
  - Kenapa route Laravel saya error 404 padahal sudah didefinisikan?
  - Penyebab paling umum: lupa menjalankan `php artisan route:clear` setelah mengedit route di production dengan route cache aktif, atau salah urutan route sehingga tertelan route dinamis di atasnya.
---

Kalau kamu baru pindah ke Laravel, `routes/web.php` adalah file pertama yang wajib dikuasai. Semua URL aplikasi didefinisikan di sana — dan cara kamu menyusunnya menentukan apakah aplikasimu rapi atau jadi spageti dalam dua minggu.

Artikel ini membahas empat fondasi: method GET dan POST, route parameter, dan route group. Semuanya dengan contoh kode yang bisa langsung dicoba.

## GET vs POST: Bukan Sekadar Dua Method

Setiap route Laravel dimulai dengan HTTP method. Dua yang paling sering dipakai:

```php
// routes/web.php

// GET: menampilkan halaman
Route::get('/tentang', function () {
    return view('tentang');
});

// POST: menerima kiriman data dari form
Route::post('/kontak', function (Request $request) {
    $nama = $request->input('nama');
    return "Halo, {$nama}! Pesanmu sudah kami terima.";
});
```

Aturannya sederhana: **GET untuk membaca, POST untuk mengubah**. Form HTML yang mengirim data harus pakai `method="POST"` dan menyertakan token CSRF:

```blade
<form method="POST" action="/kontak">
    @csrf
    <input type="text" name="nama">
    <button type="submit">Kirim</button>
</form>
```

Lupa `@csrf`? Kamu akan dapat error 419 "Page Expired" — ini jebakan pemula nomor satu di Laravel. Direktif `@csrf` menyisipkan hidden input berisi token yang melindungi dari serangan cross-site request forgery.

Untuk operasi update dan delete, Laravel memakai **method spoofing** karena form HTML cuma mendukung GET dan POST:

```php
Route::put('/produk/{id}', [ProdukController::class, 'update']);
Route::delete('/produk/{id}', [ProdukController::class, 'destroy']);
```

```blade
<form method="POST" action="/produk/5">
    @csrf
    @method('PUT')
    <!-- field form di sini -->
</form>
```

## Route Parameter: URL yang Dinamis

Daripada bikin 100 route untuk 100 artikel, pakai satu route berparameter:

```php
Route::get('/artikel/{slug}', function (string $slug) {
    return "Kamu membuka artikel: {$slug}";
});
```

Membuka `/artikel/routing-laravel` akan menampilkan `Kamu membuka artikel: routing-laravel`. Parameter opsional cukup ditandai dengan tanda tanya:

```php
Route::get('/arsip/{tahun?}', function (?string $tahun = null) {
    return $tahun ? "Arsip tahun {$tahun}" : "Semua arsip";
});
```

### Batasan Format dengan `where`

Tanpa batasan, route `/artikel/{slug}` juga akan menangkap `/artikel/admin` atau `/artikel/tambah` yang mungkin sudah kamu definisikan sebagai route statis. Amankan dengan constraint:

```php
Route::get('/artikel/{slug}', [ArtikelController::class, 'show'])
    ->where('slug', '[a-z0-9-]+');

Route::get('/user/{id}', [UserController::class, 'show'])
    ->whereNumber('id');
```

`whereNumber('id')` membuat route hanya cocok untuk angka — `/user/abc` otomatis 404 dan tidak perlu dicek manual di controller.

### Route Model Binding: Parameter Jadi Objek

Alih-alih menerima `$id` lalu query manual, Laravel bisa langsung menyuntikkan model:

```php
// routes/web.php
Route::get('/produk/{produk}', [ProdukController::class, 'show']);

// app/Http/Controllers/ProdukController.php
public function show(Produk $produk)
{
    return view('produk.show', compact('produk'));
}
```

Selama nama parameter `{produk}` sama dengan nama model `Produk`, Laravel otomatis menjalankan `Produk::findOrFail($id)`. Kalau data tidak ada, kamu dapat halaman 404 tanpa satu baris kode tambahan.

## Route Group: Merapikan Puluhan Route

Begitu aplikasimu punya area admin dengan 20 route, menulis prefix dan middleware berulang-ulang melelahkan. Group menyelesaikannya:

```php
Route::prefix('admin')->middleware('auth')->group(function () {
    Route::get('/dashboard', [AdminController::class, 'dashboard']);
    Route::get('/produk', [AdminProdukController::class, 'index']);
    Route::post('/produk', [AdminProdukController::class, 'store']);
    Route::put('/produk/{id}', [AdminProdukController::class, 'update']);
    Route::delete('/produk/{id}', [AdminProdukController::class, 'destroy']);
});
```

Semua route di dalam group otomatis menjadi `/admin/dashboard`, `/admin/produk`, dan seterusnya — semuanya dilindungi middleware `auth`. Cara modern yang setara memakai `Route::controller` agar lebih ringkas:

```php
use App\Http\Controllers\Admin\ProdukController;

Route::prefix('admin')->middleware('auth')->group(function () {
    Route::controller(ProdukController::class)->prefix('produk')->group(function () {
        Route::get('/', 'index');
        Route::post('/', 'store');
        Route::put('/{id}', 'update');
        Route::delete('/{id}', 'destroy');
    });
});
```

### Resource Route: Satu Baris untuk CRUD

Untuk operasi CRUD standar, ada jalan pintas yang lebih pendek lagi:

```php
Route::resource('produk', ProdukController::class);
```

Satu baris ini menghasilkan tujuh route sekaligus (`index`, `create`, `store`, `show`, `edit`, `update`, `destroy`) dengan method dan URL yang konvensional. Cek daftarnya dengan `php artisan route:list` — perintah ini wajib kamu kenal:

```bash
php artisan route:list

# Filter hanya route produk
php artisan route:list --name=produk
```

## Named Route: Jangan Hardcode URL

Setiap kali kamu menulis `<a href="/artikel/tentang-kami">` di template, kamu menciptakan utang teknis kecil. Begitu URL berubah, semua template harus diburu satu-satu. Named route menghilangkan masalah ini:

```php
Route::get('/artikel/{slug}', [ArtikelController::class, 'show'])
    ->name('artikel.show');
```

Di Blade atau controller, panggil namanya — bukan URL-nya:

```blade
<a href="{{ route('artikel.show', ['slug' => $artikel->slug]) }}">
    {{ $artikel->judul }}
</a>
```

```php
// Redirect ke named route setelah form tersimpan
return redirect()->route('artikel.show', $artikel->slug);
```

Sekarang kamu bebas mengganti path `/artikel/{slug}` menjadi `/post/{slug}` kapan pun: selama namanya tetap `artikel.show`, semua link di aplikasi ikut berubah otomatis. Kebiasaan ini terlihat sepele di project kecil, tapi menyelamatkan jam kerja di project yang sudah punya ratusan template. Untuk route group, kamu bisa memberi prefix nama sekaligus:

```php
Route::prefix('admin')->name('admin.')->group(function () {
    Route::get('/dashboard', [AdminController::class, 'dashboard'])->name('dashboard');
    // URL: /admin/dashboard, nama: admin.dashboard
});
```

## Kesalahan Umum dan Cara Menghindarinya

**1. Urutan route salah.** Route dinamis menangkap segalanya:

```php
// SALAH: /artikel/tambah tidak akan pernah tercapai
Route::get('/artikel/{slug}', ...);
Route::get('/artikel/tambah', ...);

// BENAR: route statis dulu
Route::get('/artikel/tambah', ...);
Route::get('/artikel/{slug}', ...);
```

Aturan praktisnya: **dari yang paling spesifik ke yang paling umum**.

**2. Route cache bikin route baru tidak terbaca.** Di production (atau setelah menjalankan `php artisan route:cache`), edit route tidak berpengaruh sampai cache dibersihkan:

```bash
php artisan route:clear   # hapus cache
php artisan route:cache   # buat ulang (hanya untuk production)
```

Catatan: route yang memakai closure tidak bisa di-cache. Kalau kamu ingin memakai route cache, pindahkan logic closure ke controller.

**3. Lupa `@csrf` di form POST** → error 419, seperti dibahas di atas.

**4. Nama parameter dan argumen tidak cocok.** Route `/artikel/{slug}` tapi method menerima `(string $judul)` → error. Namanya harus sama persis.

## Checklist Praktis

1. Buat route `/halo/{nama}` yang menampilkan sapaan personal.
2. Tambahkan `->where('nama', '[a-zA-Z]+')` dan coba buka `/halo/123` — harus 404.
3. Buat form POST sederhana dengan `@csrf`, kirim, dan tampilkan kembali datanya.
4. Bungkus tiga route latihanmu dalam satu `Route::prefix('latihan')->group(...)`.
5. Jalankan `php artisan route:list` dan pastikan semua route terdaftar seperti yang kamu harapkan.

Kuasai empat pola ini dan kamu sudah bisa menyusun struktur URL untuk mayoritas aplikasi Laravel. Berikutnya yang layak dipelajari: middleware custom untuk proteksi yang lebih granular, dan route model binding dengan kolom selain `id` memakai `getRouteKeyName()`.
