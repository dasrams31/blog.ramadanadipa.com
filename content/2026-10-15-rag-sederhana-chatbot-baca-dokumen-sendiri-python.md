---
title: RAG Python: Chatbot yang Bisa Baca Dokumen Kamu Sendiri
description: Pelajari RAG dari nol: bikin chatbot baca dokumen sendiri pakai Python, pilihan embedding model lokal terbaik 2026, dan jebakan umum yang wajib dihindari.
date: 2026-10-15
tags: [rag, python, ai, embedding, chatbot]
faq:
  - Apa itu RAG dalam AI?
  - RAG (Retrieval-Augmented Generation) adalah teknik membuat LLM menjawab berdasarkan dokumen yang kamu berikan. Dokumen dipecah jadi potongan kecil, diubah jadi embedding, lalu potongan paling relevan disisipkan ke prompt sebelum LLM menjawab.
  - Apa bedanya RAG dan fine-tuning model AI?
  - Fine-tuning mengubah bobot model secara permanen lewat training yang mahal dan lama. RAG tidak mengubah model sama sekali, cukup tambah dokumen baru lalu index ulang. Untuk data yang sering berubah, RAG jauh lebih praktis dan murah.
  - Model embedding apa yang bagus untuk RAG lokal di 2026?
  - Qwen3-Embedding-0.6B jadi pilihan default terbaik (1024 dimensi, konteks 32K, lisensi Apache 2.0). Untuk dokumen Indonesia, BAAI/bge-m3 unggul karena multilingual dan lisensinya MIT. Keduanya bisa jalan di CPU.
  - Berapa biaya membuat chatbot RAG sederhana?
  - Bisa nol rupiah kalau full lokal: embedding model open source di CPU plus LLM lokal seperti Llama via llama.cpp. Kalau pakai API cloud, biaya utamanya di embedding sekali saat indexing dan token LLM tiap pertanyaan, biasanya masih hitungan ribu rupiah untuk skala kecil.
---

Aku pernah dapat pertanyaan menarik: bisa nggak bikin chatbot yang menjawab berdasarkan SOP internal perusahaan, bukan dari pengetahuan umum model AI? Jawabannya bisa, dan tekniknya namanya **RAG** (Retrieval-Augmented Generation).

RAG adalah cara paling praktis membuat AI "membaca" dokumen kamu sendiri: PDF manual, dokumentasi internal, catatan kuliah, apa pun. Tanpa training ulang model, tanpa biaya fine-tuning yang mahal. Artikel ini menunjukkan pipeline lengkapnya dengan Python, dari nol sampai chatbot yang bisa ditanya.

## Cara kerja RAG dalam 3 langkah

Bayangkan RAG seperti asisten riset yang super cepat:

1. **Indexing.** Dokumen kamu dipecah jadi potongan kecil (disebut *chunk*). Tiap chunk diubah jadi *embedding*, yaitu deretan angka yang mewakili makna teks. Semua embedding disimpan.
2. **Retrieval.** Saat ada pertanyaan, pertanyaan itu juga diubah jadi embedding. Sistem mencari chunk yang maknanya paling mirip dengan pertanyaan memakai perhitungan *cosine similarity*.
3. **Generation.** Chunk terpilih disisipkan ke dalam prompt, lalu LLM diminta menjawab **hanya berdasarkan konteks tersebut**.

Kenapa tidak fine-tuning saja? Fine-tuning itu mahal, lama, dan setiap data berubah kamu harus training ulang. Dengan RAG, dokumen baru cukup di-index ulang dalam hitungan menit. Data dan model terpisah, jadi keduanya bisa diganti independen.

## Langkah 1: pecah dokumen jadi chunk

Embedding model punya batas panjang teks yang bisa diproses sekaligus. Dokumen utuh jelas kebesaran, jadi kita pecah jadi potongan 500 sampai 1000 karakter. Tambahkan *overlap* supaya kalimat yang terpotong di batas chunk tidak kehilangan makna.

```python
def chunk_text(text, max_chars=800, overlap=150):
    """Pecah teks panjang jadi potongan kecil dengan overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks

teks = open("dokumen.txt", encoding="utf-8").read()
chunks = chunk_text(teks)
print(f"Dokumen dipecah jadi {len(chunks)} chunk")
```

Fungsi ini murni Python standar, tidak butuh library apa pun. Untuk PDF, kamu bisa ekstrak teksnya dulu dengan library seperti `pypdf`, lalu hasilnya dilempar ke fungsi yang sama.

