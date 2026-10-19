---
title: Laravel Queue dan Jobs: Kirim Email Tanpa Bikin Web Lemot
description: Pelajari cara kerja Laravel Queue dan Jobs: kirim email, notifikasi, dan proses berat di background agar aplikasi tetap cepat. Contoh kode lengkap untuk pemula.
date: 2026-10-19
tags: [laravel, php, queue, jobs]
faq:
  - Apa itu queue di Laravel dan kenapa harus dipakai?
  - Queue adalah antrean pekerjaan yang dijalankan di background, di luar HTTP request. Tanpa queue, tugas berat seperti kirim email atau resize gambar membuat user menunggu loading lama. Dengan queue, request langsung selesai dan pekerjaan berat dikerjakan oleh worker di belakang layar.
  - Apa bedanya queue:work dan queue:listen di Laravel?
  - queue:work menjalankan worker satu proses yang terus memproses job tanpa restart, lebih cepat dan hemat resource. queue:listen restart aplikasi tiap job, berguna kalau kamu sering mengubah kode dan tidak mau restart manual, tapi lebih lambat. Di production, pakai queue:work dengan Supervisor.
  - Kenapa job saya tidak jalan setelah di-dispatch?
  - Tiga penyebab paling umum: pertama, queue worker belum dijalankan, jadi jalankan php artisan queue:work. Kedua, config cache basi setelah mengubah .env, jalankan php artisan config:clear. Ketiga, QUEUE_CONNECTION masih sync sehingga job dieksekusi langsung dan errornya tertelan di request.
  - Bagaimana cara menjalankan queue worker di production dengan aman?
  - Gunakan Supervisor untuk menjaga proses queue:work tetap hidup dan otomatis restart kalau crash. Jangan lupa jalankan php artisan queue:restart setiap deploy kode baru agar worker memuat kode terbaru. Pisahkan juga antrean dengan nama queue berbeda untuk job penting dan job berat.
---

Pernah buka halaman web yang loading-nya lama banget padahal cuma daftar akun? Penyebab klasiknya: server kirim email verifikasi dulu, baru halaman selesai dimuat. Handshake SMTP itu makan waktu 1 sampai 3 detik. Kalau dikirim sinkron di dalam HTTP request, semua user harus menunggu. Solusinya di Laravel: Queue dan Jobs.

Queue memindahkan pekerjaan berat keluar dari HTTP request. Controller-mu selesai dalam hitungan milidetik, sementara kirim email, resize gambar, atau hit API pihak ketiga dikerjakan di background oleh queue worker. Artikel ini membahas setup lengkapnya dari nol, dengan contoh kode yang bisa langsung dijalankan.

## Masalahnya: Tugas Berat di Dalam Request

Bayangkan alur registrasi tanpa queue:

```php
public function register(Request $request)
{
    $user = User::create($request->validated());

    // Ini makan 2 detik. User menunggu.
    Mail::to($user->email)->send(new WelcomeEmail($user));

    // Ini makan 3 detik. User masih menunggu.
    $this->notifyAdminOnSlack($user);

    return redirect('/dashboard');
}
```

Total tambahan 5 detik hanya untuk menunggu pekerjaan yang tidak ada hubungannya dengan halaman yang diminta. Di traffic tinggi, PHP-FPM worker habis dipakai menunggu SMTP, dan seluruh aplikasi ikut melambat. Dengan queue, alurnya berubah: controller hanya memasukkan pekerjaan ke antrean, lalu selesai. Worker memprosesnya nanti.

## Cara Kerja Queue di Laravel

Konsepnya sederhana, tiga komponen:

- **Job**: class PHP berisi pekerjaan yang harus dilakukan, misalnya `SendWelcomeEmail`.
- **Queue (antrean)**: tempat job menunggu giliran. Bisa berupa tabel database, Redis, atau layanan seperti Amazon SQS.
- **Worker**: proses background yang terus mengambil job dari antrean dan menjalankannya satu per satu.

Alurnya: HTTP request dispatch job ke antrean, response langsung kembali ke user, worker di background mengambil job dan mengeksekusi. Kalau job gagal, Laravel bisa retry otomatis dan mencatatnya di tabel failed jobs.

## Langkah 1: Setup Driver Queue

Untuk development, driver `database` paling gampang karena tidak butuh Redis. Cek `.env`:

```env
QUEUE_CONNECTION=database
```

Lalu buat tabel antrean dan migrate:

```bash
php artisan queue:table
php artisan migrate
```

Perintah pertama membuat migration untuk tabel `jobs`, `job_batches`, dan `failed_jobs`. Perintah kedua menjalankannya. Kalau project-mu sudah besar dan traffic tinggi, pindah ke `redis` nanti. Untuk belajar, database cukup.

Satu jebakan klasik: setelah mengubah `.env`, jalankan ini kalau config-mu pernah di-cache:

