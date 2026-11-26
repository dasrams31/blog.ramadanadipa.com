---
title: File Instruksi Review AI: AGENTS.md vs Copilot
description: AGENTS.md, copilot-instructions.md, dan CLAUDE.md menentukan kualitas review AI di repo kamu. Peta file mana yang dibaca tool apa, plus contoh untuk Laravel.
cover: /assets/img/covers/file-instruksi-review-agents-md-copilot-instructions.jpg
date: 2026-11-26
tags: [agents-md, ai-code-review, github-copilot, claude-code, developer-tools]
faq:
  - Apa itu AGENTS.md dan kenapa banyak repo memakainya?
  - AGENTS.md adalah file Markdown di root repo yang berisi aturan kerja untuk AI coding agent: perintah build dan test, struktur folder, dan konvensi kode. Format ini terbuka, dipakai lebih dari 60.000 proyek open source, dan dibaca Codex, Copilot, Cursor, Gemini CLI, dan Claude Code.
  - Apakah Copilot membaca AGENTS.md?
  - Ya, tapi tidak di semua permukaan. Cloud agent, Copilot CLI, dan code review di GitHub.com membaca AGENTS.md, begitu juga VS Code chat. File yang dibaca hampir semua permukaan Copilot tetap .github/copilot-instructions.md, jadi banyak tim menyimpan aturan bersama di AGENTS.md dan catatan khusus Copilot di sana.
  - Apakah Claude Code membaca AGENTS.md?
  - Ya, sejak versi 2.1.277 yang rilis 18 September 2026, tapi hanya bila proyek tidak punya CLAUDE.md. Kalau kedua file ada, Claude Code membaca CLAUDE.md saja, jadi jangan isi keduanya dengan aturan yang bertentangan.
  - Seberapa panjang idealnya file instruksi review?
  - Median AGENTS.md di GitHub sekitar 437 kata atau 56 baris. Tulis yang singkat dan spesifik: perintah build dan test, aturan yang sering dilanggar, dan hal yang dilarang. File yang terlalu panjang membuat agen mengabaikan sebagian isinya dan memboroskan token di setiap request.
---

Pull request pertamaku yang direview Copilot dapat komentar yang isinya salah semua. Ia menyuruhku mengganti query Eloquent dengan query builder mentah, padahal aturan timku jelas: Eloquent dulu, query builder hanya untuk laporan berat. Ia juga menyarankan pola penamaan yang sudah kami tinggalkan dua bulan sebelumnya. Masalahnya bukan modelnya bodoh. Masalahnya, model itu tidak pernah diberi tahu aturan main di repo ini.

Solusinya satu file Markdown kecil di root repo. Sejak itu, kualitas review AI di proyekku naik drastis, dan artikel ini menjelaskan file apa saja yang terlibat, tool mana yang membaca file mana, plus contoh yang bisa langsung kamu salin.

## Kenapa review AI butuh file instruksi

AI code review bekerja dari konteks. Tanpa konteks proyek, model hanya menebak berdasarkan pola umum di internet, dan pola umum itu sering bertabrakan dengan keputusan yang sudah dibuat timmu. File instruksi menyelesaikan ini dengan cara yang paling murah: tulis sekali, lalu setiap sesi agent dan setiap review pull request membacanya otomatis.

Satu detail penting: Copilot code review membaca instruksi dari head branch pull request, bukan dari branch main. Perubahan aturan di pull request yang sama langsung memengaruhi review pull request itu, jadi perlakukan file instruksi seperti kode dan review perubahannya dengan serius.

## Tiga file yang perlu kamu kenal

Ekosistem ini sempat berantakan karena tiap tool memilih nama file sendiri. Per November 2026, peta besarnya sudah jauh lebih rapi.

**AGENTS.md** adalah format terbuka yang dikelola Agentic AI Foundation di bawah Linux Foundation. File ini diletakkan di root repo, atau di subfolder untuk aturan per modul. Aturan mainnya sederhana: file AGENTS.md yang paling dekat dengan file yang sedang diedit yang menang, dan perintah langsung dari manusia di chat selalu mengalahkan isi file. Data per 18 November 2026 menunjukkan 348 dari 1.000 repo GitHub paling banyak bintang sudah punya AGENTS.md di root, dan situs resminya mencatat pemakaian di lebih dari 60.000 proyek open source.

**`.github/copilot-instructions.md`** adalah file khusus GitHub Copilot, dibaca hampir semua permukaannya: chat di VS Code dan Visual Studio, cloud agent, code review, dan CLI. Kalau timmu hanya memakai Copilot, file ini saja sudah cukup.

