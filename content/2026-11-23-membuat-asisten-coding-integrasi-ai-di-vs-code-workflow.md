---
title: Asisten Coding AI di VS Code: Setup Workflow yang Efektif
description: Cara mengintegrasikan asisten coding AI ke workflow VS Code: setup Copilot dan Continue, file instruksi, dan kebiasaan yang bikin AI benar-benar membantu.
cover: /assets/img/covers/membuat-asisten-coding-integrasi-ai-di-vs-code-workflow.jpg
date: 2026-11-23
tags: [vs code, ai, copilot, developer, workflow]
faq:
  - Apakah GitHub Copilot gratis untuk developer Indonesia?
  - Ada paket gratis dengan batasan jumlah completion dan chat per bulan. Paket Pro berbayar memberi akses penuh, termasuk Agent Mode dan model yang lebih baru.
  - Apakah kode saya dikirim ke server saat memakai asisten AI di VS Code?
  - Tergantung alatnya. Copilot dan layanan cloud mengirim potongan kode yang relevan ke server mereka. Kalau butuh privasi penuh, pakai Continue dengan model lokal lewat Ollama.
  - Apa bedanya Copilot Chat dan Agent Mode di VS Code?
  - Chat menjawab pertanyaan dan menulis potongan kode yang kamu minta. Agent Mode bisa menjalankan banyak langkah sendiri: membaca file, mengedit, menjalankan terminal, lalu memperbaiki error sampai selesai.
  - Bisakah asisten coding AI dipakai offline dengan model lokal?
  - Bisa. Continue dan Cline mendukung Ollama atau LM Studio, jadi model jalan di laptop sendiri tanpa internet. Kualitasnya di bawah model cloud besar, tapi cukup untuk autocomplete dan tugas sederhana.
---

Aku pertama kali memasang asisten coding AI di VS Code dengan ekspektasi terlalu tinggi. Kukira ia akan menulis seluruh fitur sendirian sementara aku menonton. Kenyataannya, minggu pertama justru lebih lambat: saran autocomplete yang salah arah, potongan kode yang kelihatan benar tapi gagal di runtime, dan chat yang menjawab dengan solusi untuk library versi lama. Masalahnya bukan di AI-nya, tapi di setup dan cara kupakai.

Setelah setahun memakai Copilot dan Continue setiap hari, workflow-ku sekarang stabil. Artikel ini merangkum setup yang kupakai: alat apa yang dipilih, file instruksi yang membuat AI paham project-mu, dan kebiasaan harian yang membedakan AI sebagai asisten atau sebagai sumber bug baru.

## Pilih alatnya dulu

Tiga pilihan yang paling masuk akal untuk developer Indonesia saat ini.

**GitHub Copilot** adalah pilihan paling gampang. Integrasinya paling dalam dengan VS Code: autocomplete, chat, Agent Mode, sampai review pull request. Harganya masuk akal dan ada paket gratis dengan kuota terbatas. Kekurangannya, kode kamu dikirim ke server GitHub, dan kamu tidak bisa memilih model lokal.

**Continue** adalah extension open source yang fleksibel. Kamu bisa menyambungkan API apa pun: OpenAI, Anthropic, Google, sampai model lokal lewat Ollama. Cocok kalau kamu sudah punya API key sendiri atau mau privasi penuh. Setup awalnya sedikit lebih panjang, tapi kamu tidak terkunci ke satu vendor.

**Cline** (dulu bernama Claude Dev) fokus ke mode agen: ia membaca struktur project, menjalankan terminal, dan mengerjakan tugas multi-langkah. Bagus untuk tugas besar seperti refactor, tapi butuh pengawasan ketat karena ia banyak mengubah file sekaligus.

Saranku: mulai dari Copilot kalau mau langsung produktif, atau Continue kalau kamu sudah nyaman mengatur API key dan model sendiri. Jangan memasang ketiganya sekaligus, karena autocomplete yang saling berebut justru bikin editor lambat dan saran jadi dobel.

## Setup dasar: Copilot di VS Code

Install extension GitHub Copilot dan GitHub Copilot Chat dari marketplace, lalu login dengan akun GitHub. Setelah itu, aktifkan beberapa pengaturan penting di `settings.json`.

```json
{
  "github.copilot.enable": {
    "*": true,
    "markdown": false,
    "plaintext": false
  },
  "github.copilot.chat.localeOverride": "en",
  "github.copilot.nextEditSuggestions.enabled": true,
  "editor.inlineSuggest.enabled": true,
  "editor.tabCompletion": "on"
}
```

