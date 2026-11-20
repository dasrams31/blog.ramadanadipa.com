---
title: Cara Bikin Fitur Ringkasan Teks Otomatis dengan AI API
description: Mau tambah fitur ringkasan otomatis di aplikasimu? Panduan integrasi AI API di Laravel: chunking teks panjang, prompt yang tepat, dan kontrol biaya.
cover: /assets/img/covers/cara-bikin-fitur-ringkasan-teks-otomatis-dengan-ai-api.jpg
date: 2026-11-20
tags: [ai-api, laravel, ringkasan-otomatis, javascript]
faq:
  - Berapa biaya membuat fitur ringkasan teks dengan AI API?
  - Sangat murah untuk pemakaian wajar. Model ringan seperti GPT-4o mini atau model open source sekelasnya mematok harga per token, dan satu ringkasan artikel 3.000 kata biasanya menghabiskan kurang dari Rp100. Biaya bisa ditekan lagi dengan caching dan membatasi panjang input.
  - Apakah AI API bisa meringkas teks berbahasa Indonesia?
  - Bisa. Model AI modern sudah dilatih dengan data berbahasa Indonesia dalam jumlah besar. Hasil ringkasannya cukup akurat, asal prompt ditulis jelas dan teks sumbernya tidak berantakan.
  - Bagaimana cara meringkas dokumen yang sangat panjang, misalnya 50 halaman?
  - Potong dokumen menjadi beberapa bagian, ringkas tiap bagian secara terpisah, lalu gabungkan dan ringkas sekali lagi. Teknik ini disebut map-reduce dan dijelaskan langkah demi langkah di artikel ini.
  - Apakah hasil ringkasan AI bisa dipercaya begitu saja?
  - Tidak sepenuhnya. Model AI kadang menambahkan detail yang tidak ada di teks asli. Untuk konten penting seperti dokumen hukum atau laporan medis, selalu tampilkan ringkasan bersama sumber aslinya dan minta pengguna memverifikasi poin kritis.
---

Pernah buka artikel panjang lalu langsung menutupnya karena tidak ada waktu baca sampai habis? Pengguna aplikasimu merasakan hal yang sama. Fitur ringkasan otomatis menyelesaikan masalah itu: pengguna tempel teks atau unggah dokumen, lalu mendapat versi singkatnya dalam hitungan detik.

Fitur ini tidak butuh model AI sendiri. Cukup panggil AI API dari provider seperti OpenAI, atau endpoint yang kompatibel dengan format yang sama, lalu bungkus hasilnya di aplikasimu. Artikel ini menunjukkan cara lengkapnya di Laravel, dari memotong teks panjang sampai menampilkannya di frontend.

## Cara kerja fitur ringkasan

Alurnya sederhana dan terdiri dari empat langkah.

Pertama, aplikasi menerima teks dari pengguna, entah lewat textarea, file yang diunggah, atau artikel yang sudah tersimpan di database. Kedua, teks dipotong menjadi bagian-bagian kecil kalau terlalu panjang, karena setiap model AI punya batas token input. Ketiga, tiap bagian dikirim ke AI API bersama prompt yang memerintahkan model untuk meringkas. Keempat, hasilnya digabung, dibersihkan, lalu ditampilkan ke pengguna.

Satu hal penting: jangan kirim seluruh dokumen 50 halaman dalam satu request. Selain berisiko melebihi batas token, biayanya membengkak dan hasilnya cenderung menurun kualitasnya. Potong dulu, ringkas per bagian, lalu ringkas hasil gabungannya. Pola ini akan kita pakai di kode nanti.

## Siapkan API key dan endpoint

Simpan API key di file `.env`, jangan pernah menulisnya langsung di kode. Tambahkan dua baris ini:

```env
AI_API_KEY=sk-isi-api-key-kamu-di-sini
AI_API_URL=https://api.openai.com/v1
AI_SUMMARY_MODEL=gpt-4o-mini
```

Lalu daftarkan di `config/services.php` supaya bisa dibaca dari mana saja:

```php
'ai' => [
    'key' => env('AI_API_KEY'),
    'url' => env('AI_API_URL', 'https://api.openai.com/v1'),
    'summary_model' => env('AI_SUMMARY_MODEL', 'gpt-4o-mini'),
],
```

Pakai model ringan untuk tugas ringkasan. Model besar memang lebih pintar, tapi untuk meringkas teks biasa selisih kualitasnya kecil sementara harganya bisa sepuluh kali lipat. Model ringan juga merespons lebih cepat, dan kecepatan terasa langsung oleh pengguna.

