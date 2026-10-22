---
title: Prompt Engineering Praktis untuk Developer: Contoh Langsung
description: Prompt engineering praktis untuk developer: contoh system prompt, struktur prompt XML, prompt chaining, dan cara evaluasi hasil AI dengan kode nyata yang bisa langsung dicoba.
date: 2026-10-22
tags: [prompt engineering, ai, developer]
faq:
  - Apa itu prompt engineering untuk developer?
  - Prompt engineering adalah teknik menyusun instruksi, konteks, dan aturan format agar model AI menghasilkan output yang konsisten dan bisa dipakai langsung di aplikasi, bukan sekadar teks acak.
  - Kenapa prompt yang bagus di ChatGPT gagal saat dipakai lewat API?
  - Karena lewat API kamu harus mengatur sendiri system prompt, temperature, dan format output. Interface chat sudah menyembunyikan banyak konfigurasi ini, jadi pindahkan semua asumsi tersembunyi itu ke prompt.
  - Berapa temperature ideal untuk tugas pemrograman?
  - Pakai 0 sampai 0.3 untuk tugas deterministik seperti generate query SQL, dokumentasi, atau klasifikasi. Nilai di atas 0.7 cocok untuk brainstorming, bukan untuk output yang harus konsisten.
  - Bagaimana cara menguji kualitas prompt secara objektif?
  - Siapkan 20 sampai 100 contoh input nyata, definisikan kriteria lolos atau gagal per output, lalu bandingkan prompt kandidat secara otomatis. Penilaian berdasarkan perasaan adalah jebakan paling umum di production.
---

Setelah menulis puluhan prompt untuk fitur AI di berbagai project, saya sampai pada satu kesimpulan: prompt engineering itu bukan sulap kata, melainkan desain sistem. Di tahun 2026, model memang jauh lebih pintar, tapi sensitivitas terhadap cara kita bertanya tidak hilang. Kabar baiknya, teknik yang benar-benar bekerja bisa diringkas jadi beberapa pola konkret. Artikel ini berisi contoh langsung yang bisa kamu salin dan pakai.

## Pola 1: System Prompt yang Eksplisit

Kesalahan paling umum: semua instruksi ditaruh di user message, lalu heran kenapa perilakunya berubah-ubah. Pisahkan peran tetap ke system prompt, dan data dinamis ke user message. Contoh untuk API OpenAI-compatible (bisa dipakai ke model lokal juga, karena endpoint-nya standar):

```javascript
const response = await fetch("http://localhost:11434/v1/chat/completions", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "qwen3:8b",
    temperature: 0.2,
    messages: [
      {
        role: "system",
        content: [
          "Kamu adalah asisten yang mengubah deskripsi bahasa Indonesia",
          "menjadi query PostgreSQL yang valid.",
          "Aturan: hanya jawab dengan satu blok kode SQL, tanpa penjelasan.",
          "Jangan pernah mengubah struktur tabel atau menghapus data.",
        ].join(" "),
      },
      {
        role: "user",
        content: "Tampilkan 10 produk dengan stok paling sedikit.",
      },
    ],
  }),
});

const sql = await response.json();
console.log(sql.choices[0].message.content);
```

Catatan penting: aturan "jangan menghapus data" bukan sekadar formalitas. Tanpa guardrail eksplisit, model bisa saja menjawab permintaan seperti "bersihkan tabel produk lama" dengan `DELETE FROM products`. Aturan negatif memang berguna di sini, bertolak belakang dengan saran lama yang bilang "selalu pakai instruksi positif". Untuk constraint keamanan, kata "jangan" justru wajib ditulis tegas.

## Pola 2: XML Tag untuk Memisahkan Konteks

Prompt panjang yang mencampur instruksi, data, dan contoh adalah sumber halusinasi. Bungkus tiap bagian dengan tag XML, terutama untuk keluarga model Claude yang memang dilatih memahami struktur ini. Contoh prompt RAG sederhana dalam Python:

```python
PROMPT = """<role>
Kamu adalah asisten dokumentasi internal tim.
</role>

<konteks>
{dokumen_retrieval}
</konteks>

<tugas>
Jawab pertanyaan user HANYA berdasarkan bagian <konteks>.
Jika jawaban tidak ada di konteks, balas persis: "Tidak ditemukan di dokumentasi."
</tugas>

<format>
- Maksimal 3 kalimat.
- Bahasa Indonesia santai.
</format>

<pertanyaan>
{pertanyaan_user}
</pertanyaan>
"""
```

Hasilnya jauh lebih konsisten daripada prompt satu paragraf. Model tahu persis mana instruksi, mana data, mana format. Ini juga memudahkan debugging: kalau output meleset, kamu tahu bagian mana yang perlu diperketat.

## Pola 3: Prompt Chaining, Bukan Satu Prompt Raksasa

Godaan terbesar developer: memasukkan seluruh workflow ke satu prompt 2.000 kata, lalu frustrasi karena hasilnya tidak stabil. Pecah jadi rantai kecil, tiap tahap punya tugas tunggal. Contoh workflow "bug report menjadi patch":

