---
title: Query Builder vs Eloquent Laravel: Kapan Pakai yang Mana
description: Bingung pilih query builder atau Eloquent di Laravel? Simak perbandingan lengkap dengan contoh kode nyata, kapan masing-masing unggul, dan kesalahan umum pemula.
date: 2026-10-11
tags: [laravel, php, eloquent, query-builder]
faq:
  - Apa perbedaan query builder dan Eloquent di Laravel?
  - Query builder (DB::table) menulis query SQL secara langsung dan mengembalikan stdClass, sedangkan Eloquent memakai model dan mengembalikan objek model lengkap dengan fitur casting, relasi, dan event. Eloquent sendiri berjalan di atas query builder.
  - Kapan sebaiknya pakai query builder dibanding Eloquent?
  - Pakai query builder untuk laporan agregat berat, join kompleks multi-tabel, bulk update/delete jutaan baris, atau query yang butuh kontrol SQL presisi. Untuk CRUD sederhana dan relasi, Eloquent lebih nyaman.
  - Apakah Eloquent lebih lambat dari query builder?
  - Sedikit, karena Eloquent melakukan hydrasi model (instansiasi objek, casting atribut, cek events). Untuk mayoritas aplikasi selisihnya tidak terasa; masalah performa biasanya datang dari N+1 query, bukan dari pilihan Eloquent vs builder.
  - Bisakah mencampur Eloquent dan query builder dalam satu query?
  - Bisa. Model::query() mengembalikan instance query builder yang tetap terikat ke model, jadi kamu bisa menulis query builder tapi hasil akhirnya tetap objek model.
---

Hampir setiap developer Laravel pemula menabrak pertanyaan yang sama: data ini saya ambil pakai `User::where(...)` atau pakai `DB::table('users')->where(...)`? Keduanya bisa, keduanya benar, tapi pilihan yang tepat bikin kode kamu jauh lebih enak dibaca, dan kadang jauh lebih cepat.

Artikel ini saya tulis berdasarkan cara saya sendiri mengambil keputusan di project nyata. Tidak ada jawaban "selalu pakai X". Yang ada: paham bedanya, lalu pilih sesuai kasus.

## Sebenarnya Mereka Satu Keluarga

Fakta yang sering bikin pemula kaget: **Eloquent dibangun di atas query builder**. Setiap kali kamu menulis `User::where('active', true)`, di balik layar Laravel membuat instance `Illuminate\Database\Query\Builder`, lalu membungkus hasilnya jadi objek model.

Buktinya gampang:

```php
use App\Models\User;

// Query Eloquent
$query = User::where('active', true);
echo $query->toSql();
// select * from "users" where "active" = ?

// Query builder-nya bisa diambil langsung dari model
$builder = User::query(); // instance Query\Builder, hasil akhir tetap model User
```

Artinya perdebatan ini bukan "dua teknologi berbeda", tapi "seberapa banyak fitur pembungkus yang kamu mau". Eloquent = query builder + model + casting + relasi + events + accessors. Query builder polos = SQL yang diekspresikan dalam PHP, hasil mentah.

## Contoh yang Sama, Dua Cara Tulis

Ambil contoh konkret: daftar 10 produk termahal yang stoknya masih ada.

Pakai Eloquent:

```php
use App\Models\Product;

$products = Product::where('stock', '>', 0)
    ->orderByDesc('price')
    ->limit(10)
    ->get();

foreach ($products as $product) {
    echo $product->name . ' - Rp' . number_format($product->price) . PHP_EOL;
    // $product adalah objek Product: ada casting, accessor, relasi
}
```

Pakai query builder:

```php
use Illuminate\Support\Facades\DB;

$products = DB::table('products')
    ->where('stock', '>', 0)
    ->orderByDesc('price')
    ->limit(10)
    ->get();

foreach ($products as $product) {
    echo $product->name . ' - Rp' . number_format($product->price) . PHP_EOL;
    // $product adalah stdClass: data mentah dari database
}
```

Hasilnya sama. Bedanya: di versi Eloquent, `$product->price` sudah di-cast sesuai definisi `$casts` di model (misal jadi integer atau decimal), ada accessor kalau kamu definisikan, dan kamu bisa panggil `$product->category` untuk relasinya. Di versi builder, yang kamu dapat persis apa yang dikembalikan database, tidak lebih.

