---
title: AI Review untuk GitLab dan Bitbucket: Pilihan Tool 2026
description: Repo di GitLab atau Bitbucket dan butuh AI code review? Bandingkan CodeRabbit, Greptile, Qodo, PR-Agent, dan GitLab Duo: harga, kelebihan, dan cara pasangnya.
cover: /assets/img/covers/ai-review-gitlab-bitbucket-pilihan-tool-di-luar-github.jpg
date: 2026-11-19
tags: [ai-code-review, gitlab, bitbucket, code-review]
faq:
  - Tool AI code review apa saja yang mendukung GitLab dan Bitbucket?
  - CodeRabbit, Greptile, Qodo, Cursor Bugbot, dan PR-Agent mendukung GitLab dan Bitbucket. GitLab punya opsi bawaan bernama GitLab Duo, sedangkan Bitbucket tidak punya reviewer AI bawaan sehingga harus memakai tool pihak ketiga.
  - Apakah GitHub Copilot code review bisa dipakai di GitLab?
  - Tidak. Copilot code review hanya berjalan di GitHub, dengan Azure DevOps masih berstatus public preview. Repo GitLab dan Bitbucket harus memakai tool lain seperti CodeRabbit atau PR-Agent.
  - Apa itu GitLab Duo Code Review dan berapa biayanya?
  - GitLab Duo adalah reviewer AI bawaan GitLab yang dipanggil lewat @GitLabDuo di merge request. Code Review Flow yang agentic tersedia di tier Free, Premium, dan Ultimate dengan tagihan GitLab Credits, sedangkan Duo Code Review non-agentic butuh seat Duo Enterprise di atas Premium atau Ultimate.
  - Adakah AI code review gratis untuk GitLab atau Bitbucket?
  - Ada. PR-Agent bersifat open source dengan lisensi MIT dan bisa di-host sendiri secara gratis. CodeRabbit gratis untuk repo publik, Greptile punya paket Starter gratis untuk satu developer, dan Code Review Flow GitLab tersedia di tier Free dengan GitLab Credits.
---

Kalau repo kamu di GitHub, urusan AI code review gampang. Copilot sudah terpasang, tinggal minta review. Tapi begitu repo pindah ke GitLab atau Bitbucket, pilihannya langsung menyempit. Copilot tidak mendukung kedua host itu, dan banyak tool review yang terlihat populer ternyata GitHub saja.

Artikel ini membandingkan tool yang benar-benar mendukung GitLab dan Bitbucket per November 2026, lengkap dengan harga dan cara pasangnya. Semua harga diambil dari halaman resmi vendor dan situs perbandingan yang memeriksa ulang pada 10 sampai 17 November 2026.

## Kenapa GitLab dan Bitbucket beda dari GitHub

GitHub punya ekosistem review yang matang karena Copilot terintegrasi langsung ke pull request. GitLab punya jawaban sendiri lewat GitLab Duo, tapi Bitbucket tidak punya reviewer AI bawaan sama sekali. Tim Bitbucket selalu butuh tool pihak ketiga, sementara tim GitLab bisa memilih antara fitur bawaan atau tool eksternal.

Ada satu perbedaan teknis yang sering luput. Merge request GitLab bukan sekadar pull request dengan nama lain. GitLab punya approval rules, discussion threads yang bisa di-resolve, dan pipeline yang terikat ke MR. Tool review yang baik harus paham konteks itu, bukan sekadar menempel komentar di diff.

## GitLab Duo: opsi bawaan yang paling mudah

Kalau repo kamu di GitLab, mulai dari sini dulu sebelum membeli tool lain. GitLab Duo adalah reviewer AI bawaan yang dipanggil lewat handle `@GitLabDuo` di merge request.

