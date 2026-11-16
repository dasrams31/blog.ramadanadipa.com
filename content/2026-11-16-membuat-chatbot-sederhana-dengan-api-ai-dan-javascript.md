---
title: "Membuat Chatbot Sederhana dengan API AI dan JavaScript"
description: "Bangun chatbot sendiri dengan API AI dan JavaScript: server proxy Node.js yang aman, antarmuka chat, dan riwayat percakapan yang bisa langsung dicoba."
cover: /assets/img/covers/membuat-chatbot-sederhana-dengan-api-ai-dan-javascript.jpg
date: 2026-11-16
tags: [JavaScript, AI, chatbot]
faq:
  - Apakah API key AI boleh ditulis langsung di kode JavaScript frontend?
  - Tidak boleh. API key yang ada di kode frontend bisa dibaca siapa saja lewat DevTools dan dipakai orang lain sampai kuota kamu habis. Selalu panggil API AI dari server, lalu frontend hanya bicara ke server kamu sendiri.
  - Berapa biaya menjalankan chatbot sederhana seperti ini?
  - Untuk pemakaian pribadi dan percobaan, biasanya di bawah Rp20.000 per bulan kalau pakai model murah seperti gpt-4o-mini atau model lokal. Biaya terbesar datang dari riwayat percakapan yang panjang, jadi batasi jumlah pesan yang dikirim ke API.
  - Bisakah chatbot ini dibuat tanpa server Node.js?
  - Bisa, tapi hanya untuk percobaan lokal. Kamu bisa panggil API AI langsung dari browser memakai API key sementara, lalu hapus key itu setelah selesai. Untuk dipakai orang lain, server proxy tetap wajib supaya key tidak bocor.
  - Kenapa chatbot saya kadang menjawab tidak nyambung?
  - Biasanya karena riwayat percakapan tidak dikirim ke API, atau system prompt tidak jelas. Kirim beberapa pesan terakhir sebagai konteks dan tulis system prompt yang spesifik tentang peran chatbot kamu.
---

Chatbot AI sekarang bukan lagi proyek besar yang butuh tim dan server mahal. Dengan satu API key dan sekitar seratus baris JavaScript, kamu sudah bisa punya chatbot yang menjawab pertanyaan di websitemu sendiri. Artikel ini membangun chatbot itu dari nol: server kecil sebagai perantara, halaman chat sederhana, dan JavaScript yang mengirim pesan lalu menampilkan balasan.

Saya pakai API yang kompatibel dengan format OpenAI, jadi contoh ini jalan untuk OpenAI, model lokal yang diekspos lewat endpoint OpenAI-compatible, atau penyedia lain yang memakai format pesan yang sama. Yang berubah hanya URL dan nama modelnya.

## Arsitektur yang benar: jangan panggil API dari browser

Kesalahan pertama yang dilakukan hampir semua pemula adalah menulis API key langsung di file JavaScript frontend, lalu memanggil `api.openai.com` dari browser. Itu jalan, tapi key kamu terlihat jelas di DevTools siapa pun yang membuka websitemu. Orang lain bisa memakai key itu sampai tagihanmu membengkak.

Arsitektur yang benar punya tiga lapis:

1. **Frontend** (HTML + JavaScript) hanya menampilkan chat dan mengirim pesan ke server kamu sendiri.
2. **Server proxy** (Node.js + Express) menerima pesan, menambahkan API key, lalu meneruskannya ke API AI.
3. **API AI** menjawab, server meneruskan jawaban itu ke frontend.

Dengan cara ini API key tidak pernah keluar dari server. Bonusnya, server juga jadi tempat yang tepat untuk membatasi jumlah pesan, memotong riwayat yang terlalu panjang, dan mencatat pemakaian.

## 1. Siapkan server proxy dengan Node.js

Buat folder proyek dan install dua package: `express` untuk server dan `dotenv` untuk menyimpan API key di file `.env`.

```bash
mkdir chatbot-sederhana && cd chatbot-sederhana
npm init -y
npm install express dotenv
```

Isi file `.env` dengan key kamu. File ini jangan pernah di-commit ke Git.

```bash
AI_API_KEY=sk-isi-dengan-api-key-kamu
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_MODEL=gpt-4o-mini
PORT=3000
```

Sekarang tulis `server.js`. Server ini punya satu endpoint `POST /api/chat` yang menerima array pesan, memotong riwayat ke 10 pesan terakhir supaya token tidak membengkak, lalu meneruskannya ke API AI.