## Perbedaan yang Benar-Benar Penting

**1. Tipe hasil.** Eloquent mengembalikan `Collection` berisi objek model. Builder mengembalikan `Collection` berisi `stdClass`. Ini penting kalau kode kamu mengandalkan method model.

**2. Fitur model tidak berlaku di builder.** Casting atribut, accessor/mutator, model events (`creating`, `saving`, dll), dan relasi hanya hidup di Eloquent. Kalau kamu pakai `DB::table('users')->insert(...)`, tidak ada event yang jalan dan tidak ada validasi level model.

**3. Mass assignment protection.** `Product::create([...])` menghormati `$fillable`/`$guarded`. `DB::table('products')->insert([...])` tidak peduli sama sekali.

**4. Performa.** Builder sedikit lebih ringan karena tidak ada hydrasi model. Pada query yang mengembalikan puluhan ribu baris atau agregat kompleks, selisihnya bisa terasa. Untuk query biasa yang mengembalikan puluhan baris, selisihnya bisa diabaikan.

**5. Ekspresivitas SQL.** Untuk join berlapis, subquery, dan agregat dengan `GROUP BY`, builder (atau `DB::raw`) sering lebih jujur dan mudah dibaca daripada memaksakan semuanya lewat relasi Eloquent.

## Kapan Pakai Eloquent

Aturan praktis saya: **mulai dari Eloquent, pindah ke builder kalau ada alasan konkret**. Eloquent menang di kasus-kasus ini:

**CRUD standar.** Ambil, buat, ubah, hapus satu atau beberapa baris. Eloquent jauh lebih ringkas:

```php
// Jauh lebih enak dibaca daripada versi builder + manual casting
$order = Order::with('items.product')->findOrFail($id);
$order->update(['status' => 'shipped']);
```

**Operasi yang butuh relasi.** Begitu query kamu melibatkan "user punya banyak post" atau "produk milik kategori", Eloquent dengan eager loading hampir selalu lebih bersih.

**Logika yang menempel di model.** Kalau kamu punya accessor seperti ini, cuma Eloquent yang bisa memakainya:

```php
// app/Models/Product.php
protected function finalPrice(): Attribute
{
    return Attribute::make(
        get: fn () => $this->price - ($this->price * $this->discount / 100),
    );
}

// $product->final_price hanya tersedia lewat Eloquent
```

**Butuh model events.** Audit log, kirim notifikasi saat data dibuat, atau sinkronisasi ke layanan lain, semua mengandalkan event Eloquent yang tidak akan jalan kalau kamu menulis lewat builder.

## Kapan Pakai Query Builder

**Laporan dan agregat berat.** Contoh: total pendapatan per bulan per kategori selama setahun. Menulis ini lewat Eloquent memaksa kamu melawan arusnya; lewat builder jauh lebih natural:

```php
$report = DB::table('order_items')
    ->join('orders', 'orders.id', '=', 'order_items.order_id')
    ->join('products', 'products.id', '=', 'order_items.product_id')
    ->join('categories', 'categories.id', '=', 'products.category_id')
    ->where('orders.status', 'paid')
    ->whereYear('orders.created_at', 2026)
    ->select(
        'categories.name as category',
        DB::raw("DATE_FORMAT(orders.created_at, '%Y-%m') as bulan"),
        DB::raw('SUM(order_items.qty * order_items.price) as total')
    )
    ->groupBy('category', 'bulan')
    ->orderBy('bulan')
    ->get();
```

**Bulk update/delete.** Mengubah 100 ribu baris satu per satu lewat model itu lambat dan boros memori. Satu query builder selesai dalam satu statement SQL:

```php
// Satu query, tanpa hydrasi 100 ribu objek model
DB::table('notifications')
    ->where('read_at', '<', now()->subYear())
    ->delete();

// Atau versi model kalau kamu tetap mau event... tapi sadar konsekuensinya
```

Catatan penting: `User::where(...)->update([...])` (mass update Eloquent) juga **tidak** memicu model events dan tidak menjalankan casting. Jadi untuk bulk operation, perilaku Eloquent dan builder praktis sama, pilih yang sintaksnya lebih pas.

**Query yang butuh kontrol SQL presisi.** Window function, `UNION`, subquery di `WHERE EXISTS`, atau hint khusus database, builder dengan `DB::raw` dan `selectSub` memberi kamu kendali penuh tanpa akrobat.