```bash
# Tahap 1: analisis
curl -s http://localhost:11434/v1/chat/completions -d '{
  "model": "qwen3:8b",
  "temperature": 0,
  "messages": [{"role": "user",
    "content": "Analisis log error berikut. Identifikasi akar masalah dalam 2 kalimat. Log: '"$(cat error.log)"'"}]
}'

# Tahap 2: patch (output tahap 1 jadi input tahap 2)
# Tahap 3: tulis test untuk patch tersebut
```

Tiap tahap bisa diuji, di-log, dan diganti modelnya secara terpisah. Kalau tahap analisis jelek, kamu perbaiki prompt analisis saja, bukan merombak semuanya. Ini pola yang sama dipakai pipeline Homeless Media dan banyak sistem production: keandalan datang dari dekomposisi, bukan dari prompt yang makin panjang.

## Pola 4: Few-Shot dengan Contoh yang Pendek

Untuk tugas dengan format ketat (ekstraksi data, klasifikasi, konversi format), 2 sampai 4 contoh berkualitas mengalahkan paragraf instruksi. Aturannya: contoh pendek, fokus pada format, bukan isi. Jangan kirim 20 contoh, karena token membengkak dan manfaatnya mentok di sekitar 10 contoh menurut benchmark yang dirangkum FutureAGI awal tahun ini.

Contoh buruk versus contoh bagus untuk tugas debugging:

```
Buruk : "Fix this."
Bagus : "Identifikasi bug pada kode berikut, jelaskan akar masalahnya,
         lalu berikan patch terkecil yang aman beserta satu unit test."
```

Perbedaannya: yang bagus mendefinisikan peran (identifikasi, jelaskan, berikan), batasan (patch terkecil), dan format output (beserta unit test). Model tidak menebak ekspektasimu, ia mengikuti kontrak yang kamu tulis.

## Pola 5: Evaluasi dengan Harness, Bukan Perasaan

Ini teknik yang memisahkan hobi dari production. Menurut tulisan Technolynx yang merangkum tren 2026, mode kegagalan dominan adalah "vibes-based prompt tuning": prompt terasa bagus di 3 contoh, lalu hancur di data nyata. Solusinya: buat set evaluasi kecil dan skrip pembanding otomatis.

```python
import json, subprocess

CASES = [
    {"input": "Tampilkan total penjualan per bulan tahun ini",
     "must_contain": ["GROUP BY", "SUM"]},
    {"input": "Cari user yang belum login 30 hari",
     "must_contain": ["WHERE", "INTERVAL"]},
]

def run_prompt(prompt_template, user_input):
    prompt = prompt_template.format(pertanyaan=user_input)
    out = subprocess.run(
        ["ollama", "run", "qwen3:8b", prompt],
        capture_output=True, text=True, timeout=120,
    )
    return out.stdout

def score(template):
    passed = 0
    for case in CASES:
        result = run_prompt(template, case["input"]).upper()
        if all(k in result for k in case["must_contain"]):
            passed += 1
    return passed, len(CASES)

for name, template in [("v1", TEMPLATE_V1), ("v2", TEMPLATE_V2)]:
    p, total = score(template)
    print(f"{name}: {p}/{total} lolos")
```

Dengan harness seperti ini, kamu bisa membandingkan dua versi prompt dalam hitungan menit, bukan berdasarkan "kayaknya lebih bagus". Tools seperti Promptfoo atau LangSmith membantu di skala lebih besar, tapi skrip 30 baris di atas sudah cukup untuk memulai.

## Kesalahan Umum Pemula

Pertama, instruksi samar. "Buatkan artikel yang bagus" menghasilkan teks generik. Sebutkan audiens, panjang, format, dan batasan secara eksplisit. Kedua, lupa format output. Kalau API-mu butuh JSON, tulis skemanya di prompt, atau lebih baik pakai structured output bawaan provider. Parsing teks bebas dengan regex adalah sumber bug yang tidak perlu.

Ketiga, temperature dibiarkan default untuk tugas deterministik. Default 0.7 sampai 1.0 cocok untuk ngobrol, buruk untuk generate SQL atau klasifikasi. Turunkan ke 0 sampai 0.3. Keempat, tidak menguji lintas model. Prompt yang bagus di satu model bisa butuh penyesuaian di model lain, apalagi kalau kamu berencana pindah dari API cloud ke model lokal seperti Qwen atau Llama untuk menghemat biaya.

## Langkah Praktis Hari Ini

Ambil satu fitur AI yang sedang kamu bangun, lalu lakukan tiga hal ini berurutan. Pertama, pindahkan semua aturan tetap ke system prompt dan biarkan user message hanya membawa data. Kedua, bungkus bagian prompt dengan tag XML dan turunkan temperature ke 0.2. Ketiga, buat 20 contoh input nyata dan skrip evaluasi sederhana seperti di atas, lalu bandingkan sebelum dan sesudah perubahan.

Kamu akan kaget betapa banyak "masalah model" yang ternyata masalah prompt. Di tahun 2026, prompt engineering bukan lagi soal merangkai kata yang puitis. Ini soal presisi linguistik, desain konteks, dan arsitektur constraint, persis seperti menulis kode yang bagus. Bedanya, compiler-nya adalah model bahasa, dan test suite-nya kamu tulis sendiri.