Kalau kamu memakai provider lain yang menyediakan endpoint kompatibel OpenAI, cukup ganti `AI_API_URL` dan nama modelnya. Kode di bawah memakai format request standar, jadi tidak perlu diubah.

## Potong teks panjang jadi bagian kecil

Model AI menghitung input dalam token, bukan kata. Sebagai patokan kasar, 1 token kira-kira sama dengan 4 karakter teks Bahasa Indonesia atau Inggris. Artikel 3.000 kata berarti sekitar 12.000 karakter, atau 3.000 token. Masih aman untuk satu request, tapi dokumen yang lebih panjang harus dipotong.

Buat service class `app/Services/SummarizerService.php`. Method pertama memotong teks berdasarkan jumlah kata, bukan karakter, supaya potongan tidak berhenti di tengah kalimat secara brutal:

```php
<?php

namespace App\Services;

class SummarizerService
{
    public function chunkText(string $text, int $maxWords = 1200): array
    {
        $words = preg_split('/\s+/', trim($text));
        $chunks = [];

        foreach (array_chunk($words, $maxWords) as $part) {
            $chunks[] = implode(' ', $part);
        }

        return $chunks;
    }
}
```

Kenapa 1.200 kata per potongan? Satu potongan 1.200 kata kira-kira 1.500 sampai 1.800 token, menyisakan ruang untuk prompt dan jawaban di dalam batas konteks model ringan yang biasanya 128 ribu token. Angka ini aman dan hasilnya tetap koheren, karena tiap potongan masih cukup panjang untuk dipahami konteksnya.

## Panggil AI API dari Laravel

Tambahkan method `summarize` di service yang sama. Method ini mengirim satu potongan teks ke AI API dan mengembalikan ringkasannya:

```php
use Illuminate\Support\Facades\Http;

public function summarizeChunk(string $chunk): string
{
    $response = Http::withToken(config('services.ai.key'))
        ->timeout(60)
        ->post(config('services.ai.url') . '/chat/completions', [
            'model' => config('services.ai.summary_model'),
            'temperature' => 0.3,
            'max_tokens' => 500,
            'messages' => [
                [
                    'role' => 'system',
                    'content' => 'Kamu adalah peringkas teks. Ringkas teks berikut '
                        . 'dalam Bahasa Indonesia, maksimal 5 poin penting. '
                        . 'Pakai kalimat sendiri, jangan menambah fakta baru, '
                        . 'dan jangan mengubah angka atau nama yang disebut.',
                ],
                ['role' => 'user', 'content' => $chunk],
            ],
        ]);

    if ($response->failed()) {
        throw new \RuntimeException(
            'Gagal memanggil AI API: ' . $response->status()
        );
    }

    return trim($response->json('choices.0.message.content', ''));
}
```

Perhatikan tiga detail di kode ini. Nilai `temperature` 0.3 membuat jawaban lebih konsisten dan faktual, karena ringkasan butuh ketepatan, bukan kreativitas. `max_tokens` 500 membatasi biaya sekaligus mencegah jawaban bertele-tele. Prompt system secara eksplisit melarang model menambah fakta baru, ini penting untuk mengurangi halusinasi.

Method utama menggabungkan semuanya dengan pola map-reduce:

```php
public function summarize(string $text): string
{
    $chunks = $this->chunkText($text);

    $summaries = array_map(
        fn (string $chunk) => $this->summarizeChunk($chunk),
        $chunks
    );

    if (count($summaries) === 1) {
        return $summaries[0];
    }

    $combined = implode("\n\n", $summaries);

    return $this->summarizeChunk(
        "Gabungkan ringkasan-ringkasan berikut menjadi satu ringkasan utuh:\n\n" . $combined
    );
}
```

Kalau teks hanya menghasilkan satu potongan, hasilnya langsung dikembalikan tanpa request kedua. Kalau ada banyak potongan, tiap potongan diringkas dulu, lalu hasil gabungannya diringkas sekali lagi menjadi satu ringkasan utuh. Dua tahap ini jauh lebih murah daripada mengirim dokumen utuh sekaligus, dan hasilnya lebih rapi.

Terakhir, buat endpoint API di `routes/api.php` dan controllernya:

```php
use App\Services\SummarizerService;
use Illuminate\Http\Request;

Route::post('/summarize', function (Request $request, SummarizerService $summarizer) {
    $validated = $request->validate([
        'text' => 'required|string|min:200|max:100000',
    ]);

    $summary = $summarizer->summarize($validated['text']);

    return response()->json(['summary' => $summary]);
});
```

