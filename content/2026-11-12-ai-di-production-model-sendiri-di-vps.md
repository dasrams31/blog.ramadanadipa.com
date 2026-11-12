---
title: AI di Production: Pelajaran Menjalankan Model Sendiri di VPS
description: Model AI sendiri di VPS terdengar hemat, tapi production punya jebakan: CPU lambat, cold start, dan keamanan. Ini 7 pelajaran nyata dari serverku.
cover: /assets/img/covers/ai-di-production-model-sendiri-di-vps.jpg
date: 2026-11-12
tags: [ai-production, model-lokal, vps, llm, developer]
faq:
  - Apakah VPS biasa tanpa GPU bisa menjalankan model AI?
  - Bisa, untuk model kecil. Model 1B sampai 3B yang sudah dikuantisasi Q4 masih responsif di CPU, tapi model 7B ke atas di VPS tanpa GPU akan terasa sangat lambat untuk dipakai interaktif.
  - Berapa RAM yang dibutuhkan untuk menjalankan LLM 8B di VPS?
  - Sekitar 5 GB untuk bobot model 8B pada kuantisasi 4-bit, ditambah memori untuk KV cache. Praktisnya siapkan minimal 8 GB RAM dan batasi panjang konteks supaya tidak kehabisan memori.
  - Ollama atau vLLM, mana yang cocok untuk production?
  - Ollama cocok untuk pemakaian pribadi dan prototipe karena paling mudah dijalankan. vLLM cocok untuk production dengan banyak pengguna bersamaan karena throughput-nya jauh lebih tinggi, tapi butuh GPU.
  - Kapan model lokal lebih murah daripada API cloud?
  - Hanya saat pemakaianmu berat dan konsisten, misalnya jutaan token setiap hari. Kalau trafik sporadis, API cloud hampir selalu lebih murah karena kamu hanya bayar token yang dipakai.
---

Aku pertama kali menjalankan model AI di VPS dengan ekspektasi sederhana: unduh model, jalankan server, selesai. Kenyataannya, tiga minggu pertama kuhabiskan untuk memahami kenapa responsnya lambat dan kenapa server mati diam-diam setelah restart. Production itu bukan soal modelnya jalan, melainkan soal modelnya tetap jalan, cepat, dan aman di tangan pengguna nyata.

Ini dari pengalaman menjalankan model kecil seperti SmolLM2 di VPS tanpa GPU, dibungkus llama.cpp dan di-routing lewat gateway API sendiri.

## 1. VPS tanpa GPU itu CPU-bound, pilih model kecil

VPS biasa tidak punya GPU, jadi semua inferensi dikerjakan CPU yang menghasilkan token jauh lebih lambat. Model 7B di CPU VPS bisa merangkak di bawah 10 token per detik, sementara model 1B sampai 2B masih terasa responsif untuk tugas ringan seperti klasifikasi atau ringkasan pendek.

Rumus kasar dari Qovery, 24 September 2026: model 4-bit butuh sekitar 0,6 GB memori per 1 miliar parameter, 8-bit sekitar 1 GB, FP16 sekitar 2 GB, belum termasuk KV cache. Jadi model 8B pada Q4 butuh sekitar 5 GB hanya untuk bobotnya, dan praktisnya kamu butuh VPS 8 GB ke atas.

Patokan sederhananya:

- Model 1B sampai 2B, Q4: sekitar 1 sampai 2 GB, cukup di VPS 4 GB.
- Model 7B sampai 8B, Q4: sekitar 5 GB, cukup di VPS 8 GB ke atas dengan pengguna sedikit.
- Model 13B ke atas, Q4: sekitar 8 GB atau lebih, dan di CPU akan sangat lambat untuk dipakai interaktif.

Contoh menjalankan SmolLM2 1.7B dengan llama.cpp di VPS:

```bash
./llama-server -m smollm2-1.7b-instruct-q4_k_m.gguf \
  --port 8080 --host 127.0.0.1 \
  -c 4096 -t 4 --api-key rahasia-kamu
```

Perintah ini mengikat server ke localhost, membatasi konteks 4096 token, dan memakai 4 thread CPU.

## 2. Pilih engine sesuai beban, bukan sesuai hype

Ollama, llama.cpp, vLLM, SGLang. Empat nama ini muncul di semua panduan, tapi fungsinya beda. Qovery pada 24 September 2026 merangkumnya: Ollama plus Open WebUI adalah jalan tercepat untuk satu orang, sementara vLLM adalah pilihan untuk banyak pengguna bersamaan, dengan klaim benchmark vLLM sendiri 14 sampai 24 kali throughput dibanding serving biasa. NemesisNet pada 24 Juni 2026 merangkumnya lebih singkat: Ollama untuk mulai, llama.cpp untuk tuning, vLLM untuk melayani.

