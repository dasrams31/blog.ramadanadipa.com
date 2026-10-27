---
title: Fine-tuning vs RAG vs Prompt: Kapan Pakai yang Mana
description: Prompt, RAG, atau fine-tuning? Pahami bedanya lewat kasus nyata dan contoh kode Python, supaya kamu tidak buang biaya training yang tidak perlu.
date: 2026-10-27
tags: [ai, rag, fine-tuning, prompt-engineering, python]
faq:
  - Apa beda RAG dan fine-tuning secara sederhana?
  - RAG memberi model akses ke dokumenmu saat menjawab, jadi jawaban berdasarkan data terbaru. Fine-tuning mengubah perilaku model lewat training, cocok untuk gaya dan format yang konsisten, bukan untuk menyimpan fakta yang sering berubah.
  - Harus mulai dari yang mana dulu?
  - Selalu mulai dari prompt engineering. Kalau jawaban masih salah karena model tidak tahu datamu, tambah RAG. Fine-tuning baru dipertimbangkan setelah dua langkah itu mentok dan kamu punya data training berkualitas.
  - Berapa data yang dibutuhkan untuk fine-tuning?
  - Untuk gaya dan format, puluhan sampai ratusan contoh berkualitas sering sudah cukup. Untuk pengetahuan baru yang luas, butuh jauh lebih banyak, dan itu biasanya tanda kamu lebih cocok pakai RAG.
  - Apakah fine-tuning membuat model tidak berhalusinasi?
  - Tidak. Fine-tuning tidak menjamin jawaban faktual. Kalau jawaban harus akurat terhadap dokumen tertentu, RAG dengan sitasi sumber jauh lebih bisa diandalkan.
---

Kamu punya aplikasi yang harus menjawab dari dokumen perusahaan, tapi model AI menjawab ngawur. Atau sebaliknya: jawabannya benar, tapi formatnya selalu berantakan. Dua masalah ini kelihatan mirip, tapi solusinya beda, dan salah pilih bisa berarti buang waktu berminggu-minggu plus biaya training yang tidak perlu.

Tiga teknik ini sering dibenturkan: prompt engineering, RAG, dan fine-tuning. Padahal di produksi tahun 2026, konsensus praktisinya sudah jelas: ketiganya bukan pesaing, tapi lapisan yang dipakai bersama untuk masalah yang berbeda.

## Tiga teknik, tiga masalah berbeda

**Prompt engineering** adalah instruksi kerja yang kamu tulis untuknya. Murah, bisa diubah dalam hitungan menit, tanpa training. Kamu menentukan peran, aturan, format output, dan contoh jawaban.

**RAG** adalah akses ke arsip perusahaan. Saat ada pertanyaan, sistem mencari dokumen yang relevan dan menyodorkannya ke model bersama pertanyaan. Model menjawab berdasarkan dokumen itu, bukan dari hafalannya.

**Fine-tuning** adalah pelatihan ulang. Kamu memberi ratusan contoh instruksi dan jawaban ideal, lalu bobot model disesuaikan supaya perilakunya berubah permanen. Cocok untuk gaya bahasa, format output, dan kosakata domain yang harus konsisten.

Satu kalimat dari panduan praktisi 2026 (dev.to): RAG mengajarkan model apa pengetahuan domainmu, fine-tuning mengajarkan model bagaimana berperilaku. Masalah fakta berarti masalah RAG, masalah perilaku berarti masalah fine-tuning.

## Mulai dari prompt, bukan dari training

Kesalahan paling umum: developer langsung loncat ke fine-tuning begitu model menjawab tidak sesuai harapan, padahal mayoritas kasus selesai di prompt.

Prompt yang baik itu spesifik soal tiga hal: peran, aturan, dan format. Bukan "kamu asisten hebat", tapi "kamu asisten CS toko ini, jawab hanya dari konteks yang diberikan, kalau tidak ada di konteks katakan tidak tahu, dan balas dalam JSON dengan field jawaban dan sumber".

Contoh prompt terstruktur yang langsung bisa dipakai:

```python
from openai import OpenAI

client = OpenAI(api_key="MASUKKAN_API_KEY_KAMU")

SYSTEM_PROMPT = """Kamu adalah asisten customer service Toko Maju.
Aturan:
1. Jawab HANYA dari konteks dokumen yang diberikan.
2. Kalau jawaban tidak ada di konteks, jawab persis: "Info itu tidak ada di dokumen kami, silakan hubungi CS."
3. Jangan mengarang harga, tanggal, atau kebijakan.
4. Balas dalam Bahasa Indonesia yang sopan dan singkat.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Konteks:\n"
                "Kebijakan retur: maksimal 14 hari setelah diterima, "
                "segel harus utuh.\n\n"
                "Pertanyaan: Apakah saya bisa retur barang yang sudah dibuka?"
            ),
        },
    ],
)
print(response.choices[0].message.content)
```

