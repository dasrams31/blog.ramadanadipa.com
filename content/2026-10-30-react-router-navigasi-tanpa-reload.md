---
title: React Router: Navigasi Halaman Tanpa Reload
description: Pindah halaman React tanpa reload itu tugas React Router. Pelajari setup Routes, Link, NavLink, useParams, nested route, dan lazy loading dengan contoh lengkap.
date: 2026-10-30
tags: [react, javascript, react-router, frontend]
faq:
  - Apa itu React Router dan kenapa dibutuhkan?
  - React Router adalah library routing untuk aplikasi React. Ia mengubah URL dan menampilkan komponen yang sesuai tanpa reload halaman, sehingga aplikasi terasa cepat seperti aplikasi native.
  - Apa bedanya Link dan tag a biasa di React?
  - Tag a biasa meminta halaman baru ke server dan me-reload seluruh aplikasi, termasuk state React yang hilang. Link dari React Router hanya mengubah URL dan merender komponen baru, state tetap terjaga.
  - Kenapa halaman React Router blank setelah refresh di production?
  - Karena server tidak mengenali URL seperti /dashboard dan mengembalikan 404. Solusinya, konfigurasi server agar semua route diarahkan ke index.html, misalnya lewat fallback di Nginx atau konfigurasi hosting SPA.
  - Apakah React Router masih relevan kalau sudah ada Next.js?
  - Ya, untuk aplikasi single page yang dibangun dengan Vite atau Create React App, React Router tetap pilihan standar. Next.js lebih cocok kalau kamu butuh server side rendering dan routing berbasis file.
---

Kalau aplikasi React kamu memakai tag `<a href="/dashboard">` untuk pindah halaman, kamu sebenarnya sedang merusak keunggulan utama React. Setiap klik meminta halaman baru ke server, browser me-reload seluruh aplikasi, dan semua state di memori hilang begitu saja. Form yang sedang diisi pengguna ikut terhapus, data yang sudah di-fetch harus diambil ulang, dan perpindahan halaman terasa lambat.

React Router menyelesaikan masalah ini. Ia mencegat perubahan URL di sisi klien, mencocokkannya dengan daftar route yang kamu definisikan, lalu merender komponen yang sesuai tanpa reload. State tetap hidup, transisi terasa instan, dan URL tetap bisa dibagikan, di-bookmark, dan dibuka langsung.

## Instalasi dan Setup Minimal

Instal dulu librarynya di project React kamu:

```bash
npm install react-router-dom
```

Lalu bungkus aplikasi dengan `BrowserRouter` dan definisikan route di dalam `Routes`. Setiap `Route` memasangkan satu path dengan satu komponen:

```jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Beranda from "./pages/Beranda";
import Tentang from "./pages/Tentang";
import TidakDitemukan from "./pages/TidakDitemukan";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Beranda />} />
        <Route path="/tentang" element={<Tentang />} />
        <Route path="*" element={<TidakDitemukan />} />
      </Routes>
    </BrowserRouter>
  );
}
```

Tiga hal penting di sini. Pertama, `BrowserRouter` harus membungkus semua komponen yang memakai fitur routing, jadi letakkan di level paling atas. Kedua, path `*` adalah route penangkap untuk URL yang tidak cocok dengan route lain, pakai ini untuk halaman 404. Ketiga, di React Router versi 6 ke atas tidak ada lagi props `exact`, karena pencocokan path sudah eksak secara default.

## Link, NavLink, dan Navigasi Programatik

Jangan pakai tag `<a>` untuk navigasi internal. Pakai `Link`, yang merender tag `<a>` di DOM tapi mencegat kliknya agar tidak reload:

```jsx
import { Link, NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav>
      <Link to="/">Beranda</Link>
      <Link to="/tentang">Tentang</Link>
      <NavLink
        to="/dashboard"
        className={({ isActive }) => (isActive ? "aktif" : "")}
      >
        Dashboard
      </NavLink>
    </nav>
  );
}
```

`NavLink` sama seperti `Link`, tapi memberi tahu kamu apakah route-nya sedang aktif lewat fungsi `className` atau `style`. Ini cara paling bersih untuk menandai menu yang sedang dibuka, tanpa harus membandingkan `window.location` secara manual.

Untuk navigasi dari dalam kode, misalnya setelah login berhasil atau form tersimpan, pakai hook `useNavigate`:

```jsx
import { useNavigate } from "react-router-dom";

export default function FormLogin() {
  const navigate = useNavigate();

  function handleSubmit(event) {
    event.preventDefault();
    // proses login di sini, misalnya simpan token
    navigate("/dashboard", { replace: true });
  }

  return <form onSubmit={handleSubmit}>{/* input login */}</form>;
}
```

Opsi `replace: true` mengganti entri history saat ini, jadi tombol back browser tidak membawa pengguna kembali ke halaman login setelah berhasil masuk. Detail kecil seperti ini yang membedakan aplikasi yang terasa rapi dengan yang terasa asal jadi.

## Route Dinamis dengan useParams

Halaman detail seperti profil user atau artikel tidak mungkin ditulis satu per satu sebagai route statis. Pakai parameter di path dengan titik dua, lalu baca nilainya dengan `useParams`:

```jsx
import { Routes, Route, useParams } from "react-router-dom";

function DetailProduk() {
  const { id } = useParams();
  return <h1>Detail produk dengan ID: {id}</h1>;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/produk/:id" element={<DetailProduk />} />
    </Routes>
  );
}
```

Mengunjungi `/produk/42` akan merender komponen dengan `id` bernilai `"42"`. Ingat, nilai dari `useParams` selalu string. Kalau kamu butuh angka untuk query database atau API, konversi dulu dengan `Number(id)` dan tangani kasus nilainya bukan angka.

