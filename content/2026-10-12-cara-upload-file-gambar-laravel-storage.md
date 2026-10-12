---
title: Cara Upload File dan Gambar di Laravel: Panduan Lengkap
description: Bingung upload file di Laravel? Panduan lengkap storage, symlink, validasi, dan contoh kode nyata. Dari form HTML sampai file tampil di browser.
date: 2026-10-12
tags: [laravel, php, upload-file, storage]
faq:
  - Kenapa gambar yang diupload Laravel tidak bisa tampil (error 404)?
  - Penyebab paling umum adalah symlink public/storage belum dibuat. Jalankan php artisan storage:link. File upload tersimpan di storage/app/public, dan symlink itulah yang membuatnya bisa diakses lewat URL /storage/.
  - Di mana Laravel menyimpan file yang diupload?
  - Secara default ke storage/app/public bila kamu memakai disk public. Folder storage tidak bisa diakses dari browser, jadi Laravel menyediakan symlink public/storage agar file bisa diakses publik tanpa memindahkan file fisik.
  - Bagaimana cara membatasi tipe dan ukuran file upload di Laravel?
  - Pakai validasi di controller, contohnya: 'avatar' => 'required|image|mimes:jpeg,png,webp|max:2048'. Rule image memastikan file benar-benar gambar, mimes membatasi ekstensi, dan max:2048 membatasi ukuran maksimal 2 MB karena satuannya kilobyte.
  - Bagaimana cara menghapus file lama saat user upload file baru?
  - Sebelum menyimpan file baru, hapus yang lama dengan Storage::disk('public')->delete($pathLama). Cek dulu path-nya tidak null agar tidak error.
---

Hampir semua aplikasi web butuh fitur upload: foto profil, lampiran dokumen, gambar produk. Di Laravel, fitur ini gampang setelah kamu paham satu konsep kunci: **filesystem disks**. Tapi sebelum paham, konsep ini justru sumber kebingungan nomor satu pemula: file berhasil diupload tapi tidak tampil di browser.

Artikel ini saya tulis dari pengalaman memasang fitur upload di banyak project. Ikuti urutannya, dan di akhir kamu bisa upload, validasi, tampilkan, sampai hapus file dengan benar.

## Konsep Dasar: Kenapa Ada Folder storage dan public

Struktur Laravel memisahkan dua hal:

**Folder `storage/`** adalah tempat file disimpan secara fisik. Folder ini tidak bisa diakses langsung dari browser, dan itu disengaja demi keamanan.

**Folder `public/`** adalah satu-satunya folder yang bisa diakses browser. Semua request ke `domainkamu.com/apa-pun` dipetakan ke folder ini.

Masalahnya: file upload disimpan di `storage/app/public`, tapi browser cuma bisa baca dari `public/`. Solusi Laravel: **symbolic link** (symlink). Perintah `php artisan storage:link` membuat link `public/storage` yang menunjuk ke `storage/app/public`. Jadi file yang kamu simpan di disk `public` otomatis bisa diakses lewat URL `/storage/nama-file.jpg`.

Konsep disks di `config/filesystems.php` mengatur ini. Disk `public` memakai driver `local` dengan root `storage/app/public` dan url `/storage`. Saat kamu menulis `->store('avatars', 'public')`, artinya: simpan ke folder `avatars` di dalam disk `public`.

## Langkah 1: Buat Form Upload

Satu atribut yang wajib dan paling sering dilupakan: `enctype="multipart/form-data"`. Tanpa ini, file tidak ikut terkirim dan `$request->file('avatar')` akan bernilai null.

```blade
<form action="/profile/avatar" method="POST" enctype="multipart/form-data">
    @csrf
    <label for="avatar">Foto Profil</label>
    <input type="file" id="avatar" name="avatar" accept="image/*">
    <button type="submit">Upload</button>
</form>
```

Atribut `accept="image/*"` hanya filter di dialog file browser, bukan keamanan. Validasi sesungguhnya tetap di server.

## Langkah 2: Terima dan Simpan di Controller

Route-nya:

