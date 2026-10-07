---
title: Validasi Form Laravel: Cara Mudah & Error Bahasa Indonesia
description: Panduan validasi form Laravel untuk pemula: aturan validasi, tampilkan error di Blade, pesan error Bahasa Indonesia, dan Form Request dengan contoh kode.
date: 2026-10-07
tags: [laravel, php, validasi, tutorial]
faq:
  - Bagaimana cara menampilkan pesan error validasi di Blade?
  - Pakai directive @error('nama_field') di Blade untuk menampilkan pesan error tiap field, dan old('nama_field') agar input user tidak hilang saat validasi gagal dan halaman di-redirect kembali.
  - Bagaimana cara mengganti pesan error validasi Laravel ke Bahasa Indonesia?
  - Ada dua cara: kirim array pesan custom sebagai argumen ketiga $request->validate(), atau buat file lang/id/validation.php berisi terjemahan lalu ubah 'locale' => 'id' di config/app.php agar berlaku global.
  - Apa bedanya $request->validate() dengan Form Request?
  - $request->validate() cocok untuk form kecil karena ditulis langsung di controller. Form Request (php artisan make:request) memindahkan rules, pesan custom, dan otorisasi ke class tersendiri — lebih rapi untuk form besar dan bisa dipakai ulang.
  - Bagaimana validasi unique saat update data supaya tidak konflik dengan data sendiri?
  - Pakai Rule::unique('users')->ignore($user->id) agar baris data yang sedang diupdate dikecualikan dari pengecekan unique. Tanpa ignore, update tanpa mengubah email pun akan gagal validasi.
---

Form tanpa validasi itu seperti pintu tanpa kunci: user bisa memasukkan apa saja, dan database kamu yang menanggung akibatnya. Kabar baiknya, Laravel punya sistem validasi yang menurut saya salah satu yang paling enak dipakai di antara framework PHP — dan artikel ini membahasnya sampai tuntas, termasuk cara membuat pesan error-nya berbahasa Indonesia.

## Cara Paling Cepat: $request->validate()

Di controller, cukup satu baris:

```php
// app/Http/Controllers/RegisterController.php

public function store(Request $request)
{
    $validated = $request->validate([
        'name'     => 'required|string|max:255',
        'email'    => 'required|email|unique:users,email',
        'password' => 'required|min:8|confirmed',
    ]);

    User::create($validated);

    return redirect('/dashboard');
}
```

Perilaku bawaannya sudah pintar: kalau validasi gagal, Laravel otomatis me-redirect kembali ke form sebelumnya, menyimpan pesan error di session, dan menyimpan input lama supaya tidak hilang. Kalau request-nya AJAX/JSON, ia mengembalikan response 422 dengan daftar error — tanpa kamu perlu menulis satu baris pun kode redirect manual.

Tiga aturan di contoh itu sudah mencakup 80% kebutuhan form:

| Aturan | Artinya |
|---|---|
| `required` | Field wajib diisi |
| `email` | Harus format email valid |
| `unique:users,email` | Email belum ada di tabel `users` |
| `min:8` | Minimal 8 karakter |
| `confirmed` | Harus ada field `password_confirmation` yang nilainya sama |
| `max:255` | Maksimal 255 karakter |
| `numeric`, `integer` | Harus angka |
| `date` | Harus tanggal valid |
| `in:admin,user` | Nilainya harus salah satu dari daftar |
| `image`, `mimes:jpg,png` | Untuk upload file gambar |

Aturan ditulis sebagai string dipisah pipe `|`, atau sebagai array kalau butuh objek rule:

```php
use Illuminate\Validation\Rule;

$request->validate([
    'email' => ['required', 'email', Rule::unique('users')],
]);
```

## Menampilkan Error di Blade

Pesan error tidak muncul sendiri — kamu harus menampilkannya di template. Pola standarnya:

```blade
<form method="POST" action="/register">
    @csrf

    <label>Nama</label>
    <input type="text" name="name" value="{{ old('name') }}">
    @error('name')
        <div class="error">{{ $message }}</div>
    @enderror

    <label>Email</label>
    <input type="email" name="email" value="{{ old('email') }}">
    @error('email')
        <div class="error">{{ $message }}</div>
    @enderror

    <label>Password</label>
    <input type="password" name="password">
    @error('password')
        <div class="error">{{ $message }}</div>
    @enderror

    <label>Konfirmasi Password</label>
    <input type="password" name="password_confirmation">

    <button type="submit">Daftar</button>
</form>
```

Dua hal penting di sini:

1. **`old('name')`** — mengisi kembali input dengan data yang user ketik sebelum validasi gagal. Tanpa ini, user harus mengetik ulang semuanya dan pasti kesal.
2. **`@error('name')`** — blok ini hanya tampil kalau field `name` gagal validasi. Variabel `$message` berisi pesan error-nya.

Kalau mau menampilkan semua error sekaligus di atas form:

```blade
@if ($errors->any())
    <div class="alert">
        <ul>
            @foreach ($errors->all() as $error)
                <li>{{ $error }}</li>
            @endforeach
        </ul>
    </div>
@endif
```

## Pesan Error Bahasa Indonesia

Secara default pesan error Laravel berbahasa Inggris: *"The email field is required."* Untuk aplikasi berbahasa Indonesia, ada dua cara mengubahnya.

### Cara 1: Pesan Custom per Validasi (Cepat)

Kirim array pesan sebagai argumen ketiga `validate()`:

```php
$request->validate(
    [
        'email'    => 'required|email|unique:users,email',
        'password' => 'required|min:8|confirmed',
    ],
    [
        'email.required'    => 'Email wajib diisi.',
        'email.email'       => 'Format email tidak valid.',
        'email.unique'      => 'Email ini sudah terdaftar, silakan login.',
        'password.required' => 'Password wajib diisi.',
        'password.min'      => 'Password minimal :min karakter.',
        'password.confirmed'=> 'Konfirmasi password tidak cocok.',
    ]
);
```