Perlu dibedakan dua fitur yang memakai handle sama. **Code Review Flow** adalah flow agentic yang mencapai GA di GitLab 18.8. Ia tersedia di tier Free, Premium, dan Ultimate, tidak butuh add-on, dan ditagih per pemakaian lewat GitLab Credits. Premium mendapat 12 GitLab Credits per user per bulan dan Ultimate 24, sementara tier Free harus membeli add-on Credits dulu. **GitLab Duo Code Review** adalah versi non-agentic yang butuh seat Duo Enterprise di atas Premium atau Ultimate. Versi ini menganalisis MR dan diff dalam satu pass, sedangkan Code Review Flow memakai penalaran agentic multi-langkah dengan konteks struktur repo dan dependensi lintas file.

Fitur mana yang jalan tergantung siapa yang memicu review. Kalau user pemicu punya seat Duo Enterprise, Duo Code Review yang jalan. Kalau tidak, Code Review Flow yang jalan.

GitLab terus mengembangkan fitur ini selama 2026. Duo Agent Platform mencapai GA pada 15 Januari 2026, lalu tersedia di tier Free GitLab.com sejak GitLab 18.10 pada 19 Maret 2026. GitLab 19.0 menambah review instructions di level group, dan GitLab 19.5 pada 15 Oktober 2026 menambah follow-up review di semua tier, sehingga Duo bisa melanjutkan dari komentar sebelumnya dan balasan kamu.

Kamu bisa menulis aturan review sendiri di file `.gitlab/duo/mr-review-instructions.yaml`:

```yaml
review_instructions:
  - "Fokus pada keamanan: periksa SQL injection, XSS, dan validasi input."
  - "Tandai setiap query database baru yang tidak memakai index."
  - "Abaikan perubahan di folder docs dan file *.md."
  - "Jawaban dan komentar review dalam Bahasa Indonesia."
```

Ada dua batasan yang perlu dicatat. Pertama, kamu terkunci ke model AI GitLab, tidak bisa memilih Claude, Gemini, atau GPT. Kedua, Duo memposting komentar secara otomatis tanpa alur persetujuan manusia dulu. Keputusan approval dari Duo sendiri masih Beta sejak GitLab 19.5 dan tidak dihitung sebagai required approval, jadi manusia tetap memegang keputusan merge. Untuk instalasi Self-Managed, Duo butuh GitLab 16.8 ke atas dan konektivitas cloud, jadi instalasi air-gapped tidak bisa memakainya.

## CodeRabbit: paling luas dukungannya

CodeRabbit adalah pilihan komersial yang paling sering direkomendasikan untuk tim di luar GitHub. Ia mendukung GitHub, GitLab, Azure DevOps, dan Bitbucket, termasuk edisi self-managed dari masing-masing host. Menurut perbandingan aicodereview.cc yang diperiksa 18 Oktober 2026, CodeRabbit adalah satu-satunya tool komersial yang mendokumentasikan keempat host besar beserta semua edisi self-managed-nya.

Harga per November 2026: gratis untuk repo publik. Paket Essentials 24 dolar per developer per bulan bila ditagih tahunan, atau 30 dolar bila bulanan. Paket Team dan Advanced menambah test generation, triage, dan audit blast radius. Kelebihannya adalah cakupan host dan kemampuan review di IDE serta CLI, bukan hanya di merge request. Kekurangannya, harga per seat bisa terasa mahal untuk tim kecil, dan self-hosting hanya tersedia di paket Enterprise dengan minimal 500 seat.

## Greptile: konteks seluruh repo tanpa biaya seat

Greptile memakai pendekatan berbeda. Ia mengindeks seluruh codebase dan membangun graf fungsi, class, dan dependensi, sehingga review-nya mempertimbangkan konteks di luar diff. Ia mendukung GitHub, GitLab, Bitbucket, dan Gitea.

Model harganya menarik untuk tim kecil. Paket Starter gratis untuk satu developer dengan 50 kredit per bulan. Paket Pro memakai 1 dolar per kredit tanpa biaya seat, jadi tim tidak membayar untuk anggota yang jarang membuka MR. Repo open source non-komersial yang memenuhi syarat bisa memakai Greptile gratis.

Pilih Greptile kalau review kamu sering gagal karena reviewer hanya melihat diff. Contoh klasik: fungsi diubah di satu file, tapi pemanggilnya di file lain ikut rusak. Reviewer berbasis diff tidak melihat itu.

