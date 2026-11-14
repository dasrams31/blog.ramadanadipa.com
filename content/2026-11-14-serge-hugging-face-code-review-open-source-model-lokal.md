---
title: Serge Hugging Face: Code Review AI Open Source Model Lokal
description: Serge dari Hugging Face mereview pull request pakai model AI apa pun, termasuk model lokal di VPS kamu. Simak cara setup, aturan repo, dan batasannya.
cover: /assets/img/covers/serge-hugging-face-code-review-open-source-model-lokal.jpg
date: 2026-11-14
tags: [ai, serge, code-review, github]
faq:
  - Apa itu Serge dari Hugging Face?
  - Serge adalah code reviewer AI open source dari Hugging Face yang membaca diff pull request, lalu memposting komentar review inline lewat GitHub Pull Request Reviews API. Ia memakai model AI apa pun yang menyediakan endpoint kompatibel OpenAI, termasuk model lokal.
  - Apakah Serge bisa jalan dengan model lokal seperti Ollama?
  - Bisa. Serge hanya butuh endpoint OpenAI-compatible, dan Ollama menyediakannya di alamat localhost:11434/v1. Syaratnya, mesin yang menjalankan Serge harus bisa menjangkau endpoint itu, jadi untuk model lokal kamu butuh self-hosted runner atau mode GitHub App.
  - Apakah Serge gratis?
  - Ya. Kode Serge berlisensi Apache 2.0 dan bisa dipakai serta di-host sendiri secara gratis. Biaya yang muncul hanya dari model yang kamu pakai, dan nol rupiah bila modelnya jalan lokal di VPS kamu sendiri.
  - Bagaimana cara memicu review Serge di pull request?
  - Tulis komentar `@askserge please review` sebagai kata pertama di pull request yang masih terbuka. Hanya komentar dari MEMBER, OWNER, atau COLLABORATOR repo yang diproses.
---

Pull request menumpuk bukan karena tim malas review. PR dibuka sore hari, reviewer baru sempat membacanya besok pagi, dan penulisnya sudah pindah ke tugas lain. Serge, reviewer AI open source dari Hugging Face, menawarkan jalan keluar yang beda dari Copilot dan CodeRabbit: kodenya terbuka, modelnya bisa kamu pilih sendiri, dan reviewnya bisa jalan di model lokal yang tidak pernah keluar dari VPS kamu. Tool ini diumumkan Hugging Face pada 12 Juni 2026, berlisensi Apache 2.0, dan sudah dipakai di repo besar seperti `diffusers` dan `transformers`.

## Serge itu apa, dan kenapa beda

Serge adalah code reviewer yang hidup di dalam workflow GitHub, bukan tool terpisah yang harus kamu buka. Kamu memanggilnya dengan komentar, ia membaca diff PR, menerapkan aturan review milik repo, lalu memposting komentar inline lewat GitHub Pull Request Reviews API. Setiap komentar yang ia usulkan divalidasi terhadap posisi diff yang sebenarnya, jadi hanya komentar yang menunjuk baris nyata yang diterbitkan.

Yang membedakan Serge dari reviewer AI berbayar adalah kebebasan memilih model. Serge berbicara ke endpoint chat completion yang kompatibel dengan OpenAI, jadi ia bekerja dengan OpenAI, Hugging Face Router, dan endpoint lokal vLLM, TGI, atau LM Studio. Konfigurasinya kecil: cukup atur API base, API key, dan model bila perlu. Kalau model tidak dikonfigurasi, Serge menanyakan endpoint `/models` lalu memakai model pertama yang dikembalikan.

Serge juga punya sisi human-in-the-loop. Di mode web app, hasil model menjadi draft dulu. Manusia bisa mengedit ringkasan, menulis ulang atau membuang komentar sebelum ada satu pun yang sampai ke PR. Review yang memberi approval diblokir secara default, kecuali kamu mengaktifkan `ALLOW_APPROVE=1`.

## Tiga cara menjalankan Serge

Pilih mode sesuai seberapa besar kontrol yang kamu butuhkan.

**GitHub Action.** Cara tercepat untuk satu repo. Tambah secret, pasang workflow, lalu panggil lewat komentar. Tidak butuh server dan tidak butuh GitHub App.

**GitHub App webhook.** Mode untuk organisasi dan repo yang banyak menerima PR dari fork. Serge jalan sebagai service yang kamu host, menerima event komentar GitHub, dan memposting review memakai token instalasi GitHub App. Sekali App terpasang, repo tidak butuh workflow file lagi, dan satu App bisa melayani banyak repo.

**Web app staged.** Mode human-in-the-loop. Reviewer memulai review, melihat model bekerja secara live, mengedit atau membuang komentar, lalu memublikasikan hanya bagian yang berguna.

