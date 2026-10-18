---
title: Kirim Email di Laravel: Mailtrap, SMTP Gmail & Queue
description: Pelajari cara kirim email di Laravel: setup Mailtrap untuk testing, bikin Mailable, konfigurasi SMTP Gmail production, dan hindari kesalahan umum pemula.
date: 2026-10-18
tags: [laravel, php, email, smtp]
faq:
  - Kenapa email Laravel-ku tidak terkirim tapi tidak ada error?
  - Penyebab paling umum adalah cache config yang basi. Jalankan php artisan config:clear setelah mengubah file .env, lalu pastikan MAIL_MAILER dan credential SMTP terisi dengan benar.
  - Apa itu Mailtrap dan kenapa dipakai untuk testing?
  - Mailtrap adalah inbox SMTP palsu untuk development. Semua email dari aplikasi ditangkap di dashboard Mailtrap, bukan dikirim ke alamat asli. Kamu bisa cek tampilan template dan attachment tanpa risiko mengirim spam ke pengguna nyata.
  - Bagaimana cara kirim email via SMTP Gmail di Laravel?
  - Aktifkan 2FA di akun Google, buat App Password 16 karakter, lalu isi .env dengan MAIL_MAILER=smtp, MAIL_HOST=smtp.gmail.com, MAIL_PORT=587, MAIL_USERNAME=alamat Gmail-mu, MAIL_PASSWORD=app password tersebut, dan MAIL_ENCRYPTION=tls.
  - Apakah perlu queue untuk kirim email di production?
  - Ya. Handshake SMTP makan waktu 1 sampai 3 detik per email, dan kalau dikirim sinkron di dalam HTTP request, halaman jadi lemot. Implementasikan ShouldQueue di Mailable agar email dikirim di background oleh queue worker.
---

Hampir semua aplikasi web pada akhirnya harus mengirim email: verifikasi akun, reset password, invoice, notifikasi order masuk. Kabar baiknya, Laravel punya sistem mail yang lengkap dan enak dipakai. Kabar buruknya, pemula sering stuck di hal sepele seperti credential SMTP yang tidak kebaca atau email yang terkirim tapi tidak sampai. Artikel ini membahas alur yang benar dari testing sampai production, dengan contoh kode yang benar-benar bisa dijalankan.

## Cara Kerja Mail di Laravel

Ada tiga komponen inti yang perlu kamu kenal:

- **Mailer**: mesin pengirim. Diatur lewat `MAIL_MAILER` di `.env`. Nilainya bisa `smtp` untuk pengiriman nyata, `log` untuk sekadar dicatat di `storage/logs/laravel.log`, atau `array` untuk ditangkap saat testing otomatis.
- **Mailable**: class PHP yang merepresentasikan satu jenis email. Di sinilah kamu menentukan subject, template Blade, attachment, dan data yang dikirim ke view.
- **Notification**: alternatif untuk pesan pendek yang bisa dikirim lewat banyak channel (email, database, Slack). Untuk email transaksional yang butuh template rapi, Mailable biasanya lebih cocok.

## Langkah 1: Testing Aman dengan Mailtrap

Jangan pernah testing kirim email pakai alamat asli. Gunakan Mailtrap, layanan inbox SMTP palsu khusus development.

1. Daftar di mailtrap.io dan buka halaman **Email Testing**.
2. Salin credential SMTP yang disediakan.
3. Tempel ke `.env` Laravel-mu:

```env
MAIL_MAILER=smtp
MAIL_HOST=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=salin_dari_dashboard_mailtrap
MAIL_PASSWORD=salin_dari_dashboard_mailtrap
MAIL_ENCRYPTION=tls
MAIL_FROM_ADDRESS="noreply@aplikasimu.com"
MAIL_FROM_NAME="Aplikasiku"
```

Setiap kali mengubah `.env`, jalankan:

```bash
php artisan config:clear
```

Ini langkah yang paling sering dilupakan pemula. Laravel men-cache config, jadi perubahan `.env` tidak terbaca sampai cache dibersihkan.

## Langkah 2: Bikin Mailable Pertama

Buat class Mailable dengan artisan:

```bash
php artisan make:mail WelcomeMail
```

File-nya muncul di `app/Mail/WelcomeMail.php`. Isi seperti ini:

```php
<?php

namespace App\Mail;

use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class WelcomeMail extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(
        public string $namaPengguna,
    ) {}

    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Selamat datang di Aplikasiku',
        );
    }

    public function content(): Content
    {
        return new Content(
            view: 'emails.welcome',
        );
    }
}
```

Hal penting di sini: property `public` di constructor otomatis tersedia di view Blade. Kamu tidak perlu mengoper data secara manual.

Sekarang buat template-nya di `resources/views/emails/welcome.blade.php`:

```blade
<h1>Halo, {{ $namaPengguna }}!</h1>

<p>Akunmu berhasil dibuat. Kamu bisa mulai memakai aplikasi sekarang.</p>

<p>Butuh bantuan? Balas email ini, tim kami akan membantu.</p>
```

Sintaks `{{ }}` di atas adalah Blade, template engine Laravel, bukan placeholder yang harus kamu ganti.

## Langkah 3: Kirim dari Route atau Controller

Cara paling sederhana untuk mengetes:

```php
use App\Mail\WelcomeMail;
use Illuminate\Support\Facades\Mail;

Route::get('/test-email', function () {
    Mail::to('user@example.com')->send(new WelcomeMail('Dipa'));

    return 'Email dikirim, cek dashboard Mailtrap!';
});
```

Buka URL tersebut di browser, lalu buka dashboard Mailtrap. Email harus muncul di sana dalam beberapa detik. Kalau butuh CC, BCC, atau attachment:

```php
Mail::to('user@example.com')
    ->cc('tim@example.com')
    ->bcc('arsip@example.com')
    ->send(new WelcomeMail('Dipa'));
```

Attachment ditambahkan di dalam class Mailable lewat method `attachments()`:

```php
use Illuminate\Mail\Mailables\Attachment;

public function attachments(): array
{
    return [
        Attachment::fromPath(storage_path('app/invoice/invoice-123.pdf'))
            ->as('invoice-123.pdf'),
    ];
}
```

## Langkah 4: Production dengan SMTP Gmail

Mailtrap hanya untuk development. Untuk production, opsi gratis termudah adalah SMTP Gmail. Tapi ada satu syarat penting: **kamu tidak bisa pakai password Gmail biasa**. Google sudah lama mematikan opsi "less secure apps", jadi login dengan password biasa selalu gagal.

Langkahnya:

1. Aktifkan **2-Step Verification** di akun Google.
2. Buka pengaturan akun, cari **App Passwords**, buat satu password baru untuk aplikasi "Mail". Google memberikan password 16 karakter.
3. Update `.env`:

```env
MAIL_MAILER=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=akun@gmail.com
MAIL_PASSWORD=xxxx_xxxx_xxxx_xxxx
MAIL_ENCRYPTION=tls
```

Lalu `php artisan config:clear` lagi. Catatan jujur: Gmail gratis punya limit harian sekitar 500 email per hari. Untuk skala kecil seperti notifikasi admin atau verifikasi user, ini cukup. Kalau aplikasimu mengirim ribuan email, pindah ke layanan khusus seperti Amazon SES, Mailgun, atau Resend.

## Langkah 5: Jangan Kirim Sinkron, Pakai Queue

Ini perbedaan antara aplikasi yang terasa cepat dan yang lemot. Setiap pengiriman SMTP butuh handshake ke server mail, biasanya 1 sampai 3 detik. Kalau kamu memanggil `->send()` di dalam HTTP request, user menunggu selama itu. Kalau email-nya lima, user menunggu 15 detik. Solusinya: queue.

Ubah Mailable agar bisa di-queue:

```php
use Illuminate\Contracts\Queue\ShouldQueue;

class WelcomeMail extends Mailable implements ShouldQueue
{
    // ... sisanya sama
}
```

Lalu setup queue database:

```bash
php artisan queue:table
php artisan migrate
```

Di `.env`, pastikan:

```env
QUEUE_CONNECTION=database
```

Cara mengirimnya berubah dari `send()` menjadi `queue()`:

```php
Mail::to('user@example.com')->queue(new WelcomeMail('Dipa'));
```

Perintah ini hanya memasukkan job ke tabel `jobs`, selesai dalam milidetik. Worker yang jalan di background yang akan benar-benar mengirim emailnya:

```bash
php artisan queue:work
```

Untuk server production, jalankan worker ini lewat Supervisor atau systemd agar selalu hidup dan otomatis restart kalau mati. Job yang gagal akan tercatat di tabel `failed_jobs`, jadi kamu bisa investigasi dan retry dengan `php artisan queue:retry all`.

**Bonus untuk automated test:** kamu tidak perlu Mailtrap sama sekali saat menulis test. Set `MAIL_MAILER=array` di `.env.testing`, lalu assert dengan `Mail::assertSent(WelcomeMail::class)`. Email yang "dikirim" hanya disimpan di memori dan hilang setelah test selesai, jadi test cepat, deterministik, dan aman dijalankan di CI/CD yang biasanya memblokir akses SMTP eksternal.

## Kesalahan Umum Pemula dan Cara Menghindarinya

**1. Lupa `config:clear` setelah ubah `.env`.**
Gejalanya: email tetap tidak terkirim padahal credential sudah benar. Biasakan menjalankan `php artisan config:clear` setiap kali menyentuh `.env`.

**2. Pakai password Gmail biasa.**
Google menolak login dan Laravel melempar error authentication. Solusinya selalu App Password dengan 2FA aktif, seperti di Langkah 4.

**3. Kirim email sinkron di production.**
Halaman register yang tadinya 200ms jadi 4 detik. Implementasikan `ShouldQueue` dan jalankan queue worker. Ini satu perubahan kecil dengan dampak besar.

**4. Tidak set `MAIL_FROM_ADDRESS`.**
Email dari alamat kosong atau `hello@example.com` gampang dianggap spam oleh Gmail. Isi `MAIL_FROM_ADDRESS` dan `MAIL_FROM_NAME` dengan identitas aplikasimu yang sebenarnya.

**5. Ngetes pakai alamat email asli.**
Risikonya: template rusak terkirim ke user beneran, atau akun SMTP-mu kena rate limit. Selalu pakai Mailtrap (atau `MAIL_MAILER=log`) selama development.

## Langkah Praktis yang Bisa Langsung Dicoba Hari Ini

1. Daftar Mailtrap dan pasang credential SMTP di `.env` project Laravel-mu.
2. Buat satu Mailable, misalnya `OrderConfirmation`, lengkap dengan view Blade-nya.
3. Kirim satu email test lewat route sementara, verifikasi tampilannya di dashboard Mailtrap.
4. Tambahkan `implements ShouldQueue` ke Mailable tersebut, ganti `send()` jadi `queue()`, dan jalankan `php artisan queue:work` untuk melihat job dieksekusi.

Kalau keempat langkah itu berhasil, kamu sudah menguasai 90 persen kebutuhan email di aplikasi Laravel: testing aman, template rapi, SMTP production, dan pengiriman background yang tidak memperlambat aplikasi.