## Qodo: satu pool kredit untuk satu tim

Qodo, dulu bernama CodiumAI, mendukung GitHub, GitLab, Bitbucket, dan Azure DevOps, plus review lewat IDE dan CLI. Paket Pro Team-nya seharga 30 dolar per bulan untuk pool kredit bersama yang dirancang sampai 30 user, bukan per seat. Model ini cocok untuk tim kecil yang pemakaian review-nya tidak merata.

Qodo tidak punya paket gratis permanen, tapi punya program open source gratis lewat aplikasi. Paket Enterprise tersedia untuk single-tenant dan on-prem.

## Cursor Bugbot: kalau tim sudah pakai Cursor

Cursor Bugbot adalah reviewer dari tim Cursor. Ia mendukung GitHub, GitLab, Bitbucket, dan Azure DevOps, dan ditagih berdasarkan pemakaian di atas paket Cursor, dengan dokumentasi Cursor menyebutnya mulai dari paket Premium seharga 30 dolar per bulan. Harga itu adalah harga paket Cursor, bukan harga Bugbot sendiri.

Pilih Bugbot kalau tim kamu sudah membayar Cursor dan memakai IDE-nya setiap hari. Jangan memilihnya hanya demi Bugbot, karena ada opsi yang lebih murah dan lebih transparan harganya.

## PR-Agent: jalur gratis dan self-hosted

PR-Agent adalah jawaban kalau anggaran nol atau data tidak boleh keluar dari server sendiri. Tool ini open source dengan lisensi MIT, dikelola komunitas sejak 23 April 2026, dan mendukung GitHub, GitLab, Bitbucket, Azure DevOps, dan Gitea. Ia adalah tool paling portabel dalam daftar ini.

Kamu menjalankannya sebagai server webhook dengan Docker. Contoh minimal untuk GitLab Self-Managed:

```bash
docker run -d --name pr-agent \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e CONFIG.GIT_PROVIDER="gitlab" \
  -e CONFIG.GITLAB.URL="https://gitlab.contoh.com" \
  -e CONFIG.GITLAB.PERSONAL_ACCESS_TOKEN="$GITLAB_TOKEN" \
  -p 3000:3000 \
  qodoai/pr-agent:latest
```

Setelah server jalan, daftarkan webhook di proyek GitLab yang mengarah ke `https://review.contoh.com/webhook`, dengan event Merge Request. PR-Agent akan memberi review otomatis setiap MR dibuka atau diperbarui. Kamu juga bisa memanggilnya dari CLI untuk satu MR tertentu:

```bash
pr-agent --pr_url="https://gitlab.contoh.com/grup/proyek/-/merge_requests/42" review
```

Kekurangannya, kamu yang mengurus semuanya: hosting, API key model, update, dan tuning prompt. Tidak ada dashboard dan tidak ada dukungan resmi, dan kualitas review sangat tergantung model yang kamu pilih. Tapi untuk tim yang butuh kontrol penuh atas data, ini satu-satunya opsi gratis yang serius.

## Bitbucket: tidak ada jalan pintas bawaan

Bitbucket tidak punya reviewer AI bawaan seperti GitLab Duo. Semua tim Bitbucket harus memakai tool pihak ketiga, dan pilihannya lebih sedikit dibanding GitLab. Untuk Bitbucket Cloud, tool yang mendokumentasikan dukungan adalah CodeRabbit, Cursor Bugbot, Greptile, Qodo, dan PR-Agent. Untuk Bitbucket Data Center, pilihannya menyempit ke CodeRabbit, Cursor Bugbot, Greptile Enterprise, dan Qodo.

Satu hal yang perlu dicek sebelum membeli: pastikan tool mendukung edisi Bitbucket kamu, Cloud atau Data Center, karena tidak semua paket mencakup keduanya.

## Tabel perbandingan cepat

