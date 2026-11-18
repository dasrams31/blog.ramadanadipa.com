---
title: Prompt Engineering untuk Developer: Kode Lebih Akurat
description: Prompt asal-asalan menghasilkan kode asal-asalan. Pelajari cara menulis prompt agar AI memberi kode akurat, lengkap dengan contoh Laravel dan JavaScript.
cover: /assets/img/covers/prompt-engineering-untuk-developer-kode-lebih-akurat.jpg
date: 2026-11-18
tags: [prompt-engineering, ai-coding, developer, chatgpt]
faq:
  - Apa itu prompt engineering untuk developer?
  - Prompt engineering adalah teknik menulis instruksi yang jelas dan terstruktur ke AI agar hasil kode yang diberikan akurat, sesuai konteks project, dan minim revisi. Kuncinya ada di konteks, contoh, dan batasan yang eksplisit.
  - Kenapa AI sering memberi kode yang salah atau tidak jalan?
  - Biasanya karena prompt terlalu umum, tanpa konteks stack, versi, dan batasan. AI menebak bagian yang kosong, dan tebakannya sering tidak cocok dengan project kamu.
  - Apakah prompt yang bagus harus panjang?
  - Tidak harus panjang, tapi harus lengkap. Prompt yang baik berisi peran, konteks, tugas, format output, dan batasan. Lima baris yang padat sering lebih baik daripada satu kalimat yang samar.
  - Bagaimana cara membuat AI mengikuti gaya kode project saya?
  - Tempelkan contoh kode yang sudah ada di project sebagai referensi, sebutkan aturan penamaan dan struktur folder, lalu minta AI mengikuti pola yang sama. Semakin konkret contohnya, semakin konsisten hasilnya.
---

Kamu pasti pernah mengalaminya. Minta AI buatkan fungsi login, hasilnya terlihat meyakinkan, lalu saat dijalankan malah error di tiga tempat. Atau minta dibuatkan query, hasilnya pakai sintaks MySQL padahal project kamu PostgreSQL. Masalahnya jarang ada di AI-nya. Masalahnya ada di prompt yang kita kirim.

Prompt engineering untuk developer bukan soal trik kata ajaib. Ini soal memberi AI semua informasi yang dibutuhkan seorang rekan kerja untuk menyelesaikan tugas dengan benar.

## Kenapa prompt yang samar menghasilkan kode yang salah

Model AI tidak membaca isi kepala kamu. Ia hanya membaca teks yang kamu kirim. Kalau prompt kamu berbunyi "buatkan API produk", AI harus menebak framework, bahasa, struktur database, format respons, sampai aturan autentikasi. Setiap tebakan adalah peluang salah.

Prompt yang buruk biasanya punya tiga ciri. Pertama, tidak menyebut stack dan versi. Kedua, tidak menjelaskan keadaan yang sudah ada, misalnya tabel database atau kode yang sudah ditulis. Ketiga, tidak mendefinisikan seperti apa hasil yang dianggap benar.

Bandingkan dua prompt ini. Prompt pertama: "Buatkan endpoint untuk tambah produk." Prompt kedua: "Buatkan endpoint POST /api/products di Laravel 12. Tabel products punya kolom name, price, stock, dan category_id. Validasi: name wajib minimal 3 karakter, price angka lebih dari 0, stock integer minimal 0. Kembalikan JSON dengan status 201 dan data produk. Pakai Form Request dan Resource, jangan tulis validasi di controller."

Prompt kedua jauh lebih panjang, tapi hasilnya hampir selalu langsung bisa dipakai. AI tidak perlu menebak, jadi tidak ada tebakan yang salah.

## Pola prompt yang bisa dipakai ulang

Setelah mencoba berbagai bentuk prompt di project nyata, saya menemukan satu pola yang konsisten memberi hasil bagus. Polanya punya lima bagian: peran, konteks, tugas, batasan, dan format output. Kamu tidak harus selalu memakai kelimanya, tapi untuk tugas yang kompleks, kelimanya penting.

### 1. Peran: tentukan siapa AI di tugas ini

Awali dengan peran yang spesifik. "Kamu adalah senior Laravel developer" memberi hasil yang berbeda dengan "Kamu adalah tutor pemula". Peran menentukan kedalaman jawaban, istilah yang dipakai, dan seberapa banyak penjelasan yang diberikan.

Untuk tugas coding, peran yang efektif biasanya seperti ini: "Kamu adalah senior backend developer Laravel dengan pengalaman 8 tahun. Kamu menulis kode yang mengikuti konvensi Laravel dan PSR-12."

### 2. Konteks: beri bahan mentah yang relevan

