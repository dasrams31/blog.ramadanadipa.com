---
title: Biaya API AI 2026: Model Lokal vs Cloud, Mana Lebih Hemat?
description: Harga API AI November 2026, dari $0,10 sampai $50 per juta token. Hitung titik impas model lokal vs cloud, plus contoh kode router hemat biaya.
cover: /assets/img/covers/biaya-api-ai-model-lokal-vs-cloud-cara-hemat.jpg
date: 2026-11-10
tags: [biaya-api-ai, llm, model-lokal, cloud, developer]
faq:
  - Berapa biaya API AI per 1 juta token di November 2026?
  - Model kecil seperti GPT-6 Luna dan Claude Haiku 5.5 dipatok $0,10 input dan $0,50 output per 1 juta token, kelas menengah seperti GPT-6.1 Sol dan Claude Sonnet 5.5 di $2 dan $10, sedangkan flagship seperti GPT-6 Astra dan Claude Fable 5.1 di $10 dan $50. Harga dicek dari halaman resmi tiap penyedia pada 3 November 2026.
  - Apakah menjalankan model AI lokal lebih murah daripada API cloud?
  - Tergantung pemakaian. Kalau pemakaianmu sporadis, API cloud jauh lebih murah. Model lokal baru menang kalau pemakaianmu berat dan konsisten, misalnya jutaan token setiap hari, karena biaya hardware-nya tetap sedangkan biaya cloud naik mengikuti pemakaian.
  - Model lokal apa yang bagus untuk developer Indonesia?
  - Qwen3 Coder 30B untuk coding dan Llama 4 8B untuk tugas ringan adalah pilihan populer karena bobotnya terbuka dan bisa jalan di GPU konsumen. Untuk tugas sederhana, model kecil 7B sampai 8B sering sudah cukup dan jauh lebih murah dijalankan.
  - Bagaimana cara paling cepat menurunkan tagihan API AI?
  - Pakai model kecil untuk tugas mudah, aktifkan prompt caching untuk konteks yang berulang, dan kirim pekerjaan yang tidak mendesak lewat batch API yang umumnya memberi diskon 50 persen. Tiga langkah ini saja bisa memangkas tagihan sampai separuh tanpa mengganti arsitektur.
---

Tagihan API AI pertamaku dulu bikin kaget. Aplikasi chatbot kecil, trafiknya belum seberapa, tapi invoice bulan pertama sudah tembus ratusan ribu rupiah. Bukan karena modelnya mahal, tapi karena aku memakai model flagship untuk semua hal, termasuk tugas sepele seperti mengklasifikasi satu kalimat. Kesalahan itu umum, dan solusinya bukan berhenti memakai AI, melainkan paham struktur harganya lalu memilih jalur yang tepat: API cloud, model lokal, atau gabungan keduanya.

Artikel ini membandingkan biaya keduanya dengan angka nyata per November 2026, menghitung titik impasnya, dan memberi contoh kode router yang bisa langsung kamu pakai supaya tagihanmu tidak bocor lagi.

## Harga API cloud per November 2026

Semua harga di bawah ini dalam dolar AS per 1 juta token, tier standar, dan diambil dari halaman harga resmi tiap penyedia yang dicek pada 3 November 2026 menurut perbandingan Klevere.ai. Harga bisa berubah, jadi selalu cek halaman resmi sebelum masuk production.

| Model | Input | Output | Kelas |
| --- | --- | --- | --- |
| GPT-6 Luna | $0,10 | $0,50 | Kecil |
| Claude Haiku 5.5 | $0,10 | $0,50 | Kecil |
| Gemini 3.5 Flash-Lite | $0,30 | $2,50 | Kecil |
| Gemini 3.8 Flash | $0,75 | $3,75 | Menengah |
| GPT-6.1 Sol | $2,00 | $10,00 | Menengah |
| Claude Sonnet 5.5 | $2,00 | $10,00 | Menengah |
| Claude Opus 5.5 | $4,00 | $20,00 | Flagship |
| GPT-6 Astra | $10,00 | $50,00 | Flagship |
| Claude Fable 5.1 | $10,00 | $50,00 | Flagship |

