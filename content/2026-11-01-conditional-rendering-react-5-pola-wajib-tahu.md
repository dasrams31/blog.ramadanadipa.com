---
title: Conditional Rendering di React: 5 Pola yang Wajib Tahu
description: 5 pola conditional rendering di React: early return, ternary, operator &&, switch, dan object lookup, lengkap contoh kode dan jebakan sering menjebak pemula.
date: 2026-11-01
tags: [react, javascript, frontend, jsx]
faq:
  - Apa itu conditional rendering di React?
  - Conditional rendering adalah teknik menampilkan komponen atau elemen yang berbeda berdasarkan kondisi, misalnya status login, hasil fetch data, atau peran pengguna. Di React ini dilakukan dengan JavaScript biasa, karena JSX pada dasarnya adalah ekspresi JavaScript.
  - Kenapa angka 0 muncul di layar saat memakai operator && di React?
  - Karena 0 adalah nilai falsy yang tetap dirender oleh React sebagai teks. Solusinya, ubah kondisi menjadi perbandingan eksplisit seperti jumlah > 0, atau ubah nilainya menjadi boolean dengan Boolean(jumlah) sebelum dipakai di dalam JSX.
  - Kapan memakai ternary dan kapan memakai early return?
  - Pakai ternary untuk pilihan singkat di dalam JSX, misalnya teks tombol atau satu elemen yang berganti. Pakai early return kalau satu kondisi mengubah seluruh isi komponen, misalnya saat loading, error, atau data belum ada.
  - Apakah boleh menulis if di dalam JSX?
  - Tidak. Kurung kurawal di JSX hanya menerima ekspresi, sedangkan if adalah statement. Tulis if di luar return, atau ubah logikanya menjadi ternary, operator &&, switch di dalam fungsi, atau object lookup.
---

Hampir semua antarmuka React adalah soal kondisi. Tampilkan tombol keluar kalau pengguna sudah login, spinner kalau data masih dimuat, pesan kosong kalau keranjang belanja belum ada isinya, dan panel admin hanya untuk peran admin. Semua itu conditional rendering, dan cara menuliskannya menentukan apakah komponenmu enak dibaca atau berubah menjadi teka teki.

React tidak menyediakan sintaks khusus untuk ini. Tidak ada `v-if` seperti di Vue atau `ngIf` seperti di Angular. Kamu memakai JavaScript biasa di dalam dan di sekitar JSX. Polanya sedikit dan mudah dihafal. Yang sulit adalah memilih pola yang tepat dan menghindari jebakan kecil seperti angka 0 yang tiba tiba muncul di layar.

## Kenapa JSX Tidak Punya If Sendiri

JSX terlihat seperti HTML, tapi setelah dikompilasi ia menjadi pemanggilan fungsi JavaScript. Di dalam kurung kurawal `{ }`, React hanya menerima ekspresi, yaitu kode yang menghasilkan nilai. Pernyataan `if` bukan ekspresi, sehingga tidak bisa ditulis di tengah JSX:

```jsx
// Ini SALAH dan tidak akan jalan
return (
  <div>
    {if (sudahLogin) {
      <p>Selamat datang kembali.</p>
    }}
  </div>
);
```

Solusinya ada dua arah: pindahkan logika `if` ke luar `return` dan kembalikan JSX yang berbeda dari tiap cabang, atau ganti `if` dengan ekspresi yang setara di dalam JSX, misalnya ternary atau operator `&&`. Lima pola berikut mencakup hampir semua kebutuhan nyata.

## Pola 1: Early Return dan If Else di Luar JSX

Pola ini paling mudah dibaca untuk kondisi yang mengubah seluruh isi komponen. Periksa kondisi di awal fungsi, kembalikan tampilan khusus lebih dulu, dan biarkan kode utama menangani kasus normal. Pola ini sering disebut early return atau guard clause.

```jsx
function ProfilPengguna({ pengguna }) {
  if (!pengguna) {
    return <p>Silakan login dulu.</p>;
  }

  if (pengguna.diblokir) {
    return <p>Akun ini diblokir. Hubungi admin.</p>;
  }

  return <h1>Halo, {pengguna.nama}</h1>;
}
```

Pembaca tidak perlu menggali JSX untuk tahu kapan komponen menampilkan apa. Bagian bawah fungsi sudah pasti berurusan dengan pengguna yang valid dan tidak diblokir. Pakai pola ini untuk kondisi seperti loading, error, dan data kosong. Jangan pakai untuk mengganti satu potong kecil di tengah halaman, karena itu memaksa kamu menduplikasi seluruh JSX hanya untuk satu perbedaan kecil.

## Pola 2: Ternary untuk Dua Pilihan di Dalam JSX

