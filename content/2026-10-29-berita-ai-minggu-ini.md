---
title: Berita AI Minggu Ini: GPT-6.1 Terra, Genie 4, Gemini Carbon
description: Minggu ini OpenAI merilis GPT-6.1 Terra, Google mengumumkan Genie 4 dan Gemini 4 Carbon, Nvidia membuka model transkripsi. Ringkasan dan artinya buat developer.
date: 2026-10-29
tags: [ai, berita-ai, openai, google, developer]
faq:
  - Apa itu GPT-6.1 Terra yang dirilis OpenAI minggu ini?
  - GPT-6.1 Terra adalah model OpenAI yang dirilis 26 Oktober 2026 untuk pekerjaan berbasis komputer, seperti membaca gambar teknis, mengisi formulir, dan menyusun proposal, dengan harga API standar 1 dolar per 1 juta token input dan 5 dolar per 1 juta token output.
  - Apakah Genie 4 dari Google sudah bisa dicoba publik?
  - Belum. Per 27 Oktober 2026 Genie 4 masih dalam research preview untuk trusted tester, dengan akses lebih luas direncanakan untuk pelanggan Google AI Ultra dan mitra developer terpilih.
  - Apakah Nemotron 3.5 Transcribe dari Nvidia gratis dipakai?
  - Modelnya open-weight sehingga bisa dipakai tanpa biaya lisensi, tapi kamu tetap butuh hardware sendiri untuk menjalankannya, dari chip Jetson sampai GPU datacenter.
  - Model AI mana yang paling hemat untuk otomasi pekerjaan kantor bervolume tinggi?
  - Untuk tugas komputer berulang seperti membaca faktur dan mengisi formulir, GPT-6.1 Terra adalah kandidat paling masuk akal minggu ini karena harganya setengah dari pendahulunya, tapi tetap benchmark dulu dengan data kamu sendiri sebelum pindah total.
---

Minggu 26 sampai 28 Oktober 2026 adalah salah satu minggu paling padat buat developer yang mengikuti dunia AI. OpenAI merilis model baru yang harganya setengah dari pendahulunya, Google mengumumkan dua hal besar dalam dua hari berurutan, Nvidia membuka model transkripsi open-weight, dan dari Indonesia ada dua peluncuran yang patut dicatat. Artikel ini merangkum semuanya, dengan sumber, plus apa yang sebaiknya kamu lakukan dengan kabar ini.

## 1. OpenAI GPT-6.1 Terra: model kerja kantoran yang setengah harga

OpenAI merilis GPT-6.1 Terra pada 26 Oktober 2026 (Cirebon Times, 28 Oktober 2026; Orasi, 28 Oktober 2026). Ini bukan model paling pintar di keluarga GPT-6.1, dan itu memang poinnya. Terra dirancang untuk pekerjaan profesional sehari-hari yang berbasis komputer: menyusun proposal, membaca gambar teknis, dan mengisi formulir. Model ini tersedia di ChatGPT Work, Codex, dan API.

Dua angka yang membuat rilis ini penting buat developer:

Pertama, harga. Tarif API standar Terra adalah 1 dolar per 1 juta token input dan 5 dolar per 1 juta token output, atau 50 persen lebih rendah dari GPT-5.6 Terra dan GPT-6.1 Sol. Buat otomasi bervolume tinggi, selisih seperti ini mengubah hitungan bisnis.

Kedua, kemampuan computer use. Terra bisa memahami apa yang tampil di layar dan mengambil tindakan di aplikasi, sehingga cocok untuk alur kerja lintas aplikasi. Pada Agents' Last Exam tingkat penalaran medium, Terra mencetak skor 15 poin persentase lebih tinggi dari GPT-5.6 Terra dengan biaya sekitar sepertiganya, dan setara GPT-6 Astra. Pada Terminal-Bench 4.0, OpenAI mengklaim keberhasilan 50,3 persen pada upaya maksimum, lebih dari dua kali lipat pendahulunya yang 21,5 persen.

Catatan penting: semua angka benchmark di atas berasal dari pengujian OpenAI sendiri, jadi anggap sebagai klaim vendor dan ukur sendiri dengan datamu.

## 2. Google Genie 4: dunia virtual yang bisa diarahkan sambil jalan

Sehari setelah Terra, Google DeepMind mengumumkan Genie 4 pada 27 Oktober 2026 (IndonesiaLink, 28 Oktober 2026). Genie 4 adalah world model: sistem AI yang mensimulasikan lingkungan interaktif lengkap dengan gerakan, reaksi, dan suara. Pengguna bisa memberi perintah bahasa sehari-hari di tengah simulasi, misalnya meminta hujan turun, menggeser kamera, atau menghadirkan karakter baru.