```js
require('dotenv').config();
const express = require('express');
const app = express();

app.use(express.json());
app.use(express.static('public'));

const SYSTEM_PROMPT = `Kamu adalah asisten ramah untuk toko kopi kecil.
Jawab singkat, maksimal 3 kalimat. Kalau tidak tahu jawabannya,
katakan tidak tahu dan tawarkan untuk menghubungi pemilik toko.`;

app.post('/api/chat', async (req, res) => {
  const { messages } = req.body;

  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: 'Pesan tidak boleh kosong.' });
  }

  // Ambil 10 pesan terakhir saja, supaya biaya token tetap terkendali
  const recent = messages.slice(-10);

  try {
    const response = await fetch(process.env.AI_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.AI_API_KEY}`,
      },
      body: JSON.stringify({
        model: process.env.AI_MODEL,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          ...recent,
        ],
        temperature: 0.7,
        max_tokens: 300,
      }),
    });

    if (!response.ok) {
      const detail = await response.text();
      console.error('AI API error:', response.status, detail);
      return res.status(502).json({ error: 'Layanan AI sedang bermasalah, coba lagi sebentar lagi.' });
    }

    const data = await response.json();
    const reply = data.choices?.[0]?.message?.content?.trim() ?? '';
    res.json({ reply });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server gagal menghubungi layanan AI.' });
  }
});

app.listen(process.env.PORT || 3000, () => {
  console.log(`Chatbot jalan di http://localhost:${process.env.PORT || 3000}`);
});
```

Perhatikan tiga detail di kode ini. Pertama, `max_tokens: 300` membatasi panjang jawaban supaya biaya terkendali. Kedua, kalau API gagal, server mengembalikan pesan error yang ramah, bukan menumpahkan detail mentah ke user. Ketiga, `temperature: 0.7` memberi jawaban yang natural tapi tidak terlalu ngawur. Untuk chatbot customer service, nilai 0.3 sampai 0.7 biasanya paling aman.

## 2. Antarmuka chat di HTML

Buat folder `public` dan isi dengan `index.html`. Tampilannya sengaja minimal: daftar pesan dan satu input. Kamu bisa mempercantik nanti dengan CSS, logika intinya tidak berubah.

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chatbot Toko Kopi</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; }
    #chat { border: 1px solid #ddd; border-radius: 12px; height: 420px; overflow-y: auto; padding: 1rem; }
    .msg { margin: 0.5rem 0; padding: 0.6rem 0.9rem; border-radius: 10px; max-width: 80%; }
    .user { background: #2563eb; color: #fff; margin-left: auto; }
    .bot { background: #f1f1f1; }
    form { display: flex; gap: 0.5rem; margin-top: 1rem; }
    input { flex: 1; padding: 0.7rem; border: 1px solid #ccc; border-radius: 8px; }
    button { padding: 0.7rem 1.2rem; border: 0; border-radius: 8px; background: #2563eb; color: #fff; cursor: pointer; }
    button:disabled { opacity: 0.5; cursor: wait; }
  </style>
</head>
<body>
  <h1>Chatbot Toko Kopi</h1>
  <div id="chat"></div>
  <form id="form">
    <input id="input" type="text" placeholder="Tanya soal menu, jam buka, atau harga..." autocomplete="off">
    <button id="send" type="submit">Kirim</button>
  </form>
  <script src="script.js"></script>
</body>
</html>
```

## 3. JavaScript: kirim pesan dan tampilkan balasan

File `public/script.js` mengatur tiga hal: menyimpan riwayat percakapan, mengirim pesan ke server, dan menampilkan balasan dengan indikator "mengetik" supaya user tahu chatbot sedang bekerja.

```js
const chatBox = document.getElementById('chat');
const form = document.getElementById('form');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');

// Riwayat percakapan dalam format yang diminta API AI
const history = [];

function addMessage(text, who) {
  const div = document.createElement('div');
  div.className = `msg ${who}`;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
  return div;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  sendBtn.disabled = true;
  addMessage(text, 'user');
  history.push({ role: 'user', content: text });

  const typing = addMessage('Mengetik...', 'bot');

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: history }),
    });
    const data = await res.json();

    typing.remove();
    if (!res.ok) {
      addMessage(data.error || 'Terjadi kesalahan, coba lagi.', 'bot');
      history.pop(); // Pesan gagal tidak ikut ke riwayat
      return;
    }

    addMessage(data.reply, 'bot');
    history.push({ role: 'assistant', content: data.reply });
  } catch (err) {
    typing.remove();
    addMessage('Tidak bisa terhubung ke server. Periksa koneksimu lalu coba lagi.', 'bot');
    history.pop();
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
});

addMessage('Halo! Ada yang bisa saya bantu soal menu atau jam buka toko?', 'bot');
```

