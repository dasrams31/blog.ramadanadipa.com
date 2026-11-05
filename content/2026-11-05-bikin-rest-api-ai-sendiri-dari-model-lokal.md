---
title: Bikin REST API AI Sendiri dari Model Lokal
description: Bungkus model lokal jadi REST API OpenAI compatible dengan Ollama atau llama-server, tambah auth di Laravel, dan panggil dari kode yang sama seperti OpenAI.
date: 2026-11-05
tags: [ai, llm-lokal, openai-compatible, laravel]
faq:
  - Apa itu API OpenAI compatible?
  - API OpenAI compatible adalah endpoint lokal yang memakai format request dan response yang sama dengan API OpenAI, terutama POST /v1/chat/completions. Kode yang sudah bisa memanggil OpenAI biasanya hanya perlu mengganti base URL dan nama model untuk memakai model lokal.
  - Apakah semua aplikasi yang memakai OpenAI bisa langsung pindah ke model lokal?
  - Tidak semua. Format chat completions umumnya cocok, tetapi fitur seperti tool calling, structured output, dan embeddings tidak selalu didukung sama di setiap engine lokal. Uji endpoint yang kamu pakai sebelum menganggap semua fitur tersedia.
  - Ollama atau llama-server, mana yang sebaiknya dipakai duluan?
  - Ollama lebih cepat untuk mulai karena model tinggal di pull dan servernya langsung jalan. llama-server memberi kontrol lebih besar atas file GGUF, konteks, dan flag server, dan cocok kalau kamu ingin mengatur sendiri tiap detailnya.
  - Bagaimana cara mengamankan API AI lokal di VPS?
  - Ikat engine lokal ke 127.0.0.1, jangan membuka portnya ke internet, lalu taruh auth di API wrapper kamu sendiri. Tambahkan reverse proxy dan API key bila API wrapper itu harus diakses dari luar server.
---

Jangan bangun protokol AI baru. Kalau model lokalmu sudah bisa menjawab lewat endpoint yang formatnya sama dengan OpenAI, semua kode, SDK, dan tool yang sudah kamu tulis untuk OpenAI bisa dipakai ulang dengan mengganti dua hal saja: base URL dan nama model. Itu inti dari artikel ini. Kamu tidak sedang melatih model, kamu sedang membungkus model yang sudah ada menjadi REST API milikmu sendiri, lengkap dengan auth, validasi, dan batas yang kamu kontrol.

Saya memakai pola ini untuk model kecil di VPS. Laptop boleh mati, API tetap jalan, dan data tidak keluar dari server. Bedanya dengan menjalankan model di terminal adalah lapisan di depannya: endpoint stabil, kunci akses, dan error yang jelas kalau model belum siap.

## Pilih mesinnya dulu: Ollama, llama-server, atau vLLM

Ketiganya menyediakan endpoint OpenAI compatible, tetapi titik nyamannya berbeda. Panduan Guide to Artificial Intelligence (2 November 2026) merangkumnya: Ollama tercepat untuk satu orang, llama-server paling fleksibel, vLLM terbaik untuk banyak pengguna di GPU.

| Engine | Paling cocok untuk | Alamat bawaan | Format model utama |
|---|---|---|---|
| Ollama | Mulai cepat di laptop atau VPS | 127.0.0.1:11434 | Library Ollama, berbasis GGUF |
| llama-server | Kontrol penuh atas file dan flag | Port ditentukan sendiri | GGUF |
| vLLM | Banyak request bersamaan di GPU Linux | localhost:8000 | Model Hugging Face |

Ollama pilihan awal yang masuk akal. Ia membungkus llama.cpp, mengurus unduh model, dan servernya langsung aktif. Menurut selfhost.directory, Ollama 0.40.14 rilis 3 November 2026. llama.cpp, menurut Cloudorian (4 November 2026), sudah melewati 118 ribu star di GitHub.

vLLM baru layak kalau kamu punya GPU dan traffic yang perlu batching. Di VPS CPU biasa, ia hanya menambah kerumitan. Untuk artikel ini, pakai Qwen2.5 1.5B instruct, cukup untuk klasifikasi, ekstraksi JSON, dan draf pendek. Kalau butuh penalaran panjang, naikkan ukuran modelnya, jangan berharap trik API menutupi batas kemampuan model.

