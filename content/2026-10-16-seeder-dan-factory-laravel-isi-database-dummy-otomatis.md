---
title: Seeder dan Factory Laravel: Isi Database Dummy Otomatis
description: Pelajari seeder dan factory Laravel untuk isi database dummy otomatis. Contoh kode nyata, faker Indonesia, kesalahan umum pemula, dan langkah praktis.
date: 2026-10-16
tags: [laravel, php, database, faker]
faq:
  - Apa beda seeder dan factory di Laravel?
  - Factory adalah blueprint yang menjelaskan bentuk satu baris data dan dari mana nilai tiap kolom diambil (biasanya dari Faker). Seeder adalah class yang menjalankan pembuatan data: data apa yang dibuat, berapa banyak, dan dalam urutan apa. Keduanya bekerja berpasangan.
  - Bagaimana cara menjalankan satu seeder saja tanpa menjalankan semuanya?
  - Gunakan php artisan db:seed --class=NamaSeeder, misalnya php artisan db:seed --class=PostSeeder. Perintah php artisan db:seed tanpa flag hanya menjalankan seeder yang terdaftar di DatabaseSeeder.
  - Kenapa data hasil factory-ku selalu berbahasa Inggris?
  - Karena locale default Faker adalah en_US. Ubah ke 'faker_locale' => 'id_ID' di config/app.php supaya nama, alamat, dan teks yang dihasilkan berbahasa Indonesia.
  - Apakah aman menjalankan php artisan db:seed di server production?
  - Tidak aman. Seeder dibuat untuk development dan testing. Jangan pernah menjalankan db:seed atau migrate:fresh --seed di production kecuali kamu yakin seeder tersebut memang dirancang untuk itu. Tambahkan guard app()->isProduction() di seeder penting bila perlu.
---

Hampir setiap tutorial Laravel menyuruhmu mengisi data manual lewat database atau tinker untuk mengetes tampilan. Untuk 3 sampai 5 baris data, cara itu masih oke. Tapi begitu kamu butuh 50 postingan blog dari penulis berbeda untuk mengetes pagination, cara manual berubah jadi siksaan. Di sinilah **seeder** dan **factory** menyelamatkan harimu.

Seeder adalah class PHP berisi perintah untuk mengisi database: data apa yang dibuat, berapa banyak, dan dalam urutan apa. Factory adalah blueprint yang menjelaskan seperti apa bentuk satu baris data: kolom apa saja dan dari mana nilai tiap kolom diambil, biasanya dari Faker, library pembuat data palsu yang terlihat realistis.

Singkatnya: factory menjawab "data seperti apa?", seeder menjawab "data apa saja yang dijalankan dan kapan?". Keduanya bekerja berpasangan, dan sekali kamu terbiasa memakainya, mengisi data manual akan terasa seperti pekerjaan zaman batu.

## Langkah 1: Siapkan Model dan Migration

Factory butuh model untuk diisi. Misalkan kamu punya blog dengan model `Post` yang berelasi ke `User`. Kalau belum ada, buat sekaligus dengan migration:

```bash
php artisan make:model Post -m
```

Flag `-m` ikut membuat file migration. Isi migration-nya:

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->string('slug')->unique();
            $table->text('body');
            $table->boolean('published')->default(false);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('posts');
    }
};
```

Dan model `app/Models/Post.php`:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Post extends Model
{
    use HasFactory;

    protected $fillable = ['title', 'slug', 'body', 'published'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
```

Trait `HasFactory` itu wajib. Tanpa dia, kamu tidak bisa memanggil `Post::factory()`. Kalau kamu membuat model dengan `php artisan make:model` versi Laravel terbaru, trait ini biasanya sudah terpasang otomatis, tapi selalu cek ulang.

Jalankan migration:

```bash
php artisan migrate
```

## Langkah 2: Buat Factory

Generate factory dengan artisan:

```bash
php artisan make:factory PostFactory --model=Post
```

File-nya tersimpan di `database/factories/PostFactory.php`. Isi method `definition()` seperti ini:

```php
<?php

namespace Database\Factories;

use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

class PostFactory extends Factory
{
    protected $model = Post::class;

    public function definition(): array
    {
        $title = fake()->sentence(6);

        return [
            'user_id' => User::factory(),
            'title' => $title,
            'slug' => Str::slug($title) . '-' . fake()->unique()->numberBetween(1, 9999),
            'body' => fake()->paragraphs(4, true),
            'published' => fake()->boolean(70),
        ];
    }
}
```

Beberapa hal yang terjadi di kode ini:

- `fake()` adalah helper global Laravel untuk Faker. `fake()->sentence(6)` menghasilkan kalimat 6 kata, `fake()->paragraphs(4, true)` menghasilkan 4 paragraf sebagai satu string, dan `fake()->boolean(70)` memberi nilai true dengan peluang 70 persen.
- `'user_id' => User::factory()` berarti setiap postingan otomatis dibuatkan satu user baru. Ini praktis, tapi baca terus karena ada cara yang lebih baik kalau user-nya ingin dipakai ulang.
- Slug dibuat unik dengan tambahan angka acak, karena kolom `slug` punya constraint `unique` di database. Tanpa ini, seeder bisa gagal di tengah jalan karena duplikat slug.

### Bikin Data Faker Berbahasa Indonesia

Secara default Faker menghasilkan data berbahasa Inggris. Kalau mau nama dan teks berbahasa Indonesia, ubah locale di `config/app.php`:

```php
'faker_locale' => 'id_ID',
```

Sekarang `fake()->name()` menghasilkan nama seperti "Dimas Prasetyo", bukan "John Doe". Perubahan kecil, tapi data dummy jadi terasa jauh lebih nyata saat kamu mengetes tampilan atau mengambil screenshot untuk portfolio.

### State: Variasi Data dengan Kondisi Tertentu

Kadang kamu butuh data dengan kondisi spesifik, misalnya 5 postingan yang pasti berstatus published untuk mengetes halaman arsip. Tambahkan method state di factory:

```php
public function published(): static
{
    return $this->state(fn (array $attributes) => [
        'published' => true,
    ]);
}

public function draft(): static
{
    return $this->state(fn (array $attributes) => [
        'published' => false,
    ]);
}
```

Cara pakainya:

```php
Post::factory()->published()->count(5)->create();
Post::factory()->draft()->count(3)->create();
```

## Langkah 3: Buat Seeder

Generate seeder:

```bash
php artisan make:seeder PostSeeder
```

File-nya ada di `database/seeders/PostSeeder.php`. Isi method `run()`:

```php
<?php

namespace Database\Seeders;

use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Seeder;

class PostSeeder extends Seeder
{
    public function run(): void
    {
        User::factory()->count(5)->create()->each(function ($user) {
            Post::factory()->count(10)->for($user)->create();
        });
    }
}
```

Seeder ini membuat 5 user, dan tiap user memiliki 10 postingan, total 50 postingan. Method `for($user)` mengisi `user_id` dengan user yang sudah ada, jadi tidak ada user duplikat yang terbuang sia-sia.

Alternatif yang lebih ringkas di Laravel 11 dan 12:

```php
public function run(): void
{
    Post::factory()
        ->count(50)
        ->recycle(User::factory()->count(5)->create())
        ->create();
}
```

Method `recycle()` mengambil user dari collection yang sudah dibuat, lalu memakainya ulang secara acak untuk 50 postingan. Hasilnya sama, kodenya lebih pendek.

### Daftarkan di DatabaseSeeder

Seeder tidak berjalan otomatis. Daftarkan di `database/seeders/DatabaseSeeder.php`:

```php
public function run(): void
{
    $this->call([
        PostSeeder::class,
    ]);
}
```

Urutan di array ini penting kalau seeder-mu punya dependensi. Misalnya `PostSeeder` butuh user yang dibuat oleh `UserSeeder`, maka `UserSeeder` harus dipanggil lebih dulu.

## Langkah 4: Jalankan dan Verifikasi

Ada tiga perintah yang wajib kamu hafal:

```bash
# Jalankan semua seeder yang terdaftar di DatabaseSeeder
php artisan db:seed

# Jalankan satu seeder saja
php artisan db:seed --class=PostSeeder

# Reset total: drop semua tabel, migrate ulang, lalu seed
php artisan migrate:fresh --seed
```