```php
// routes/web.php
use App\Http\Controllers\ProfileController;

Route::post('/profile/avatar', [ProfileController::class, 'updateAvatar'])
    ->middleware('auth');
```

Controller-nya:

```php
// app/Http/Controllers/ProfileController.php
namespace App\Http\Controllers;

use Illuminate\Http\Request;

class ProfileController extends Controller
{
    public function updateAvatar(Request $request)
    {
        $validated = $request->validate([
            'avatar' => 'required|image|mimes:jpeg,png,jpg,webp|max:2048',
        ]);

        // Simpan ke storage/app/public/avatars dengan nama file acak yang unik
        $path = $request->file('avatar')->store('avatars', 'public');

        // $path berisi misalnya: "avatars/aB3dE9fGh2jkLmNoP.jpg"
        $request->user()->update(['avatar_path' => $path]);

        return back()->with('success', 'Foto profil berhasil diupload.');
    }
}
```

Method `store()` melakukan tiga hal sekaligus: membuat nama file unik (hash acak, jadi tidak ada tabrakan nama), memindahkan file ke disk yang diminta, dan mengembalikan path relatifnya. Path inilah yang kamu simpan di database, bukan file-nya.

Kalau kamu butuh nama file sendiri, pakai `storeAs()`:

```php
$filename = 'avatar-' . $request->user()->id . '.' . $request->file('avatar')->extension();
$path = $request->file('avatar')->storeAs('avatars', $filename, 'public');
```

## Langkah 3: Jalankan Symlink Sekali Saja

```bash
php artisan storage:link
```

Perintah ini membuat `public/storage` sebagai symlink ke `storage/app/public`. Jalankan sekali per environment (lokal, staging, production). Kalau kamu deploy ke VPS dan gambar tidak tampil padahal upload sukses, 90 persen kasus penyebabnya adalah perintah ini belum dijalankan di server.

## Langkah 4: Tampilkan File di Browser

Karena symlink sudah ada, file di `storage/app/public/avatars/xxx.jpg` bisa diakses lewat URL `/storage/avatars/xxx.jpg`. Di Blade:

```blade
@if ($user->avatar_path)
    <img src="{{ asset('storage/' . $user->avatar_path) }}" alt="Foto profil">
@endif
```

Atau pakai helper Storage yang lebih eksplisit:

```blade
<img src="{{ Storage::url($user->avatar_path) }}" alt="Foto profil">
```

Keduanya menghasilkan URL yang sama selama disk yang dipakai adalah `public`.

## Upload Banyak File Sekaligus

Untuk galeri atau lampiran jamak, tambahkan `multiple` di input dan tangkap sebagai array:

```blade
<input type="file" name="photos[]" multiple accept="image/*">
```

```php
$request->validate([
    'photos'   => 'required|array|max:5',
    'photos.*' => 'image|mimes:jpeg,png,webp|max:2048',
]);

$paths = [];
foreach ($request->file('photos') as $photo) {
    $paths[] = $photo->store('gallery', 'public');
}
// simpan $paths (misalnya sebagai JSON) ke database
```

Notasi `photos.*` artinya validasi berlaku untuk setiap file di dalam array. Ini pola yang rapi dan jarang diketahui pemula.

## Menghapus File Lama Saat Update

Kesalahan klasik: user ganti foto profil, file lama tetap menumpuk di storage sampai disk penuh. Pola yang benar:

```php
use Illuminate\Support\Facades\Storage;

public function updateAvatar(Request $request)
{
    $request->validate([
        'avatar' => 'required|image|mimes:jpeg,png,jpg,webp|max:2048',
    ]);

    $user = $request->user();

    // Hapus file lama dulu kalau ada
    if ($user->avatar_path) {
        Storage::disk('public')->delete($user->avatar_path);
    }

    $user->update([
        'avatar_path' => $request->file('avatar')->store('avatars', 'public'),
    ]);

    return back()->with('success', 'Foto profil berhasil diperbarui.');
}
```

Catatan: `Storage::delete()` tidak error kalau file-nya sudah tidak ada, jadi aman dipanggil tanpa cek `exists()` dulu. Tapi cek `$user->avatar_path` tetap perlu supaya tidak menghapus dengan path null.