## Jalankan engine dan tes dengan curl

Mulai dari Ollama. Dua perintah ini cukup untuk membuktikan endpointnya hidup:

```bash
ollama pull qwen2.5:1.5b
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5:1.5b","messages":[{"role":"user","content":"Halo, jawab dalam satu kalimat."}],"temperature":0.2}'
```

Perhatikan `/v1` di URL. Dev.to (4 November 2026) menekankan jebakan ini: endpoint OpenAI compatible Ollama hidup di bawah `/v1`. Tanpa `/v1`, SDK memanggil `/chat/completions` di root dan mendapat 404. Periksa URL dulu sebelum menyalahkan modelnya.

Untuk llama-server, tulis port eksplisit. Nilainya bisa berbeda antar perintah dan versi. Medium (25 Oktober 2026) mencatat `llama serve` bawaan di port 9931, sementara contoh lama sering memakai 8080:

```bash
llama-server -m qwen2.5-1.5b-instruct-q4_k_m.gguf \
  --host 127.0.0.1 --port 8080 --alias qwen-local -c 4096
```

Lalu tes health dan chatnya:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-local","messages":[{"role":"user","content":"Halo, jawab dalam satu kalimat."}]}'
```

Nama model harus cocok dengan alias atau nama model di Ollama. Respons 503 saat model masih loading berarti tunggu, bukan server rusak. Untuk streaming, tambah `"stream": true` dan pakai `curl -N`, responsnya SSE dan diakhiri `[DONE]`.

Konteks diatur di sisi server, misalnya flag `-c` di llama-server, bukan lewat payload chat completions. Kalau butuh konteks panjang, atur dari awal.

## Bungkus jadi API sendiri di Laravel

Engine lokal tidak boleh diekspos mentah. Ollama dan llama-server hanya mendengarkan localhost dan tidak memvalidasi API key. Wrapper kamu adalah tempat auth, validasi, pembatasan, dan logging. Client memanggil Laravel, Laravel meneruskan ke engine lokal, lalu mengembalikan jawaban yang dibersihkan.

Tambahkan konfigurasi di `config/services.php`:

```php
'ai' => [
    'base_url' => env('AI_BASE_URL', 'http://127.0.0.1:11434/v1'),
    'model' => env('AI_MODEL', 'qwen2.5:1.5b'),
],
```

Lalu buat controller yang hanya memakai HTTP client bawaan Laravel:

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class AiChatController extends Controller
{
    public function chat(Request $request)
    {
        $data = $request->validate([
            'prompt' => ['required', 'string', 'max:4000'],
            'temperature' => ['sometimes', 'numeric', 'min:0', 'max:1'],
        ]);

        $response = Http::timeout(60)->post(
            rtrim(config('services.ai.base_url'), '/').'/chat/completions',
            [
                'model' => config('services.ai.model'),
                'messages' => [
                    ['role' => 'system', 'content' => 'Jawab singkat dan dalam Bahasa Indonesia.'],
                    ['role' => 'user', 'content' => $data['prompt']],
                ],
                'temperature' => $data['temperature'] ?? 0.2,
                'max_tokens' => 512,
            ]
        );

        if (! $response->successful()) {
            return response()->json(['error' => 'Model lokal tidak menjawab.'], 502);
        }

        return response()->json([
            'answer' => $response->json('choices.0.message.content'),
        ]);
    }
}
```

Daftarkan route dengan auth, misalnya Sanctum untuk aplikasi yang sudah punya login, atau middleware API key buatan sendiri untuk integrasi antar service:

```php
Route::middleware('auth:sanctum')->post('/ai/chat', [AiChatController::class, 'chat']);
```

Batas `max:4000` dan `max_tokens: 512` disengaja. Model kecil di CPU lambat kalau prompt raksasa dan jawaban panjang. Validasi di wrapper lebih murah daripada menunggu timeout.

## Klien yang sama untuk cloud dan lokal

Keuntungan format ini terlihat di klien. Skrip Python berikut, hanya standard library, bekerja untuk Ollama, llama-server, dan OpenAI, selama base URL dan nama model diganti lewat environment variable:

```python
import json
import os
import urllib.request

BASE_URL = os.environ.get("AI_BASE_URL", "http://127.0.0.1:11434/v1")
MODEL = os.environ.get("AI_MODEL", "qwen2.5:1.5b")

def ask(prompt):
    payload = {
        "model": MODEL,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "Jawab singkat dan dalam Bahasa Indonesia."},
            {"role": "user", "content": prompt},
        ],
    }
    req = urllib.request.Request(
        BASE_URL + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]

print(ask("Apa bedanya Ollama dan llama-server dalam satu kalimat?"))
```

Di JavaScript, ganti `baseURL` SDK OpenAI ke endpoint lokal, isi API key dengan string apa saja, dan kode sisanya tidak berubah. Pindah ke cloud nanti hanya mengganti konfigurasi, bukan logika aplikasi.

Tangani tiga kegagalan di klien: timeout, respons tanpa `choices`, dan jawaban bukan JSON saat kamu meminta JSON. Validasi hasilnya di kode, jangan percaya mentah mentah. Kalau gagal, kembalikan error jelas, jangan tampilkan teks setengah jadi.

## Jalankan 24/7 di VPS tanpa membuka port model

Di VPS, engine harus jalan sebagai service, bukan proses terminal yang mati saat SSH ditutup. Unit llama-server minimalnya seperti ini, sesuaikan path dan akun `User`:

```ini
[Unit]
Description=Llama Server Lokal
After=network.target

[Service]
# User=akun-server-kamu
ExecStart=/usr/local/bin/llama-server -m /opt/models/qwen2.5-1.5b-instruct-q4_k_m.gguf --host 127.0.0.1 --port 8080 --alias qwen-local -c 4096
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Simpan di `/etc/systemd/system/llama-server.service`, jalankan `systemctl daemon-reload` dan `systemctl enable --now llama-server`, lalu periksa health endpointnya. Untuk Ollama, periksa `systemctl status ollama` dulu, service bawaannya biasanya sudah aktif.

Jangan ubah `--host` ke `0.0.0.0` agar bisa dites dari laptop. Kalau wrapper Laravel harus diakses dari luar, pasang Nginx, HTTPS, dan API key di depan Laravel, dan biarkan engine tetap di localhost. ComputingForGeeks (Juli 2026) memakai pola sama: aplikasi berbicara ke `/v1/chat/completions` lokal seperti ke OpenAI.

## Kesalahan umum pemula dan cara menghindarinya

Pertama, mengekspos port 11434 atau 8080 tanpa auth. Siapa pun bisa memakai modelmu dan melihat promptnya. Ikat ke localhost, taruh auth di wrapper.

Kedua, lupa `/v1` di base URL, lalu menyimpulkan model lokal tidak kompatibel. Periksa `/v1/models` dulu, endpoint itu memastikan nama modelmu sudah benar.

Ketiga, memakai nama model OpenAI seperti `gpt-4o-mini` untuk server lokal. Server lokal hanya mengenal model yang dimuat, misalnya `qwen2.5:1.5b` di Ollama atau alias di llama-server.

Keempat, tidak ada timeout dan batas token. Satu prompt panjang bisa mengunci worker PHP selama bermenit menit. Tetapkan timeout, batasi prompt, dan batasi `max_tokens` sejak awal.

Kelima, menganggap semua fitur OpenAI tersedia di lokal. Embeddings, tool calling, dan structured output dukungannya berbeda di tiap engine dan model. Uji eksplisit, siapkan fallback cloud untuk fitur yang belum didukung.

## Langkah praktis yang bisa langsung dicoba

Pilih Ollama kalau mau cepat, jalankan satu model kecil, dan tes dengan curl sampai `/v1/chat/completions` menjawab. Salin controller di atas, arahkan `AI_BASE_URL` dan `AI_MODEL` di `.env` ke engine lokalmu, dan panggil `/api/ai/chat`. Terakhir, matikan engine dan pastikan aplikasimu mengembalikan 502 yang rapi, bukan halaman kosong.

Kalau langkah itu jalan, kamu sudah punya REST API AI sendiri: model lokal, format standar, kendali di tanganmu. Naik ukuran model atau pindah cloud nanti hanya mengganti konfigurasi.

Sumber: ComputingForGeeks (Juli 2026); Medium, Deduped (25 Oktober 2026); Dev.to (4 November 2026); selfhost.directory (3 November 2026); Guide to Artificial Intelligence (2 November 2026); Cloudorian (4 November 2026).