Validasi `min:200` mencegah pengguna mengirim teks dua kalimat lalu protes karena ringkasannya sama panjangnya dengan teks asli. Batas `max:100000` melindungi server dari input raksasa yang menghabiskan kuota API dalam satu request.

## Tampilkan di frontend dengan JavaScript

Di sisi frontend, cukup kirim teks lewat `fetch` dan tampilkan hasilnya. Contoh dengan JavaScript polos:

```javascript
async function summarizeText(text) {
  const button = document.querySelector('#summarize-btn');
  button.disabled = true;
  button.textContent = 'Meringkas...';

  try {
    const response = await fetch('/api/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error('Server membalas ' + response.status);
    }

    const data = await response.json();
    document.querySelector('#summary-result').textContent = data.summary;
  } catch (error) {
    document.querySelector('#summary-result').textContent =
      'Ringkasan gagal dibuat. Coba lagi sebentar lagi.';
    console.error(error);
  } finally {
    button.disabled = false;
    button.textContent = 'Ringkas Sekarang';
  }
}
```

Tombol di-disable selama request berjalan supaya pengguna tidak mengirim request yang sama berkali-kali. Pesan error yang ditampilkan ke pengguna dibuat umum, sementara detail teknisnya dicatat di `console.error` untuk debugging.

## Kesalahan umum pemula

### Mengirim seluruh dokumen dalam satu request

Ini kesalahan paling sering. Dokumen 20 ribu kata dikirim mentah-mentah, API membalas error token limit, lalu developer mengira API-nya rusak. Selalu potong dulu seperti contoh di atas, dan tampilkan batas panjang input yang jelas di form.

### Prompt terlalu longgar

Prompt seperti "ringkas teks ini" memberi model kebebasan terlalu besar. Hasilnya tidak konsisten: kadang satu paragraf, kadang sepuluh poin, kadang malah menerjemahkan. Tulis prompt yang spesifik: sebut bahasa hasil, jumlah poin maksimal, dan larangan menambah fakta. Semakin spesifik promptnya, semakin stabil hasilnya.

### Tidak menangani error API

API bisa timeout, kehabisan kuota, atau sedang down. Kalau kode tidak menangani kegagalan, pengguna hanya melihat halaman loading yang tidak pernah selesai. Selalu bungkus pemanggilan API dengan pengecekan status dan berikan pesan error yang jelas, seperti contoh controller di atas.

### Mengabaikan biaya

Setiap request ada harganya, dan biaya kecil menjadi besar kalau fitur dipakai ribuan kali sehari. Batasi panjang input, pakai model murah, dan simpan hasil ringkasan di cache. Untuk teks yang sama, tidak ada alasan memanggil API dua kali:

```php
use Illuminate\Support\Facades\Cache;

$summary = Cache::remember(
    'summary:' . md5($text),
    now()->addDays(7),
    fn () => $summarizer->summarize($text)
);
```

Satu baris cache ini bisa memangkas tagihan secara drastis untuk konten yang sering diringkas ulang, misalnya artikel populer di blog.

### Menampilkan ringkasan tanpa sumber

Ringkasan AI kadang salah, terutama soal angka dan nama. Jangan tampilkan ringkasan sendirian untuk konten yang penting. Tampilkan berdampingan dengan teks asli, atau sertakan tautan ke sumber, supaya pengguna bisa memeriksa sendiri poin yang meragukan.

## Langkah praktis yang bisa langsung dicoba

Mulai dari yang paling kecil dan uji dengan teks nyata. Buat service class seperti contoh di atas, daftarkan route `/api/summarize`, lalu uji dengan artikel blog sepanjang 1.500 kata. Bandingkan ringkasan hasil AI dengan ringkasan yang kamu tulis sendiri. Kalau poin pentingnya tertangkap semua, prompt-mu sudah cukup bagus.

Setelah itu, tambahkan tiga hal secara bertahap. Pertama, cache seperti contoh di atas. Kedua, simpan riwayat ringkasan pengguna ke database supaya mereka bisa membuka lagi tanpa request ulang. Ketiga, tambahkan pilihan gaya ringkasan, misalnya mode singkat tiga poin dan mode detail sepuluh poin, cukup dengan mengubah prompt system.

Fitur ringkasan teks adalah salah satu integrasi AI paling mudah yang bisa langsung dirasakan manfaatnya oleh pengguna. Tidak butuh infrastruktur khusus, tidak butuh melatih model, dan biayanya kecil. Yang dibutuhkan hanya pemotongan teks yang benar, prompt yang spesifik, dan penanganan error yang rapi. Setelah tiga hal itu beres, fitur ini bisa jalan stabil di production.