Aturan nomor 2 itu penting. Tanpa instruksi eksplisit untuk mengaku tidak tahu, model akan mengisi kekosongan dengan jawaban yang terdengar meyakinkan tapi salah. Prompt seperti ini gratis dan sering menaikkan kualitas jawaban lebih banyak daripada satu putaran fine-tuning.

Kapan prompt sudah tidak cukup? Saat konteks yang dibutuhkan terlalu besar untuk dimasukkan manual ke setiap pertanyaan, misalnya 500 halaman SOP. Di situlah RAG masuk.

## RAG: saat model harus tahu datamu

RAG bekerja dalam dua tahap: dokumenmu dipecah jadi chunk, diubah jadi vektor embedding, dan disimpan. Lalu setiap pertanyaan diubah jadi embedding juga, dan sistem mengambil chunk yang paling mirip untuk diserahkan ke model sebagai konteks.

Versi minimalnya bisa ditulis dengan Python standar, tanpa vector database. Contoh di bawah memakai cosine similarity murni, jadi kamu paham mekanismenya sebelum memakai pgvector:

```python
import math
from openai import OpenAI

client = OpenAI(api_key="MASUKKAN_API_KEY_KAMU")

documents = [
    "Retur maksimal 14 hari setelah barang diterima, segel harus utuh.",
    "Ongkir gratis untuk pembelian di atas Rp500.000 di Pulau Jawa.",
    "Garansi produk elektronik berlaku 1 tahun sejak tanggal pembelian.",
]

def embed(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)

doc_vectors = [embed(doc) for doc in documents]
query = "Berapa lama garansi produk elektronik?"
query_vector = embed(query)

ranked = sorted(
    zip(documents, doc_vectors),
    key=lambda pair: cosine_similarity(query_vector, pair[1]),
    reverse=True,
)
context = "\n".join(doc for doc, _ in ranked[:2])

answer = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Jawab hanya dari konteks berikut. Kalau tidak ada, katakan tidak tahu.",
        },
        {"role": "user", "content": f"Konteks:\n{context}\n\nPertanyaan: {query}"},
    ],
)
print(answer.choices[0].message.content)
```

Tiga keuntungan RAG yang tidak dimiliki fine-tuning:

1. **Data selalu segar.** Dokumen diubah, indeks diperbarui, jawaban ikut berubah. Tidak perlu retraining.
2. **Bisa disitasi.** Jawaban merujuk ke chunk dokumen, jadi sumbernya bisa ditampilkan ke user. Ini penting untuk CS, hukum, dan dokumen kebijakan.
3. **Murah untuk iterasi.** Salah ambil dokumen? Perbaiki chunking atau tambahkan reranking, tanpa menyentuh model.

Tapi RAG bukan gratis. Setiap query membayar token konteks tambahan, dan kualitasnya sangat bergantung pada kualitas retrieval. Panduan produksi dari ClawdBytes (13 Oktober 2026) menekankan hal yang sama: demo RAG selesai dalam satu sore, RAG produksi butuh set evaluasi 50 sampai 200 pertanyaan nyata, retrieval sadar hak akses, dan pipeline re-index otomatis.

Pakai RAG saat: informasinya sering berubah, korpusnya besar, atau jawaban harus bisa ditelusur ke sumbernya.

## Fine-tuning: saat masalahnya perilaku, bukan fakta

Fine-tuning layak dipertimbangkan dalam situasi sempit tapi nyata:

- Model selalu melanggar format output yang dibutuhkan, padahal contoh di prompt sudah banyak.
- Kamu butuh nada dan gaya brand yang konsisten di ribuan jawaban.
- Model kecil yang murah bisa menangani satu tugas sempit, misalnya klasifikasi tiket CS.
- Latensi dan biaya per query penting, dan model kecil bisa dilatih untuk tugas itu.

Yang tidak boleh dilakukan: fine-tuning untuk menyuntikkan fakta yang sering berubah. Contoh nyata dari Ravoid (2026): sebuah tim melatih model dengan dokumentasi produk untuk bot support. Saat peluncuran, hasilnya bagus. Lalu produk rilis tiap minggu, dokumen berubah tiap minggu, dan model terus mengutip fitur yang sudah dihapus. Mereka membayar retraining tiap minggu, tapi modelnya selalu tertinggal tujuh hari. RAG membuat setiap perubahan dokumen jadi re-embed murah, bukan retraining mahal.

Format data fine-tuning adalah JSONL berisi percakapan contoh:

```json
{"messages": [{"role": "system", "content": "Kamu asisten CS Toko Maju, jawab singkat dan sopan."}, {"role": "user", "content": "Apakah ada ongkir gratis?"}, {"role": "assistant", "content": "Ada, untuk pembelian di atas Rp500.000 di Pulau Jawa."}]}
```

Satu file berisi ratusan baris seperti ini, masing-masing satu contoh. Aturan praktisnya: kualitas mengalahkan jumlah. Seratus contoh yang konsisten dan sudah dicek manusia lebih baik daripada seribu contoh mentah. Sebelum training, siapkan set evaluasi terpisah untuk membuktikan model hasil training benar-benar lebih baik daripada model dasar plus prompt yang bagus.

## Cara memutuskan dalam 5 menit

Pakai alur ini setiap kali ragu:

1. **Apakah model tidak tahu datamu?** Ya, berarti butuh RAG. Tidak, lanjut.
2. **Apakah jawaban benar tapi gaya atau formatnya tidak konsisten meski prompt sudah spesifik?** Ya, berarti pertimbangkan fine-tuning.
3. **Apakah tugasnya sempit, bervolume tinggi, dan biaya per query jadi masalah?** Ya, berarti fine-tuning model kecil layak dihitung.
4. **Selain itu, tetap di prompt engineering.** Ukur dulu dengan set evaluasi sebelum naik level.

## Kesalahan umum pemula (dan cara menghindarinya)

**1. Fine-tuning untuk mengajar fakta.** Ini kesalahan termahal. Dokumen berubah, model tertinggal, kamu retraining tanpa henti. Pakai RAG untuk fakta.

**2. RAG tanpa evaluasi.** Tanpa 50 sampai 200 pertanyaan uji, kamu tidak tahu apakah chunking baru memperbaiki atau merusak jawaban. Buat set evaluasi sebelum menulis kode retrieval.

**3. Chunk terlalu besar atau terlalu kecil.** Chunk sebesar satu halaman penuh membuat konteks penuh sampah. Chunk satu kalimat membuat konteks kehilangan makna. Mulai dari 300 sampai 500 kata per chunk dengan sedikit overlap, lalu ukur.

**4. Prompt tanpa aturan "tidak tahu".** Model yang dipaksa selalu menjawab akan berhalusinasi. Instruksi eksplisit untuk mengaku tidak tahu adalah fitur keamanan termurah yang ada.

**5. Mengabaikan hak akses di retrieval.** Dokumen internal tidak semuanya boleh dibaca semua user. Retrieval harus memfilter berdasarkan izin user, bukan sekadar kemiripan vektor. Ini yang membedakan demo dan produksi.

**6. Melatih dari data mentah tanpa dibersihkan.** Data training yang tidak konsisten menghasilkan model yang tidak konsisten juga. Cek contoh satu per satu, terutama format dan nada jawabannya.

## Langkah praktis yang bisa dicoba hari ini

1. Tulis system prompt dengan aturan eksplisit seperti contoh pertama, lalu uji dengan 10 pertanyaan sulit, termasuk yang jawabannya tidak ada di konteks.
2. Bangun RAG minimal dari contoh kedua dengan 20 dokumenmu sendiri, lalu ukur berapa yang dijawab benar dan berapa yang berhalusinasi.
3. Perbaiki chunking dan tambahkan aturan "tidak tahu" sampai jawaban yang berhalusinasi mendekati nol.
4. Baru setelah itu, kumpulkan 100 contoh jawaban ideal dan evaluasi apakah fine-tuning benar-benar menaikkan skor dibanding prompt plus RAG.
5. Kalau tidak ada kenaikan yang terukur, jangan fine-tuning. Waktumu lebih berguna untuk memperbaiki retrieval dan evaluasi.

Prompt dulu, RAG saat datamu yang jadi masalah, fine-tuning saat perilakunya yang jadi masalah. Ukur setiap langkah.

## Sumber

- dev.to, "RAG vs Fine-Tuning vs Context Stuffing" (2026): prompt dulu, RAG saat skala atau kesegaran menuntut, fine-tuning hanya saat konsistensi perilaku gagal dicapai cara lain.
- dev.to, "Fine-tuning Claude vs GPT vs Llama in Production" (2026): fine-tuning untuk gaya dan format, RAG untuk pengetahuan domain.
- ClawdBytes, "Stop Fine-Tuning Your Chatbot" (13 Oktober 2026): vendor besar merekomendasikan prompt dan retrieval sebelum fine-tuning, plus checklist produksi seperti set evaluasi dan retrieval sadar hak akses.
- Ravoid, "Stop Asking RAG vs Fine-Tuning. Ask This." (2026): kerangka kecepatan pengetahuan versus volume query, dan contoh tim yang membayar retraining mingguan untuk dokumen yang berubah tiap minggu.
