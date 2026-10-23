---
title: Cara Fetch Data API di React dengan useEffect dan Axios
description: Tutorial fetch data API di React dengan useEffect dan Axios: loading state, error handling, cleanup dengan AbortController, custom hook, dan interceptors. Lengkap dengan kode nyata.
date: 2026-10-23
tags: [react, axios, useeffect, api]
faq:
  - Bagaimana cara fetch data dari API di React?
  - Gunakan useEffect untuk memanggil API lewat Axios atau fetch, simpan hasilnya ke state dengan useState, dan render berdasarkan state loading, error, dan data.
  - Kenapa harus pakai cleanup saat fetch data di useEffect?
  - Karena komponen bisa di-unmount sebelum request selesai. Tanpa cleanup, kamu akan memanggil setState pada komponen yang sudah hilang dan memicu warning memory leak di React.
  - Axios atau fetch bawaan, mana yang lebih baik untuk project React?
  - Axios lebih nyaman untuk project serius karena punya interceptors, timeout, dan transformasi JSON otomatis. Fetch bawaan cukup untuk kebutuhan sederhana tanpa dependensi tambahan.
  - Kenapa data API saya tidak muncul padahal tidak ada error?
  - Biasanya karena struktur respons tidak sesuai dugaan, misalnya data bersarang di response.data.data. Cek dengan console.log respons mentahnya dulu sebelum menulis logika render.
---

Hampir semua aplikasi React yang pernah saya buat butuh mengambil data dari API: daftar produk, data user, hasil pencarian. Polanya selalu sama, yaitu panggil API saat komponen pertama kali tampil, tampilkan loading selama menunggu, lalu render datanya atau tampilkan error kalau gagal. Artikel ini membahas cara melakukannya dengan benar menggunakan `useEffect` dan Axios, termasuk jebakan yang sering membuat pemula stuck berjam-jam.

## Setup Cepat

Buat project dengan Vite, lalu install Axios:

```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install
npm install axios
```

## Pola Dasar: Fetch Sekali Saat Komponen Muncul

Ini pola yang akan kamu pakai 90% dari waktu:

```jsx
import { useState, useEffect } from "react";
import axios from "axios";

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get("https://jsonplaceholder.typicode.com/users")
      .then((response) => {
        setUsers(response.data);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []); // dependency kosong: jalan sekali saat mount

  if (loading) return <p>Memuat data...</p>;
  if (error) return <p>Gagal memuat data: {error}</p>;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

Perhatikan tiga state terpisah: `users` untuk data, `loading` untuk status menunggu, dan `error` untuk pesan kegagalan. Pemisahan ini penting. Saya dulu pernah cuma pakai satu state data dan menebak-nebak: apakah data kosong karena belum dimuat, atau karena API memang mengembalikan array kosong? Dua hal berbeda yang butuh tampilan berbeda.

Catatan penting: data dari Axios tidak ada di `response` langsung, melainkan di `response.data`. Ini sumber bug nomor satu pemula Axios. Kalau kamu terbiasa dengan `fetch` bawaan yang mengembalikan `response.json()`, ingat bahwa Axios sudah otomatis mem-parse JSON untukmu.

## Fetch Ulang Saat Parameter Berubah

Kalau data bergantung pada sesuatu yang bisa berubah, misalnya ID user dari URL atau kata kunci pencarian, masukkan variabel itu ke dependency array:

```jsx
import { useState, useEffect } from "react";
import axios from "axios";

function UserDetail({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    axios
      .get(`https://jsonplaceholder.typicode.com/users/${userId}`)
      .then((response) => setUser(response.data))
      .finally(() => setLoading(false));
  }, [userId]); // fetch ulang setiap userId berubah

  if (loading) return <p>Memuat...</p>;
  if (!user) return <p>User tidak ditemukan.</p>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

Aturan main dependency array sederhana: setiap variabel dari luar `useEffect` yang dipakai di dalamnya harus masuk ke array. Kalau tidak, kamu dapat data basi. Kalau kebanyakan, request jalan berulang-ulang tanpa henti.

## Cleanup: Hindari SetState Setelah Unmount

Ini bagian yang paling sering dilewatkan tutorial singkat, dan paling sering menimbulkan bug di aplikasi nyata. Kalau user pindah halaman sebelum request selesai, `setUsers` tetap dipanggil pada komponen yang sudah tidak ada. React akan mengeluh soal memory leak, dan di kasus race condition kamu bisa menampilkan data yang salah.

Solusinya: batalkan request dengan `AbortController` saat komponen di-unmount:

```jsx
useEffect(() => {
  const controller = new AbortController();

  axios
    .get("https://jsonplaceholder.typicode.com/users", {
      signal: controller.signal,
    })
    .then((response) => setUsers(response.data))
    .catch((err) => {
      // Abaikan error pembatalan, itu disengaja
      if (err.name === "CanceledError") return;
      setError(err.message);
    })
    .finally(() => setLoading(false));

  // Fungsi cleanup: jalan saat unmount atau sebelum effect jalan lagi
  return () => controller.abort();
}, []);
```