| Tool | GitLab | Bitbucket | Harga mulai | Gratis |
| --- | --- | --- | --- | --- |
| GitLab Duo Code Review Flow | Ya, bawaan | Tidak | GitLab Credits, Free tersedia | Ya, tier Free dengan Credits |
| CodeRabbit | Ya, termasuk Self-Managed | Ya, Cloud dan Data Center | 24 dolar/dev/bulan tahunan | Repo publik |
| Greptile | Ya | Ya | 1 dolar per kredit | Starter 50 kredit/bulan |
| Qodo | Ya | Ya | 30 dolar/bulan pool kredit | Program open source |
| Cursor Bugbot | Ya | Ya | Paket Cursor dari 30 dolar/bulan | Tidak dinyatakan |
| PR-Agent | Ya, self-host | Ya, self-host | Gratis, bawa model sendiri | Ya, MIT |
| Bito | Ya | Ya | 12 sampai 15 dolar/seat/bulan | Tidak dinyatakan |

Harga dicek pada 10 sampai 17 November 2026 dari halaman vendor dan situs perbandingan. Selalu konfirmasi di halaman resmi sebelum membeli.

## Kesalahan umum pemula dan cara menghindarinya

Pertama, memilih tool hanya karena populer di GitHub. Copilot adalah contoh paling jelas. Ia reviewer yang bagus, tapi tidak mendukung GitLab atau Bitbucket sama sekali, dan Azure DevOps-nya masih public preview. Cek matriks host dulu, baru baca fitur.

Kedua, menganggap review AI menggantikan reviewer manusia. Tidak ada tool di daftar ini yang approval-nya bisa dihitung sebagai required approval. GitLab Duo sendiri menegaskan approval-nya masih Beta dan tidak dihitung. Tetap butuh manusia untuk merge, dan tetap butuh test serta static analysis.

Ketiga, membiarkan review AI jalan di semua MR tanpa aturan. Tanpa file instruksi seperti `.gitlab/duo/mr-review-instructions.yaml` atau aturan setara di tool lain, reviewer akan berkomentar soal gaya penulisan di setiap MR dan tim berhenti membacanya. Tulis tiga sampai lima aturan yang spesifik untuk codebase kamu, lalu evaluasi komentarnya selama seminggu.

Keempat, mengabaikan soal data. Review AI mengirim diff kamu ke model pihak ketiga, kecuali kamu self-host seperti PR-Agent dengan model lokal. Kalau codebase berisi kredensial, data pelanggan, atau logika bisnis sensitif, cek kebijakan data tool sebelum memasangnya. Untuk GitLab Self-Managed, ingat Duo butuh konektivitas cloud, jadi instalasi air-gapped tidak bisa memakainya.

Kelima, tidak mengukur kualitas review. Jangan menilai tool dari jumlah komentar, tapi dari berapa komentar yang benar-benar ditindaklanjuti. Itu yang disebut addressing rate, dan topik itu dibahas di artikel berikutnya dalam seri ini.

## Langkah pertama hari ini

Ambil satu repo GitLab atau Bitbucket yang MR-nya kamu kenal baik. Kalau di GitLab, aktifkan Code Review Flow dan tambahkan file `.gitlab/duo/mr-review-instructions.yaml` dengan tiga aturan spesifik untuk codebase itu. Kalau di Bitbucket, pasang PR-Agent dengan Docker seperti contoh di atas, atau daftar trial CodeRabbit kalau kamu mau tanpa urus server.

Buka satu MR percobaan, baca semua komentar AI, dan tandai mana yang benar, mana yang salah, dan mana yang noise. Setelah dua minggu, kamu punya data sendiri untuk memutuskan.

Sumber: GitLab Docs, Duo in merge requests, versi 19.5; Qodo Glossary, What Is GitLab Duo Code Review, Oktober 2026; aicodereview.cc, AI Code Review for GitLab, Bitbucket and Azure DevOps, 18 Oktober 2026; Repowise, Best AI Code Review Tools 2026, 10 November 2026; SmartRemoteGigs, Best AI Code Review Tools 2026, 17 November 2026.
