---
title: AI Code Review dan Keamanan Data: Apa yang Boleh Dikirim
description: AI code review mengirim kodemu ke server vendor. Pelajari apa yang boleh dan tidak boleh dikirim ke model, plus checklist aman untuk Copilot dan Claude Code.
cover: /assets/img/covers/ai-code-review-dan-keamanan-data-apa-yang-boleh-dikirim-ke-model.jpg
date: 2026-11-24
tags: [ai code review, keamanan data, copilot, developer, privasi]
faq:
  - Apakah kode saya dipakai untuk melatih model AI saat memakai Copilot?
  - Tergantung paketnya. Copilot Free, Pro, dan Pro+ memakai interaksi untuk training sejak 24 April 2026 kecuali kamu mematikannya di pengaturan. Paket Business dan Enterprise tidak memakai datamu untuk training.
  - Apakah file .env ikut terkirim saat AI me-review kode saya?
  - Bisa, kalau file itu masuk konteks review atau dibaca agen AI. Jangan pernah biarkan .env, dump database, atau file berisi secret berada di working tree saat memakai AI.
  - Apakah aman memakai AI code review untuk kode perusahaan?
  - Aman kalau memakai paket bisnis dengan perjanjian perlindungan data, mengaktifkan content exclusion, dan tidak mengirim secret atau data pelanggan. Akun personal untuk kode kantor adalah kombinasi yang paling berisiko.
  - Bagaimana cara me-review kode sensitif tanpa mengirim ke server vendor?
  - Pakai model lokal lewat Ollama dengan Continue atau Cline, atau jalankan tool review open source di VPS sendiri. Kualitasnya di bawah model cloud besar, tapi datamu tidak keluar dari mesinmu.
---

Aku pernah hampir menempel isi file `.env` ke chatbot AI saat debugging, karena sedang buru-buru dan chatbot itu terasa seperti rekan kerja yang bisa dipercaya. Untung sempat sadar sebelum menekan enter. Sejak hari itu aku memakai satu asumsi: apa pun yang bisa dibaca tool itu, anggap saja sudah terkirim ke server vendor.

Asumsi itu bukan paranoia. Modelnya jalan di data center, bukan di laptopmu, jadi kode harus sampai ke sana dulu sebelum bisa di-review. Artikel ini membahas apa saja yang sebenarnya terkirim, mana yang boleh dan tidak boleh dikirim, dan bagaimana menyiapkan repo supaya aman dipakai bersama AI.

## Yang sebenarnya terkirim saat kamu minta review

Banyak developer mengira yang terkirim hanya potongan kode yang mereka sorot. Kenyataannya jauh lebih luas. Ada lima jalur data yang masuk ke model saat kamu memakai AI code review.

**Konteks editor.** Tool autocomplete mengirim kode di sekitar kursor dan sering juga potongan dari file lain yang sedang terbuka.

**Konteks yang diambil dari repo.** Tool yang mengindeks repository mengirim potongan kode yang relevan dari mana saja di repo. Sebagian vendor membangun indeks itu di server mereka sendiri.

**Bacaan dan output agen.** Agen AI membaca file apa pun yang ia anggap relevan. Kalau ia menjalankan `env`, mencetak konfigurasi, atau menjalankan test yang menulis baris database ke log, output itu ikut jadi konteks dan terkirim.

**Tempelan manual.** Log, stack trace, perintah curl lengkap dengan header, screenshot, dan baris database yang kamu tempel ke chat semuanya terkirim. Ini jalur paling sering bikin bocor karena terasa sepele.

**Tool yang terhubung.** Data yang mengalir lewat MCP server atau integrasi lain bisa diteruskan ke pihak ketiga di luar penyedia model.

Aturan praktisnya: kalau tool itu bisa membaca sesuatu, anggap saja ia sudah mengirimkannya.

## Paket personal vs bisnis: aturannya beda jauh

Ini bagian yang paling sering disalahpahami. Kebijakan data AI coding tool tidak sama untuk semua paket, dan perbedaan terbesar ada di garis personal lawan bisnis.

GitHub mengumumkan pada 25 Maret 2026 bahwa mulai 24 April 2026, interaksi Copilot Free, Pro, dan Pro+ dipakai untuk melatih model kecuali pengguna mematikannya di pengaturan. Yang dipakai termasuk prompt, saran kode yang diterima, potongan kode, dan konteks terkait. Paket Business dan Enterprise tidak kena perubahan ini. GitHub menyatakan tidak memakai data Business dan Enterprise untuk melatih model AI.

