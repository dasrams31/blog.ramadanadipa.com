---
title: AI Code Review Otomatis di GitHub Actions: Setup Praktis
description: Setup AI code review otomatis di GitHub Actions: Copilot, CodeRabbit, dan workflow rakitan sendiri dengan contoh YAML, Python, dan cara cegah spam komentar.
cover: /assets/img/covers/ai-code-review-otomatis-di-github-actions.jpg
date: 2026-11-03
tags: [ai, github-actions, code-review, copilot]
faq:
  - Apa itu AI code review di GitHub Actions?
  - AI code review di GitHub Actions adalah review otomatis yang jalan setiap pull request dibuka atau diperbarui. AI membaca diff, lalu menulis komentar soal bug, keamanan, dan kualitas kode sebelum reviewer manusia membuka PR itu.
  - Apakah AI code review bisa menggantikan reviewer manusia?
  - Belum. AI bagus sebagai penyaring pertama untuk bug yang jelas, secret yang bocor, dan pola yang berisiko. Keputusan akhir soal desain, logika bisnis, dan konteks produk tetap di tangan manusia.
  - Berapa biaya GitHub Copilot code review?
  - GitHub menghitungnya dari AI credits ditambah GitHub Actions minutes sejak 1 Juni 2026. Estimasi GitHub untuk satu review berkisar 0,05 sampai 1 dolar AS pada effort Lite dan 0,25 sampai 5 dolar AS pada effort Balanced, tergantung ukuran PR dan instruksi kustom.
  - Bagaimana cara mencegah AI code review jadi spam komentar?
  - Batasi ke file kode saja, abaikan lockfile dan file hasil generate, lewati draft PR, tetapkan ambang severity, dan minta AI hanya berkomentar pada baris yang berubah. Uji dulu di satu repo kecil sebelum diaktifkan di semua repo.
---

Pull request menumpuk bukan karena tim malas review. PR dibuka sore hari, reviewer baru sempat membacanya besok pagi, dan penulisnya sudah pindah ke tugas lain. Makin banyak kode ditulis dengan bantuan AI, jadi volume yang harus diperiksa naik lebih cepat daripada waktu review yang tersedia. AI code review otomatis memberi penyaring pertama yang cepat: setiap PR dibaca mesin dalam hitungan menit.

## Apa yang berubah di 2026

GitHub melaporkan Copilot code review sudah menyumbang lebih dari satu dari lima code review di GitHub per 5 Maret 2026, dengan lebih dari 12.000 organisasi menjalankannya otomatis, dan 71 persen reviewnya menghasilkan feedback yang bisa ditindaklanjuti. Angka itu berasal dari telemetri GitHub sendiri, jadi bacalah sebagai tanda adopsi, bukan bukti akurasi.

Sejak 1 Juni 2026, review Copilot memakai AI credits ditambah GitHub Actions minutes untuk repo privat. GitHub memperkirakan satu review memakan 0,05 sampai 1 dolar AS pada effort Lite dan 0,25 sampai 5 dolar AS pada effort Balanced, belum termasuk Actions minutes. Pada 2 Oktober 2026, GitHub menambahkan dukungan REST dan GraphQL API untuk meminta review Copilot, jadi workflow internal bisa meminta Copilot sebagai reviewer secara programatik.

Di luar GitHub, Hugging Face merilis Serge pada pertengahan Juni 2026, diumumkan 12 Juni 2026, sebagai reviewer AI open source berlisensi Apache 2.0 yang berbicara ke endpoint yang kompatibel dengan OpenAI, sehingga bisa diarahkan ke model lokal lewat vLLM atau Ollama. PR-Agent dari Qodo, yang kini dikelola komunitas di bawah lisensi MIT, dicatat punya sekitar 13.400 star di GitHub per 12 Oktober 2026.

Studi Sun dan rekan atas 22.326 komentar review AI dari 16 GitHub Actions di 178 repo menemukan tingkat addressing, yaitu komentar yang berujung pada perubahan kode, sekitar 0,9 sampai 4,2 persen untuk review level file dan 6,5 sampai 19,2 persen untuk review level hunk, dibanding sekitar 60 persen untuk komentar manusia.

## Tiga jalur setup, pilih sesuai tim

### 1. Copilot sebagai reviewer, tanpa kode tambahan

