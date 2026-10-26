---
title: Next.js App Router vs Pages Router: Mana Dipelajari Dulu?
description: Bingung mulai belajar Next.js dari App Router atau Pages Router? Ini perbandingan struktur, data fetching, dan Server Component plus rekomendasi untuk pemula.
date: 2026-10-26
tags: [nextjs, react, app-router, javascript]
faq:
  - Apa itu App Router di Next.js?
  - App Router adalah sistem routing Next.js berbasis folder app, diperkenalkan di Next.js 13. Setiap folder berisi file page.js sebagai halaman, layout.js sebagai layout, dan mendukung React Server Component secara default.
  - Apa bedanya App Router dan Pages Router di Next.js?
  - Pages Router memakai folder pages dan fungsi getServerSideProps atau getStaticProps untuk data, sedangkan App Router memakai folder app, layout.js, loading.js, dan data fetching langsung di dalam Server Component.
  - Apakah Pages Router sudah tidak boleh dipakai lagi?
  - Masih boleh. Next.js tetap mendukung Pages Router, jadi project lama tidak wajib migrasi. Untuk project baru, dokumentasi Next.js mengarahkan ke App Router.
  - Saya pemula Next.js, mulai dari App Router atau Pages Router?
  - Mulai dari App Router, kecuali kamu sedang mengerjakan project lama yang memakai Pages Router. Mayoritas tutorial, lowongan, dan fitur baru Next.js sekarang berpusat di App Router.
---

Jawaban singkatnya: kalau kamu mulai belajar Next.js hari ini, pelajari App Router dulu. Satu-satunya pengecualian adalah kalau kamu sedang mengerjakan project lama yang memakai Pages Router, atau kantor tempatmu magang masih memakai struktur itu. Untuk project baru, App Router adalah jalur utama yang didorong dokumentasi Next.js, dan semua fitur baru dirilis untuk App Router.

Perbedaan keduanya bukan sekadar nama folder. App Router mengubah cara kamu berpikir soal rendering, data fetching, dan layout. Kalau kamu belajar Pages Router dulu lalu pindah ke App Router, kamu harus membongkar banyak kebiasaan. Sebaliknya, kalau kamu mulai dari App Router, memahami Pages Router saat bertemu project lama jauh lebih mudah, karena konsep dasarnya lebih sederhana.

## Perbedaan Paling Mendasar: File Menjadi Rute

Kedua router sama-sama memakai konvensi file menjadi rute, tapi folder dan nama filenya berbeda.

Struktur Pages Router:

```text
pages/
  index.js
  about.js
  blog/
    [slug].js
  api/
    hello.js
```

Struktur App Router:

```text
app/
  layout.js
  page.js
  about/
    page.js
  blog/
    [slug]/
      page.js
  api/
    hello/
      route.js
```

Di Pages Router, satu file sama dengan satu halaman. Di App Router, satu folder sama dengan satu rute, dan file `page.js` di dalamnya adalah halaman itu. Konsekuensinya, satu folder rute bisa menampung file pendamping lain: `layout.js` untuk layout khusus rute itu, `loading.js` untuk state loading, dan `error.js` untuk state error. Di Pages Router, semua itu harus kamu rakit sendiri.

Rute dinamis juga ditulis dengan cara yang sama di kedua router, yaitu folder atau file bernama `[slug]`. Yang berubah adalah cara mengambil nilainya. Di Pages Router, nilainya datang lewat `context.params` di `getServerSideProps` atau lewat `useRouter`. Di App Router, nilainya datang sebagai props `params` di Server Component:

```tsx
export default async function BlogPost({ params }) {
  const { slug } = await params;
  return <h1>Artikel: {slug}</h1>;
}
```

## Server Component: Perubahan Cara Berpikir Terbesar

Inilah perbedaan yang paling terasa. Di Pages Router, semua komponen adalah Client Component secara default: kode berjalan di browser, dan data diambil lewat fungsi khusus lalu dikirim sebagai props. Contoh klasiknya:

```jsx
export async function getServerSideProps({ params }) {
  const res = await fetch(`https://api.example.com/posts/${params.slug}`);
  const post = await res.json();
  return { props: { post } };
}