## Kesalahan Umum Pemula (dan Cara Menghindarinya)

**1. Lupa `enctype="multipart/form-data"`.** Gejalanya: validasi selalu gagal dengan pesan field wajib diisi padahal file sudah dipilih. Selalu cek atribut form dulu sebelum menyalahkan controller.

**2. Belum menjalankan `storage:link`.** Upload sukses, data tersimpan, tapi gambar 404 di browser. Jalankan perintahnya di setiap server tempat aplikasi berjalan.

**3. Tidak ada validasi sama sekali.** Ini yang paling berbahaya. Tanpa validasi, orang bisa mengupload file `.php` berisi script jahat. Minimal selalu pakai rule `image` atau `mimes` plus batas `max`. Jangan pernah percaya ekstensi file dari nama aslinya saja.

**4. Salah paham satuan `max`.** Rule `max:2048` artinya 2048 kilobyte, yaitu 2 MB, bukan 2048 MB. Kalau user butuh upload sampai 10 MB, tulis `max:10240`.

**5. Limit PHP lebih kecil dari validasi.** Laravel tidak bisa menerima file yang ditolak PHP duluan. Cek `upload_max_filesize` dan `post_max_size` di `php.ini`. Kalau validasi mengizinkan 10 MB tapi `upload_max_filesize = 2M`, file besar akan gagal sebelum sampai ke Laravel.

**6. Menyimpan file langsung ke folder `public/`.** Bisa, tapi kamu kehilangan semua kemudahan disk: nama unik otomatis, ganti driver ke S3 suatu hari tanpa ubah kode, dan pemisahan file publik vs privat. Pakai Storage API kecuali ada alasan kuat.

**7. Menyimpan path absolut di database.** Simpan path relatif seperti `avatars/xxx.jpg`, bukan `/var/www/...` atau URL lengkap. Path absolut akan rusak saat pindah server, sedangkan path relatif tetap valid selama disk-nya sama.

## Batasan Ukuran di php.ini

Kalau upload file besar selalu gagal tanpa pesan error yang jelas, hampir pasti ini penyebabnya. Buka `php.ini` yang dipakai web server dan sesuaikan:

```ini
upload_max_filesize = 10M
post_max_size = 12M
```

`post_max_size` harus sedikit lebih besar dari `upload_max_filesize` karena mencakup seluruh body request, bukan cuma file-nya. Setelah diubah, restart PHP-FPM atau web server kamu.

## Langkah Praktis yang Bisa Dicoba Hari Ini

1. Di project Laravel kamu, buat form upload sederhana dengan `enctype` yang benar dan satu route POST.
2. Tulis controller dengan validasi `image|mimes:jpeg,png,webp|max:2048`, simpan dengan `store('coba', 'public')`, dan dump path yang dikembalikan untuk melihat formatnya.
3. Jalankan `php artisan storage:link`, lalu buka URL `/storage/coba/nama-file.jpg` di browser untuk membuktikan symlink bekerja.
4. Tambahkan logika hapus file lama, lalu uji dua kali upload beruntun dan pastikan hanya satu file yang tersisa di folder storage.
5. Coba upload file `.php` yang diganti ekstensinya jadi `.jpg` (isi script PHP) dan lihat validasi `image` menolaknya. Ini bukti kenapa validasi server tidak bisa ditawar.

## Kesimpulan Singkat

Alur upload file di Laravel selalu sama: form dengan `enctype`, validasi ketat di controller, simpan lewat `store()` ke disk `public`, simpan path relatif di database, tampilkan lewat `/storage/...` setelah `storage:link` dijalankan, dan hapus file lama saat ada pengganti.

Kuasai pola ini sekali, dan kamu bisa menerapkannya ke semua variasi: foto profil, galeri produk, lampiran dokumen, sampai upload ke S3 nanti. Yang berubah cuma konfigurasi disk-nya, kodenya tetap sama. Itu alasan kenapa Laravel memisahkan konsep disk dari awal: supaya kode upload kamu tidak perlu ditulis ulang saat infrastruktur berganti.