Aturan praktis yang kupakai:

- Satu pengguna atau prototipe: Ollama atau llama.cpp. Instalasi cepat, konfigurasi sedikit.
- Beberapa pengguna bersamaan di satu GPU: vLLM atau SGLang.
- Tanpa GPU sama sekali: llama.cpp. Ollama juga berbasis llama.cpp di balik layar, jadi keduanya sah, tapi llama.cpp memberi kontrol lebih atas thread, konteks, dan kuantisasi.

Panduan Bitdoze pada November 2026 menyebut qwen3.5 dan gemma4 sebagai shortlist model agen saat ini, sementara qwen2.5-coder dan llama 3.x mulai memunculkan peringatan deprecation di Ollama. Jangan membangun sistem baru di atas model yang tidak lagi dirawat.

Boston IT pada 25 Agustus 2026 mencatat TGI masuk mode maintenance sejak akhir 2025, jadi jangan memulai deployment baru di atasnya. Pilih vLLM atau SGLang untuk production.

Terakhir, pin versi engine-mu: update vLLM pernah mengubah flag CLI dan merusak deployment yang sebelumnya jalan.

## 3. Cold start dan context length diam-diam makan memori

Server AI yang baru dinyalakan tidak langsung cepat. vLLM mengompilasi model saat load, dan proses itu bisa makan waktu sampai sepuluh menit menurut sesi AI Talks pada 4 Juli 2026. Request pertama setelah server nyala lagi akan terasa seperti server mati.

Konteks juga mahal. Jendela 32K memakai memori jauh lebih besar dari 4K, karena KV cache tumbuh mengikuti panjang konteks. Banyak orang menyalakan konteks maksimum lalu heran kenapa RAM habis.

Pantau dua metrik: time to first token dan token per detik. Yang pertama menentukan apakah aplikasimu terasa responsif, yang kedua menentukan berapa banyak pekerjaan yang selesai.

## 4. Endpoint tanpa auth adalah pintu terbuka

Ollama secara default tidak punya autentikasi: siapa pun yang bisa mencapai port 11434 bisa memakai modelmu. Panduan Bitdoze pada November 2026 mengingatkan: bind ke localhost atau pasang firewall.

Di VPS, aturan mainnya begini:

- Jangan pernah expose port inference langsung ke internet.
- Ikat server ke 127.0.0.1, lalu akses lewat reverse proxy dengan API key.
- Batasi akses dengan firewall, misalnya hanya dari localhost.
- Tambahkan rate limit supaya satu pengguna tidak menghabiskan semua kapasitas.

Praktik yang kupakai: llama.cpp di localhost dengan API key, lalu aplikasi Laravel memanggilnya lewat HTTP internal. Contoh controller-nya:

```php
use Illuminate\Support\Facades\Http;

$response = Http::withHeaders([
        'Authorization' => 'Bearer ' . env('LOCAL_LLM_KEY'),
    ])
    ->timeout(120)
    ->post('http://127.0.0.1:8080/v1/chat/completions', [
        'model' => 'smollm2-1.7b-instruct',
        'messages' => [
            ['role' => 'user', 'content' => $request->input('message')],
        ],
        'max_tokens' => 512,
        'temperature' => 0.7,
    ]);

return response()->json($response->json());
```

Timeout 120 detik di sana bukan typo. Inferensi CPU itu lambat, dan timeout default 30 detik akan membunuh request yang sebenarnya masih diproses.

## 5. Hitung biaya dengan jujur

"Token gratis" adalah mitos. Model lokal tidak menagih per token, tapi biayanya pindah ke sewa server dan waktumu mengurus server. Qovery pada 24 September 2026 menulisnya blak-blakan: self-hosting baru mengalahkan API kalau utilisasinya tinggi dan berkelanjutan.

Di VPS kecil tanpa GPU, hitungannya mirip: biaya bulanan kecil, tapi throughput CPU juga kecil. Rumus yang kupakai: biaya server per bulan dibagi token yang dihasilkan per bulan. Kalau hasilnya lebih besar dari harga API untuk model kecil, tetap pakai API.