## Langkah 2: ubah chunk jadi embedding

Embedding mengubah teks jadi vektor angka. Dua teks yang maknanya mirip akan punya vektor yang arahnya mirip. Kita pakai `sentence-transformers`, library standar untuk ini.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
embeddings = model.encode(chunks, normalize_embeddings=True)
print(f"{len(chunks)} chunk, tiap embedding {embeddings.shape[1]} dimensi")
```

Parameter `normalize_embeddings=True` penting: vektor yang sudah dinormalisasi membuat perhitungan kemiripan di langkah berikutnya jadi sekadar perkalian dot product yang cepat.

Model embedding apa yang dipakai? Berikut pilihan lokal terbaik per 2026 berdasarkan beberapa riset terbaru:

| Model | Ukuran | Konteks | Lisensi | Cocok untuk |
|---|---|---|---|---|
| Qwen3-Embedding-0.6B | 595M param | 32K | Apache 2.0 | Default terbaik, akurat |
| BAAI/bge-m3 | 570MB | 8192 | MIT | Dokumen Indonesia, multilingual |
| nomic-embed-text-v1.5 | 137M param | 8192 | Apache 2.0 | CPU kentang, tetap bagus |
| all-MiniLM-L6-v2 | 80MB | 256 token | Apache 2.0 | Indexing jutaan chunk di CPU |
| EmbeddingGemma-300m | 308M param | 8K | Gemma | Perangkat kecil, hemat RAM |

Sumber: panduan embedding lokal BestFreeWebResources (diperbarui awal Oktober 2026), panduan StackAI, dan field guide embedding yang diverifikasi dari config Hugging Face per 18 Agustus 2026.

Dua catatan penting. Pertama, untuk dokumen Bahasa Indonesia pilih model multilingual seperti **bge-m3** atau **Qwen3-Embedding**, jangan model yang dilatih khusus Bahasa Inggris. Kedua, **cek lisensi**: model embedding Jina v3/v5 memang bagus, tapi lisensinya CC BY-NC 4.0 yang artinya non-komersial saja. Jangan dipakai untuk produk berbayar tanpa verifikasi ulang.

## Langkah 3: cari chunk paling relevan

Saat user bertanya, kita embed pertanyaannya lalu cari chunk dengan skor kemiripan tertinggi. Karena embedding sudah dinormalisasi, cosine similarity sama dengan dot product biasa.

```python
import numpy as np

def search(query, chunks, embeddings, model, top_k=3):
    q = model.encode([query], normalize_embeddings=True)[0]
    scores = embeddings @ q  # cosine similarity untuk vektor ternormalisasi
    top_idx = np.argsort(scores)[-top_k:][::-1]
    return [(chunks[i], float(scores[i])) for i in top_idx]

hasil = search("bagaimana cara refund?", chunks, embeddings, model)
for teks_chunk, skor in hasil:
    print(f"skor {skor:.3f}: {teks_chunk[:80]}...")
```

Mulai dengan `top_k=3`. Terlalu banyak chunk membuat konteks berisik dan LLM malah bingung memilih informasi yang benar. Naikkan ke 5 kalau jawaban sering "tidak tahu" padahal informasinya ada di dokumen.

## Langkah 4: minta LLM menjawab dari konteks

Chunk terpilih digabung jadi satu konteks, lalu dikirim ke LLM bersama instruksi tegas: jawab hanya dari konteks. Endpoint yang dipakai adalah protokol OpenAI-compatible, jadi kodenya sama persis baik kamu memakai API cloud maupun server lokal seperti llama.cpp.

```python
import requests

LLM_URL = "http://127.0.0.1:18090/v1"  # ganti: server lokal atau https://api.openai.com/v1
LLM_MODEL = "llama"                     # ganti sesuai nama model di server kamu
API_KEY = ""                            # isi kalau pakai API cloud

def answer(question, chunks, embeddings, model):
    hasil = search(question, chunks, embeddings, model)
    konteks = "\n\n---\n\n".join(c for c, s in hasil)

    messages = [
        {"role": "system",
         "content": "Jawab hanya berdasarkan konteks di bawah. "
                    "Kalau jawabannya tidak ada di konteks, katakan tidak tahu."},
        {"role": "user",
         "content": f"Konteks:\n{konteks}\n\nPertanyaan: {question}"},
    ]
    r = requests.post(
        f"{LLM_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"} if API_KEY else {},
        json={"model": LLM_MODEL, "messages": messages, "temperature": 0.2},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

