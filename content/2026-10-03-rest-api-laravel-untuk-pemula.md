---
title: Cara Membuat REST API dengan Laravel 12 untuk Pemula
description: Panduan lengkap membuat REST API dengan Laravel 12: routing, controller, resource, validasi, dan testing dengan contoh kode nyata langkah demi langkah.
date: 2026-10-03
tags: [laravel, php, rest api, backend]
faq:
  - Apa itu REST API?
  - REST API adalah antarmuka yang memungkinkan aplikasi berkomunikasi lewat HTTP menggunakan method standar (GET, POST, PUT, DELETE) dan format data JSON.
  - Apakah Laravel cocok untuk membuat REST API?
  - Sangat cocok. Laravel punya routing API khusus, Eloquent ORM, validasi bawaan, dan Laravel Sanctum untuk autentikasi token — semua yang dibutuhkan API modern.
  - Bagaimana cara test API Laravel tanpa frontend?
  - Gunakan tools seperti Postman, Insomnia, atau ekstensi REST Client di VS Code. Laravel juga menyediakan testing otomatis via PHPUnit.
---

REST API adalah tulang punggung aplikasi modern. Frontend React, aplikasi mobile Flutter, bahkan integrasi AI — semuanya bicara lewat API. Kabar baiknya, Laravel membuat proses ini sangat mudah.

Di artikel ini kita akan membangun REST API sederhana untuk mengelola data **artikel** — lengkap dengan operasi CRUD (Create, Read, Update, Delete).

## Persiapan Project

Pastikan PHP 8.2+, Composer, dan database (MySQL/PostgreSQL) sudah terinstall. Buat project baru:

```
composer create-project laravel/laravel blog-api
cd blog-api
```

Untuk API murni, kita tidak butuh file Blade atau session. Laravel menyediakan file `routes/api.php` khusus untuk endpoint API dengan prefix `/api` otomatis.

## Membuat Model dan Migration

Kita butuh tabel `articles`. Satu perintah artisan membuat model, migration, dan controller sekaligus:

```
php artisan make:model Article -mc --api
```

Flag `-mc` membuat migration dan controller, `--api` membuat controller versi API (tanpa method `create` dan `edit` yang hanya dipakai web).

Buka file migration di `database/migrations/` dan definisikan kolomnya:

```php
public function up(): void
{
    Schema::create('articles', function (Blueprint $table) {
        $table->id();
        $table->string('title');
        $table->string('slug')->unique();
        $table->text('content');
        $table->boolean('published')->default(false);
        $table->timestamps();
    });
}
```

Jalankan migration:

```
php artisan migrate
```

## Membuat API Resource

Jangan pernah mengembalikan model Eloquent mentah ke client. Gunakan **API Resource** agar format JSON konsisten dan kamu bisa menyembunyikan kolom sensitif:

```
php artisan make:resource ArticleResource
```

```php
// app/Http/Resources/ArticleResource.php
public function toArray(Request $request): array
{
    return [
        'id'        => $this->id,
        'title'     => $this->title,
        'slug'      => $this->slug,
        'excerpt'   => Str::limit($this->content, 120),
        'published' => (bool) $this->published,
        'created_at'=> $this->created_at->toDateTimeString(),
    ];
}
```

## Menulis Controller

Controller API fokus pada data, bukan view:

```php
// app/Http/Controllers/ArticleController.php
class ArticleController extends Controller
{
    public function index()
    {
        $articles = Article::where('published', true)
            ->latest()
            ->paginate(10);

        return ArticleResource::collection($articles);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'title'   => 'required|string|max:255',
            'content' => 'required|string|min:50',
        ]);

        $article = Article::create([
            'title'     => $validated['title'],
            'slug'      => Str::slug($validated['title']),
            'content'   => $validated['content'],
            'published' => true,
        ]);

        return new ArticleResource($article);
    }

    public function show(Article $article)
    {
        return new ArticleResource($article);
    }

    public function update(Request $request, Article $article)
    {
        $validated = $request->validate([
            'title'   => 'sometimes|string|max:255',
            'content' => 'sometimes|string|min:50',
        ]);

        $article->update($validated);

        return new ArticleResource($article);
    }

    public function destroy(Article $article)
    {
        $article->delete();

        return response()->json(['message' => 'Artikel dihapus.']);
    }
}
```

Perhatikan `Article $article` di parameter — itu **route model binding**. Laravel otomatis mencari artikel berdasarkan ID di URL dan mengembalikan 404 kalau tidak ada. Satu baris kode menggantikan banyak boilerplate.

## Mendaftarkan Route

Cukup satu baris di `routes/api.php`:

```php
use App\Http\Controllers\ArticleController;

Route::apiResource('articles', ArticleController::class);
```

Ini otomatis membuat 5 endpoint:

- `GET /api/articles` — daftar artikel (dengan pagination)
- `POST /api/articles` — buat artikel baru
- `GET /api/articles/{id}` — detail satu artikel
- `PUT /api/articles/{id}` — update artikel
- `DELETE /api/articles/{id}` — hapus artikel

Jalankan server dan test:

```
php artisan serve
```

Buka `http://localhost:8000/api/articles` — kamu akan melihat JSON rapi dari ArticleResource.

## Menambahkan Autentikasi dengan Sanctum

API publik boleh diakses siapa saja, tapi operasi tulis harus diamankan. Laravel Sanctum memberikan autentikasi token yang sederhana:

```
php artisan install:api
```

Lindungi route tulis di `routes/api.php`:

```php
Route::apiResource('articles', ArticleController::class)
    ->only(['index', 'show']); // publik

Route::middleware('auth:sanctum')->group(function () {
    Route::apiResource('articles', ArticleController::class)
        ->only(['store', 'update', 'destroy']); // butuh token
});
```

Client login, menerima token, lalu menyertakannya di header `Authorization: Bearer <token>` untuk setiap request tulis.

## Kesalahan Umum Pemula

**Mengembalikan semua kolom database.** Kolom seperti `password` atau token internal tidak boleh bocor ke JSON. Selalu pakai API Resource.

**Tidak memvalidasi input.** Validasi di controller dengan `$request->validate()` — Laravel otomatis mengembalikan error 422 dengan pesan yang jelas kalau input salah.

**N+1 query problem.** Kalau resource-mu mengakses relasi (misal `$this->author->name`), Laravel menjalankan satu query per artikel. Atasi dengan eager loading: `Article::with('author')->paginate(10)`.

## Langkah Selanjutnya

Kamu sekarang punya fondasi REST API yang solid. Pengembangan lanjutannya: rate limiting agar API tidak disalahgunakan, versioning (`/api/v1/...`), dan dokumentasi otomatis dengan Scribe atau Scramble.

API yang kamu buat hari ini bisa langsung dikonsumsi frontend React, aplikasi mobile, atau bahkan diintegrasikan dengan layanan AI. Selamat ngoding!