Operator ternary adalah `if else` versi ekspresi, sehingga legal di dalam kurung kurawal JSX. Bentuknya adalah `kondisi ? nilaiKalauBenar : nilaiKalauSalah`. Pola ini cocok untuk pilihan antara dua hal di satu tempat yang sama.

```jsx
function TombolAksi({ sudahLogin }) {
  return (
    <div>
      {sudahLogin ? <button>Keluar</button> : <button>Masuk</button>}
    </div>
  );
}

function LabelStok({ stok }) {
  return <p>{stok > 0 ? "Stok tersedia" : "Stok habis"}</p>;
}
```

Batasnya ada di keterbacaan. Satu ternary masih enak dibaca, tapi ternary di dalam ternary hampir selalu lebih sulit dipahami daripada `if else` biasa atau object lookup. Kalau salah satu cabang mulai butuh logika tambahan, pindahkan ke early return atau komponen terpisah. Ternary juga wajib punya cabang `else`. Kalau kamu hanya butuh menampilkan sesuatu saat kondisi benar, pola berikutnya lebih tepat.

## Pola 3: Operator && untuk Tampil atau Tidak Sama Sekali

Ketika elemen hanya muncul dalam satu kondisi dan hilang begitu saja dalam kondisi lain, operator `&&` adalah cara paling ringkas. Ekspresi `kondisi && <Elemen />` merender elemen saat kondisi benar, dan tidak merender apa pun saat kondisi salah.

```jsx
function Notifikasi({ jumlahBelumDibaca }) {
  return (
    <div>
      <h1>Kotak Masuk</h1>
      {jumlahBelumDibaca > 0 && (
        <p>Kamu punya {jumlahBelumDibaca} pesan belum dibaca.</p>
      )}
    </div>
  );
}
```

Perhatikan perbandingan `jumlahBelumDibaca > 0`, bukan sekadar `{jumlahBelumDibaca && ...}`. React merender angka 0 sebagai teks, sehingga variabel angka mentah di sisi kiri `&&` bisa membuat angka 0 muncul di layar saat nilainya nol. Pola `&&` ideal untuk badge, peringatan, dan banner yang hanya bergantung pada satu kondisi boolean. Jangan memakainya untuk dua pilihan yang sama sama penting, karena ketiadaan elemen adalah sinyal yang lemah. Untuk dua pilihan, ternary lebih jelas.

## Pola 4: Switch untuk Banyak Cabang yang Saling Lepas

Begitu cabangnya lebih dari dua dan tiap cabang saling lepas, `if else` berantai mulai melelahkan. Pernyataan `switch` mengelompokkan tiap nilai ke cabangnya masing masing, dan cabang `default` menangkap semua nilai yang tidak dikenali.

```jsx
function StatusPesanan({ status }) {
  switch (status) {
    case "menunggu":
      return <p>Pesanan sedang menunggu pembayaran.</p>;
    case "diproses":
      return <p>Pesanan sedang disiapkan.</p>;
    case "dikirim":
      return <p>Pesanan sedang dalam perjalanan.</p>;
    case "selesai":
      return <p>Pesanan sudah diterima. Terima kasih.</p>;
    default:
      return <p>Status pesanan tidak dikenal.</p>;
  }
}
```

Karena `switch` adalah statement, ia tidak bisa ditulis langsung di dalam JSX. Ia tinggal di badan fungsi komponen, atau di fungsi pembantu kecil yang dipanggil dari JSX. Jangan lupa cabang `default`, karena data dari API tidak selalu sesuai dugaan. Tanpa `default`, komponen bisa mengembalikan `undefined` dan React melempar error, padahal pesan fallback sederhana sudah cukup menjaga halaman tetap hidup. Switch cocok saat tiap cabang butuh logika sendiri. Kalau tiap cabang hanya memetakan satu nilai ke satu tampilan, pola kelima lebih ringkas.

## Pola 5: Object Lookup untuk Pemetaan Nilai ke Tampilan

Object lookup mengganti rantai `if else` atau `switch` dengan objek biasa. Kunci objek adalah nilai kondisinya, isi objek adalah hasil yang ingin ditampilkan. Kamu mengambil hasil dengan notasi kurung siku, seperti mengambil item dari kamus.

```jsx
const PESAN_STATUS = {
  menunggu: "Pesanan sedang menunggu pembayaran.",
  diproses: "Pesanan sedang disiapkan.",
  dikirim: "Pesanan sedang dalam perjalanan.",
  selesai: "Pesanan sudah diterima. Terima kasih.",
};

function StatusPesanan({ status }) {
  return <p>{PESAN_STATUS[status] ?? "Status pesanan tidak dikenal."}</p>;
}
```