Ini bagian yang paling sering dilewatkan. Tempelkan kode yang sudah ada, skema tabel, atau potongan error. AI yang melihat kode kamu akan mengikuti gaya dan struktur yang sama.

Contoh konteks yang berguna:

```php
// Model yang sudah ada di project
class Product extends Model
{
    protected $fillable = ['name', 'price', 'stock', 'category_id'];

    public function category()
    {
        return $this->belongsTo(Category::class);
    }
}
```

Dengan konteks ini, AI tidak akan membuat model baru yang bertabrakan dengan yang sudah ada. Ia akan memakai relasi dan field yang benar.

### 3. Tugas: satu tugas, satu prompt

Jangan minta lima hal sekaligus dalam satu prompt. "Buatkan API produk, plus halaman admin, plus export Excel, plus unit test" akan menghasilkan semuanya setengah matang. Pecah jadi beberapa prompt, satu tugas per prompt, dan bangun hasilnya selangkah demi selangkah.

### 4. Batasan: sebutkan apa yang tidak boleh dilakukan

Batasan sama pentingnya dengan instruksi. Sebutkan hal-hal yang sering salah: "Jangan pakai package tambahan", "Jangan ubah struktur tabel", "Pakai Eloquent, jangan query mentah", atau "Kode harus jalan di PHP 8.3".

### 5. Format output: tentukan bentuk jawaban

Minta format yang kamu mau: "Berikan hanya kode lengkap beserta nama file", "Jelaskan dulu pendek, lalu berikan kode", atau "Berikan kode dan daftar perubahan file yang diperlukan". Format yang jelas membuat jawaban mudah disalin ke project.

## Contoh lengkap: dari prompt buruk ke prompt bagus

Misalnya kamu butuh fitur pencarian produk di Laravel. Ini contoh prompt yang sudah diperbaiki dengan pola di atas:

```
Kamu adalah senior Laravel developer.

Konteks: project Laravel 12, PHP 8.3, PostgreSQL. Model Product punya
relasi belongsTo ke Category. Route sudah memakai Route::apiResource.

Tugas: buatkan endpoint GET /api/products dengan fitur pencarian
berdasarkan nama produk dan filter berdasarkan category_id, plus
pagination 15 item per halaman.

Batasan: pakai Eloquent query builder, jangan query mentah. Pencarian
harus case-insensitive dan aman dari karakter wildcard. Jangan ubah
model yang sudah ada.

Output: kode controller lengkap, dan sebutkan file mana saja yang
perlu diubah.
```

Hasil yang diharapkan terlihat seperti ini:

```php
<?php

namespace App\Http\Controllers;

use App\Models\Product;
use Illuminate\Http\Request;

class ProductController extends Controller
{
    public function index(Request $request)
    {
        $request->validate([
            'search' => 'nullable|string|max:100',
            'category_id' => 'nullable|integer|exists:categories,id',
        ]);

        $products = Product::query()
            ->when($request->search, function ($query, $search) {
                $escaped = str_replace(['%', '_'], ['\%', '\_'], $search);
                $query->where('name', 'ilike', '%' . $escaped . '%');
            })
            ->when($request->category_id, function ($query, $categoryId) {
                $query->where('category_id', $categoryId);
            })
            ->with('category')
            ->paginate(15);

        return response()->json($products);
    }
}
```

Ada dua detail penting di kode ini. Pertama, operator `ilike` dipakai karena PostgreSQL, bukan `like` yang case-sensitive di Postgres. Prompt yang menyebut PostgreSQL membuat AI memilih operator yang benar. Kedua, karakter `%` dan `_` di-escape supaya pengguna tidak bisa menyuntikkan wildcard ke query pencarian. Detail seperti ini jarang muncul kalau promptnya samar.

## Teknik lanjutan yang benar-benar membantu

### Beri contoh input dan output

Kalau kamu butuh fungsi transformasi data, tunjukkan contoh input dan output yang diharapkan. AI jauh lebih akurat ketika melihat bentuk data yang nyata daripada deskripsi verbal.

Contoh prompt:

```
Buatkan fungsi JavaScript yang mengubah array produk berikut menjadi
objek yang dikelompokkan per kategori.

Input: [{ id: 1, name: "Kaos", category: "Pakaian", price: 50000 }]
Output: { "Pakaian": [{ id: 1, name: "Kaos", price: 50000 }] }

Fungsi harus menangani array kosong dan kategori yang belum ada.
```

Hasilnya langsung bisa dites karena contohnya sudah jelas:

```javascript
function groupByCategory(products) {
  if (!Array.isArray(products) || products.length === 0) {
    return {};
  }

  return products.reduce((grouped, product) => {
    const { category, ...rest } = product;

    if (!grouped[category]) {
      grouped[category] = [];
    }

    grouped[category].push(rest);
    return grouped;
  }, {});
}
```

### Minta AI berpikir selangkah demi selangkah

Untuk masalah yang kompleks, tambahkan kalimat: "Jelaskan dulu rencana pendekmu, lalu tulis kodenya." Kalimat ini memaksa model menyusun langkah sebelum menulis kode, dan hasilnya biasanya lebih rapi dan lebih sedikit bug.

### Iterasi, jangan sekali kirim lalu pasrah

Prompt engineering bukan satu kali tembak. Alur yang sehat adalah: kirim prompt, uji hasilnya, lalu balas dengan koreksi spesifik. "Fungsi ini gagal saat stock bernilai null, perbaiki dengan memberi nilai default 0" jauh lebih efektif daripada mengulang prompt dari awal.

Simpan percakapan itu sebagai konteks. Kalau kamu membuka chat baru untuk setiap revisi, AI kehilangan semua konteks yang sudah dibangun.

### Pakai file instruksi di project

Kalau kamu memakai AI coding assistant di editor seperti VS Code atau Cursor, manfaatkan file instruksi project. File seperti `AGENTS.md` atau `.github/copilot-instructions.md` di root project dibaca otomatis dan berlaku untuk semua prompt di repo itu. Isinya bisa aturan sederhana: stack yang dipakai, gaya penamaan, struktur folder, dan hal yang dilarang.

Contoh isi file instruksi:

```markdown
# Aturan Project

- Framework: Laravel 12, PHP 8.3, PostgreSQL 16
- Validasi selalu di Form Request, bukan di controller
- Jangan menambah package baru tanpa izin
- Semua query pakai Eloquent, dilarang query mentah
- Bahasa komentar kode: Bahasa Indonesia
```

Dengan file ini, kamu tidak perlu mengulang konteks yang sama di setiap prompt.

## Kesalahan umum pemula dan cara menghindarinya

Pertama, menyalin kode AI tanpa membaca. AI bisa menulis kode yang terlihat benar tapi punya celah keamanan, misalnya query yang rentan injection atau validasi yang bisa dilewati. Baca setiap baris sebelum masuk ke project, terutama bagian yang menyentuh autentikasi, pembayaran, dan database.

Kedua, memberi prompt yang mengandung asumsi salah. Kalau kamu menulis "di Laravel, fungsi X bekerja seperti ini" padahal sebenarnya tidak, AI akan mengikuti asumsi kamu dan menghasilkan kode yang salah dengan percaya diri. Kalau tidak yakin, tanyakan dulu: "Apakah cara ini benar di Laravel 12?" sebelum meminta kode.

Ketiga, meminta AI memperbaiki error tanpa menyertakan pesan error lengkap. Tempelkan pesan error, file yang bermasalah, dan baris yang ditunjuk error. "Error saat migrate" tidak cukup. Pesan error lengkap plus stack trace adalah bahan bakar utama debugging.

Keempat, memakai satu prompt raksasa untuk membangun fitur besar. Pecah fitur jadi potongan kecil: skema database dulu, lalu model, lalu endpoint, lalu test. Setiap potongan diverifikasi sebelum lanjut ke potongan berikutnya.

Kelima, tidak pernah menyimpan prompt yang berhasil. Kalau satu prompt menghasilkan kode yang bagus, simpan prompt itu di catatan atau di file instruksi project. Prompt yang bagus adalah aset yang bisa dipakai ulang, sama seperti snippet kode.

## Langkah praktis yang bisa dicoba hari ini

Ambil satu tugas kecil dari project kamu, misalnya membuat endpoint sederhana atau fungsi utilitas. Tulis prompt memakai pola lima bagian di atas: peran, konteks, tugas, batasan, dan format output. Tempelkan kode yang relevan sebagai konteks. Jalankan hasilnya, catat apa yang salah, lalu perbaiki dengan satu pesan lanjutan yang spesifik.

Ulangi proses ini tiga kali dalam seminggu dengan tugas yang berbeda. Kamu akan cepat merasakan perbedaannya: AI berhenti menebak, kode yang dihasilkan makin dekat dengan gaya project kamu, dan waktu yang dihabiskan untuk memperbaiki hasil AI makin sedikit.

Prompt engineering bukan bakat, tapi kebiasaan. Kebiasaan memberi konteks yang lengkap, tugas yang jelas, dan batasan yang tegas. Semakin baik kamu menjelaskan apa yang kamu mau, semakin akurat kode yang kamu dapat.
