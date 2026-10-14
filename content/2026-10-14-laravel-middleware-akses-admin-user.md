---
title: Middleware Laravel: Cara Batasi Akses Admin dan User
description: Pelajari middleware Laravel untuk membatasi akses halaman admin. Contoh kode nyata, kesalahan umum pemula, dan langkah praktis yang bisa langsung kamu coba.
date: 2026-10-14
tags: [laravel, php, middleware, authentication]
faq:
  - Apa itu middleware di Laravel?
  - Middleware adalah lapisan kode yang dijalankan sebelum request mencapai controller. Contoh penggunaannya: memastikan user sudah login, memeriksa role admin, atau mencatat log request.
  - Bagaimana cara membuat middleware baru di Laravel?
  - Jalankan php artisan make:middleware NamaMiddleware. Middleware baru tersimpan di app/Http/Middleware/. Daftarkan aliasnya di bootstrap/app.php (Laravel 11/12), lalu pakai di route dengan ->middleware('nama-alias').
  - Kenapa muncul error "Target class [admin] does not exist"?
  - Error itu berarti alias middleware belum didaftarkan di bootstrap/app.php atau nama aliasnya salah ketik. Daftarkan dulu aliasnya, lalu pastikan nama di route sama persis dengan yang didaftarkan.
  - Apakah cukup cek role di Blade untuk mengamankan halaman admin?
  - Tidak cukup. Sembunyikan menu di Blade hanya soal tampilan, tapi URL-nya tetap bisa dibuka langsung. Keamanan sesungguhnya harus di middleware, karena middleware berjalan di server sebelum request mencapai controller.
---

Hampir setiap aplikasi web punya halaman yang tidak boleh dibuka sembarang orang: dashboard admin, halaman kelola user, laporan keuangan. Masalah klasik pemula: menu admin disembunyikan dari tampilan, tapi URL-nya tetap bisa dibuka langsung oleh siapa pun. Solusi yang benar di Laravel adalah **middleware**.

Middleware adalah lapisan kode yang dilewati request sebelum sampai ke controller. Bayangkan seperti satpam di pintu gedung: setiap orang yang mau masuk dicek dulu identitasnya. Kalau lolos, request diteruskan ke controller. Kalau tidak, request ditolak di depan pintu, controller tidak pernah dijalankan.

## Cara Kerja Middleware

Alurnya sederhana:

1. User membuka URL, misalnya `/admin/dashboard`.
2. Laravel menjalankan middleware yang terpasang di route tersebut, satu per satu sesuai urutan.
3. Setiap middleware boleh melakukan dua hal: meneruskan request ke lapisan berikutnya dengan `return $next($request)`, atau menghentikan request, misalnya dengan `abort(403)` atau redirect.
4. Kalau semua middleware lolos, controller dijalankan dan response dikirim ke user.

Karena middleware berjalan sebelum controller, ia adalah tempat yang tepat untuk semua pengecekan akses. Controller kamu jadi bersih, fokus ke logika bisnis saja.

## Langkah 1: Siapkan Kolom Role di Tabel Users

Middleware butuh cara membedakan admin dan user biasa. Cara paling sederhana: tambah kolom `role` di tabel `users`. Buat migration baru:

```bash
php artisan make:migration add_role_to_users_table
```

Isi migration-nya:

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->string('role')->default('user');
        });
    }

    public function down(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->dropColumn('role');
        });
    }
};
```

Jalankan `php artisan migrate`. Nilai default-nya `user`, jadi akun baru otomatis bukan admin. Untuk membuat akun admin, update manual lewat tinker atau seeder:

```bash
php artisan tinker
```

```php
User::where('email', 'admin@contoh.com')->update(['role' => 'admin']);
```

Catatan penting: nilai `role` harus selalu berasal dari database, tidak pernah dari input form atau hidden field. Kalau role dikirim dari browser, user bisa mengubahnya sendiri lewat inspect element.

## Langkah 2: Buat Middleware

Laravel menyediakan perintah artisan untuk membuat middleware:

```bash
php artisan make:middleware EnsureUserIsAdmin
```

File baru muncul di `app/Http/Middleware/EnsureUserIsAdmin.php`. Isi dengan logika pengecekan:

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureUserIsAdmin
{
    public function handle(Request $request, Closure $next): Response
    {
        if (! $request->user() || $request->user()->role !== 'admin') {
            abort(403, 'Akses ditolak.');
        }

        return $next($request);
    }
}
```

Perhatikan dua hal di kode ini. Pertama, kita cek `$request->user()` dulu sebelum membaca `->role`. Kalau user belum login, `$request->user()` bernilai null, dan membaca property dari null akan error. Kedua, `abort(403)` menghentikan request dengan halaman error 403 Forbidden bawaan Laravel. Alternatifnya, kamu bisa redirect ke halaman login atau dashboard user biasa.

## Langkah 3: Daftarkan Alias Middleware

Middleware yang baru dibuat belum dikenal Laravel. Di Laravel 11 dan 12, pendaftaran dilakukan di file `bootstrap/app.php` lewat method `withMiddleware`:

```php
<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware) {
        $middleware->alias([
            'admin' => \App\Http\Middleware\EnsureUserIsAdmin::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions) {
        //
    })->create();
```

Alias `admin` ini yang akan kamu pakai di route. Kalau kamu masih memakai Laravel 10 atau lebih lama, pendaftarannya ada di `app/Http/Kernel.php` pada array `$middlewareAliases`. Konsepnya sama, hanya lokasinya yang berbeda.