Soal penyimpanan, Copilot Business dan Enterprise tidak menyimpan chat IDE dan code completion. Permukaan lain, termasuk CLI dan Coding Agent, menyimpan prompt dan saran selama 28 hari. Untuk paket personal, GitHub tidak mempublikasikan angka retensi yang setara.

Cursor punya saklar Privacy Mode. Tanpa Privacy Mode, kontenmu bisa dipakai untuk perbaikan model. Dengan Privacy Mode aktif, ada perjanjian zero data retention dengan penyedia model dan retensi sekitar 30 hari. Di paket Teams dan Enterprise, Privacy Mode aktif secara default dan admin bisa memaksakannya.

Claude Code di bawah ketentuan komersial menyatakan tidak melatih model dari konten pelanggan, dengan retensi default 30 hari. Paket konsumen memakai ketentuan berbeda, jadi akun personal dan akun tim tidak punya perlindungan yang sama.

Kenapa ini penting? Stack Overflow Developer Survey 2026 mencatat 66 persen responden memakai Claude Code dalam setahun terakhir, 59 persen memakai Copilot, dan 73 persen memakai asisten coding setiap hari. Mayoritas dari kita sudah mengirim kode ke server vendor tiap hari kerja, sering kali tanpa sadar paket apa yang sebenarnya dipakai.

Kebijakan vendor bisa berubah. GitHub mengubah default training-nya pada April 2026 setelah bertahun-tahun tidak melatih dari interaksi Copilot. Jangan mengandalkan ingatan atau artikel lama, termasuk artikel ini. Kalau kodemu sensitif, cek halaman kebijakan resmi vendor saat kamu membaca ini.

## Daftar merah: jangan pernah kirim ini

Apapun tool dan paketnya, ada data yang tidak boleh keluar dari mesinmu. Simpan daftar ini di kepala.

- API key, secret key, dan token akses apa pun, termasuk yang sudah tidak aktif
- File `.env` dan semua file konfigurasi berisi kredensial
- Private key, sertifikat, dan file `.pem`
- Connection string database lengkap dengan password
- JWT dan session token yang masih berlaku
- Data pelanggan nyata: nama, email, nomor HP, NIK, IBAN, alamat
- Dump database production dan file CSV ekspor berisi data asli
- Log production yang memuat token, cookie, atau baris data
- Screenshot yang menampilkan secret, token, atau data pelanggan
- Kredensial CI/CD, webhook secret, dan kunci deploy

Perhatikan satu pola yang berulang: kebocoran paling sering bukan dari kode aplikasi itu sendiri, tapi dari data yang menempel di sekitar kode. File fixture test berisi email karyawan asli, dump CSV yang disimpan di working tree untuk reproduksi bug, dan log yang ditempel mentah ke chat.

## Daftar hijau: aman dikirim

Sebaliknya, ini data yang umumnya aman dikirim ke model untuk review: kode aplikasi umum tanpa secret dan tanpa data pelanggan, diff pull request yang sudah dibersihkan, pesan error dan stack trace yang sudah disanitasi, skema database tanpa isi barisnya, konfigurasi contoh seperti `.env.example`, potongan log yang token dan emailnya sudah diganti placeholder, dan test dengan data dummy dari Faker.

Prinsipnya sederhana. Kalau data itu boleh kamu tampilkan di screenshot untuk artikel blog publik, kemungkinan besar aman dikirim ke model. Kalau tidak, bersihkan dulu.

## Bersihkan dulu sebelum kirim: empat langkah

Jangan mengandalkan niat baik dan ingatan. Pasang pengaman yang jalan otomatis.

### 1. Aktifkan content exclusion

Copilot Business dan Enterprise punya content exclusion di level organisasi dan repository. Daftarkan path seperti `.env` dan `secrets/` di sana. Di Cursor, buat `.cursorignore` yang sama.

Ingat satu celah: exclusion tidak menutup semua jalur. Agen dan tool terminal masih bisa membaca file yang di-ignore. Jangan simpan file sensitif di repo sama sekali.

### 2. Pasang pemindai secret di pre-commit