Detail kecil yang penting: `textContent`, bukan `innerHTML`, dipakai untuk menampilkan pesan. Kalau kamu memakai `innerHTML`, user bisa menyisipkan tag HTML atau script lewat pesan mereka. Ini celah XSS klasik yang sering lolos di tutorial chatbot. Pesan gagal juga dihapus dari riwayat dengan `history.pop()` supaya percakapan tidak tercemar pesan yang tidak pernah dijawab.

Jalankan dengan `node server.js`, buka `http://localhost:3000`, dan chatbot kamu sudah bisa dipakai.

## 4. Batasi riwayat percakapan supaya biaya tidak membengkak

Setiap pesan yang kamu kirim ke API ikut dihitung sebagai token input. Percakapan yang panjang berarti tagihan yang ikut panjang. Server di atas sudah memotong ke 10 pesan terakhir, tapi kamu juga bisa lebih hemat dengan meringkas.

Aturan praktis yang saya pakai: simpan maksimal 6 sampai 10 pesan terakhir di client, dan potong lagi di server sebagai pengaman ganda. Kalau chatbot kamu butuh ingatan panjang, misalnya asisten belanja yang mengingat preferensi user, simpan ringkasannya di database dan kirim ringkasan itu sebagai bagian dari system prompt, bukan seluruh riwayat mentah.

Satu hal lagi: jangan simpan data sensitif di riwayat. Kalau user mengetik nomor telepon atau alamat, jangan teruskan mentah-mentah ke API pihak ketiga tanpa alasan yang jelas. Saring dulu di server, atau beri tahu user untuk tidak mengirim data pribadi lewat chat.

## Kesalahan umum pemula dan cara menghindarinya

**API key bocor di frontend.** Ini yang paling fatal. Solusinya selalu server proxy seperti di atas, dan tambahkan `.env` ke `.gitignore` sejak hari pertama.

**Tidak ada batasan di server.** Tanpa validasi, siapa saja bisa mengirim pesan raksasa atau ribuan request ke endpoint kamu dan menguras kuota API. Tambahkan batas panjang pesan, misalnya 500 karakter, dan rate limit sederhana dengan package `express-rate-limit`.

**System prompt terlalu umum.** Prompt "kamu adalah asisten AI" menghasilkan jawaban yang generik dan kadang keluar topik. Tulis peran yang spesifik, sebut batasan jawabannya, dan beri contoh gaya bahasa yang kamu mau. Prompt di contoh ini hanya tiga baris tapi sudah jauh lebih baik daripada prompt satu baris.

**Tidak menangani error API.** API bisa down, key bisa kedaluwarsa, kuota bisa habis. Kalau frontend tidak menangani itu, user hanya melihat loading yang tidak pernah selesai. Selalu tampilkan pesan error yang jelas dan beri user jalan untuk mencoba lagi.

**Jawaban ditampilkan mentah sebagai HTML.** Seperti dijelaskan di atas, pakai `textContent` atau sanitasi dulu. Jangan pernah menempel balasan AI ke DOM dengan `innerHTML` tanpa sanitasi.

## Langkah praktis yang bisa dicoba hari ini

Mulai dari versi paling sederhana, lalu kembangkan selangkah demi selangkah:

1. Jalankan contoh di artikel ini sampai chatbot menjawab di browser kamu.
2. Ganti system prompt dengan bisnis atau topik kamu sendiri, lalu uji dengan 10 pertanyaan yang kira-kira ditanyakan pengunjung.
3. Tambahkan `express-rate-limit` supaya satu IP tidak bisa membanjiri endpoint kamu.
4. Deploy servernya ke VPS dengan PM2 supaya chatbot tetap jalan setelah kamu menutup terminal. Saya sudah menulis panduan deploy Node.js ke VPS di artikel sebelumnya tentang PM2.
5. Kalau sudah stabil, tambahkan tombol yang sering ditanyakan, misalnya "Lihat menu" atau "Jam buka", supaya user tidak harus mengetik semuanya.

Chatbot sederhana seperti ini adalah fondasi yang bagus. Setelah arsitekturnya benar, kamu bisa menambah kemampuan tanpa merombak semuanya: ganti modelnya, tambah pencarian dokumen dengan RAG, atau hubungkan ke database produk supaya chatbot bisa menjawab stok dan harga secara langsung. Yang penting, bangun dulu versi yang aman dan jalan, baru tambah fitur.