Pengaturan `nextEditSuggestions` mengaktifkan saran edit berikutnya: setelah kamu menerima satu perubahan, Copilot menebak edit selanjutnya di file yang sama. Fitur ini terasa seperti pair programming, bukan sekadar autocomplete.

Matikan Copilot untuk Markdown dan plaintext. Saran kode di tengah catatan atau file teks biasa hanya mengganggu, dan tidak ada gunanya.

Untuk Continue, instal extension-nya, lalu isi `config.yaml` di folder `.continue` dengan provider yang kamu pakai. Contoh paling sederhana memakai Ollama lokal:

```yaml
name: Local Assistant
version: 1.0.0
schema: v1
models:
  - name: Qwen2.5 Coder 7B
    provider: ollama
    model: qwen2.5-coder:7b
    roles: [chat, edit, apply]
context:
  - provider: code
  - provider: docs
  - provider: diff
  - provider: terminal
```

Model 7B seperti Qwen2.5 Coder berjalan lumayan di laptop dengan RAM 16 GB. Jangan memaksakan model 32B di laptop biasa, karena token per detiknya akan sangat lambat dan kamu malah kembali mengetik manual.

## File instruksi: otak kedua asistenmu

Ini bagian yang paling sering dilewatkan, padahal dampaknya paling besar. Tanpa instruksi, AI menebak gaya coding dari potongan file yang sedang kamu buka. Dengan file instruksi, ia tahu stack, konvensi, dan larangan project kamu sebelum menulis satu baris pun.

Buat file `.github/copilot-instructions.md` di root project. Isinya singkat dan spesifik, bukan esai.

```markdown
# Project instructions

- Stack: Laravel 12, PHP 8.3, PostgreSQL, Blade, Tailwind CSS.
- Ikuti PSR-12. Gunakan Eloquent, jangan query mentah kecuali ada alasan jelas.
- Validasi selalu di Form Request, bukan di controller.
- Bahasa antarmuka: Bahasa Indonesia. Komentar kode: Bahasa Inggris singkat.
- Jangan menambahkan package baru tanpa bertanya dulu.
- Kalau ada dua cara menyelesaikan sesuatu, pilih yang paling sederhana.
- Selalu sertakan contoh pemakaian saat membuat helper baru.
```

Copilot membaca file ini otomatis di setiap chat dan Agent Mode. Hasilnya langsung terasa: kode yang dihasilkan mengikuti konvensi project, bukan gaya generik dari tutorial internet.

Selain itu, simpan pengaturan khusus project di `.vscode/settings.json`. Misalnya, matikan Copilot untuk file environment dan aktifkan format on save supaya AI dan formatter tidak saling bertabrakan.

```json
{
  "github.copilot.enable": {
    ".env*": false
  },
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "files.exclude": {
    "**/node_modules": true,
    "**/vendor": true
  }
}
```

Satu aturan penting: jangan menulis API key, token, atau password di file instruksi. File ini sering ikut ter-commit ke Git, dan AI tidak butuh secret untuk menulis kode yang bagus.

## Prompt file dan custom chat mode

VS Code mendukung prompt file yang bisa dipakai ulang. Buat folder `.github/prompts/`, lalu simpan prompt yang sering kamu pakai sebagai file `.prompt.md`. Contoh prompt review kode:

```markdown
---
mode: agent
description: Review perubahan di branch ini sebelum pull request
---

Review semua perubahan di branch ini terhadap main.

1. Cari bug logika, terutama kondisi tepi dan input kosong.
2. Periksa apakah ada query N+1 atau loop yang memanggil database.
3. Pastikan tidak ada secret atau kredensial yang ter-commit.
4. Tulis temuan dalam Bahasa Indonesia, urutkan dari yang paling parah.
5. Untuk setiap temuan, sebut file dan nomor baris, lalu usulkan perbaikan konkret.
```

Panggil prompt ini dari Copilot Chat dengan mengetik `/review-branch` atau dari command palette. Kamu tidak perlu mengetik instruksi yang sama setiap kali review.

Kamu juga bisa membuat custom chat mode, misalnya mode `planner` yang hanya boleh menulis rencana dan dilarang mengedit kode, atau mode `tdd` yang selalu menulis test dulu sebelum implementasi. Simpan sebagai file `.chatmode.md` di folder `.github/chatmodes/`. Mode seperti ini berguna saat kamu mau AI berpikir dulu sebelum menyentuh kode.

## Workflow harian yang kupakai

Setup saja tidak cukup. Yang menentukan adalah urutan kerja saat memakai AI.