print(answer("bagaimana cara refund?", chunks, embeddings, model))
```

Instruksi sistem itu adalah kunci anti-halusinasi seluruh pipeline. Tanpa kalimat "jawab hanya berdasarkan konteks", LLM akan mencampur pengetahuan umumnya dengan isi dokumen, dan kamu tidak bisa bedakan mana jawaban dari dokumen mana yang dikarang.

## Kesalahan umum pemula (dan cara menghindarinya)

**1. Chunk terlalu besar atau tanpa overlap.** Kalimat penting terpotong di batas chunk, retrieval dapat potongan yang tidak lengkap. Solusi: 500 sampai 1000 karakter dengan overlap 10 sampai 20 persen.

**2. top_k terlalu besar.** Mengambil 20 chunk sekaligus membuat prompt penuh informasi tidak relevan. Solusi: mulai dari 3, naikkan bertahap sambil uji kualitas jawaban.

**3. Model embedding tidak cocok dengan bahasa dokumen.** Dokumen Indonesia di-embed pakai model English-only menghasilkan retrieval yang buruk. Solusi: pakai bge-m3 atau Qwen3-Embedding yang memang multilingual.

**4. Lupa instruksi sistem.** Ini kesalahan paling fatal: chatbot menjawab lancar tapi dari pengetahuan umum model, bukan dari dokumen kamu. Solusi: selalu tulis aturan main di system prompt, dan uji dengan pertanyaan yang jawabannya pasti tidak ada di dokumen untuk memastikan ia berani bilang tidak tahu.

**5. Embedding dihitung ulang setiap run.** Indexing ratusan halaman tiap kali program jalan itu buang waktu. Solusi: simpan embedding ke file (`np.save`) atau pakai vector database ringan, lalu load saat program mulai.

## Langkah praktis yang bisa langsung dicoba

1. Install dependensi: `pip install sentence-transformers numpy requests pypdf`
2. Siapkan satu file teks atau PDF, ekstrak jadi teks polos
3. Jalankan langkah 1 dan 2 sekali untuk indexing, simpan hasilnya
4. Buat loop sederhana di terminal: baca pertanyaan, panggil `answer()`, cetak jawaban
5. Uji dengan 10 pertanyaan yang jawabannya kamu tahu ada di dokumen, hitung berapa yang benar

Sebagai gambaran kecepatan: di CPU biasa, meng-index 100 halaman PDF (sekitar 500 chunk) dengan model kecil seperti MiniLM cuma butuh hitungan menit. Setelah itu tiap pertanyaan dijawab dalam detik.

## Kapan RAG tidak cukup

Bagian ini opini berdasarkan pengalaman, bukan klaim mutlak. Pilih teknik sesuai masalahnya:

- **Prompt engineering** cukup kalau aturannya pendek dan statis, misalnya format jawaban atau persona.
- **RAG** tepat kalau datanya banyak, sering berubah, dan jawabannya harus bisa dilacak ke sumber dokumen.
- **Fine-tuning** baru dipertimbangkan kalau kamu mau mengubah perilaku atau gaya bahasa model secara permanen, dan siap dengan biaya training-nya.

Tren 2026 yang layak diperhatikan: RAG bergerak ke arah yang lebih *agentic*, di mana retrieval tidak sekadar pencarian semantik tapi melibatkan penalaran atas dokumen. Beberapa riset komunitas juga mencatat bahwa menambah *reranker* (model yang menyusun ulang hasil retrieval) sering memberi lonjakan akurasi lebih besar daripada sekadar ganti embedding model. Kalau butuh solusi siap pakai kelas enterprise, engine open source seperti RAGFlow dari infiniflow sudah sangat matang dengan puluhan ribu stars di GitHub. Sumber: analisis tren open source AI agents-radar (Mei 2026) dan benchmark embedding Milvus (30 Juni 2026).

## Penutup

RAG pada intinya sederhana: pecah dokumen, ubah jadi angka, cari yang paling mirip dengan pertanyaan, lalu minta LLM menjawab dari potongan tersebut. Empat langkah di artikel ini sudah cukup untuk chatbot dokumentasi yang fungsional. Setelah versi dasarnya jalan, peningkatan terbesar biasanya datang dari tuning chunk size dan menambah reranker, bukan dari ganti model yang lebih besar. Selamat mencoba.
