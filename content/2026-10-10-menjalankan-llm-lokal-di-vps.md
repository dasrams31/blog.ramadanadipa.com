---
title: Jalankan LLM Lokal di VPS: Llama, SmolLM2, Qwen
description: Jalankan LLM lokal di VPS sebagai API 24/7: hitung RAM, pilih Llama/SmolLM2/Qwen, install llama.cpp, pasang systemd, plus update model terbaru Oktober 2026.
date: 2026-10-10
tags: [ai, llm, vps, tutorial]
faq:
  - Berapa RAM VPS minimal untuk menjalankan LLM lokal?
  - VPS 2GB sudah cukup untuk model 1–2B parameter seperti Llama 3.2 1B atau SmolLM2 1.7B versi GGUF Q4_K_M, yang filenya hanya sekitar 0,8–1GB. Sisakan minimal 1GB untuk sistem operasi agar tidak kena OOM killer.
  - Apakah LLM bisa jalan di VPS tanpa GPU?
  - Bisa. llama.cpp berjalan murni di CPU dan tetap responsif untuk model kecil — ekspektasinya sekitar 5–15 token per detik untuk model 1–2B, cukup untuk chatbot, ringkasan, dan klasifikasi teks.
  - Model LLM apa yang paling cocok untuk VPS RAM kecil?
  - Llama 3.2 1B, SmolLM2 1.7B, atau Qwen3.5 0.8B/2B yang berlisensi Apache 2.0. Ketiganya tersedia dalam format GGUF Q4_K_M yang hemat memori dan bisa diunduh gratis dari Hugging Face.
  - Bagaimana cara membuat LLM lokal bisa dipanggil sebagai API?
  - llama.cpp menyediakan llama-server yang OpenAI-compatible: cukup jalankan dengan flag --port, lalu panggil endpoint /v1/chat/completions dari kode PHP, Python, atau JavaScript seperti memanggil OpenAI biasa — tanpa API key.
---

Menjalankan LLM di laptop itu seru buat eksperimen. Tapi begitu kamu butuh AI yang **selalu online** — buat chatbot customer service, bot Telegram, atau cron job yang meringkas sesuatu tiap jam — laptop bukan tempatnya. Di sinilah VPS bersinar: mesin kecil yang nyala 24/7, dan ternyata cukup kuat untuk menjalankan model AI sendiri.

Di VPS saya (7.7GB RAM), dua model jalan permanen sebagai service: **Llama 3.2 1B** dan **SmolLM2 1.7B** — gratis, tanpa API key, tanpa data keluar dari server. Artikel ini panduan persis seperti yang saya lakukan, plus update model terbaru Oktober 2026.

## Langkah 0: Hitung Dulu RAM-mu (Jangan Skip Ini)

Kesalahan paling mahal di VPS: mengunduh model yang RAM-mu tidak sanggup. Aturan praktis untuk versi quantisasi **GGUF Q4_K_M** (format yang dipakai llama.cpp):

> **Ukuran file ≈ jumlah parameter × 0,6 byte.** Tambahkan ±1GB untuk sistem operasi.

| Model | Ukuran file (Q4_K_M) | VPS minimal yang aman |
|---|---|---|
| Llama 3.2 1B | ±800 MB | 2 GB |
| SmolLM2 1.7B | ±1 GB | 2 GB |
| Qwen3.5 2B | ±1,4 GB | 2–4 GB |
| Qwen3.5 4B | ±2,6 GB | 4 GB |
| Qwen3.5 9B | ±5,8 GB | 8 GB |

Cek RAM bebas di VPS-mu sebelum mulai:

```bash
free -h
```

Kalau `available` di bawah 1,5GB, jangan paksakan model di atas 2B. Linux akan membunuh prosesmu lewat OOM killer — dan yang dibunuh biasanya justru si model yang paling rakus memori.

## Update Oktober 2026: Model Apa yang Lagi Hangat

Sebelum install, ada baiknya tahu lanskap minggu ini. Perbandingan model kecil terbaru (vdf.ai, diperiksa terhadap Hugging Face per Oktober 2026) mencatat beberapa nama penting:

- **Qwen3.5 0.8B / 2B / 4B / 9B** — lisensi Apache 2.0 (aman komersial), konteks sampai 262K token, dan mendukung tool calling. Buat VPS, varian 2B dan 4B adalah sweet spot baru.
- **SmolLM3-3B** (Hugging Face) — penerus SmolLM2, Apache 2.0, konteks 64K (bisa 128K dengan YaRN). Kalau SmolLM2 terasa kurang pintar, ini upgrade natural tanpa ganti keluarga.
- **Saluki** — dilaporkan alextech.ai (9 Okt 2026): Qwen3.8-27B yang dikompres menjadi ±7,89GB oleh Underdog, dirancang jalan langsung dengan llama.cpp, lisensi Apache 2.0. Buat kamu yang punya VPS 16GB+, ini cara mencicipi model kelas 27B secara lokal.
- **Riset Byteification** (paper di Nature, 7 Okt 2026, dilaporkan aiweekly.co) — peneliti me-retrofit OLMo 3, Qwen3, dan Llama 3 menjadi model byte-level (Bolmo, Bwen, Blama); Bolmo 7B naik +16,5% absolut di tugas STEM. Belum untuk production, tapi sinyal model open weight berevolusi cepat.

Catatan lisensi: Qwen3.5 dan SmolLM3 pakai Apache 2.0 (bebas komersial), sedangkan Llama 3.2 memakai Llama Community License (ada batasan tertentu) — baca dulu sebelum dipakai di produk berbayar.

## Install llama.cpp di VPS

llama.cpp adalah engine-nya. Build dari source agar optimal di CPU VPS-mu:

```bash
sudo apt update && sudo apt install -y build-essential cmake git
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release -j$(nproc)
```

Binary server-nya ada di `build/bin/llama-server`. Tidak perlu GPU, tidak perlu Docker — satu binary, selesai.

## Unduh Model yang Tepat

Dari Hugging Face, selalu pilih dua hal: varian **Instruct** (bukan base — model base tidak bisa diajak ngobrol) dan format **GGUF Q4_K_M** (kompromi terbaik antara kualitas dan ukuran):

```bash
mkdir -p ~/llm-models && cd ~/llm-models
# Contoh: SmolLM2 1.7B Instruct (±1GB)
wget https://huggingface.co/HuggingFaceTB/smollm2-1.7b-instruct-gguf/resolve/main/smollm2-1.7b-instruct-q4_k_m.gguf
```

Untuk Qwen3.5 atau Llama 3.2, cari repo GGUF resmi atau komunitas di Hugging Face dengan pola nama yang sama: `{nama-model}-instruct-q4_k_m.gguf`.

## Jadikan Service 24/7 dengan systemd

Inilah bedanya "coba-coba" dengan "production". Jangan jalankan `llama-server` manual di tmux — buat systemd service agar otomatis nyala saat reboot dan restart sendiri kalau crash:

```ini
# /etc/systemd/system/smollm2-server.service
[Unit]
Description=SmolLM2 local LLM server
After=network.target

[Service]
Type=simple
User=hatch
ExecStart=/home/hatch/llama.cpp/build/bin/llama-server \
  -m /home/hatch/llm-models/smollm2-1.7b-instruct-q4_k_m.gguf \
  --host 127.0.0.1 --port 18091 -c 4096 -t 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now smollm2-server.service
curl http://127.0.0.1:18091/health
```

Penjelasan flag penting:

- `--host 127.0.0.1` — **wajib**. Jangan bind ke `0.0.0.0` karena llama-server tidak punya autentikasi; siapa pun yang tahu port-mu bisa memakainya gratis.
- `-c 4096` — panjang konteks. Mulai dari 4096; konteks lebih besar = KV cache lebih besar = RAM jebol diam-diam.
- `-t 4` — jumlah thread CPU. Sesuaikan dengan core VPS-mu (`nproc` untuk cek).
- `Restart=always` — service bangkit sendiri kalau proses mati.

Mau dua model sekaligus seperti saya? Duplikat unit file-nya dengan port berbeda (misal 18090 untuk Llama, 18091 untuk SmolLM2).

## Ekspektasi Realistis: Seberapa Cepat di CPU?

Jujur saja: CPU VPS bukan GPU. Untuk model 1–2B, ekspektasinya **5–15 token per detik** — cukup untuk chatbot, ringkasan artikel, klasifikasi sentimen, atau ekstraksi data terstruktur. Satu jawaban 150 kata keluar dalam 10–20 detik.