**Mulai dari test atau contoh pemakaian.** Sebelum meminta AI menulis fungsi, tulis dulu contoh pemakaian atau test sederhana. Ini memaksa kamu memikirkan input dan output yang diharapkan, dan AI jadi punya target yang jelas. Fungsi yang ditulis tanpa target cenderung melebar dan menambah parameter yang tidak perlu.

**Pakai inline completion untuk kode yang sudah jelas polanya.** Autocomplete paling berguna untuk boilerplate: definisi route, migrasi, atau komponen yang polanya sama dengan file lain. Terima saran dengan Tab, tapi baca dulu sebelum lanjut mengetik.

**Pakai chat untuk menjelaskan, bukan sekadar meminta kode.** Contoh prompt yang bagus: "Jelaskan kenapa query ini lambat dan usulkan dua alternatif, lengkap dengan trade-off-nya." Prompt seperti ini menghasilkan jawaban yang bisa kamu pelajari, bukan sekadar potongan kode yang kamu tempel tanpa paham.

**Pakai Agent Mode untuk tugas multi-file.** Contohnya: "Tambahkan field phone ke tabel users, form profil, dan validasinya, lalu buat migrasinya." Agent Mode akan membaca file terkait, membuat migrasi, mengedit model, form, dan request validation. Setelah selesai, jalankan test dan baca diff-nya sebelum commit. Jangan pernah menerima diff besar tanpa membaca.

**Minta review sebelum commit.** Jalankan prompt review di atas untuk perubahan hari itu. AI sering menemukan hal yang kamu lewatkan saat lelah: variabel yang tidak dipakai, kondisi yang tidak pernah tercapai, atau pesan error yang tidak konsisten.

## Kesalahan umum pemula

**Menerima semua saran tanpa membaca.** Ini kesalahan paling mahal. AI bisa menulis kode yang sintaksnya benar tapi logikanya salah, misalnya memakai kolom yang tidak ada di tabel atau memanggil method yang sudah deprecated. Aturannya sederhana: kalau kamu tidak paham kode yang dihasilkan, jangan commit. Minta AI menjelaskan dulu, atau tulis sendiri.

**Prompt terlalu umum.** "Buatkan fitur login" akan menghasilkan kode generik yang tidak cocok dengan project kamu. Prompt yang baik menyebut konteks: stack, file yang relevan, dan batasan. Contoh: "Buatkan login dengan Laravel Breeze di project ini, tapi ganti email verification jadi opsional dan pakai Bahasa Indonesia untuk semua pesan."

**Meminta AI menulis seluruh project dari nol.** AI bagus untuk potongan fitur dan refactor, tapi buruk untuk arsitektur yang belum dipikirkan. Tentukan dulu struktur folder, model data, dan alur utama sendiri. Setelah itu, minta AI mengisi bagian-bagian kecil di dalam struktur tersebut.

**Tidak memberi feedback saat jawaban salah.** Kalau AI mengusulkan solusi yang salah, jangan diam lalu menulis prompt baru dari awal. Balas di chat yang sama: "Cara itu tidak jalan karena kita pakai Laravel 12 dan method itu sudah dihapus di versi ini. Cari alternatif yang didukung Laravel 12." Koreksi seperti ini membuat jawaban berikutnya jauh lebih akurat.

**Menyimpan semua prompt di kepala.** Prompt yang bagus itu aset. Simpan di `.github/prompts/` supaya tim kamu bisa memakai yang sama, dan kamu tidak mengulang mengetik instruksi panjang setiap hari.

## Coba hari ini: checklist 30 menit

1. Install Copilot atau Continue, lalu atur `settings.json` seperti contoh di atas.
2. Buat `.github/copilot-instructions.md` dengan stack dan aturan project kamu, maksimal 15 baris.
3. Buat satu prompt file untuk review kode dan coba jalankan ke branch yang sedang kamu kerjakan.
4. Kerjakan satu tugas kecil dengan urutan: tulis contoh pemakaian dulu, minta AI menulis implementasinya, lalu baca diff sebelum commit.
5. Catat satu hal yang AI kerjakan dengan baik dan satu hal yang ia salah pahami. Koreksi hal kedua lewat file instruksi.

Tiga puluh menit ini cukup untuk merasakan bedanya. Asisten coding AI bukan pengganti kemampuanmu menulis kode, tapi pengali kecepatan untuk pekerjaan yang polanya sudah kamu pahami. Setup yang rapi di awal membuat pengali itu bekerja setiap hari, bukan hanya saat demo.