Contoh kasar: aplikasi internal dengan 50 ribu token per hari tidak akan pernah menang dengan model lokal, karena servernya jalan 24 jam untuk melayani 10 menit trafik. Sebaliknya, chatbot yang melayani ribuan percakapan setiap hari dan konsisten, di situlah model lokal mulai masuk akal. Detailnya ada di [artikel tentang biaya API AI](https://blog.ramadanadipa.com/posts/biaya-api-ai-model-lokal-vs-cloud-cara-hemat/).

## 6. Kalau tidak diukur, kamu tidak tahu servermu lambat

Tiga hal minimal yang kupasang di setiap deployment model lokal.

Pertama, health check. llama.cpp menyediakan endpoint /health yang menjawab status server. Script kecil yang mengecek endpoint ini dan me-restart service kalau gagal sudah menyelamatkanku dari downtime diam-diam:

```bash
#!/bin/bash
if ! curl -sf http://127.0.0.1:8080/health > /dev/null; then
  echo "LLM server tidak merespons, restart..."
  systemctl restart llama-server
fi
```

Jalankan script itu dari cron tiap 5 menit, dan catat setiap restart ke log.

Kedua, systemd dengan Restart=always supaya server bangkit sendiri setelah crash atau setelah VPS restart:

```ini
[Unit]
Description=llama.cpp server SmolLM2
After=network.target

[Service]
ExecStart=/opt/llama.cpp/llama-server -m /opt/models/smollm2-1.7b-instruct-q4_k_m.gguf --port 8080 --host 127.0.0.1 -c 4096 -t 4 --api-key rahasia-kamu
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ketiga, log sederhana: waktu respons dan jumlah token per request, supaya kamu tahu kapan performa mulai menurun.

## 7. Kesalahan umum pemula

Rangkuman dari semua yang di atas, plus dua yang belum disebut:

- Mengekspos port inference ke internet tanpa autentikasi.
- Memilih model terbesar yang muat, bukan model terkecil yang cukup.
- Menyalakan konteks maksimum untuk semua request.
- Tidak mem-pin versi engine, lalu deployment rusak setelah update.
- Tidak ada fallback: saat model lokal mati, seluruh fitur AI ikut mati.
- Mengabaikan log, sehingga tidak tahu kapan server mulai lambat.

Yang paling sering merugikan adalah tidak adanya fallback. Model lokal akan mati di saat yang tidak kamu duga, entah karena RAM habis atau VPS restart. Router kecil yang melempar request ke API cloud saat endpoint lokal gagal adalah pembeda antara demo dan produk.

## Coba sendiri hari ini

Kamu bisa merasakan semua pelajaran di atas dalam satu jam:

1. Cek RAM VPS dengan `free -h`, minimal 4 GB untuk model 1 sampai 2B.
2. Unduh llama.cpp dan satu model GGUF Q4, misalnya SmolLM2 1.7B.
3. Jalankan llama-server di localhost dengan konteks 4096.
4. Tes dengan curl:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer rahasia-kamu" \
  -d '{"model": "smollm2-1.7b-instruct", "messages": [{"role": "user", "content": "Jelaskan apa itu API dalam satu kalimat."}]}'
```

5. Buat systemd unit supaya server restart otomatis.
6. Pasang health check cron dan fallback ke API cloud di aplikasimu.

Kalau langkah 4 terasa lambat, itu bukan kegagalan, itu data. Catat token per detiknya, lalu putuskan apakah model itu cukup.

## Kapan tetap pakai API cloud

Menjalankan model sendiri bukan tujuan, melainkan alat. Tetap pakai API cloud kalau trafikmu sporadis, kalau kamu butuh model besar yang tidak muat di VPS, atau kalau kamu tidak punya waktu mengurus server. Hybrid itu sah: tugas ringan jalan di model lokal, tugas berat dilempar ke API cloud.

Pelajaran terbesarnya: production bukan soal model apa yang kamu jalankan, tapi soal seberapa disiplin kamu mengurus hal-hal membosankan di sekitarnya: keamanan, monitoring, biaya, dan fallback.

## Sumber

- Qovery, "How to Self-Host an Open Source LLM in 2026", 24 September 2026.
- NemesisNet Lab, "Running Local LLMs: A Practical Guide for Production", 24 Juni 2026.
- AI Talks Hub, "Session 51: Running LLMs Locally with Ollama and vLLM", 4 Juli 2026.
- Boston IT, "How to Deploy a Private LLM (Self-Hosted, On-Premise)", 25 Agustus 2026.
- Bitdoze, "OpenClaw with Ollama: Best Local Models (2026 Guide)", November 2026.