## Langkah 4: Pasang Middleware di Route

Sekarang lindungi route admin. Cara paling rapi: bungkus dalam route group.

```php
<?php

use App\Http\Controllers\AdminController;
use Illuminate\Support\Facades\Route;

// Route publik, bisa dibuka siapa saja
Route::get('/', function () {
    return view('welcome');
});

// Route user yang sudah login
Route::middleware('auth')->group(function () {
    Route::get('/dashboard', function () {
        return view('dashboard');
    });
});

// Route khusus admin: harus login DAN rolenya admin
Route::middleware(['auth', 'admin'])->group(function () {
    Route::get('/admin/dashboard', [AdminController::class, 'index']);
    Route::get('/admin/users', [AdminController::class, 'users']);
});
```

Urutan `['auth', 'admin']` itu penting. Middleware `auth` memastikan user sudah login, baru middleware `admin` memeriksa role. Kalau dibalik, middleware `admin` akan menerima user yang belum login dan `$request->user()` bernilai null. Kode kita memang sudah aman dari null, tapi urutan yang benar membuat logikanya lebih jelas: tamu yang belum login diarahkan ke halaman login oleh `auth`, bukan malah dapat halaman 403.

## Langkah 5: Middleware dengan Parameter (Bonus)

Sering kali kamu butuh pengecekan role yang lebih fleksibel, misalnya satu middleware untuk admin, editor, dan author. Daripada bikin tiga middleware, buat satu middleware berparameter:

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class CheckRole
{
    public function handle(Request $request, Closure $next, string $role): Response
    {
        if (! $request->user() || $request->user()->role !== $role) {
            abort(403, 'Akses ditolak.');
        }

        return $next($request);
    }
}
```

Daftarkan dengan alias `role`, lalu pakai seperti ini:

```php
Route::middleware(['auth', 'role:admin'])->group(function () {
    Route::get('/admin/dashboard', [AdminController::class, 'index']);
});

Route::middleware(['auth', 'role:editor'])->group(function () {
    Route::get('/editor/artikel', [EditorController::class, 'index']);
});
```

Parameter setelah titik dua (`role:admin`) otomatis dikirim sebagai argumen `$role` di method `handle`. Satu class middleware, banyak kebutuhan terpenuhi.

## Kesalahan Umum Pemula (dan Cara Menghindarinya)

**1. Lupa mendaftarkan alias.** Ini error paling sering: `Target class [admin] does not exist`. Middleware-nya sudah dibuat, tapi aliasnya belum didaftarkan di `bootstrap/app.php`, atau nama alias di route salah ketik. Solusinya: cek ejaan alias di dua tempat itu, pastikan sama persis termasuk huruf besar kecil.

**2. Cek role tanpa cek login dulu.** Kode seperti `$request->user()->role !== 'admin'` akan error `Attempt to read property "role" on null` kalau dibuka tamu yang belum login. Selalu cek `$request->user()` dulu, atau pastikan middleware `auth` dipasang sebelum middleware role di route.

**3. Lupa `return $next($request)`.** Kalau method `handle` tidak me-return `$next($request)` di akhir, request berhenti di middleware dan user dapat halaman kosong. Pola yang benar: semua kondisi penolakan di atas, dan baris terakhir selalu `return $next($request);`.

**4. Cuma sembunyikan menu di Blade.** Menulis `@if(auth()->user()->role === 'admin')` di navbar memang menyembunyikan menu dari user biasa, tapi itu hanya tampilan. URL `/admin/dashboard` tetap bisa diketik manual di address bar. Blade mengatur apa yang terlihat, middleware mengatur apa yang boleh diakses. Keduanya dipakai bersama, tapi keamanan sesungguhnya ada di middleware.

**5. Role diambil dari input user.** Jangan pernah percaya data role yang dikirim dari form, hidden input, atau query string. Role harus selalu dibaca dari database lewat `$request->user()->role`. Data dari browser bisa dimanipulasi, data di database tidak.

## Langkah Praktis yang Bisa Langsung Dicoba

1. Tambah kolom `role` ke tabel users dengan migration, lalu migrate.
2. Buat satu akun admin lewat tinker dengan mengupdate kolom `role` jadi `admin`.
3. Buat middleware `EnsureUserIsAdmin` dengan artisan, isi method `handle` seperti contoh di atas.
4. Daftarkan alias `admin` di `bootstrap/app.php`.
5. Buat route group `/admin/*` yang dilindungi `['auth', 'admin']`, dan satu route `/dashboard` biasa untuk user login.
6. Uji dengan tiga skenario: buka `/admin/dashboard` tanpa login (harus diarahkan ke login), login sebagai user biasa (harus dapat 403), login sebagai admin (harus terbuka).

Kalau tiga skenario itu lolos, sistem akses kamu sudah benar. Dari sini kamu bisa kembangkan: halaman 403 custom, middleware berparameter untuk banyak role, atau pencatatan log setiap ada upaya akses ditolak.

Middleware memang terlihat seperti detail kecil, tapi ia adalah fondasi keamanan aplikasi Laravel. Setiap kali kamu menambahkan halaman sensitif baru, pertanyaan pertamanya selalu sama: middleware apa yang menjaga route ini? Kalau jawabannya tidak ada, route itu terbuka untuk siapa pun.
