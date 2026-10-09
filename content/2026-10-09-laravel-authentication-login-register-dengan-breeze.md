---
title: Laravel Authentication: Login & Register dengan Breeze
description: Panduan Laravel Breeze untuk pemula: install, alur login & register, email verification, password reset, plus kesalahan umum dan cara memperbaikinya dengan contoh kode.
date: 2026-10-09
tags: [laravel, php, authentication, breeze]
faq:
  - Apa itu Laravel Breeze?
  - Laravel Breeze adalah starter kit authentication resmi dari Laravel: ia men-generate semua kode login, register, lupa password, dan verifikasi email memakai Blade biasa, jadi kamu bisa langsung belajar dan memodifikasinya tanpa bergantung pada package pihak ketiga.
  - Bagaimana cara install Laravel Breeze di Laravel 12?
  - Jalankan `composer require laravel/breeze --dev`, lalu `php artisan breeze:install blade` dan `php artisan migrate`. Buka `/register` dan `/login` di browser — halaman auth sudah langsung bisa dipakai.
  - Kenapa setelah install Breeze muncul error "table users doesn't exist"?
  - Kamu lupa menjalankan `php artisan migrate`. Breeze hanya men-generate kode, bukan tabel database — jalankan migrasi agar tabel `users` dan `password_reset_tokens` terbuat.
  - Apakah Laravel Breeze aman dipakai untuk production?
  - Aman, selama kamu memakainya di project sendiri: Breeze men-generate kode yang bisa kamu audit baris per baris, termasuk rate limiting login dan hashing password Bcrypt/Argon2. Yang tidak aman adalah lupa mengatur `APP_URL` dan session domain dengan benar di server production.
---

Setiap aplikasi web butuh login dan register, dan hampir semua pemula Laravel menundanya karena kelihatannya rumit: hashing password, session, "remember me", lupa password, verifikasi email. Padahal Laravel sudah menyediakan starter kit resmi bernama Breeze — sekali install, semua alur itu langsung jadi dan kamu bisa membaca setiap baris kodenya. Artikel ini membahas instalasi Breeze di Laravel 12, cara kerja alurnya, dan jebakan yang paling sering saya lihat dialami pemula.

## Install Breeze: Tiga Perintah Saja

Breeze sengaja ringan: ia men-generate kode auth memakai Blade biasa (bisa juga React/Vue, tapi mulai dari Blade). Jalankan di root project Laravel-mu:

```bash
composer require laravel/breeze --dev
php artisan breeze:install blade
php artisan migrate
npm install && npm run dev
```

Perintah `breeze:install` men-generate controller di `app/Http/Controllers/Auth/`, view di `resources/views/auth/`, request `LoginRequest`, file route `routes/auth.php`, dan meng-wire semuanya di `routes/web.php`. Perintah `migrate` membuat tabel `users` — tanpa ini, halaman register akan error karena tabelnya belum ada.

Coba buka `/register` di browser. Kamu dapat form register yang berfungsi penuh: validasi, hashing password otomatis, lalu user langsung login. Buka `/login`: ada fitur "remember me", rate limiting, dan link lupa password.

## Bedah Alur Register: Kode yang Sebenarnya Terjadi

Mari lihat `RegisteredUserController@store` yang baru saja di-generate Breeze:

```php
// app/Http/Controllers/Auth/RegisteredUserController.php

public function store(Request $request): RedirectResponse
{
    $request->validate([
        'name' => ['required', 'string', 'max:255'],
        'email' => ['required', 'string', 'lowercase', 'email', 'max:255', 'unique:'.User::class],
        'password' => ['required', 'confirmed', Rules\Password::defaults()],
    ]);

    $user = User::create([
        'name' => $request->name,
        'email' => $request->email,
        'password' => Hash::make($request->password),
    ]);

    event(new Registered($user));

    Auth::login($user);

    return redirect(route('dashboard', absolute: false));
}
```

Ada lima hal yang patut kamu perhatikan di sini. Pertama, `'confirmed'` berarti field `password` harus cocok dengan `password_confirmation` di form. Kedua, `Rules\Password::defaults()` menerapkan aturan password bawaan Laravel (minimal 8 karakter di production). Ketiga, password di-hash dengan `Hash::make` — jangan pernah simpan plaintext. Keempat, `event(new Registered($user))` memicu pengiriman email verifikasi kalau model `User` mengimplementasikan `MustVerifyEmail`. Kelima, `Auth::login($user)` langsung memasukkan user ke session setelah register — pengalaman yang mulus.

## Bedah Alur Login: Authenticate + Rate Limiting

Login di Breeze ditangani `LoginRequest` yang dipanggil dari `AuthenticatedSessionController`:

```php
// app/Http/Requests/Auth/LoginRequest.php

public function authenticate(): void
{
    $this->ensureIsNotRateLimited();

    if (! Auth::attempt($this->only('email', 'password'), $this->boolean('remember'))) {
        RateLimiter::hit($this->throttleKey());

        throw ValidationException::withMessages([
            'email' => trans('auth.failed'),
        ]);
    }

    RateLimiter::clear($this->throttleKey());
}
```