## Nested Route dan Layout Bersama

Halaman dashboard biasanya berbagi layout yang sama: sidebar, header, lalu konten yang berganti. Menyalin layout ke setiap halaman adalah pemborosan. Definisikan route induk dengan layout, lalu letakkan route anak di dalamnya. Komponen layout merender `Outlet` di posisi konten anak:

```jsx
import { Routes, Route, Outlet } from "react-router-dom";

function LayoutDashboard() {
  return (
    <div>
      <aside>Sidebar dashboard</aside>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

function Ringkasan() {
  return <h1>Ringkasan dashboard</h1>;
}

function Pengaturan() {
  return <h1>Pengaturan</h1>;
}

export default function AppRoutes() {
```

Route `index` adalah halaman default saat pengguna membuka `/dashboard` persis, tanpa segmen tambahan. Path anak ditulis relatif, tanpa slash di depan, sehingga `/dashboard/pengaturan` terbentuk otomatis dari gabungan path induk dan anak. Kesalahan paling umum di sini adalah lupa menulis `Outlet`, akibatnya halaman anak tidak pernah tampil padahal route-nya sudah benar.

## Route Terproteksi dengan Pola Sederhana

React Router tidak punya konsep route terproteksi bawaan, tapi polanya mudah dibuat sendiri dengan komponen pembungkus. Komponen ini memeriksa status login, dan mengarahkan ke halaman login kalau belum masuk:

```jsx
import { Navigate } from "react-router-dom";

function RouteTerproteksi({ children }) {
  const token = localStorage.getItem("token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/dashboard"
        element={
          <RouteTerproteksi>
            <LayoutDashboard />
          </RouteTerproteksi>
        }
      />
    </Routes>
  );
}
```

Ini proteksi di sisi tampilan saja, bukan keamanan sungguhan. API backend kamu tetap harus memvalidasi token di setiap request, karena siapa pun bisa mengutak-atik `localStorage` dari DevTools. Anggap route terproteksi sebagai soal pengalaman pengguna, bukan soal keamanan.

## Lazy Loading Supaya Bundle Tidak Membengkak

Kalau semua halaman di-import di awal, pengguna harus mengunduh seluruh aplikasi sebelum melihat halaman pertama. Pecah bundle per halaman dengan `React.lazy` dan `Suspense`:

```jsx
import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

const Beranda = lazy(() => import("./pages/Beranda"));
const Dashboard = lazy(() => import("./pages/Dashboard"));

export default function AppRoutes() {
  return (
    <Suspense fallback={<p>Memuat halaman...</p>}>
      <Routes>
        <Route path="/" element={<Beranda />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Suspense>
  );
}
```

Dengan pola ini, kode halaman dashboard baru diunduh saat pengguna benar-benar membukanya. Untuk aplikasi kecil perbedaannya tidak terasa, tapi begitu halaman bertambah banyak dan ada dependensi berat seperti chart atau editor, efeknya langsung terasa di waktu muat awal.

## Kesalahan Umum Pemula

Pertama, memakai komponen routing di luar `BrowserRouter`. Errornya jelas, React Router akan mengeluh bahwa `useNavigate` atau `Link` dipakai di luar konteks Router. Solusinya selalu sama: pastikan `BrowserRouter` membungkus seluruh pohon komponen yang butuh routing.

Kedua, mencampur tag `<a>` dan `Link` untuk navigasi internal. Satu `<a>` yang lolos saja sudah cukup untuk me-reset seluruh state aplikasi. Aturan praktisnya: `<a>` hanya untuk link eksternal atau unduhan file, `Link` untuk semua navigasi di dalam aplikasi.

Ketiga, menulis path anak dengan slash di depan di dalam nested route. Path `/pengaturan` di dalam route induk `/dashboard` bukan berarti `/dashboard/pengaturan`, melainkan route absolut `/pengaturan` yang lepas dari induknya. Tulis path anak tanpa slash di depan kalau kamu memang memaksudkannya sebagai anak.

Keempat, lupa mengonfigurasi fallback server di production. Di development, Vite sudah menangani ini otomatis. Di production, server seperti Nginx harus diarahkan agar semua path yang tidak cocok dengan file statis dikembalikan ke `index.html`, supaya React Router yang mengambil alih. Tanpa ini, refresh di `/dashboard` menghasilkan 404 dari server padahal navigasi dari dalam aplikasi berjalan normal.

Kelima, menyimpan data penting hanya di state React lalu heran kenapa hilang saat refresh. Routing sisi klien tidak mengubah fakta bahwa refresh halaman me-reset memori aplikasi. Data yang harus bertahan, seperti token login atau isi keranjang, simpan di `localStorage` atau ambil ulang dari server saat halaman dimuat.

## Langkah Praktis yang Bisa Langsung Dicoba

Buat project Vite React baru, instal `react-router-dom`, lalu terapkan potongan kode di atas secara bertahap. Mulai dari tiga route statis dan navigasi `Link`, kemudian tambah satu route dinamis dengan `useParams`, lalu satu layout nested dengan `Outlet`. Setelah semuanya jalan, bungkus satu route dengan komponen proteksi dan pecah halaman dengan `lazy`. Di setiap tahap, buka DevTools di tab Network dan perhatikan: pindah halaman tidak lagi memicu request dokumen baru, hanya request data kalau ada. Begitu kamu melihat sendiri perbedaannya, konsep routing di React akan menempel jauh lebih kuat daripada sekadar membaca dokumentasinya.

React Router memang bukan satu-satunya cara routing di ekosistem React, tapi untuk aplikasi single page ia tetap alat yang paling lugas. Pahami `Routes`, `Link`, `useParams`, dan `Outlet`, dan kamu sudah memegang 90 persen kebutuhan routing aplikasi nyata.