Ini jalur tercepat kalau tim sudah memakai Copilot Business atau Enterprise. Buka PR, pilih Copilot di daftar reviewer, atau tulis `@copilot review` untuk review ulang setelah push baru. Admin juga bisa mengaktifkan review otomatis lewat ruleset.

Kuncinya ada di file instruksi. Copilot code review membaca file seperti `.github/copilot-instructions.md`, `AGENTS.md`, dan `REVIEW.md` bila ada. Di situlah kamu menulis aturan tim secara singkat: stack yang dipakai, pola yang dilarang, dan hal yang tidak perlu dikomentari, misalnya prioritas keamanan dan query N+1 di proyek Laravel dan larangan mengomentari gaya yang sudah ditangani Pint. Tanpa file ini, AI menebak konvensi dari diff saja, dan tebakannya sering generik.

### 2. Tool review khusus: CodeRabbit dan Qodo

Tool seperti CodeRabbit dan Qodo hidup sebagai GitHub App. Pasang aplikasinya ke repo, dan setiap PR otomatis direview tanpa workflow YAML buatan sendiri. Kelebihannya adalah fitur yang sudah jadi: ringkasan PR, komentar inline, aturan review berbahasa natural, dan integrasi linter deterministik. CodeRabbit membundel puluhan linter di samping review AI, jadi sebagian temuannya bisa diverifikasi mesin.

Perbandingan LogRocket yang diperbarui Oktober 2026 menempatkan Copilot sebagai pilihan paling minim setup, Qodo untuk test generation dan deployment on premises, dan CodeRabbit untuk cakupan host terluas. Harga yang dikutip di sana adalah 24 dolar AS per developer per bulan untuk CodeRabbit Pro dan 30 dolar AS untuk Qodo Teams, ditagih tahunan, dan bisa berubah. Untuk tim kecil dengan PR sedikit, workflow rakitan sendiri dengan API murah sering kali jauh lebih hemat.

### 3. Rakit sendiri dengan GitHub Actions dan API model

Jalur ini paling fleksibel dan paling murah untuk repo pribadi atau tim kecil. Kamu menulis workflow yang mengambil diff PR, mengirimkannya ke API model, lalu memposting hasilnya sebagai komentar PR. Kamu yang mengatur promptnya, ambang severitynya, dan file apa saja yang direview. Kekurangannya: kamu yang merawatnya saat API berubah atau komentar model makin berisik.

## Setup praktis: workflow rakitan dalam 30 menit

Diff diambil lewat GitHub CLI, bukan lewat `git diff` terhadap branch yang mungkin belum ter-fetch, supaya hasilnya konsisten di runner. Untuk model lokal, pakai self hosted runner, karena runner GitHub tidak bisa menjangkau `localhost` kamu. Buat file `.github/workflows/ai-code-review.yml`:

```yaml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize]
    paths: ['**.php', '**.js', '**.ts']
    paths-ignore: ['package-lock.json', 'composer.lock', '**/*.md']
permissions: {contents: read, pull-requests: write}
jobs:
  review:
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: {fetch-depth: 1}
      - name: Ambil diff PR
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: gh pr diff "$PR_NUMBER" > pr.diff
      - name: Jalankan review AI
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python3 tools/ai_review.py pr.diff > review.md
      - name: Posting komentar review
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: gh pr comment "$PR_NUMBER" --body-file review.md
```

Permission dibatasi, draft PR dilewati, dan lockfile serta file Markdown diabaikan, karena mereview kode yang masih berubah atau file hasil generate hanya menambah noise.

Lalu buat script `tools/ai_review.py` yang hanya memakai standard library Python:

```python
#!/usr/bin/env python3
import json, os, sys, urllib.request
MAX_CHARS = 12000
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
PROMPT = ("Kamu adalah reviewer kode senior. Tulis maksimal 5 temuan, "
    "urut dari yang paling berisiko. Setiap temuan harus menyebut "
    "file dan baris, menjelaskan risikonya, dan memberi perbaikan konkret.")
diff = open(sys.argv[1], encoding="utf-8").read()[:MAX_CHARS]
if not diff.strip():
    print("Tidak ada perubahan kode pada PR ini."); raise SystemExit
payload = {"model": MODEL, "messages": [
    {"role": "system", "content": PROMPT},
    {"role": "user", "content": diff}], "temperature": 0.2}
request = urllib.request.Request(
    "https://api.openai.com/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
             "Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(request, timeout=120) as response:
    print(json.load(response)["choices"][0]["message"]["content"])
```