**CLAUDE.md dan GEMINI.md** adalah file khusus Claude Code dan Gemini CLI. Claude Code membaca CLAUDE.md di beberapa level: level organisasi, level personal di `~/.claude/CLAUDE.md`, dan level proyek. Perubahan besar tahun ini: sejak versi 2.1.277 yang rilis 18 September 2026, Claude Code membaca AGENTS.md sendiri bila tidak ada CLAUDE.md di proyek itu. Permintaan fitur ini adalah yang paling banyak didukung di repo Claude Code, dengan 5.190 tanda jempol.

Tabel berikut merangkum siapa membaca apa, berdasarkan dokumentasi vendor per November 2026.

| File | Dibaca oleh |
| --- | --- |
| AGENTS.md | Codex, Copilot (cloud agent, CLI, code review, VS Code), Cursor, Gemini CLI, Claude Code (bila tanpa CLAUDE.md), dan 20 tool lain |
| .github/copilot-instructions.md | Hampir semua permukaan Copilot |
| .github/instructions/*.instructions.md | Cloud agent dan code review Copilot, terikat path lewat applyTo |
| CLAUDE.md | Claude Code, dan Copilot CLI ikut membacanya |
| GEMINI.md | Gemini CLI, dan Copilot CLI ikut membacanya |

## Copilot punya lapisan instruksi sendiri

Copilot adalah tool dengan lapisan instruksi paling banyak, dan di sinilah kebanyakan tim salah kaprah. Ada tiga lapisan yang perlu dipahami.

**Lapisan pertama, repository-wide.** File `.github/copilot-instructions.md` ditambahkan ke setiap request dalam konteks repo. Isinya aturan umum yang berlaku di semua file.

**Lapisan kedua, path-specific.** File di folder `.github/instructions/` dengan akhiran `.instructions.md` hanya berlaku untuk path yang cocok dengan glob `applyTo` di frontmatter-nya. Misalnya aturan migrasi database hanya berlaku untuk file di folder `database/migrations`. Ada juga kunci `excludeAgent` di frontmatter untuk menyembunyikan satu file dari agen tertentu, misalnya `"code-review"` atau `"cloud-agent"`.

**Lapisan ketiga, personal dan organisasi.** Copilot CLI dan VS Code membaca instruksi personal dari `~/.copilot/copilot-instructions.md`. Pemilik organisasi bisa menetapkan instruksi yang berlaku untuk semua repo. Di GitHub.com, urutan prioritasnya personal, lalu repo, lalu organisasi, tapi ketiganya dikirim ke model sekaligus, jadi jangan menulis aturan yang saling bertentangan.

## Contoh AGENTS.md untuk proyek Laravel

Teori tanpa contoh tidak ada gunanya, jadi ini template yang kupakai di proyek Laravel. Sesuaikan nama perintahnya dengan proyekmu, tapi pertahankan strukturnya yang pendek.

```markdown
# AGENTS.md

## Perintah

- Jalankan test: `php artisan test`
- Cek gaya kode: `./vendor/bin/pint --test`
- Jalankan dev server: `php artisan serve`

## Aturan kode

- Gunakan Eloquent untuk query biasa. Query builder mentah hanya
  untuk laporan agregat yang berat.
- Semua input user wajib divalidasi di Form Request, bukan di controller.
- Jangan ubah file migrasi yang sudah terlanjur di-merge ke main.
  Buat migrasi baru untuk perubahan skema.
- Bahasa antarmuka dan pesan error memakai Bahasa Indonesia.

## Aturan review

- Kalau menemukan query N+1, tunjukkan barisnya dan sarankan
  `with()` yang tepat, jangan tulis ulang seluruh controller.
- Jangan menyarankan paket baru tanpa menyebut alternatif bawaan
  Laravel terlebih dahulu.
- Jangan memberi komentar tentang typo di file yang tidak disentuh
  oleh pull request ini.
```

Perhatikan apa yang tidak ada di file itu: tidak ada penjelasan panjang tentang apa itu Laravel, tidak ada sejarah proyek, dan tidak ada aturan gaya yang sudah ditangani Pint secara otomatis. Setiap baris di sana adalah sesuatu yang tidak bisa ditebak model dari membaca kode saja. Untuk aturan review yang lebih detail, banyak tim menambahkan file `REVIEW.md` di samping AGENTS.md, dan Copilot code review ikut membacanya.

## Kesalahan umum pemula

**File ditulis sekali lalu dilupakan.** Data dari sekitar satu juta file AGENTS.md di GitHub menunjukkan 47,5 persen file tidak pernah diedit setelah commit yang menambahkannya. Padahal repo berubah: perintah test berganti, folder dipindah, aturan lama dicabut. Dalam satu studi, agen mengikuti file instruksi yang sudah basi alih-alih mengikuti kode yang benar dalam 90,1 persen pilihan. Aturan praktisnya: setiap kali kamu mengubah perintah build, perbarui juga file instruksinya di commit yang sama.

**Menyalin file yang sama ke banyak nama.** Sekitar sepertiga repo yang punya file untuk dua agen atau lebih menyimpan teks yang identik di bawah dua nama berbeda. Begitu satu file diperbarui dan satunya tidak, aturanmu bertentangan dengan dirimu sendiri. Pilih AGENTS.md sebagai satu sumber kebenaran, lalu tautkan dari file lain dengan satu baris `@AGENTS.md` atau symlink.

**Menulis instruksi yang bertentangan antar file.** Ini jebakan paling umum di repo yang punya CLAUDE.md dan AGENTS.md sekaligus. Claude Code membaca CLAUDE.md saja bila keduanya ada, jadi aturan di AGENTS.md menjadi tidak terlihat olehnya. Putuskan satu file utama per tool, dan pastikan file lainnya hanya menunjuk ke file utama, bukan menduplikasi isinya.

**File terlalu panjang.** Median AGENTS.md adalah 437 kata. Kalau filemu sudah melewati 1.000 kata, kemungkinan besar isinya campuran aturan dan dokumentasi proyek. Pindahkan penjelasan proyek ke README, dan biarkan file instruksi hanya berisi perintah yang harus diikuti agen.

**Menyimpan rahasia di file instruksi.** File instruksi ikut terkirim ke model di setiap request dan tersimpan di repo. Jangan pernah menulis token, kata sandi, atau URL internal yang sensitif di sana. Kalau agen butuh kredensial untuk menjalankan test, arahkan ia ke file `.env.example` dan perintah setup yang benar, bukan ke nilai aslinya.

**Menulis aturan yang tidak bisa diuji.** "Tulis kode yang bersih" bukan instruksi, itu harapan. "Semua method public di service harus punya return type" adalah instruksi, karena agen dan reviewer manusia bisa memeriksanya dari diff.

## Langkah praktis: setup 15 menit

Kalau kamu belum punya file instruksi sama sekali, lakukan ini sekarang juga.

1. Buat `AGENTS.md` di root repo dengan tiga bagian: Perintah, Aturan kode, dan Aturan review. Salin template di atas dan sesuaikan perintah build dan test dengan proyekmu.
2. Kalau timmu memakai Copilot, buat `.github/copilot-instructions.md` yang isinya satu paragraf: aturan ada di AGENTS.md, plus catatan yang memang khusus Copilot, misalnya permukaan mana yang boleh menyarankan paket baru.
3. Kalau timmu memakai Claude Code dan sudah punya CLAUDE.md, isi CLAUDE.md dengan satu baris `@AGENTS.md` supaya tidak ada duplikasi. Kalau belum punya CLAUDE.md sama sekali, tidak perlu membuatnya: Claude Code versi 2.1.277 ke atas sudah membaca AGENTS.md langsung.
4. Buat satu aturan khusus untuk folder yang rawan, misalnya `.github/instructions/migrations.instructions.md` dengan `applyTo` ke `database/migrations/**`, berisi larangan mengubah migrasi yang sudah di-merge.
5. Buka satu pull request kecil dan periksa hasil review AI-nya. Kalau komentarnya masih menyarankan hal yang sudah dilarang di file instruksi, perbaiki kata-kata aturannya, bukan modelnya. Aturan yang gagal diikuti biasanya aturannya yang ambigu.
6. Tambahkan pengingat di checklist pull request tim: perubahan perintah build atau struktur folder wajib disertai pembaruan AGENTS.md.

## Penutup

File instruksi review bukan dokumentasi dan bukan tempat curhat tentang arsitektur. Ia adalah kontrak singkat antara tim dan mesin yang membaca kode mereka setiap hari: pendek, spesifik, dan diperbarui setiap kali repo berubah.

Mulai dari AGENTS.md. Satu file, tiga bagian, lima belas menit. Review AI berikutnya akan terasa seperti datang dari rekan tim yang benar-benar pernah membaca repo kamu, bukan dari orang asing yang menebak-nebak.

Sumber: LeanOps, 18 November 2026; Simplify Software, survei 18 November 2026; host0.ai, November 2026; Codersera, 5 Oktober 2026; DEV Community, 2026.