export default function BlogPost({ post }) {
  return <h1>{post.title}</h1>;
}
```

Di App Router, komponen adalah Server Component secara default: kode berjalan di server, dan kamu mengambil data langsung di dalam komponen, tanpa fungsi perantara:

```tsx
export default async function BlogPost({ params }) {
  const { slug } = await params;
  const res = await fetch(`https://api.example.com/posts/${slug}`, {
    cache: "no-store",
  });
  const post = await res.json();
  return <h1>{post.title}</h1>;
}
```

Keuntungan praktisnya nyata. Kamu bisa mengakses database, membaca file, atau memakai API key langsung di Server Component tanpa takut kodenya terkirim ke browser. Bundle JavaScript yang dikirim ke pengguna juga lebih kecil, karena komponen yang hanya merender data tidak perlu dihidrasi di browser. Di Pages Router, semua komponen masuk ke bundle client kecuali kamu memisahkannya secara manual.

Batasnya jelas: begitu komponen butuh interaktivitas seperti `useState`, `useEffect`, atau event handler `onClick`, komponen itu harus menjadi Client Component. Tandanya satu baris di paling atas file:

```tsx
"use client";

import { useState } from "react";

export default function LikeButton() {
  const [likes, setLikes] = useState(0);
  return <button onClick={() => setLikes(likes + 1)}>Suka ({likes})</button>;
}
```

Pola yang benar di App Router adalah: Server Component sebagai kerangka dan pengambil data, Client Component hanya untuk bagian yang benar-benar interaktif. Jangan mengubah seluruh halaman menjadi Client Component hanya karena ada satu tombol di dalamnya. Pisahkan tombol itu ke komponen kecil, dan biarkan sisanya tetap Server Component.

## Layout, Loading, dan Error Tanpa Boilerplate

Di Pages Router, layout bersama biasanya dipasang di `pages/_app.js`, dan state loading harus kamu kelola sendiri dengan `useState` atau dengan memantau event router.

Di App Router, tiga hal ini sudah punya konvensi file:

```tsx
export default function RootLayout({ children }) {
  return (
    <html lang="id">
      <body>
        <header>Blog Saya</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

File `layout.js` membungkus semua halaman di dalam foldernya, dan layout ini tidak di-render ulang saat pengguna berpindah halaman. File `loading.js` di folder yang sama otomatis menjadi fallback saat halaman sedang memuat data:

```tsx
export default function Loading() {
  return <p>Memuat...</p>;
}
```

Dan `error.js` otomatis menangkap error di segmen rute itu dan menampilkan UI pengganti dengan tombol coba lagi. Tiga file kecil ini menggantikan banyak kode boilerplate yang di Pages Router harus kamu tulis dan pelihara sendiri. Buat pemula, ini keuntungan besar: kamu belajar satu konvensi, dan konvensi itu berlaku sama di semua project App Router.

## Perbandingan Cepat

| Aspek | Pages Router | App Router |
|---|---|---|
| Folder rute | `pages/` | `app/` |
| File halaman | `index.js`, `about.js` | `page.js` di dalam folder rute |
| Layout bersama | `pages/_app.js` manual | `layout.js` per segmen, otomatis |
| State loading | Kelola sendiri | `loading.js` otomatis |
| Data fetching | `getServerSideProps`, `getStaticProps` | Langsung di Server Component |
| Komponen default | Client Component | Server Component |
| API route | `pages/api/*.js` | `app/api/*/route.js` |
| Cocok untuk | Project lama yang sudah jalan | Project baru dan yang dipelajari pemula |

Satu hal yang sering disalahpahami: App Router bukan sekadar Pages Router dengan nama folder baru. Model mentalnya berbeda, terutama soal Server Component dan data fetching di dalam komponen. Kalau kamu mencoba menulis kode App Router dengan pola pikir Pages Router, misalnya memaksakan semua data lewat props dari satu tempat, kamu akan melawan framework dan kodenya terasa canggung.

## Kapan Pages Router Masih Masuk Akal

Ada tiga situasi di mana Pages Router adalah jawaban yang benar, dan ketiganya bukan soal selera:

**1. Kamu memelihara project lama.** Kalau codebase sudah memakai Pages Router dan berjalan stabil, tidak ada kewajiban untuk migrasi. Migrasi router adalah pekerjaan besar yang menyentuh struktur folder, data fetching, dan layout sekaligus. Lakukan hanya kalau ada alasan bisnis yang jelas, misalnya butuh fitur yang hanya ada di App Router.

**2. Kamu bekerja di codebase yang masih Pages Router.** Di situasi ini, pelajari Pages Router secukupnya untuk bekerja efektif di codebase itu. Pengetahuan App Router-mu tetap berguna, karena konsep React di baliknya sama, tapi ikuti konvensi project yang sedang kamu kerjakan.

**3. Kamu mengikuti tutorial atau kursus lama.** Banyak materi berkualitas masih memakai Pages Router. Itu tidak masalah selama kamu sadar bahwa kamu sedang belajar pola lama, dan setelah paham dasarnya, kamu pindah ke App Router untuk project barumu.

Di luar tiga situasi itu, tidak ada alasan kuat untuk memulai project baru dengan Pages Router. Dokumentasi resmi Next.js, template `create-next-app`, dan mayoritas tutorial baru sudah memakai App Router sebagai default.

## Kesalahan Umum Pemula dan Cara Menghindarinya

**1. Belajar keduanya bersamaan.** Ini kesalahan paling boros waktu. Kamu akan mencampur sintaksnya: menulis `getServerSideProps` di file `app/page.js` yang tidak akan pernah dipanggil, atau mencari folder `pages` di project App Router. Pilih satu, kuasai sampai bisa membuat project kecil sendiri, baru pelajari yang lain saat kebutuhan muncul.

**2. Lupa menulis `"use client"` saat memakai hooks.** Kalau komponen App Router memakai `useState` atau `useEffect` tanpa baris `"use client"` di atasnya, Next.js akan menampilkan error yang menyatakan komponen itu membutuhkan hooks tapi dirender sebagai Server Component. Solusinya bukan memindahkan semua kode ke halaman, melainkan memisahkan bagian interaktif itu ke komponen kecil bertanda `"use client"`.

**3. Menaruh API key di Client Component.** API key yang ditulis di Client Component akan terkirim ke browser dan bisa dilihat siapa saja lewat developer tools. Aturannya sederhana: rahasia hanya boleh dipakai di Server Component, Route Handler, atau variabel environment server. Kalau sebuah komponen butuh data dari API berbayar, ambil datanya di Server Component lalu kirim hasilnya sebagai props ke Client Component.

**4. Mengubah seluruh halaman menjadi Client Component karena satu tombol.** Ini membuang keuntungan utama App Router. Halaman yang tadinya ringan berubah menjadi bundle client yang besar. Pisahkan tombolnya, bukan halamannya.

**5. Salah nama file di App Router.** File halaman wajib bernama `page.js`, bukan `index.js` dan bukan `Page.js`. Folder tanpa `page.js` bukan halaman, hanya segmen rute.

## Langkah Praktis yang Bisa Langsung Dicoba

1. Buat project baru dengan `npx create-next-app@latest belajar-nextjs`, terima default yang memakai App Router, lalu jalankan `npm run dev`.
2. Buat halaman blog dinamis di `app/blog/[slug]/page.js` yang mengambil data dari API publik, misalnya JSONPlaceholder, dan menampilkan judul serta isi artikel berdasarkan `params.slug`.
3. Tambahkan `app/blog/loading.js` berisi teks "Memuat...", lalu amati fallback itu muncul saat kamu membatasi kecepatan jaringan lewat tab Network di developer tools.
4. Buat komponen `LikeButton` bertanda `"use client"` seperti contoh di atas, pasang di halaman blog, dan periksa bahwa sisa halaman tetap dirender sebagai Server Component.
5. Sengaja buat satu kesalahan dari daftar di atas, misalnya hapus `"use client"` dari komponen yang memakai `useState`, lalu baca pesan errornya sampai paham. Pesan error Next.js di kasus ini cukup jelas dan merupakan guru yang bagus.

Pilih App Router, bangun satu project kecil sampai selesai, dan biarkan Pages Router menjadi pengetahuan kedua yang kamu pelajari saat bertemu project lama. Urutan belajar ini menghemat waktu paling banyak, karena kamu belajar pola yang dipakai project baru sambil tetap bisa membaca pola lama saat dibutuhkan.
