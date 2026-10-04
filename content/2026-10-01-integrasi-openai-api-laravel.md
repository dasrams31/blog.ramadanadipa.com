---
title: Cara Integrasi OpenAI API di Aplikasi Laravel (Lengkap dengan Contoh)
description: Tutorial integrasi OpenAI API di Laravel: setup API key, kirim prompt, streaming response, hemat biaya dengan caching, dan contoh fitur ringkasan teks otomatis.
date: 2026-10-01
tags: [laravel, ai, api, php]
faq:
  - Berapa biaya menggunakan OpenAI API?
  - Model seperti GPT-4o mini dibanderol per token dan sangat murah untuk project kecil — ratusan ribu request bisa di bawah Rp50 ribu. Selalu pasang limit di dashboard OpenAI.
  - Apakah API key aman disimpan di file .env?
  - Ya, selama file .env tidak di-commit ke Git dan tidak bisa diakses publik. Jangan pernah hardcode API key di kode atau frontend JavaScript.
  - Apa bedanya API OpenAI dengan ChatGPT?
  - ChatGPT adalah aplikasinya, OpenAI API adalah layanan backend yang bisa kamu panggil dari kodemu sendiri untuk membangun fitur AI di aplikasimu.
---

Menambahkan fitur AI ke aplikasi Laravel tidak serumit yang dibayangkan. Tanpa training model sendiri, kamu bisa memakai OpenAI API untuk ringkasan teks, chatbot, klasifikasi, sampai generasi konten — semuanya lewat HTTP request biasa.

## Persiapan: API Key

Daftar di [platform.openai.com](https://platform.openai.com), buat API key baru, dan simpan di `.env`:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
```

Tambahkan ke `config/services.php` agar bisa diakses rapi dari kode:

```php
'openai' => [
    'key'   => env('OPENAI_API_KEY'),
    'model' => env('OPENAI_MODEL', 'gpt-4o-mini'),
],
```

**Peringatan keamanan:** jangan pernah commit `.env` ke Git dan jangan expose API key ke frontend. Semua panggilan API harus lewat backend.

## Membuat Service Class

Jangan panggil API langsung dari controller — bungkus dalam service agar mudah di-test dan diganti provider:

```php
// app/Services/OpenAiService.php
namespace App\Services;

use Illuminate\Support\Facades\Http;

class OpenAiService
{
    public function chat(array $messages, array $options = []): string
    {
        $response = Http::withToken(config('services.openai.key'))
            ->timeout(60)
            ->post('https://api.openai.com/v1/chat/completions', [
                'model'       => $options['model'] ?? config('services.openai.model'),
                'messages'    => $messages,
                'temperature' => $options['temperature'] ?? 0.7,
                'max_tokens'  => $options['max_tokens'] ?? 500,
            ]);

        if ($response->failed()) {
            throw new \Exception('OpenAI API error: ' . $response->body());
        }

        return $response->json('choices.0.message.content');
    }

    public function summarize(string $text): string
    {
        return $this->chat([
            ['role' => 'system', 'content' => 'Kamu adalah peringkas teks. Jawab dalam Bahasa Indonesia yang ringkas dan jelas.'],
            ['role' => 'user', 'content' => "Ringkas teks berikut dalam 3 poin:\n\n{$text}"],
        ], ['max_tokens' => 300, 'temperature' => 0.3]);
    }
}
```

Perhatikan dua hal: `temperature` rendah (0.3) untuk tugas faktual seperti ringkasan agar output konsisten, dan `max_tokens` dibatasi agar biaya terkendali.

## Memakai di Controller

```php
// app/Http/Controllers/SummaryController.php
class SummaryController extends Controller
{
    public function __invoke(Request $request, OpenAiService $ai)
    {
        $validated = $request->validate([
            'text' => 'required|string|min:100|max:10000',
        ]);

        $summary = $ai->summarize($validated['text']);

        return response()->json(['summary' => $summary]);
    }
}
```

Laravel otomatis meng-inject `OpenAiService` lewat dependency injection. Route-nya:

```php
Route::post('/api/summarize', SummaryController::class)
    ->middleware('auth:sanctum');
```

## Menghemat Biaya dengan Caching

Panggilan AI berbayar per token. Kalau teks yang sama diringkas berulang kali, cache hasilnya:

```php
public function summarize(string $text): string
{
    $key = 'summary:' . md5($text);

    return Cache::remember($key, now()->addDays(7), function () use ($text) {
        return $this->chat([...]);
    });
}
```

Satu baris `Cache::remember` bisa memangkas biaya API hingga 80% untuk konten yang sering diakses — misalnya ringkasan artikel populer di blog.

## Menangani Error dengan Anggun

API eksternal bisa gagal: rate limit, timeout, atau key kedaluwarsa. Jangan biarkan user melihat error mentah:

```php
try {
    $summary = $ai->summarize($text);
} catch (\Exception $e) {
    Log::error('AI summarize gagal', ['error' => $e->getMessage()]);
    return response()->json([
        'message' => 'Layanan AI sedang sibuk, coba lagi sebentar.',
    ], 503);
}
```

Untuk proses yang lama (lebih dari 30 detik), pindahkan ke **queue job** agar request HTTP tidak timeout — user dapat notifikasi saat hasilnya siap.

## Prompt yang Baik = Output yang Baik

Kualitas output AI sangat ditentukan prompt. Tiga prinsip:

1. **Spesifik.** "Ringkas dalam 3 poin Bahasa Indonesia" jauh lebih baik dari "ringkas ini".
2. **Beri peran.** System prompt seperti "kamu adalah editor profesional" mengarahkan gaya bahasa.
3. **Batasi format.** Minta output JSON kalau hasilnya akan diproses kode — jauh lebih reliable daripada parsing teks bebas.

## Langkah Selanjutnya

Setelah dasar ini jalan, kamu bisa bereksperimen: **streaming response** agar user melihat jawaban muncul kata per kata (pakai Server-Sent Events), **function calling** agar AI bisa memanggil fungsi di aplikasimu, atau **RAG** agar AI menjawab berdasarkan dokumen milikmu sendiri.

Integrasi AI bukan lagi fitur mewah — ini sudah jadi ekspektasi user. Mulai dari satu fitur kecil seperti ringkasan otomatis, dan kembangkan dari sana.
