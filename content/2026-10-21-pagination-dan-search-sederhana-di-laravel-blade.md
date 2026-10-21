---
title: Pagination dan Search di Laravel Blade: Tutorial Lengkap
description: Tutorial pagination dan search Laravel Blade: setup paginate, form search GET, withQueryString agar filter tidak hilang, custom tampilan, dan kesalahan umum.
date: 2026-10-21
tags: [laravel, php, blade, mysql]
faq:
  - Kenapa kata kunci search hilang saat pindah halaman pagination?
  - Karena parameter query tidak ikut terbawa ke link halaman. Tambahkan withQueryString() pada hasil paginate agar kata kunci search tetap ada di URL setiap halaman.
  - Apa beda paginate() dan simplePaginate() di Laravel?
  - paginate() menghitung total data dan menampilkan nomor halaman, sedangkan simplePaginate() hanya menyediakan tombol sebelum dan sesudah tanpa menghitung total, sehingga lebih cepat untuk tabel yang sangat besar.
  - Bagaimana cara mengubah tampilan pagination bawaan Laravel?
  - Jalankan php artisan vendor:publish --tag=laravel-pagination, lalu edit file Blade di resources/views/vendor/pagination sesuai desain yang kamu mau.
  - Apakah pencarian dengan LIKE aman dari SQL injection?
  - Aman selama memakai query builder atau Eloquent, karena nilai input otomatis di-binding sebagai parameter dan tidak disisipkan mentah ke query SQL.
---

Menampilkan 10.000 data dalam satu halaman adalah cara tercepat membuat web lemot dan user kabur. Solusinya ada dua: pagination untuk membagi data per halaman, dan search supaya user bisa menemukan data yang dicari. Di Laravel, keduanya bisa dibuat dalam hitungan menit, tapi ada satu jebakan klasik yang hampir semua pemula kena: kata kunci search hilang begitu pindah halaman. Artikel ini membahas cara yang benar dari awal sampai selesai.

## Persiapan: Data Contoh

Saya pakai contoh tabel `products` dengan kolom `name`, `price`, dan `stock`. Kalau kamu mengikuti tutorial ini dengan project sendiri, sesuaikan nama model dan kolomnya. Pastikan tabel sudah berisi minimal 30 data dummy supaya pagination terlihat bekerja. Factory bawaan Laravel bisa dipakai untuk ini, cukup panggil `Product::factory(50)->create()` di seeder.

## Pagination Dasar dengan paginate()

Di controller, cukup satu baris:

```php
public function index()
{
    $products = Product::orderBy('name')->paginate(10);

    return view('products.index', compact('products'));
}
```

Di Blade, tampilkan data lalu panggil `links()`:

```blade
<table>
    @foreach ($products as $product)
        <tr>
            <td>{{ $product->name }}</td>
            <td>{{ $product->price }}</td>
        </tr>
    @endforeach
</table>

{{ $products->links() }}
```

`links()` otomatis merender tombol halaman dengan style Tailwind. Kalau project memakai Bootstrap, ubah di `AppServiceProvider`:

```php
use Illuminate\Pagination\Paginator;

public function boot(): void
{
    Paginator::useBootstrapFive();
}
```

Satu hal penting: `paginate()` harus dipanggil langsung pada query builder atau Eloquent, bukan pada collection. Kode seperti `Product::all()->paginate(10)` akan error karena `all()` mengembalikan collection yang tidak punya method `paginate`. Ini kesalahan paling umum yang saya lihat di forum Laravel Indonesia.

## Menambah Search dengan Form GET

Untuk search, pakai method GET supaya kata kunci muncul di URL. Ini penting: URL yang berisi kata kunci bisa di-bookmark, di-share ke orang lain, dan bekerja normal dengan tombol back browser.

```blade
<form method="GET" action="{{ route('products.index') }}">
    <input type="text" name="search" value="{{ request('search') }}"
           placeholder="Cari nama produk...">
    <button type="submit">Cari</button>
</form>
```

Di controller, tangkap inputnya:

```php
public function index(Request $request)
{
    $search = $request->input('search');

    $products = Product::when($search, function ($query, $search) {
            $query->where('name', 'like', "%{$search}%");
        })
        ->orderBy('name')
        ->paginate(10);

    return view('products.index', compact('products'));
}
```

Method `when()` hanya menjalankan closure kalau `$search` tidak kosong, jadi satu method melayani dua kondisi: halaman biasa dan halaman hasil pencarian. Nilai `value="{{ request('search') }}"` membuat kata kunci tetap tampil di kotak input setelah form disubmit.

Catatan soal LIKE: di MySQL, LIKE tidak case sensitive secara default, jadi mencari "laptop" akan menemukan "Laptop" dan "LAPTOP". Di PostgreSQL, LIKE itu case sensitive, jadi pakai ILIKE kalau butuh pencarian yang tidak peduli huruf besar kecil.

## Jebakan Klasik: Search Hilang Saat Pindah Halaman

Ini bagian yang paling sering bikin bingung. Kamu search "laptop", hasil muncul dengan benar, lalu klik halaman 2 dan hasilnya balik menampilkan semua produk seolah search tidak pernah dilakukan. Penyebabnya sederhana: link pagination yang dirender `links()` hanya berisi `?page=2`, parameter `search` tidak ikut terbawa.