Yang TIDAK cocok untuk model sekecil ini: reasoning berlapis, coding kompleks, atau konteks puluhan ribu token. Pola yang terbukti di production: **model lokal untuk tugas cepat dan murah, API cloud murah (atau model 27B lokal seperti Saluki) untuk yang berat**. Routing-nya bisa otomatis di kode — contoh Laravel:

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class LocalLlm
{
    // Port 18091 = SmolLM2 (cepat), 18090 = Llama (sedikit lebih pintar)
    protected array $ports = ['cepat' => 18091, 'pintar' => 18090];

    public function ask(string $mode, string $prompt, int $maxTokens = 300): ?string
    {
        $port = $this->ports[$mode] ?? $this->ports['cepat'];

        $response = Http::timeout(60)
            ->post("http://127.0.0.1:{$port}/v1/chat/completions", [
                'model' => 'local',
                'messages' => [
                    ['role' => 'system', 'content' => 'Jawab dalam Bahasa Indonesia, singkat dan jelas.'],
                    ['role' => 'user', 'content' => $prompt],
                ],
                'max_tokens' => $maxTokens,
                'temperature' => 0.3,
            ]);

        return $response->successful()
            ? $response->json('choices.0.message.content')
            : null;
    }
}
```

Endpoint-nya OpenAI-compatible, jadi pola `Http::post` di atas bisa dipakai ulang untuk provider mana pun — ganti base URL saja.

## Kesalahan Umum Pemula (dan Cara Menghindarinya)

1. **Mengunduh format yang salah.** llama.cpp hanya makan **GGUF**. File `.safetensors` atau `.bin` tidak akan jalan — pastikan nama file berakhiran `.gguf` sebelum mengunduh gigabyte-an data.

2. **Tidak menyisakan RAM untuk OS.** Model 4B di VPS 4GB = bunuh diri. OOM killer tidak memberi peringatan; servicemu tiba-tiba mati tanpa log yang jelas. Patokannya: RAM bebas ≥ ukuran file model + 1GB.

3. **Expose port ke publik tanpa proteksi.** Karena llama-server tanpa auth, selalu bind `127.0.0.1` dan akses dari aplikasi di mesin yang sama. Butuh akses remote? Lewat SSH tunnel atau reverse proxy dengan autentikasi — jangan langsung buka port-nya.

4. **Menjalankan aplikasi rakus RAM di mesin yang sama.** Pengalaman pribadi: saya mematikan permanen server game di VPS ini demi memberi ruang napas untuk Llama dan SmolLM2. Model LLM + aplikasi berat lain dalam satu VPS kecil = dua-duanya lemot.

5. **Konteks terlalu besar di model kecil.** Flag `-c 32768` di model 1B memang bisa jalan — sampai KV cache memakan gigabite RAM dan semuanya crash. Mulai dari 4096, naikkan hanya kalau use case-mu benar-benar butuh.

6. **Berharap kualitas GPT-4 lalu kecewa.** Setel ekspektasi di awal: model lokal 1–2B adalah asisten gratis yang selalu online untuk tugas terstruktur, bukan pengganti model frontier. Untuk tugas yang memang sulit, route ke model yang lebih besar.

## Monitoring Sederhana: Pastikan Tetap Hidup

`Restart=always` menangani crash, tapi tidak menangani kasus server "hidup tapi hang". Tambahkan health check via cron (root) tiap 5 menit:

```bash
#!/bin/bash
# /usr/local/bin/cek-llm.sh
if ! curl -sf http://127.0.0.1:18091/health > /dev/null; then
    systemctl restart smollm2-server.service
    echo "$(date): smollm2-server direstart" >> /var/log/llm-monitor.log
fi
```

```bash
sudo chmod +x /usr/local/bin/cek-llm.sh
(sudo crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/cek-llm.sh") | sudo crontab -
```

## Langkah Praktis yang Bisa Langsung Dicoba Hari Ini

1. Jalankan `free -h` di VPS-mu dan tentukan model yang muat (lihat tabel di atas).
2. Build llama.cpp dari source (5–10 menit di VPS kecil).
3. Unduh satu model GGUF Q4_K_M varian **Instruct** dari Hugging Face.
4. Tes manual dulu: `./build/bin/llama-server -m model.gguf --port 18091`, lalu curl endpoint `/v1/chat/completions`.
5. Kalau responsnya oke, bungkus jadi systemd service + health check cron seperti contoh di atas.
6. Hubungkan ke satu fitur nyata — misal endpoint `/ai/ringkas` di Laravel yang meringkas teks pakai class `LocalLlm`.

## Kesimpulan

LLM lokal di VPS bukan lagi eksperimen — ini infrastruktur production yang layak untuk tugas yang tepat. Kuncinya tiga: **pilih model sesuai RAM**, **bungkus jadi systemd service**, dan **jangan expose port tanpa proteksi**. Dengan Qwen3.5 dan SmolLM3-3B yang berlisensi Apache 2.0, opsi untuk VPS kecil justru makin bagus.

Mulai dari satu model kecil minggu ini. Begitu kamu punya "API AI sendiri" yang nyala 24/7 tanpa tagihan, cara kamu membangun fitur akan berubah permanen.