Gitleaks memindai staged file sebelum commit dan menggagalkan commit kalau menemukan pola secret. Pasang lewat pre-commit hook supaya kebocoran tertangkap sebelum masuk git history.

### 3. Ganti data asli dengan Faker di test dan seeder

Ini perbaikan paling murah untuk kebocoran lewat fixture. Jangan pernah memakai data pelanggan asli sebagai contoh di test. Di Laravel, factory bawaan sudah memakai Faker, jadi manfaatkan itu dan jangan menimpanya dengan data nyata.

```php
// database/factories/UserFactory.php
public function definition(): array
{
    return [
        'name' => fake()->name(),
        'email' => fake()->unique()->safeEmail(),
    ];
}
```

### 4. Model lokal untuk repo yang benar-benar sensitif

Kalau repo-mu berisi logika bisnis inti, data pelanggan, atau kode yang terikat NDA, jalankan model lokal. Continue dengan Ollama adalah kombinasi paling gampang di laptop. Kualitasnya di bawah model cloud besar, tapi datamu tidak keluar dari mesin.

```yaml
# .continue/config.yaml
name: Local Reviewer
version: 1.0.0
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
  - provider: problems
  - provider: folder
  - provider: codebase
```

## Kesalahan umum pemula

Pertama, menempel `.env` ke chat AI saat debugging error koneksi database. Kirim `.env.example` dan pesan errornya saja, lalu isi sendiri nilai yang hilang di kepalamu. Jangan pernah menempel nilai aslinya.

Kedua, memakai akun personal untuk kode kantor. Kebijakan bisnis melekat pada seat-nya, bukan pada orangnya. Developer yang login dengan Copilot Pro personal di repo perusahaan berada di bawah ketentuan konsumen, dan tidak ada kebijakan organisasi yang bisa menjangkaunya. Kalau kantormu belum menyediakan seat bisnis, itu diskusi yang layak dibawa ke lead, bukan risiko yang ditanggung diam-diam.

Ketiga, percaya `.gitignore` melindungi dari AI. File yang di-ignore memang tidak masuk git, tapi agen AI masih bisa membacanya dari disk. File sensitif harus tidak ada di working tree saat AI bekerja, bukan sekadar di-ignore.

Keempat, mengirim seluruh repository ke chat web untuk minta review. Chat web punya kebijakan data yang berbeda dari API, dan konteks yang kamu kirim di sana biasanya disimpan lebih lama. Review di IDE atau lewat API dengan paket yang tepat selalu lebih aman daripada menempel repo ke chat gratis.

## Langkah praktis hari ini

Kerjakan checklist ini sekali, lalu jadikan kebiasaan.

1. Cek paket AI coding yang kamu pakai. Kalau masih paket personal untuk kode kantor, matikan pengaturan training-nya dan ajukan seat bisnis.
2. Aktifkan content exclusion untuk `.env`, `secrets/`, dan folder ekspor data. Di Cursor, buat `.cursorignore` yang sama.
3. Pasang Gitleaks sebagai pre-commit hook dan jalankan sekali untuk seluruh repo.
4. Hapus file berisi data asli dari repo: dump, CSV ekspor, dan fixture. Ganti dengan Faker.
5. Sebelum menempel log ke AI, ganti token, email, dan nama pelanggan dengan placeholder.
6. Untuk repo paling sensitif, siapkan model lokal dengan Ollama dan Continue.

AI code review adalah alat yang bagus. Ia menemukan bug yang luput dari mataku dan mempercepat review pull request yang membosankan. Tapi ia bukan rekan kerja yang duduk di sebelahmu. Ia adalah layanan di server orang lain, dan setiap potongan konteks yang kamu berikan adalah data yang keluar dari mesinmu. Perlakukan ia seperti itu.

## Sumber

- GitHub Blog, 25 Maret 2026: pengumuman perubahan kebijakan data Copilot, berlaku 24 April 2026.
- jazz.security, Oktober 2026: perbandingan kebijakan training dan retensi Copilot, Cursor, Claude Code, dan Codex.
- DEV Community, 2026: panduan privasi data AI untuk developer.
- Stack Overflow Developer Survey 2026: 66 persen responden memakai Claude Code, 59 persen Copilot, 73 persen memakai asisten coding setiap hari.
