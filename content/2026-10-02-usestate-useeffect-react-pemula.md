---
title: "useState dan useEffect di React: Penjelasan untuk Pemula dengan Contoh Nyata"
description: Bingung dengan useState dan useEffect di React? Panduan pemula dengan contoh kode nyata: counter, fetch data API, dan kesalahan umum yang wajib dihindari.
date: 2026-10-02
tags: [react, javascript, frontend]
faq:
  - Apa bedanya useState dan useEffect?
  - useState menyimpan data yang bisa berubah dan me-render ulang komponen saat berubah. useEffect menjalankan efek samping (fetch data, timer, subscription) sebagai respons terhadap render atau perubahan data.
  - Kenapa useEffect saya jalan dua kali?
  - Itu StrictMode di development yang sengaja menjalankan efek dua kali untuk mendeteksi bug. Di production build hanya jalan sekali.
  - Kapan harus pakai useEffect?
  - Hanya untuk sinkronisasi dengan sistem luar: fetch API, timer, event listener, atau manipulasi DOM langsung. Kalau bisa dihitung dari state yang ada, jangan pakai useEffect.
---

Dua hooks ini — `useState` dan `useEffect` — adalah 80% dari yang kamu butuhkan untuk membangun aplikasi React. Memahaminya dengan benar akan menghemat banyak jam debugging.

## useState: Menyimpan Data yang Bisa Berubah

Komponen React adalah fungsi. Variabel biasa di dalam fungsi akan hilang setiap render. `useState` memberi komponen sebuah "memori":

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Klik: {count} kali</p>
      <button onClick={() => setCount(count + 1)}>
        Tambah
      </button>
    </div>
  );
}
```

`useState(0)` mengembalikan pasangan: nilai saat ini (`count`) dan fungsi untuk mengubahnya (`setCount`). Setiap kali `setCount` dipanggil, React me-render ulang komponen dengan nilai baru.

**Aturan penting:** jangan ubah state langsung (`count = 5` tidak akan me-render ulang). Selalu lewat fungsi setter.

Untuk state berupa object atau array, buat salinan baru:

```jsx
const [user, setUser] = useState({ name: 'Rama', role: 'developer' });

// Salah: user.name = 'Budi';
// Benar:
setUser({ ...user, name: 'Budi' });
```

## useEffect: Merespons Perubahan

`useEffect` menjalankan kode sebagai respons terhadap render. Pola dasarnya:

```jsx
useEffect(() => {
  // kode efek di sini
}, [dependensi]);
```

Array dependensi menentukan **kapan** efek jalan:

- **Tidak ada array** — jalan setiap render (jarang dibutuhkan)
- **Array kosong `[]`** — jalan sekali saat komponen pertama muncul
- **`[count]`** — jalan saat pertama muncul DAN setiap `count` berubah

## Contoh Nyata: Fetch Data API

Ini kasus paling umum di aplikasi nyata:

```jsx
import { useState, useEffect } from 'react';

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://jsonplaceholder.typicode.com/users')
      .then(res => res.json())
      .then(data => {
        setUsers(data);
        setLoading(false);
      });
  }, []); // [] = fetch sekali saat komponen muncul

  if (loading) return <p>Memuat...</p>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

Perhatikan tiga state terpisah: data, loading. Pola ini muncul di hampir setiap aplikasi React profesional.

## Cleanup: Membersihkan Efek

Beberapa efek butuh dibersihkan — timer, subscription, event listener. Kembalikan fungsi cleanup dari efek:

```jsx
useEffect(() => {
  const timer = setInterval(() => {
    console.log('tick');
  }, 1000);

  // Cleanup: jalan saat komponen dihapus atau sebelum efek jalan lagi
  return () => clearInterval(timer);
}, []);
```

Tanpa cleanup, timer terus jalan walau komponen sudah hilang — sumber klasik memory leak.

## Kesalahan Umum Pemula

**1. Lupa dependency array.** Efek tanpa array jalan setiap render. Kalau di dalamnya ada `setState`, kamu dapat infinite loop.

**2. Fetch data di dalam render, bukan di useEffect.** Render harus murni — tanpa side effect. Fetch adalah side effect, tempatnya di `useEffect`.

**3. Menghitung nilai turunan dengan useEffect + state.** Ini berlebihan:

```jsx
// Berlebihan:
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(firstName + ' ' + lastName);
}, [firstName, lastName]);

// Cukup:
const fullName = firstName + ' ' + lastName;
```

Kalau nilainya bisa dihitung langsung saat render, hitung langsung. Simpan `useEffect` untuk sinkronisasi dengan dunia luar.

**4. Object/array baru sebagai dependensi.** `useEffect(..., [{...}])` akan jalan setiap render karena object selalu "baru". Pindahkan ke dalam efek atau pakai nilai primitif sebagai dependensi.

## Kapan Pakai Apa: Ringkasan

- Butuh data yang berubah saat user berinteraksi → `useState`
- Butuh fetch API saat halaman dibuka → `useEffect` + `[]`
- Butuh fetch ulang saat filter berubah → `useEffect` + `[filter]`
- Butuh timer atau listener → `useEffect` + cleanup
- Nilai yang bisa dihitung dari state lain → hitung langsung, tanpa hooks

Kuasai dua hooks ini dan kamu sudah bisa membangun sebagian besar fitur aplikasi React modern. Hooks lain seperti `useRef`, `useMemo`, dan `useContext` adalah pelengkap — pelajari setelah fondasi ini kokoh.