Ini kode yang bagus untuk dipelajari pemula: `Auth::attempt` membandingkan password yang dimasukkan dengan hash di database (bukan string mentah). `ensureIsNotRateLimited` membatasi maksimal 5 percobaan login gagal per IP+email — brute force otomatis ditahan. Dan perhatikan: pesan errornya selalu "These credentials do not match our records" tanpa membedakan email salah atau password salah — sengaja, supaya penyerang tidak bisa menebak email mana yang terdaftar.

Satu detail penting yang sering terlewat: `Auth::attempt` dengan `'remember' => true` membuat cookie remember-me berumur panjang. Kalau user mengeluh "kok saya tiba-tiba logout", biasanya bukan bug — session-nya expired dan mereka login tanpa mencentang remember me.

## Melindungi Halaman: Middleware auth dan guest

Buka `routes/web.php` hasil generate Breeze, kamu akan melihat pola ini:

```php
use App\Http\Controllers\ProfileController;

Route::get('/dashboard', function () {
    return view('dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
```

`auth` berarti hanya user yang login boleh lewat; belum login otomatis di-redirect ke `/login`. `verified` berarti email user sudah terverifikasi (hanya aktif kalau model `User` implements `MustVerifyEmail`). Sebaliknya, semua route di `routes/auth.php` memakai middleware `guest` — user yang sudah login tidak bisa membuka `/login` lagi, langsung di-redirect ke dashboard. Kalau di project-mu ada halaman "hanya boleh dibuka setelah login", tinggal tambahkan `->middleware('auth')` — semudah itu.

## Kesalahan Umum Pemula (dan Cara Menghindarinya)

**1. Lupa `php artisan migrate` setelah install.** Error-nya: `SQLSTATE[42S02]: Base table or view not found: users doesn't exist`. Breeze tidak otomatis membuat tabel. Solusinya selalu: setiap kali pull code auth baru atau ganti database, jalankan migrasi dulu.

**2. Install Breeze di project yang sudah jadi lalu bingung file mana yang bentrok.** Breeze dirancang untuk project fresh. Kalau project-mu sudah punya route/web.php yang dimodifikasi berat, backup dulu sebelum `breeze:install` karena perintah itu menulis ulang beberapa file. Lihat diff-nya dengan git sebelum commit.

**3. Email verifikasi dan lupa password "tidak jalan".** Breeze men-generate kode-nya, tapi pengiriman email butuh konfigurasi mail yang benar. Untuk development, pakai Mailtrap atau `MAIL_MAILER=log` di `.env` supaya isi email tertulis di `storage/logs/laravel.log` — bisa kamu baca tanpa setup SMTP apa pun:

```env
MAIL_MAILER=log
```

Untuk production, isi `MAIL_MAILER=smtp` beserta host, port, username, dan password SMTP-mu. Tanpa ini, user yang klik "forgot password" tidak akan pernah menerima email reset.

**4. Session tidak persist / selalu logout di production.** Ini hampir selalu masalah konfigurasi, bukan bug Breeze. Pastikan `APP_URL` di `.env` sesuai domain aslimu (termasuk `https://`), dan `SESSION_DOMAIN` tidak salah. Cookie session tidak akan terkirim kalau domain-nya tidak cocok.

**5. Mengubah validasi password tapi lupa sisi frontend.** Kalau kamu memperketat `Rules\Password::defaults()` (misalnya wajib simbol), pastikan pesan error dari validasi tampil di form Blade. Untungnya view bawaan Breeze sudah memakai `<x-input-error>`, jadi selama kamu tidak menghapus komponen itu, error akan muncul otomatis.

## Langkah Praktis yang Bisa Langsung Dicoba

Sudah install Breeze? Coba latihan 15 menit ini untuk memahami auth sampai ke tulang:

1. Buka `/register`, daftar akun baru, lalu cek tabel `users` di database — pastikan password tersimpan sebagai hash `$2y$...`, bukan plaintext.
2. Coba login dengan password salah 5 kali berturut-turut, lalu perhatikan pesan throttle yang muncul. Ini rate limiter Breeze bekerja.
3. Tambahkan `implements MustVerifyEmail` di `app/Models/User.php`, set `MAIL_MAILER=log`, register akun baru, lalu baca link verifikasi di `storage/logs/laravel.log`.
4. Buat route baru yang dilindungi middleware `auth` dan coba akses tanpa login — pastikan kamu di-redirect ke `/login`.

## Kapan Pakai Breeze, Kapan Tidak

Breeze adalah pilihan tepat untuk aplikasi web tradisional dengan Blade — blog, dashboard admin, aplikasi CRUD internal. Ia men-generate kode yang bisa kamu baca dan ubah, tanpa magic tersembunyi.

Kalau kamu membangun SPA (React/Vue terpisah) atau mobile app yang butuh token API, pilih Laravel Sanctum sebagai gantinya — Breeze berbasis session cookie, tidak cocok untuk client yang tidak berbagi domain. Dan kalau project-mu sudah punya sistem auth custom yang berjalan, jangan install Breeze hanya demi "standar": migrasi auth yang sedang berjalan jauh lebih berisiko daripada mempertahankannya.

Intinya: untuk mayoritas project Laravel pemula sampai menengah, Breeze adalah jalan tercepat menuju sistem login yang benar dan aman — dan karena kodenya terbuka di project-mu sendiri, ia sekaligus guru authentication terbaik yang bisa kamu baca baris per baris.