Batas 12.000 karakter itu disengaja. Diff besar yang dikirim utuh akan mahal, lambat, dan membuat model kehilangan fokus. Simpan API key sebagai repository secret bernama `OPENAI_API_KEY`, jangan pernah menuliskannya di workflow atau di kode.

Kalau kamu memilih jalur Copilot tapi ingin memicunya dari script, pakai endpoint baru ini. Login `copilot-pull-request-reviewer[bot]` adalah identitas resmi Copilot sebagai reviewer, dan tokennya butuh permission `Pull requests: write`.

```bash
curl -L -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/requested_reviewers" \
  -d '{"reviewers":["copilot-pull-request-reviewer[bot]"]}'
```

## Aturan main supaya reviewnya tidak jadi spam

AI yang terlalu rajin lebih merusak daripada AI yang diam, karena tim akan mengabaikan semua komentarnya, termasuk yang benar. Tetapkan ambang severity: minta AI hanya melaporkan temuan medium ke atas, dan serahkan temuan minor ke linter yang deterministik dan gratis, seperti Pint, ESLint, atau PHPStan. Review hanya baris yang berubah, dan batasi temuan per PR, karena lima temuan yang tajam lebih berguna daripada tiga puluh komentar yang setengahnya salah. Jangan jadikan AI gate yang memblokir merge sendirian: status check yang menggagalkan merge sebaiknya tetap dipegang test dan static analysis.

## Kesalahan umum pemula dan cara menghindarinya

Pertama, mengirim seluruh repo atau seluruh diff tanpa batas ke model. Biayanya membengkak, hasilnya generik, dan data sensitif ikut terkirim. Kirim diff saja, potong di batas karakter, dan abaikan file hasil generate.

Kedua, memakai event `pull_request_target` untuk workflow kustom yang memegang secret, supaya bisa mereview PR dari fork. Event itu berjalan dengan konteks repo target dan secret tersedia, jadi kode dari fork yang belum direview bisa dieksekusi dengan akses itu. Untuk PR dari fork, pakai event `pull_request` biasa tanpa secret, atau tool resmi yang dirancang menangani fork dengan aman.

Ketiga, membiarkan AI mengutip secret yang ia temukan di komentar PR. Putar secret itu, hapus dari histori bila sudah terlanjur ter-commit, dan perbaiki lewat jalur yang tidak mengekspos nilainya.

Keempat, tidak menulis instruksi repo. Tanpa file instruksi yang menyebut stack dan larangan spesifik, AI memberi saran generik yang tidak cocok dengan codebase kamu.

Kelima, mengukur sukses dari jumlah komentar. Ukur dari berapa komentar yang berujung pada perubahan kode, berapa yang ditolak, dan berapa lama PR menunggu review manusia.

## Cara mengukur dan langkah pertama hari ini

Ambil 10 PR terakhir yang direview AI, lalu catat berapa komentar yang berujung commit perbaikan, berapa yang ditolak, dan berapa yang diabaikan. Kalau lebih dari separuh diabaikan, masalahnya hampir pasti di prompt atau ambang severity, bukan di modelnya. Kalau AI selesai dalam hitungan menit tapi manusia baru membuka PR besok pagi, masalah utamamu adalah beban reviewer, bukan tool review.

Mulai dari satu repo kecil yang PR-nya kamu kenal baik. Kalau sudah punya Copilot, aktifkan review otomatis di repo itu saja, tulis file instruksi sepanjang 10 sampai 15 baris, dan pantau 5 PR pertama. Kalau mau jalur gratis, salin workflow dan script di atas, pasang secret API key, dan buka satu PR percobaan dengan satu bug yang jelas, misalnya query mentah dengan input user atau N+1 di loop Blade.

AI code review di 2026 sudah cukup matang untuk menjadi penyaring pertama di setiap PR, dan belum cukup bisa dipercaya untuk menjadi satu-satunya reviewer. Setup yang benar menempatkannya di posisi itu: cepat, spesifik, hemat, dan selalu diawasi manusia.