## Setup tercepat: GitHub Action dalam 10 menit

Tiga langkah, sesuai dokumentasi resmi. Pertama, tambah repository secret bernama `LLM_API_KEY`. Kedua, buat file `.github/workflows/ai-review.yml`:

```yaml
name: AI PR Review

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  review:
    if: |
      (startsWith(github.event.comment.body, '@askserge ') ||
       github.event.comment.body == '@askserge') &&
      (github.event.comment.author_association == 'MEMBER' ||
       github.event.comment.author_association == 'OWNER' ||
       github.event.comment.author_association == 'COLLABORATOR')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: refs/pull/${{ github.event.issue.number || github.event.pull_request.number }}/head
        continue-on-error: true
      - uses: huggingface/serge@main
        with:
          llm_api_key: ${{ secrets.LLM_API_KEY }}
          llm_api_base: ${{ secrets.LLM_API_BASE || 'https://api.openai.com/v1' }}
```

Ketiga, tulis komentar `@askserge please review` di PR yang masih terbuka. Perhatikan dua detail di workflow itu. Trigger hanya jalan bila `@askserge` adalah kata pertama di komentar, dan hanya bila penulis komentar adalah MEMBER, OWNER, atau COLLABORATOR repo. Komentar dari kontributor luar diabaikan, jadi orang asing tidak bisa memicu review berbayar di repo kamu. Kamu juga bisa memberi instruksi tambahan setelah trigger, misalnya `@askserge focus on the new auth flow and ignore generated files`, dan membalas komentar review inline yang sudah ada untuk bertanya di thread yang sama. Untuk perilaku yang bisa direproduksi, pin `huggingface/serge` ke tag atau commit SHA, jangan memakai `@main` di repo produksi.

## Arahkan Serge ke model lokal di VPS

Di sinilah Serge menarik buat developer Indonesia yang sudah punya VPS. Ollama menyediakan endpoint yang kompatibel dengan OpenAI di `http://localhost:11434/v1`, jadi Serge bisa langsung bicara ke model lokal tanpa satu baris kode tambahan.

Jalankan Ollama di VPS dengan Docker, lalu unduh model coding yang cukup besar untuk review:

```bash
docker run -d --gpus=all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama ollama/ollama

docker exec ollama ollama pull qwen2.5-coder:14b
```

Model `qwen2.5-coder:14b` adalah titik awal yang masuk akal: cukup besar untuk memahami diff, cukup kecil untuk jalan di satu GPU kelas menengah. Kalau VPS kamu tanpa GPU, mulai dari model 7B dan terima review yang lebih dangkal.

Lalu ada jebakan yang paling sering membuat setup lokal gagal: runner GitHub yang di-host GitHub hidup di cloud GitHub, jadi ia tidak bisa menjangkau model yang terikat ke `localhost` di laptop atau VPS kamu. Solusinya ada dua. Pertama, pakai self-hosted runner di mesin yang sama dengan Ollama, lalu ubah `runs-on` jadi `self-hosted` dan isi secret `LLM_API_BASE` dengan `http://localhost:11434/v1`. Kedua, kalau belum mau mengurus runner, pakai Hugging Face Router sebagai jalan tengah dengan base `https://router.huggingface.co/v1`, lalu pindah ke model lokal setelah alurnya terbukti jalan.

Satu detail teknis dari dokumentasi provider: Serge meminta output JSON saat review penuh. Model lokal yang lemah di instruksi terstruktur kadang menghasilkan JSON yang rusak, jadi pilih model yang kuat mengikuti format, dan naikkan `LLM_MAX_TOKENS` bila model memakai token untuk reasoning sebelum mengeluarkan JSON.

## Aturan review tinggal di repo, bukan di prompt

Reviewer AI yang generik akan mengomentari hal yang salah, karena ia tidak tahu konvensi repo kamu. Serge menyelesaikan ini dengan file `.ai/review-rules.md` di branch default repo. Isinya singkat dan ditulis manusia, contohnya seperti ini:

```markdown
Focus on:
- correctness bugs
- security issues
- missing tests for behavior changes
Avoid:
- style-only comments
- generated files
- comments that do not require action
```

File aturan dimuat dari branch default dengan sengaja: PR yang sedang direview tidak boleh menulis ulang kebijakan yang dipakai untuk mereview dirinya sendiri. Kamu juga bisa menambah `.ai/context-script` untuk konteks tambahan, plus tool read-only seperti `read_file`, `list_dir`, dan `grep` yang dibatasi di dalam checkout repo, supaya reviewer bisa memeriksa file di luar diff tanpa akses shell.