Fungsi yang di-return dari `useEffect` adalah cleanup. React menjalankannya saat komponen di-unmount, dan juga sebelum effect dijalankan ulang karena dependency berubah. Dengan `controller.abort()`, request yang belum selesai dibatalkan, dan `catch` akan menerima error bernama `CanceledError` yang kita abaikan secara eksplisit.

Untuk kasus pencarian dengan input yang berubah cepat, cleanup ini juga mencegah race condition klasik: hasil pencarian "a" datang setelah hasil pencarian "ab" dan menimpa tampilan dengan data yang salah. Request lama dibatalkan sebelum request baru dikirim.

## Custom Hook: Rapikan Kode yang Berulang

Kalau kamu fetch data di banyak komponen, pola loading/error/data di atas akan di-copy paste terus. Bungkus jadi custom hook:

```jsx
import { useState, useEffect } from "react";
import axios from "axios";

function useApi(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);

    axios
      .get(url, { signal: controller.signal })
      .then((response) => setData(response.data))
      .catch((err) => {
        if (err.name === "CanceledError") return;
        setError(err.message);
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [url]);

  return { data, loading, error };
}

// Pakainya jadi bersih:
function PostList() {
  const { data: posts, loading, error } = useApi(
    "https://jsonplaceholder.typicode.com/posts"
  );

  if (loading) return <p>Memuat...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

Satu hook, dipakai di mana saja. Logika fetch terpusat, komponen cuma peduli tampilan. Ini juga tempat yang tepat kalau nanti kamu mau tambah caching atau retry.

## Axios Instance dan Interceptors untuk Project Serius

Di project nyata, base URL dan token auth dipakai di semua request. Jangan tulis ulang di tiap panggilan, buat satu instance:

```jsx
// api.js
import axios from "axios";

const api = axios.create({
  baseURL: "https://api.domainkamu.com",
  timeout: 10000, // batalkan otomatis kalau lebih dari 10 detik
  headers: { "Content-Type": "application/json" },
});

// Sisipkan token ke semua request secara otomatis
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Tangani error global di satu tempat
api.interceptors.response.use(
  (response) => response,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;
```

Dengan ini, `api.get("/users")` otomatis membawa base URL, timeout, dan token. Interceptor respons menangani 401 di satu tempat: hapus token basi dan arahkan ke login. Tanpa pola ini, kamu akan menulis logika token di puluhan file dan pasti ada yang kelewat.

## Kesalahan Umum Pemula dan Cara Menghindarinya

**1. Lupa dependency array.** `useEffect` tanpa array kedua jalan setiap render. Fetch di dalamnya berarti request baru setiap kali state berubah, yang mengubah state, yang memicu render, yang memicu fetch lagi. Loop tak berujung. Selalu tulis array-nya, walau kosong.

**2. Menulis async langsung di useEffect.** `useEffect(async () => {...})` itu salah karena effect harus mengembalikan fungsi cleanup atau undefined, bukan Promise. Bungkus dalam fungsi async di dalam effect:

```jsx
useEffect(() => {
  const controller = new AbortController();

  async function loadData() {
    try {
      const response = await axios.get(url, { signal: controller.signal });
      setData(response.data);
    } catch (err) {
      if (err.name === "CanceledError") return;
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  loadData();
  return () => controller.abort();
}, [url]);
```

**3. Tidak menangani error sama sekali.** Request bisa gagal karena network putus, server down, atau token kedaluwarsa. Tanpa state error, aplikasi cuma stuck di loading selamanya dan user tidak tahu apa-apa. Selalu ada cabang error.

**4. Salah membaca struktur respons.** API mengembalikan `{ data: { users: [...] } }` tapi kode membaca `response.data` langsung sebagai array. Selalu `console.log(response.data)` dulu saat integrasi API baru, jangan menebak strukturnya.

**5. Fetch di dalam event handler tanpa loading state.** Tombol diklik berkali-kali karena user mengira tidak terjadi apa-apa. Disable tombol saat `loading` true.

## Langkah Praktis yang Bisa Langsung Dicoba

1. Buat project Vite baru dan install Axios seperti di bagian setup.
2. Buat komponen `UserList` dengan pola dasar, pakai API gratis jsonplaceholder.typicode.com.
3. Tambahkan cleanup dengan `AbortController` dan uji dengan React StrictMode (dia sengaja me-remount komponen di development, jadi bug cleanup langsung ketahuan).
4. Refactor jadi custom hook `useApi` dan pakai di dua komponen berbeda.
5. Buat file `api.js` dengan Axios instance dan interceptor, lalu ganti semua `axios.get` dengan instance tersebut.
6. Coba matikan koneksi internet dan pastikan UI menampilkan pesan error yang jelas, bukan loading abadi.

Kuasai pola ini dan kamu sudah siap untuk 90% kebutuhan data fetching di aplikasi React. Sisanya, seperti caching agresif atau sinkronisasi real-time, baru butuh library seperti React Query atau SWR saat aplikasinya memang butuh.