Bedanya dari pendahulunya adalah audio native dan live scene direction: suara ambient, musik, dan dialog interaktif ikut dihasilkan bersama perubahan visual. Menurut TechCrunch, adegan bisa tetap koheren sekitar dua menit, kira kira dua kali lipat model sebelumnya. Google mengakui keterbatasannya: detail yang melenceng, object permanence, konsistensi audio, dan keterbacaan teks.

Buat developer, Genie 4 saat ini lebih relevan sebagai sinyal arah daripada alat yang bisa langsung dipakai: game yang dibuat on the fly dan simulasi untuk melatih robot dan agen. Tapi jangan merencanakan produk di atasnya sampai akses umumnya jelas.

## 3. Google Gemini 4 Carbon: model untuk keamanan siber

Masih dari Google, Reuters melaporkan pada 28 Oktober 2026 bahwa Google meluncurkan Gemini 4 Carbon, model frontier yang fokus ke keamanan siber. Carbon diklaim punya performa state of the art untuk tugas keamanan siber seperti menemukan kerentanan, eksploitasi, dan patching perangkat lunak. Google menyebut Carbon menghasilkan kode yang aman dengan tingkat keberhasilan lebih dari dua kali lipat Gemini 4 Argon pada benchmark internal.

Harganya 2 dolar per 1 juta token input dan 10 dolar per 1 juta token output, sama dengan harga perkenalan Gemini 4 Argon. Akses awal diberikan ke subset defender keamanan siber lewat Fairwind Program Google.

Buat developer keamanan aplikasi, Carbon menarik karena model yang dilatih khusus menemukan kerentanan dan menulis patch bisa masuk ke pipeline code review, bukan cuma jadi chatbot. Karena aksesnya masih terbatas, siapkan pipeline review keamananmu sekarang supaya tinggal pakai saat model seperti ini tersedia umum.

## 4. Nvidia Nemotron 3.5 Transcribe: transkripsi open-weight 40 bahasa

Nvidia merilis Nemotron 3.5 Transcribe pada 28 Oktober 2026 (TechCrunch, 28 Oktober 2026). Model transkripsi open-weight gratis ini menangani audio 40 bahasa, menerjemahkan 31 bahasa ke dan dari bahasa Inggris, menangani rekaman sampai satu jam, dan membedakan sampai delapan pembicara. Nvidia mengklaim model ini mengungguli kompetitor pada Hugging Face Open ASR Leaderboard.

Model 30 miliar parameter ini diklaim bisa jalan di satu chip, dari controller robotik Jetson AGX Thor sampai GPU datacenter Blackwell. Nvidia juga merilis Granary versi 2, dataset speech open source untuk menyesuaikan model ke jargon industri tertentu.

Satu keterbatasan: Transcribe bekerja untuk audio rekaman, bukan livestream. Jadi cocok untuk transkripsi rapat dan arsip audio, tapi belum untuk caption real time. Rilis ini datang bersama gelombang model suara lain bulan ini, seperti Voxtral 3 dari Mistral dan Realtime dari ElevenLabs.

## 5. Liquid AI LFM3: model kecil untuk perangkat edge

Liquid AI merilis LFM3 pada 27 Oktober 2026, keluarga enam model open-weight di kisaran dua miliar parameter yang bercabang dari satu model dasar. Developer bisa memilih varian teks, vision, audio, multimodal, atau structured decision, daripada memuat semua kemampuan untuk setiap tugas. Menurut Local AI Zone, LFM3 mencatat rata rata skor 49,37, dibanding 47,24 untuk Qwen3.5-9B, sambil muat di sekitar 1 GB memori pada kuantisasi 4-bit. Buat developer Indonesia yang target penggunanya memakai HP kelas menengah atau VPS murah, model sekelas ini jauh lebih realistis dijalankan sendiri daripada model frontier.

## 6. Dari Indonesia: Pemuda.ai dan Sovereign Digital Technology Telkom

Dari dalam negeri, platform AI buatan Indonesia Pemuda.ai resmi diluncurkan pada 28 Oktober 2026, bertepatan dengan Hari Sumpah Pemuda (Industry.co.id, 28 Oktober 2026). Platform ini memperkenalkan Asmuni, asisten AI untuk kreator dan developer, plus Pemuda Token, Pemuda Studio untuk produksi video AI, dan Pemuda Satria untuk keamanan siber.