Dua pola langsung terlihat. Pertama, output token harganya 5 sampai 8 kali lipat dari input token, jadi model yang banyak "ngomong" jauh lebih mahal daripada yang banyak "membaca". Kedua, jarak harga antar kelas sangat lebar: satu juta output token di model flagship harganya 100 kali lipat dibanding model kecil.

Ada satu peringatan soal harga promo. Gemini 4 Argon saat ini dipatok $2 input dan $10 output, tapi halaman harga Google menyebutkan tarif itu naik jadi $4 dan $20 mulai 1 Desember 2026. Gemini 3.8 Flash juga naik dari $0,75 dan $3,75 menjadi $1,50 dan $7,50 mulai 1 Januari 2027. Kalau kamu membangun anggaran tahunan di atas harga promo, sisakan margin untuk kenaikan ini.

## Kenapa tagihan API membengkak

Harga per token itu cuma separuh cerita. Tiga hal ini yang biasanya bikin tagihan membengkak diam-diam.

Pertama, konteks yang dikirim berulang. Aplikasi RAG atau coding agent mengirim riwayat percakapan dan potongan dokumen yang sama di setiap request. Kalau tiap request membawa 30 ribu token input dan kamu menjalankan 150 langkah per hari, itu hampir 100 juta token input per bulan hanya untuk konteks yang itu-itu saja. Solusinya prompt caching: penyedia seperti Anthropic dan OpenAI memberi harga cache read yang sangat murah, misalnya $0,20 per juta token untuk Claude Opus 5.5, dibanding $4 untuk input segar.

Kedua, memakai model flagship untuk tugas receh. Klasifikasi sentimen, ekstraksi field dari struk, dan ringkasan satu paragraf tidak butuh model $50 per juta output token. Model kecil di $0,50 per juta output token menyelesaikan tugas itu dengan kualitas yang sama untuk sebagian besar kasus.

Ketiga, tidak ada batas dan tidak ada log biaya. Tanpa pencatatan per request, kamu baru sadar ada yang salah saat invoice datang. Padahal satu loop retry yang tidak dibatasi atau satu user yang mengirim prompt raksasa bisa menghabiskan anggaran seminggu dalam satu malam.

## Berapa biaya model lokal sebenarnya

Model lokal sering dipromosikan sebagai "token gratis", dan itu menyesatkan. Tokennya memang tidak ditagih per pemakaian, tapi biayanya pindah ke hardware, listrik, dan waktumu. Rumus jujurnya begini:

```
biaya per 1 juta token (lokal) =
  (harga hardware / bulan amortisasi + listrik + waktu admin)
  / (token yang dihasilkan per bulan / 1.000.000)
```

Contoh nyata dari perbandingan Presenc.ai yang diperbarui Oktober 2026: NVIDIA DGX Spark harganya $4.699, dan total biaya kepemilikannya sekitar $1.750 per tahun. Untuk model kelas 7B dengan utilisasi workstation 30 persen, titik impas melawan API cloud setara tercapai dalam 4 sampai 9 bulan. Tapi untuk pemakaian sporadis di bawah 10 persen utilisasi, cloud jauh lebih murah dan titik impasnya molor sampai 2 sampai 4 tahun.

Perbandingan lain dari Decode the Future, September 2026, memakai workload coding agent: 300 juta token input dan 20 juta token output per bulan, dengan 70 persen cache hit. Hasilnya Claude Sonnet 5.5 sekitar $475 per bulan, Claude Opus 5.5 sekitar $907 per bulan, sedangkan klaster empat Mac Studio yang menjalankan model yang sama sekitar $1.400 per bulan. Di workload itu, cloud menang telak.

Untuk developer Indonesia, contoh dari Velona.in juga menarik: developer yang menjalankan coding agent seharian penuh menghabiskan sekitar 983 rupee per bulan lewat API DeepSeek V4 Flash, sementara GPU sendiri yang mampu menjalankan Qwen3 Coder 30B menghabiskan sekitar 9.100 rupee per bulan kalau dihitung penyusutan tiga tahun plus listrik. Sekali lagi, cloud menang untuk pemakaian perorangan.