Solusinya, tambahkan `withQueryString()`:

```php
$products = Product::when($search, function ($query, $search) {
        $query->where('name', 'like', "%{$search}%");
    })
    ->orderBy('name')
    ->paginate(10)
    ->withQueryString();
```

Sekarang URL halaman 2 menjadi `?search=laptop&page=2` dan filter tetap berlaku di semua halaman. Alternatif lama yang masih sering dipakai adalah `appends()`:

```php
->paginate(10)->appends($request->query());
```

`withQueryString()` lebih praktis karena otomatis membawa semua query string yang ada, sementara `appends()` berguna kalau kamu mau memilih parameter tertentu saja, misalnya `->appends(['search' => $search])`.

## Menampilkan Info Halaman

Selain tombol navigasi, Laravel menyediakan method untuk info halaman yang membuat UI terasa lebih profesional:

```blade
<p>
    Menampilkan {{ $products->firstItem() }} sampai {{ $products->lastItem() }}
    dari {{ $products->total() }} produk
</p>
```

Hati-hati: kalau hasil pencarian kosong, `firstItem()` mengembalikan null dan tampilannya jadi aneh. Bungkus dengan pengecekan:

```blade
@if ($products->total() > 0)
    <p>Menampilkan {{ $products->firstItem() }} sampai {{ $products->lastItem() }}</p>
@else
    <p>Tidak ada produk yang cocok dengan pencarian kamu.</p>
@endif
```

## simplePaginate untuk Tabel Besar

`paginate()` menjalankan satu query COUNT tambahan untuk menghitung total data. Untuk tabel dengan jutaan baris, COUNT bisa terasa lambat. Kalau kamu tidak butuh nomor halaman dan cukup dengan tombol "sebelum" dan "sesudah", pakai `simplePaginate()`:

```php
$products = Product::orderBy('name')->simplePaginate(10);
```

Di Blade tetap pakai `{{ $products->links() }}`. Perlu diingat, method seperti `total()`, `firstItem()`, dan `lastItem()` tidak tersedia di simple paginator, jadi sesuaikan bagian info halamannya. Untuk kebanyakan aplikasi CRUD biasa, `paginate()` sudah lebih dari cukup. Pakai `simplePaginate()` hanya kalau profiling menunjukkan query COUNT jadi masalah.

## Custom Tampilan Pagination

Tampilan bawaan kadang tidak cocok dengan desain yang sudah dibuat. Publish view pagination ke project:

```bash
php artisan vendor:publish --tag=laravel-pagination
```

File Blade muncul di `resources/views/vendor/pagination/`. Edit `tailwind.blade.php` atau buat file sendiri dari nol, lalu panggil dengan nama view:

```blade
{{ $products->links('vendor.pagination.custom') }}
```

Cara ini jauh lebih rapi daripada menimpa CSS bawaan dengan `!important` di mana-mana. Kamu punya kontrol penuh atas markup tombolnya, termasuk menambahkan ikon atau mengubah struktur HTML-nya.

## Kesalahan Umum dan Cara Menghindarinya

Pertama, memakai POST untuk form search. Selain URL tidak bisa dibagikan, link pagination yang memakai GET akan kehilangan konteks search. Selalu pakai GET untuk pencarian, simpan POST untuk aksi yang mengubah data.

Kedua, memanggil `paginate()` setelah `get()` atau `all()`. Ingat, paginate adalah method query builder, bukan collection. Urutan yang benar: bangun query dulu, paginate paling akhir sebelum dikirim ke view.

Ketiga, lupa `withQueryString()`. Gejalanya selalu sama: filter hilang di halaman 2 ke atas. Kalau kamu baru sadar setelah fitur jadi, cukup tambahkan satu method chain ini tanpa mengubah logika lain.

Keempat, search di kolom yang tidak di-index pada tabel besar. LIKE dengan wildcard di depan (`%laptop`) tidak bisa memakai index B-tree, jadi databasenya harus scan satu per satu. Untuk data di bawah ratusan ribu baris ini masih aman, tapi kalau sudah jutaan baris pertimbangkan full text index atau layanan seperti Meilisearch.

Kelima, tidak membatasi panjang input search. Tambahkan validasi ringan supaya query LIKE tidak menerima string raksasa:

```php
$request->validate([
    'search' => 'nullable|string|max:100',
]);
```

## Langkah Praktis yang Bisa Langsung Dicoba

1. Buat route dan controller index seperti contoh di atas pada project Laravel kamu.
2. Isi tabel dengan minimal 30 data lewat factory di seeder, lalu jalankan `php artisan db:seed`.
3. Buka halaman, search satu kata kunci, lalu klik halaman 2. Pastikan kata kunci tetap ada di URL dan hasil tetap terfilter.
4. Coba ganti `paginate(10)` dengan `simplePaginate(10)` dan perhatikan perbedaan tombol navigasinya.
5. Publish view pagination dan ubah satu class CSS untuk melihat seberapa mudah kustomisasinya.

Pagination dan search terlihat sepele, tapi implementasi yang benar membuat aplikasi terasa jauh lebih profesional. Kuncinya cuma tiga: paginate di level query, form search pakai GET, dan jangan lupa `withQueryString()`. Kuasai tiga ini dan kamu sudah selangkah lebih maju dari kebanyakan tutorial copy paste di luar sana.