```bash
php artisan config:clear
```

## Langkah 2: Membuat Job

Generate class job dengan Artisan:

```bash
php artisan make:job SendWelcomeEmail
```

Isi file `app/Jobs/SendWelcomeEmail.php`:

```php
<?php

namespace App\Jobs;

use App\Mail\WelcomeEmail;
use App\Models\User;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Mail;

class SendWelcomeEmail implements ShouldQueue
{
    use Queueable;

    public function __construct(
        public User $user,
    ) {}

    public function handle(): void
    {
        Mail::to($this->user->email)->send(new WelcomeEmail($this->user));
    }
}
```

Kunci utamanya adalah interface `ShouldQueue`. Tanpa itu, job dijalankan langsung (sinkron) saat di-dispatch, dan kamu tidak dapat manfaat queue sama sekali. Constructor menerima data yang dibutuhkan job. Method `handle()` berisi pekerjaan sebenarnya.

Catatan penting soal model: trait `Queueable` otomatis memakai `SerializesModels`, jadi instance `User` tidak disimpan mentah di database antrean. Yang disimpan hanya class dan ID-nya. Saat worker menjalankan job, model diambil ulang dari database. Ini penting: kalau user dihapus sebelum job jalan, `$this->user` akan `null` di worker. Selalu cek null untuk model yang mungkin sudah tidak ada.

## Langkah 3: Dispatch Job dari Controller

Controller registrasi sekarang jadi ringan:

```php
use App\Jobs\SendWelcomeEmail;

public function register(Request $request)
{
    $user = User::create($request->validated());

    SendWelcomeEmail::dispatch($user);

    return redirect('/dashboard');
}
```

Satu baris, selesai dalam milidetik. Pekerjaan berat pindah ke background.

Beberapa varian dispatch yang sering dipakai:

```php
// Tunda eksekusi 10 menit dari sekarang
SendWelcomeEmail::dispatch($user)->delay(now()->addMinutes(10));

// Masukkan ke antrean bernama "emails", bukan default
SendWelcomeEmail::dispatch($user)->onQueue('emails');

// Kirim setelah response terkirim ke browser (masih di request yang sama,
// tapi tidak menunda halaman). Cocok untuk pekerjaan super cepat.
SendWelcomeEmail::dispatch($user)->afterResponse();
```

Perbedaan `afterResponse()` dan queue murni: `afterResponse()` tetap berjalan di proses PHP yang sama setelah response dikirim. Kalau prosesnya crash, pekerjaan hilang. Queue dengan worker terpisah jauh lebih aman untuk pekerjaan penting seperti email transaksional.

## Langkah 4: Menjalankan Worker

Tanpa worker, job hanya menumpuk di tabel `jobs` dan tidak pernah dieksekusi. Jalankan di terminal terpisah:

```bash
php artisan queue:work
```

Worker akan terus berjalan dan memproses job satu per satu. Coba daftar akun baru, lalu lihat: halaman dashboard langsung muncul, dan beberapa detik kemudian email terkirim.

Untuk development, ada flag yang berguna:

```bash
# Proses satu job lalu berhenti (enak untuk debugging)
php artisan queue:work --once

# Berhenti setelah 60 detik (mencegah memory leak di kode jelek)
php artisan queue:work --max-time=60

# Restart worker setelah 100 job
php artisan queue:work --max-jobs=100

# Hanya proses antrean "emails"
php artisan queue:work --queue=emails
```

Ingat: `queue:work` memuat kode aplikasimu sekali di awal, lalu mempertahankannya di memori. Setiap kamu mengubah kode job, restart worker secara manual, atau jalankan:

```bash
php artisan queue:restart
```

Perintah ini memberi sinyal ke semua worker yang berjalan agar berhenti dengan anggun setelah job saat ini selesai. Ini cara standar setiap deploy.

## Menangani Job yang Gagal

Job bisa gagal: SMTP down, API pihak ketiga timeout, atau bug di kode. Laravel punya mekanisme retry bawaan. Tambahkan properti ini di job:

```php
class SendWelcomeEmail implements ShouldQueue
{
    use Queueable;

    // Coba maksimal 3 kali
    public int $tries = 3;

    // Tunggu makin lama tiap percobaan: 10 detik, 60 detik, 300 detik
    public array $backoff = [10, 60, 300];

    // Timeout 120 detik per percobaan, jangan gantung selamanya
    public int $timeout = 120;

    public function handle(): void
    {
        // ...
    }

    // Dipanggil kalau semua percobaan gagal
    public function failed(\Throwable $exception): void
    {
        \Log::error('Gagal kirim welcome email', [
            'user_id' => $this->user->id,
            'error' => $exception->getMessage(),
        ]);
    }
}
```

Job yang gagal total tercatat di tabel `failed_jobs`. Kamu bisa melihat daftarnya dan mencoba ulang:

```bash
# Lihat job yang gagal
php artisan queue:failed

# Coba ulang satu job berdasarkan ID
php artisan queue:retry 5

# Coba ulang semuanya
php artisan queue:retry all

# Hapus yang memang tidak perlu dicoba lagi
php artisan queue:flush
```

## Contoh Nyata: Resize Gambar di Background

Queue bukan cuma untuk email. Contoh lain yang umum: user upload foto profil, dan kamu perlu membuat thumbnail. Tanpa queue, user menunggu proses resize. Dengan queue:

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Storage;
use Intervention\Image\ImageManager;

class GenerateThumbnail implements ShouldQueue
{
    use Queueable;

    public int $tries = 3;

    public function __construct(
        public string $path,
    ) {}

    public function handle(): void
    {
        if (! Storage::disk('public')->exists($this->path)) {
            return; // File sudah dihapus, skip saja
        }

        $manager = new ImageManager(new \Intervention\Image\Drivers\Gd\Driver());
        $image = $manager->read(Storage::disk('public')->path($this->path));
        $image->cover(300, 300);

        $thumbPath = 'thumbnails/' . basename($this->path);
        $image->save(Storage::disk('public')->path($thumbPath));
    }
}
```

Controller cukup simpan file asli lalu dispatch:

```php
$path = $request->file('avatar')->store('avatars', 'public');
GenerateThumbnail::dispatch($path);

return back()->with('success', 'Foto berhasil diupload!');
```

User langsung dapat response sukses. Thumbnail muncul beberapa detik kemudian. Pengalaman seperti ini yang membedakan aplikasi yang terasa cepat dan yang tidak.

## Kesalahan Umum Pemula

**1. Lupa menjalankan worker di production.** Job menumpuk di tabel `jobs` selamanya. Di production, worker harus jalan sebagai daemon yang diawasi Supervisor, bukan `queue:work` manual di terminal yang mati saat SSH disconnect.

**2. Tidak restart worker setelah deploy.** Worker memegang kode lama di memori. Bug yang sudah kamu fix di job tetap muncul di production. Selalu jalankan `php artisan queue:restart` di script deploy.

**3. Mengirim model besar atau resource ke job.** Constructor job di-serialize ke database. Jangan kirim instance `UploadedFile`, koneksi database, atau HTTP client. Kirim ID atau path string saja, lalu ambil ulang di `handle()`.

**4. Job tanpa timeout dan retry.** Satu job yang hang karena API tidak merespons bisa memblokir seluruh antrean. Selalu set `$timeout` dan `$tries` yang masuk akal.

**5. Query N+1 di dalam job.** Karena job jalan di background tanpa user menunggu, developer sering malas mengoptimasi. Tapi 10.000 job yang masing-masing query N+1 tetap membunuh database. Pakai eager loading seperti biasa.

**6. Pakai driver `sync` di production.** `QUEUE_CONNECTION=sync` membuat job jalan langsung di request. Itu default yang nyaman untuk testing, tapi di production artinya kamu tidak pakai queue sama sekali. Pastikan `.env` production memakai `database` atau `redis`.

## Menjalankan Worker di Production

Contoh config Supervisor minimal (`/etc/supervisor/conf.d/laravel-worker.conf`):

```ini
[program:laravel-worker]
process_name=%(program_name)s_%(process_num)02d
command=php /var/www/aplikasi-mu/artisan queue:work --sleep=3 --tries=3 --max-time=3600
autostart=true
autorestart=true
numprocs=2
user=www-data
redirect_stderr=true
stdout_logfile=/var/www/aplikasi-mu/storage/logs/worker.log
stopwaitsecs=3600
```

Jalankan `sudo supervisorctl reread && sudo supervisorctl update` untuk menerapkan. Supervisor memastikan dua worker selalu hidup dan restart otomatis kalau crash. Pisahkan antrean kalau perlu: satu worker khusus `emails`, satu untuk `default`, supaya email penting tidak antre di belakang job berat.

## Langkah Praktis Hari Ini

1. Di project Laravel-mu, set `QUEUE_CONNECTION=database`, jalankan `php artisan queue:table && php artisan migrate`.
2. Buat satu job nyata: pindahkan kirim email atau notifikasi yang sekarang ada di controller ke dalam job.
3. Jalankan `php artisan queue:work` di terminal kedua, lalu uji alurnya end to end.
4. Sengaja gagalkan satu job (misalnya matikan koneksi SMTP) dan lihat perilakunya di `php artisan queue:failed`. Coba `queue:retry`.
5. Kalau sudah nyaman, pelajari Redis sebagai driver queue untuk performa lebih tinggi.

Queue adalah salah satu fitur yang paling underrated di Laravel. Sekali kamu terbiasa memindahkan pekerjaan berat ke background, hampir tidak ada alasan untuk kembali membuat user menunggu loading yang tidak perlu.