Kuncinya adalah utilisasi. Hardware yang menyala 24 jam tapi cuma dipakai satu jam sehari adalah hardware yang mahal. Hardware yang dipakai terus menerus oleh banyak user adalah hardware yang murah.

## Titik impas: kapan lokal menang, kapan cloud menang

Dari angka-angka di atas, aturan praktisnya seperti ini.

Pakai API cloud kalau pemakaianmu tidak menentu, trafikmu masih kecil, kamu butuh model paling pintar untuk tugas sulit, atau datamu boleh keluar dari servermu. Ini kondisi sebagian besar developer indie dan startup tahap awal. Mulai dari model kecil, naik kelas hanya untuk tugas yang terbukti gagal di model kecil.

Pakai model lokal kalau kamu memproses jutaan token setiap hari secara konsisten, datamu tidak boleh keluar dari mesinmu karena alasan hukum atau kontrak, kamu butuh jalan offline, atau kamu sudah punya hardware-nya. Model open weight yang disajikan lewat API cloud pihak ketiga juga patut dilirik: Llama 4 8B dan Qwen3 32B disajikan di kisaran $0,10 sampai $0,50 per juta output token, jadi kamu dapat harga nyaris lokal tanpa mengurus hardware.

Jalur yang paling masuk akal untuk kebanyakan orang adalah hybrid: model kecil lokal atau model murah di cloud untuk 80 persen tugas rutin, model flagship di cloud hanya untuk 20 persen tugas yang benar-benar sulit. Keputusan ini bisa dibuat otomatis oleh router di kode, bukan oleh tebakan.

## Contoh kode: router hemat biaya

Contoh berikut adalah router sederhana di Python. Tugas mudah dikirim ke model lokal lewat Ollama, tugas sulit ke API cloud, dan setiap request dicatat biayanya ke file CSV supaya kamu bisa audit tagihanmu sendiri. Simpan API key di environment variable, jangan pernah ditulis langsung di kode.

```python
import csv
import json
import os
import urllib.request
from datetime import datetime

# Harga per 1 juta token, dicek dari halaman resmi 3 November 2026.
# Perbarui angka ini kalau penyedia mengubah tarifnya.
PRICES = {
    "local-qwen3-8b": {"input": 0.0, "output": 0.0},
    "gpt-6-luna": {"input": 0.10, "output": 0.50},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00},
}

# Kata kunci tugas berat: kalau prompt mengandung salah satunya,
# naik kelas ke model cloud yang lebih pintar.
HARD_KEYWORDS = ["refactor", "arsitektur", "debug", "keamanan", "optimasi query"]

LOG_FILE = "ai_cost_log.csv"


def is_hard_task(prompt: str) -> bool:
    lowered = prompt.lower()
    return any(word in lowered for word in HARD_KEYWORDS)


def call_local(prompt: str) -> str:
    payload = json.dumps({
        "model": "qwen3:8b",
        "prompt": prompt,
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)["response"]


def call_cloud(prompt: str, model: str) -> str:
    # Contoh memakai endpoint yang kompatibel dengan OpenAI.
    # Ganti base URL dan nama model sesuai penyedia yang kamu pakai.
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)["choices"][0]["message"]["content"]


def log_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICES[model]
    cost = (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000
    exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "model", "input_tokens", "output_tokens", "cost_usd"])
        writer.writerow([datetime.now().isoformat(), model, input_tokens, output_tokens, round(cost, 6)])
    return cost


def ask(prompt: str) -> str:
    # Estimasi kasar: 1 token kira-kira 4 karakter teks.
    # Untuk tagihan akurat, pakai angka pemakaian dari respons API.
    input_tokens = max(1, len(prompt) // 4)
    if is_hard_task(prompt):
        model = "claude-sonnet-5-5"
        answer = call_cloud(prompt, model)
    else:
        model = "local-qwen3-8b"
        answer = call_local(prompt)
    output_tokens = max(1, len(answer) // 4)
    cost = log_cost(model, input_tokens, output_tokens)
    print(f"[{model}] cost: ${cost:.6f}")
    return answer


if __name__ == "__main__":
    print(ask("Ringkas dokumen ini dalam 3 poin: ..."))
    print(ask("Refactor fungsi pembayaran ini supaya aman dari race condition: ..."))
```