Operator `??` menangani kunci yang tidak ada. Tanpa itu, status yang tidak dikenal menghasilkan `undefined` dan paragraf tampil kosong. Pola yang sama berlaku untuk komponen: buat objek yang memetakan peran ke komponen, lalu render hasil lookup dengan nama variabel berhuruf besar, karena JSX menganggap tag berhuruf kecil sebagai tag HTML biasa. Letakkan objek lookup di luar komponen kalau isinya tetap, supaya objek tidak dibuat ulang di setiap render. Pola ini paling enak untuk daftar pemetaan yang sering dibaca sekilas, misalnya status atau peran. Ia kurang cocok kalau tiap cabang butuh logika rumit yang berbeda beda, dan untuk kasus itu kembalilah ke `switch` atau `if else`.

## Kapan Memakai Pola yang Mana

Early return untuk kondisi yang mengubah seluruh isi komponen, seperti belum login, loading, error, atau data kosong. Ternary untuk dua pilihan singkat di satu tempat di dalam JSX, seperti label atau satu tombol yang berganti. Operator `&&` untuk elemen opsional yang muncul atau hilang berdasarkan satu kondisi boolean. Switch untuk banyak cabang yang masing masing butuh logika sendiri. Object lookup untuk pemetaan sederhana dari satu nilai ke satu tampilan, terutama kalau daftarnya panjang tapi tiap cabangnya pendek. Kalau ragu, pilih pola yang paling cepat dipahami orang yang baru pertama kali membaca komponen itu. Kode conditional rendering dibaca jauh lebih sering daripada ditulis.

## Kesalahan Umum Pemula

Pertama, jebakan angka 0 dengan operator `&&`. Di JavaScript, `0` adalah nilai falsy, tapi React tetap merendernya sebagai teks. Kode `{jumlah && <p>Ada pesan</p>}` menampilkan angka 0 sendirian saat `jumlah` bernilai 0. Perbaikannya adalah perbandingan eksplisit seperti `jumlah > 0`, atau `Boolean(jumlah)`.

Kedua, ternary bersarang. Kode `a ? x : b ? y : z` memaksa pembaca berhenti dan mengurai urutan evaluasinya. Begitu muncul ternary kedua, pindahkan logika ke `if else`, `switch`, atau object lookup.

Ketiga, menumpuk logika di dalam JSX. Hitung dulu nilainya di atas `return`, beri nama variabel yang menjelaskan maksudnya, lalu pakai variabel itu di JSX. Contohnya, hitung `const adaPesan = jumlahBelumDibaca > 0` sebelum `return`, lalu tulis `{adaPesan && <p>...</p>}`.

Keempat, lupa menangani kasus tidak dikenal. Tanpa cabang `default` di `switch` atau fallback `??` di object lookup, komponen bisa mengembalikan `undefined` atau menampilkan area kosong. Selalu sediakan tampilan fallback, walau hanya pesan singkat.

Kelima, memaksa menulis `if` di dalam JSX. Kurung kurawal JSX hanya menerima ekspresi. Tulis `if` di luar `return`, atau ubah menjadi ternary, `&&`, atau pemanggilan fungsi pembantu.

Keenam, mengembalikan `undefined` saat tidak ada yang perlu ditampilkan. Kembalikan `null` secara eksplisit, karena `null` adalah cara React yang sah untuk berkata tidak ada tampilan, sedangkan `undefined` dari komponen membuat React protes.

## Langkah Praktis yang Bisa Langsung Dicoba

Latihan terbaik adalah satu komponen daftar yang menangani empat keadaan: sedang memuat, gagal, kosong, dan berisi data. Keempat keadaan ini muncul di hampir semua halaman aplikasi nyata.

```jsx
function DaftarProduk({ produk, sedangMemuat, galat }) {
  if (sedangMemuat) {
    return <p>Memuat produk...</p>;
  }

  if (galat) {
    return <p>Gagal memuat produk: {galat}</p>;
  }

  if (produk.length === 0) {
    return <p>Belum ada produk.</p>;
  }

  return (
    <ul>
      {produk.map((item) => (
        <li key={item.id}>{item.nama}</li>
      ))}
    </ul>
  );
}
```

Buat komponen di atas dengan data contoh berupa array kosong, array berisi dua produk, dan nilai `sedangMemuat` yang bisa diubah. Uji keempat keadaan satu per satu dan pastikan tidak ada yang menampilkan halaman kosong tanpa pesan. Lalu tambahkan badge jumlah produk dengan operator `&&` dan kondisi `produk.length > 0`, dan uji dengan array kosong untuk memastikan angka 0 tidak muncul. Terakhir, buat komponen status pesanan versi `switch`, tulis ulang sebagai object lookup, dan bandingkan mana yang lebih cepat kamu pahami saat membacanya ulang keesokan hari.

Conditional rendering bukan soal menghafal lima pola, melainkan kebiasaan memilih pola yang membuat maksud kode langsung terlihat. Kuasai kelimanya, dan sebagian besar kebingungan soal tampilkan apa dan kapan di React akan hilang dengan sendirinya.