`migrate:fresh --seed` adalah kombinasi yang paling sering dipakai saat development. Database dibersihkan total, lalu diisi data dummy dalam sekali jalan. Perhatian: perintah ini menghapus SEMUA data di database. Jangan pernah dijalankan di production.

Verifikasi hasilnya lewat tinker:

```bash
php artisan tinker
```

```php
>>> App\Models\Post::count();
=> 50
>>> App\Models\User::count();
=> 5
>>> App\Models\Post::first()->title;
=> "Judul contoh postingan dummy untuk testing"
```

Kalau angkanya sesuai, seeder-mu berjalan dengan benar.

## Kesalahan Umum Pemula

**1. Lupa mendaftarkan seeder di DatabaseSeeder, lalu bingung kenapa datanya tidak muncul.**
`php artisan db:seed` tanpa flag hanya menjalankan seeder yang terdaftar di method `run()` milik `DatabaseSeeder`. Kalau kamu membuat `PostSeeder` tapi tidak memanggilnya di sana, datanya tidak akan pernah dibuat. Solusinya: daftarkan dengan `$this->call([PostSeeder::class])`, atau jalankan langsung dengan `--class=PostSeeder`.

**2. Menulis loop `Model::create()` manual dengan data hardcode di seeder.**
Banyak pemula menulis `for` loop berisi array data yang diketik manual di dalam seeder. Itu mengalahkan tujuan factory. Pakai factory dan Faker: datamu jadi bervariasi dan realistis, dan kodenya jauh lebih pendek.

**3. `'user_id' => User::factory()` tanpa sadar membuat ratusan user.**
Kalau kamu generate 100 postingan dan tiap postingan membuat user baru, kamu berakhir dengan 100 user yang tidak kamu butuhkan. Untuk relasi yang ingin dipakai ulang, gunakan `for()`, `has()`, atau `recycle()` seperti contoh di langkah 3.

**4. Truncate tabel tanpa menonaktifkan foreign key constraint.**
Kalau seeder-mu membersihkan tabel dulu sebelum mengisi, `Post::truncate()` akan error di MySQL karena kolom `user_id` terikat foreign key. Bungkus dengan:

```php
use Illuminate\Support\Facades\Schema;

Schema::disableForeignKeyConstraints();
Post::truncate();
Schema::enableForeignKeyConstraints();
```

**5. Menjalankan seeder di production.**
Seeder dibuat untuk development dan testing, bukan untuk server production. Jangan pernah menjalankan `db:seed` atau `migrate:fresh --seed` di production kecuali kamu sepenuhnya paham isi seeder tersebut. Untuk seeder yang benar-benar sensitif, tambahkan guard di awal method `run()`:

```php
if (app()->isProduction()) {
    return;
}
```

## Langkah Praktis yang Bisa Langsung Dicoba

1. Buka project Laravel yang sedang kamu kerjakan, atau buat project baru untuk latihan.
2. Buat factory untuk satu model yang sudah ada, dan isi `definition()` dengan Faker yang relevan dengan kolomnya.
3. Ubah `faker_locale` ke `id_ID` di `config/app.php`, lalu bandingkan hasilnya dengan locale default.
4. Buat seeder yang mengisi 50 sampai 100 baris data dengan relasi yang benar, pakai `recycle()` atau `for()` supaya tidak ada data relasi yang terbuang.
5. Jalankan `php artisan migrate:fresh --seed`, lalu buka halaman daftar data di browser. Rasakan bedanya: pagination, pencarian, dan filter yang kemarin tidak bisa dites karena datanya cuma 3 baris, sekarang bisa dites dengan sungguhan.

Sekali kamu terbiasa dengan factory dan seeder, kamu tidak akan pernah mengisi data manual lagi. Setiap fitur baru yang kamu bangun langsung bisa dites dengan data realistis dalam hitungan detik, bukan menit. Waktu yang tadinya habis untuk klik-klik phpMyAdmin bisa dipakai untuk hal yang lebih penting: menulis kode yang benar-benar jalan.