Tiga detail di kode ini yang penting. Pertama, klasifikasi tugasnya eksplisit dan bisa kamu ubah: tambah kata kunci atau ganti dengan skor kompleksitas dari model kecil. Kedua, biaya dicatat per request ke CSV, jadi kamu bisa membuka file itu tiap akhir minggu dan melihat model mana yang paling banyak makan anggaran. Ketiga, estimasi tokennya kasar, jadi untuk tagihan akurat pakai angka `usage` yang dikembalikan API dan hitung dari sana.

Untuk melihat total biaya sejauh ini dari terminal, satu baris awk cukup:

```bash
awk -F, 'NR > 1 {sum += $5} END {printf "Total biaya AI: $%.4f\n", sum}' ai_cost_log.csv
```

## Kesalahan umum pemula

Kesalahan pertama adalah memakai satu model untuk semua tugas. Ini paling mahal dan paling mudah diperbaiki: petakan tugasmu ke tiga kelas, kecil, menengah, dan flagship, lalu turunkan kelasnya sampai kualitasnya mulai terasa kurang.

Kesalahan kedua adalah mengabaikan prompt caching. Kalau aplikasimu mengirim system prompt dan dokumen yang sama berulang kali, caching bisa memangkas biaya input sampai 90 persen. Cek apakah penyediamu mendukungnya, lalu aktifkan, karena sering kali ini cuma satu parameter tambahan di request.

Kesalahan ketiga adalah tidak membatasi output. Model yang dibiarkan menjawab bebas bisa menghabiskan ribuan token output untuk jawaban yang sebenarnya cukup satu paragraf. Set `max_tokens` yang masuk akal dan minta format jawaban yang ringkas di system prompt.

Kesalahan keempat adalah membeli GPU dulu, menghitung kemudian. Hitung dulu berapa token yang benar-benar kamu hasilkan per bulan. Kalau angkanya di bawah 50 juta token, hampir pasti API cloud lebih murah daripada cicilan hardware, dan uangnya lebih baik dipakai untuk hal lain.

Kesalahan kelima adalah lupa harga promo punya tanggal kedaluwarsa. Gemini 4 Argon naik harga 1 Desember 2026, Gemini 3.8 Flash naik 1 Januari 2027. Catat tanggal-tanggal itu di kalendermu kalau aplikasimu bergantung pada model tersebut.

## Langkah praktis yang bisa langsung dicoba

Mulai hari ini, lakukan lima langkah ini secara berurutan. Pertama, buka dashboard pemakaian penyedia AI yang kamu pakai dan catat berapa token input dan output bulan lalu. Kedua, hitung tagihanmu dengan harga terbaru dari halaman resmi, bukan dari ingatan. Ketiga, pisahkan tugasmu jadi mudah dan sulit, lalu pindahkan semua tugas mudah ke model kecil yang harganya $0,10 sampai $0,50 per juta token. Keempat, aktifkan prompt caching untuk konteks yang berulang. Kelima, pasang pencatatan biaya seperti contoh kode di atas, lalu evaluasi lagi setelah dua minggu.

Kalau setelah dua minggu tagihanmu turun kurang dari 30 persen, kemungkinan besar masalahnya bukan di pemilihan model, melainkan di desain prompt: konteks yang dikirim terlalu besar atau percakapan yang tidak pernah diringkas. Di titik itu, perbaiki retrieval dan manajemen konteks dulu sebelum menyalahkan harga.

## Sumber

Harga model per November 2026 dari perbandingan Klevere.ai yang mengecek langsung halaman harga resmi OpenAI, Anthropic, dan Google pada 3 November 2026. Perbandingan biaya lokal vs cloud dari Presenc.ai, diperbarui Oktober 2026, dan Decode the Future, 28 September 2026. Contoh biaya coding agent harian dari Velona.in, 16 Oktober 2026. Kenaikan harga Gemini 4 Argon dan Gemini 3.8 Flash dari halaman harga resmi Google, dikutip lytvynov-production.com dan aimodelcalc.com, November 2026.