Kedua, TelkomGroup meluncurkan Sovereign Digital Technology pada 26 Oktober 2026 dalam rangkaian Danantara Technology Innovation Investment Forum (ItWorks, 28 Oktober 2026), mencakup AI Ready Data Center, AI ModelHub, National IoT Platform, dan PaDiSera. Buat developer lokal, AI ModelHub paling relevan karena infrastruktur model lokal bisa memangkas latensi dan biaya dibanding selalu memanggil API luar negeri. Di sisi enterprise global, Oracle juga mengumumkan kemitraan yang diperluas dengan OpenAI di Oracle AI World pada 27 Oktober 2026 (Unite.ai, 27 Oktober 2026).

## Apa artinya buat developer Indonesia

Kalau dirangkum jadi satu kalimat: minggu ini bukan soal model paling pintar, tapi soal model yang lebih murah, lebih kecil, dan lebih bisa bertindak. Tiga implikasinya:

Pertama, otomasi pekerjaan kantor berulang makin murah. Harga Terra yang setengah dari pendahulunya membuat tugas seperti entri faktur dan pemrosesan formulir jadi kandidat otomasi yang lebih masuk akal, terutama untuk UMKM dan tim kecil.

Kedua, suara dan model kecil adalah lahan yang masih terbuka. Transkripsi 40 bahasa dan model 2 miliar parameter yang jalan di perangkat murah membuka peluang produk lokal, misalnya transkripsi rapat berbahasa Indonesia.

Ketiga, jangan membangun di atas model yang masih preview. Gunakan waktu ini untuk menyiapkan pipeline dan prototipe dengan model yang sudah tersedia, supaya kamu tinggal mengganti modelnya saat akses umum dibuka.

## Coba sendiri minggu ini

Langkah paling masuk akal minggu ini bukan mencoba semua rilis sekaligus, tapi satu eksperimen kecil yang terukur. Ambil satu tugas berulang di pekerjaanmu, misalnya membaca faktur PDF lalu memasukkan datanya ke spreadsheet, dan ukur dulu berapa lama tugas itu memakan waktu secara manual.

Skrip Python berikut menghitung biaya bulanan tugas seperti itu dengan tarif Terra dan Carbon:

```python
# Tarif per 1 juta token: Terra $1 input / $5 output, Carbon $2 input / $10 output.

RATES = {
    "gpt-6.1-terra": (1.0, 5.0),
    "gemini-4-carbon": (2.0, 10.0),
}

def monthly_cost(model, input_tokens_per_task, output_tokens_per_task, tasks_per_month):
    input_rate, output_rate = RATES[model]
    cost_per_task = (
        input_tokens_per_task / 1_000_000 * input_rate
        + output_tokens_per_task / 1_000_000 * output_rate
    )
    return cost_per_task * tasks_per_month

# Contoh: 1 tugas = 3.000 token input + 500 output, 2.000 kali sebulan.
for model in RATES:
    cost = monthly_cost(model, 3000, 500, 2000)
    print(f"{model}: ${cost:.2f} per bulan")
```

Setelah angkanya masuk akal, uji modelnya dengan 20 sampai 50 contoh nyata dari datamu dan catat tingkat keberhasilannya. Kalau hasilnya di bawah ekspektasi, masalahnya hampir selalu ada di instruksi atau data, bukan di modelnya.

Pola panggilan Terra lewat API sama seperti model OpenAI lain lewat Responses API. Cek nama model yang persis di dokumentasi resmi sebelum dipakai di produksi:

```bash
curl https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-6.1-terra",
    "input": "Ringkas faktur berikut menjadi JSON dengan field vendor, tanggal, dan total."
  }'
```

## Kesalahan umum saat menyikapi rilis model baru

Kesalahan pertama adalah langsung memindahkan semua workload ke model baru pada hari rilis. Uji dengan datamu sendiri dulu, dengan sampel yang cukup, sebelum memindahkan traffic produksi.

Kesalahan kedua adalah mengabaikan biaya output. Banyak developer hanya melihat harga input yang murah, padahal tugas computer use menghasilkan output token yang jauh lebih banyak. Hitung total biaya per tugas, seperti contoh skrip di atas.

Kesalahan ketiga adalah mengirim data sensitif ke API tanpa memeriksa kebijakan retensi datanya. Cek dulu apakah penyedia menyimpan prompt untuk training, dan pertimbangkan model lokal untuk data yang paling sensitif.

Kesalahan keempat adalah membangun produk di atas model yang masih preview tertutup. Pakai model preview untuk belajar dan prototipe, tapi jangan jadikan fondasi produk yang sudah dijual ke pelanggan.

Arah industri minggu ini jelas: AI yang bertindak, bukan cuma menjawab, dengan harga yang makin turun dan ukuran yang makin kecil. Developer yang menang bukan yang paling cepat mencoba setiap rilis, tapi yang paling cepat mengukur satu tugas nyata dan membuktikan hasilnya dengan datanya sendiri.