Format kuncinya `nama_field.nama_aturan`. Placeholder seperti `:min` dan `:attribute` otomatis diganti Laravel dengan nilai sebenarnya.

Cara ini cocok kalau aplikasimu kecil atau hanya punya satu-dua form. Kalau form-nya banyak, menulis pesan custom di setiap controller cepat jadi repetitif.

### Cara 2: File Bahasa Global (Rapi, Sekali Setting)

Buat file `lang/id/validation.php` berisi terjemahan aturan validasi:

```php
<?php
// lang/id/validation.php

return [
    'required' => ':attribute wajib diisi.',
    'email'    => ':attribute harus berupa alamat email yang valid.',
    'unique'   => ':attribute sudah digunakan.',
    'min'      => [
        'string' => ':attribute minimal :min karakter.',
    ],
    'max'      => [
        'string' => ':attribute maksimal :max karakter.',
    ],
    'confirmed' => 'Konfirmasi :attribute tidak cocok.',

    'attributes' => [
        'name'     => 'nama',
        'email'    => 'email',
        'password' => 'kata sandi',
    ],
];
```

Lalu ubah locale aplikasi di `config/app.php`:

```php
'locale' => 'id',
'fallback_locale' => 'en',
```

Sejak itu, semua pesan validasi di seluruh aplikasi otomatis berbahasa Indonesia. Bagian `attributes` mengubah nama field teknis (`password`) menjadi nama yang ramah (`kata sandi`), sehingga pesannya terbaca natural: *"Kata sandi minimal 8 karakter."* bukan *"The password must be at least 8 characters."*

Kamu tidak perlu menerjemahkan semua aturan sekaligus — cukup yang aplikasimu pakai. Yang belum diterjemahkan akan jatuh ke `fallback_locale` (Inggris), jadi tidak ada yang rusak.

## Naik Level: Form Request

Kalau satu form punya belasan field, controller jadi penuh dengan aturan validasi. Solusinya: pindahkan ke class tersendiri.

```bash
php artisan make:request StoreProductRequest
```

```php
<?php
// app/Http/Requests/StoreProductRequest.php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreProductRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true; // ubah sesuai kebutuhan, misal: auth()->user()->is_admin
    }

    public function rules(): array
    {
        return [
            'nama'      => 'required|string|max:255',
            'harga'     => 'required|numeric|min:0',
            'stok'      => 'required|integer|min:0',
            'kategori'  => 'required|in:elektronik,fashion,makanan',
            'foto'      => 'nullable|image|mimes:jpg,png|max:2048',
        ];
    }

    public function messages(): array
    {
        return [
            'nama.required'  => 'Nama produk wajib diisi.',
            'harga.numeric'  => 'Harga harus berupa angka.',
            'foto.max'       => 'Ukuran foto maksimal 2 MB.',
        ];
    }
}
```

Controller-nya jadi bersih:

```php
public function store(StoreProductRequest $request)
{
    // Kalau sampai sini, data SUDAH lolos validasi.
    Product::create($request->validated());

    return redirect('/produk');
}
```

Validasi berjalan otomatis sebelum method controller dieksekusi. `$request->validated()` hanya mengembalikan field yang ada aturannya — field asing yang dikirim user nakal otomatis dibuang. Bonus: `authorize()` memberi tempat resmi untuk cek izin akses.

## Kesalahan Umum Pemula

**1. Lupa `@csrf` di form.** Tanpa token CSRF, Laravel menolak POST dengan error 419. Setiap form POST wajib ada `@csrf` — ini bukan bagian validasi, tapi error yang paling sering dikira masalah validasi.

**2. Validasi dijalankan setelah data disimpan.** Urutannya harus: validasi dulu, baru simpan. `$request->validate()` melempar exception saat gagal, jadi kode setelahnya tidak jalan — itu memang desainnya. Jangan dibalik.

**3. Aturan `unique` gagal saat update data.** Ini jebakan klasik:

```php
// SALAH saat update: email user sendiri dianggap "sudah dipakai"
'email' => 'required|email|unique:users,email',
```

Solusinya, kecualikan baris yang sedang diupdate:

```php
use Illuminate\Validation\Rule;

'email' => [
    'required',
    'email',
    Rule::unique('users')->ignore($user->id),
],
```

**4. Mengandalkan validasi JavaScript saja.** Validasi di browser itu untuk UX, bukan keamanan — user bisa mematikannya atau mengirim request langsung via curl/Postman. Validasi server-side di Laravel hukumnya wajib.

**5. Tidak memakai `old()` sehingga input hilang.** User mengisi 10 field, satu gagal, semua hilang. Mereka tidak akan mengisi ulang — mereka akan pergi.

## Langkah Praktis: Coba Sekarang

1. Buat route dan form registrasi sederhana dengan field nama, email, password, dan konfirmasi password.
2. Tambahkan `$request->validate()` dengan aturan `required`, `email`, `unique`, `min:8`, dan `confirmed`.
3. Tampilkan error dengan `@error` dan kembalikan input dengan `old()`. Sengaja kirim form kosong dan lihat pesannya.
4. Tambahkan pesan custom Bahasa Indonesia, lalu upgrade ke file `lang/id/validation.php` + locale `id`.
5. Refactor ke Form Request dan rasakan controller-mu jadi jauh lebih bersih.

Validasi yang baik itu tidak terasa oleh user yang mengisi dengan benar, tapi sangat membantu user yang salah — pesan yang jelas dalam bahasa mereka sendiri adalah perbedaan antara form yang dipakai dan form yang ditinggalkan.