Tulis aturan ini sepanjang 10 sampai 15 baris saja. Sebut stack kamu, pola yang dilarang, dan hal yang tidak perlu dikomentari, misalnya larangan mengomentari gaya yang sudah ditangani Pint. Tanpa file ini, Serge menebak konvensi dari diff saja, dan tebakannya sering generik.

## Batasan keamanan yang wajib kamu tahu

Konten pull request adalah input yang tidak tepercaya. Prompt di Serge memerintahkan model untuk tidak mengikuti instruksi yang tertanam di diff, komentar, atau string. Kalau PR berisi teks prompt injection, reviewer harus memperlakukannya sebagai sesuatu yang direview, bukan instruksi yang ditaati.

Tool bantuan berjalan tanpa shell, dan environment-nya dibersihkan dari token GitHub, kunci LLM, secret OAuth, secret sesi, dan secret webhook. File kustomisasi repo selalu dimuat dari branch default. Ini penting karena PR dari fork bisa berisi apa saja. Untuk PR dari fork, mode Action memang bukan jawaban yang tepat: GitHub tidak mengirim repository secret ke workflow yang dipicu dari fork, dan token default biasanya hanya read-only. Untuk repo yang banyak menerima kontribusi eksternal, pakai mode GitHub App atau web app.

## Jujur soal model lokal: apa yang bisa dan tidak bisa

Ini bagian yang perlu ekspektasi realistis. Menurut panduan setup independen yang membandingkan pengalaman menjalankan Serge dengan model lokal, model kelas 7B sampai 14B cukup untuk menangkap bug yang jelas, null check yang hilang, dan test yang terlupa. Tapi jangan harap ia menangkap kesalahan logika yang halus seperti model frontier. Itu bukan cacat Serge, itu batas modelnya. Kalau review lokal kamu terasa dangkal, yang perlu diganti adalah modelnya, bukan tool-nya.

Biaya juga perlu dihitung dengan jujur. Model lokal menghilangkan tagihan per token setelah hardware dibeli, dan kode kamu tidak pernah keluar dari jaringan sendiri. Tapi kamu membayarnya dengan operasional: GPU harus menyala, Ollama harus dijaga, dan runner harus online saat PR dibuka. Untuk developer solo dengan PR sedikit, beban operasional itu sering lebih besar daripada nilainya. Untuk tim kecil yang PR-nya ramai dan datanya sensitif, hitungannya berbalik. Jaga juga ukuran PR: diff besar membuat model kehilangan fokus, jadi PR kecil yang fokus pada satu perubahan akan direview jauh lebih tajam.

## Kesalahan umum pemula dan cara menghindarinya

Pertama, memakai `runs-on: ubuntu-latest` sambil menunjuk `localhost` sebagai API base. Runner cloud tidak bisa menjangkau model lokal kamu. Pakai self-hosted runner, atau pakai endpoint publik seperti Hugging Face Router.

Kedua, tidak menulis `.ai/review-rules.md`. Tanpa aturan repo, Serge memberi saran generik yang tidak cocok dengan codebase kamu.

Ketiga, membiarkan AI mengomentari semua file. Abaikan lockfile, file hasil generate, dan file Markdown, karena mereview file yang bukan kode hanya menambah noise.

Keempat, menjadikan AI satu-satunya gate merge. Approval review diblokir Serge secara default karena satu alasan yang sama: keputusan merge tetap di tangan manusia dan test. Status check yang menggagalkan merge sebaiknya tetap dipegang test dan static analysis.

Kelima, mengaktifkan review otomatis di semua repo sekaligus. Uji dulu di satu repo kecil yang PR-nya kamu kenal baik, pantau lima PR pertama, dan ukur dari berapa komentar yang berujung pada perubahan kode, bukan dari jumlah komentar.

## Langkah pertama hari ini

Ambil satu repo kecil yang PR-nya kamu kenal baik. Jalankan Ollama dan model coding 14B di VPS, pasang self-hosted runner di mesin yang sama, salin workflow di atas, dan tulis `.ai/review-rules.md` sepanjang 10 sampai 15 baris. Lalu buka satu PR percobaan dengan satu bug yang jelas, misalnya query mentah dengan input user atau N+1 di loop Blade, dan tulis `@askserge please review`.

Kalau komentarnya tajam dan berujung pada perbaikan kode, kamu baru saja mendapat reviewer pertama yang tidak pernah tidur dan tidak pernah membawa kode kamu keluar dari VPS. Kalau komentarnya masih generik, perbaiki aturan repo dan modelnya dulu sebelum menyalahkan tool-nya.

Sumber: blog Hugging Face "Introducing Serge: GitHub-Native AI Code Review", 12 Juni 2026; dokumentasi resmi di huggingface.github.io/serge; panduan setup lokal independen aifoss.dev, 5 Juli 2026.