**Seeder dan migrasi data.** Untuk memindahkan atau mentransformasi data dalam jumlah besar, builder lebih cepat dan tidak membawa beban model yang tidak kamu butuhkan.

## Pola Hibrida: Yang Terbaik dari Keduanya

Kamu tidak harus memilih kubu. `Model::query()` adalah jembatan resminya: query builder yang hasilnya tetap model.

```php
use App\Models\Product;
use Illuminate\Support\Facades\DB;

// Tulis agregat ala builder, dapat objek model di akhir
$products = Product::query()
    ->select('products.*')
    ->selectSub(
        DB::table('order_items')
            ->selectRaw('SUM(qty)')
            ->whereColumn('order_items.product_id', 'products.id'),
        'total_terjual'
    )
    ->orderByDesc('total_terjual')
    ->limit(10)
    ->get();

// $products berisi objek Product, accessor & relasi tetap bisa dipakai
foreach ($products as $product) {
    echo $product->name . ' terjual ' . $product->total_terjual . PHP_EOL;
}
```

Pola ini saya pakai paling sering di project nyata: fleksibilitas builder untuk query-nya, kenyamanan model untuk hasilnya.

## Kesalahan Umum Pemula (dan Cara Menghindarinya)

**1. Hydrasi puluhan ribu model lalu kehabisan memori.** `Product::all()` di tabel berisi 200 ribu baris akan mencoba membuat 200 ribu objek di memori. Solusinya: pakai `chunk()`/`lazy()` kalau butuh model, atau builder + `cursor()` kalau cuma butuh datanya:

```php
// Aman untuk data besar
DB::table('products')->orderBy('id')->chunk(1000, function ($rows) {
    // proses 1000 baris per batch
});
```

**2. Menyalahkan Eloquent atas query yang lambat, padahal masalahnya N+1.** Sembilan dari sepuluh kasus "Eloquent lemot" yang saya temui ternyata lupa `with()`. Perbaiki dulu eager loading-nya sebelum pindah ke builder.

**3. Pakai builder untuk insert lalu heran kenapa `created_at` kosong dan event tidak jalan.** Builder tidak mengisi timestamp otomatis dan tidak memicu event. Kalau kamu butuh itu, pakai model, atau isi manual dengan `now()`.

**4. `DB::raw` dengan input user tanpa binding.** Ini lubang SQL injection. Selalu pakai parameter binding:

```php
// SALAH, rawan injection
->whereRaw("status = '{$request->status}'")

// BENAR
->whereRaw('status = ?', [$request->status])
```

**5. Over-engineering: memaksakan Eloquent untuk query analitik kompleks.** Kalau query-nya sudah butuh lima `DB::raw` dan tiga subquery di dalam rantai Eloquent, itu sinyal untuk pindah ke builder murni. Kode yang jujur lebih baik daripada kode yang "murni Eloquent" tapi tidak bisa dibaca.

## Langkah Praktis yang Bisa Dicoba Hari Ini

1. Buka satu controller di project kamu yang query-nya terasa berbelit. Cetak SQL-nya dengan `->toSql()` (atau `DB::listen` untuk binding-nya) dan baca query mentahnya.
2. Tulis ulang query itu dalam versi builder murni. Bandingkan: mana yang lebih mudah kamu pahami enam bulan dari sekarang?
3. Cari satu tempat di mana kamu me-loop hasil query besar, ganti dengan `chunk()` atau `cursor()`.
4. Kalau kamu punya laporan agregat yang ditulis dengan me-loop collection di PHP (`$collection->sum(...)` setelah `get()`), pindahkan agregatnya ke database dengan `SUM()`/`COUNT()` di query. Ini satu perubahan kecil yang sering memangkas waktu eksekusi drastis.

## Kesimpulan Singkat

Pakai **Eloquent** untuk operasi sehari-hari: CRUD, relasi, dan apa pun yang butuh fitur model. Pakai **query builder** untuk laporan berat, join kompleks, dan operasi massal. Dan jangan ragu mencampur keduanya lewat `Model::query()`.

Aturan yang saya pegang sampai sekarang: pilih yang bikin niat query-nya paling jelas dibaca. Performa menyusul, dan ketika performa memang jadi masalah, `toSql()` plus `explain` akan memberi tahu kamu persis di mana masalahnya, tidak peduli kamu pakai yang mana.
