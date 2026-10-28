---
title: Form Terkontrol di React: Cara Kerja dan Contoh Lengkap
description: Form React yang inputnya tak terkendali bikin validasi berantakan. Pelajari controlled form: value, onChange, dan contoh form lengkap yang siap dipakai.
date: 2026-10-28
tags: [react, javascript, form, frontend]
faq:
  - Apa itu controlled form di React?
  - Controlled form adalah form yang nilai setiap inputnya disimpan di state React lewat props value dan diubah lewat onChange. React menjadi satu-satunya sumber kebenaran untuk isi form.
  - Apa bedanya controlled dan uncontrolled component di React?
  - Controlled component menyimpan nilai input di state React, sedangkan uncontrolled component membiarkan DOM menyimpan nilainya sendiri dan dibaca lewat ref saat dibutuhkan. Controlled lebih mudah divalidasi dan dimanipulasi.
  - Kenapa input React tidak bisa diketik padahal sudah ada value?
  - Karena props value dikunci ke state tapi tidak ada onChange yang memperbarui state itu. React menganggap input tersebut read only, jadi ketikan pengguna tidak mengubah apa pun.
  - Kapan sebaiknya memakai uncontrolled component?
  - Untuk form sekali pakai yang sangat sederhana, seperti input file atau form yang tidak butuh validasi langsung. Untuk form dengan validasi, format otomatis, atau tombol submit yang bergantung pada isi, controlled component adalah pilihan yang lebih aman.
---

Kalau kamu pernah membuat form di React dan inputnya tiba-tiba tidak bisa diketik, kemungkinan besar kamu sudah bertemu controlled form tanpa sengaja. Kamu menulis `value={nama}` tapi lupa `onChange`, lalu React mengunci input itu ke nilai state yang tidak pernah berubah. Hasilnya: form terlihat benar, tapi tidak bisa dipakai.

Controlled form bukan konsep yang sulit. Intinya satu kalimat: nilai input disimpan di state React, dan setiap ketikan pengguna memperbarui state itu. Begitu kamu paham pola ini, validasi, format otomatis, dan tombol submit yang aktif atau nonaktif berdasarkan isi form menjadi jauh lebih mudah.

## Masalah yang Diselesaikan Controlled Form

Di HTML biasa, browser yang menyimpan nilai input. Kamu baru membaca nilainya saat form disubmit. Pola ini di React disebut uncontrolled component, dan masih sah dipakai. Masalahnya muncul saat kamu butuh sesuatu di tengah jalan: menampilkan pesan error begitu pengguna mengetik email yang salah, menonaktifkan tombol submit selama ada kolom kosong, atau memformat nomor telepon otomatis menjadi 0812-3456-7890 selagi diketik.

Semua kebutuhan itu memaksa kamu membaca nilai input secara terus menerus. Kalau nilainya hanya ada di DOM, kamu harus mengintip DOM lewat `ref` setiap kali ada perubahan. Kalau nilainya ada di state React, kamu tinggal membaca state itu seperti variabel biasa. Itulah alasan controlled form menjadi pola standar untuk form React yang serius.

## Pola Dasar: value dan onChange

Satu input terkontrol hanya butuh dua props: `value` yang membaca state, dan `onChange` yang menulis state.

```jsx
import { useState } from "react";

export default function FormNama() {
  const [nama, setNama] = useState("");

  return (
    <form>
      <label>
        Nama:
        <input
          type="text"
          value={nama}
          onChange={(e) => setNama(e.target.value)}
        />
      </label>
      <p>Halo, {nama || "tamu"}!</p>
    </form>
  );
}
```

Alurnya selalu sama dan tidak pernah berubah: pengguna mengetik satu huruf, event `onChange` terpanggil, `setNama` memperbarui state, React merender ulang, dan input menampilkan nilai state yang baru. Satu lingkaran penuh untuk setiap huruf yang diketik. Kedengarannya boros, tapi React sudah dioptimalkan untuk render ulang sekecil ini, dan untuk form biasa kamu tidak akan merasakan masalah performa.

Dua props ini adalah pasangan yang tidak boleh dipisahkan. `value` tanpa `onChange` membuat input read only. `onChange` tanpa `value` membuat input tidak terkontrol, karena React tidak lagi menentukan apa yang tampil di dalamnya. Keduanya harus ada bersamaan.

## Mengelola Banyak Input dengan Satu State

Form asli jarang punya satu kolom. Form pendaftaran biasanya punya nama, email, dan password sekaligus. Daripada membuat satu `useState` per kolom, simpan semuanya dalam satu objek dan perbarui berdasarkan atribut `name` dari input.

```jsx
import { useState } from "react";

export default function FormPendaftaran() {
  const [form, setForm] = useState({
    nama: "",
    email: "",
    password: "",
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    console.log("Data dikirim:", form);
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Nama:
        <input name="nama" value={form.nama} onChange={handleChange} />
      </label>
      <label>
        Email:
        <input
          name="email"
          type="email"
          value={form.email}
          onChange={handleChange}
        />
      </label>
      <label>
        Password:
        <input
          name="password"
          type="password"
          value={form.password}
          onChange={handleChange}
        />
      </label>
      <button type="submit">Daftar</button>
    </form>
  );
}
```

Ada tiga detail penting di contoh ini. Pertama, `handleChange` memakai bentuk fungsi dari setter, `setForm((prev) => ...)`, supaya pembaruan selalu berangkat dari state terbaru, bukan dari nilai state yang tertangkap saat render. Kedua, spread `...prev` menjaga kolom lain tidak hilang saat satu kolom berubah. Kalau kamu menulis `setForm({ [name]: value })` tanpa spread, dua kolom lainnya akan terhapus setiap kali pengguna mengetik. Ketiga, `e.preventDefault()` di `handleSubmit` mencegah browser me-reload halaman, karena submit form HTML secara default memuat ulang halaman.

## Jenis Input Lain: Select, Checkbox, dan Textarea

Pola `value` dan `onChange` berlaku untuk hampir semua elemen form, tapi ada dua pengecualian yang perlu diingat.

Untuk `textarea`, React tidak memakai children sebagai nilai seperti HTML biasa. Kamu memakai props `value` yang sama seperti input teks:

```jsx
const [pesan, setPesan] = useState("");

<textarea value={pesan} onChange={(e) => setPesan(e.target.value)} />;
```

Untuk `select`, cara kerjanya juga sama: `value` di elemen `select`, bukan atribut `selected` di `option`:

```jsx
const [kota, setKota] = useState("jakarta");

<select value={kota} onChange={(e) => setKota(e.target.value)}>
  <option value="jakarta">Jakarta</option>
  <option value="bandung">Bandung</option>
  <option value="surabaya">Surabaya</option>
</select>;
```

Pengecualian yang benar-benar berbeda adalah `checkbox`. Checkbox tidak memakai `value` sebagai sumber kebenaran, melainkan props `checked`, dan nilainya dibaca dari `e.target.checked`, bukan `e.target.value`:

```jsx
const [setuju, setSetuju] = useState(false);

<label>
  <input
    type="checkbox"
    checked={setuju}
    onChange={(e) => setSetuju(e.target.checked)}
  />
  Saya setuju dengan syarat dan ketentuan
</label>;
```

Kalau kamu memakai pola `value` dan `onChange` yang sama untuk semua jenis input tanpa memperhatikan checkbox, handler generik di atas akan menyimpan string `"on"` untuk checkbox, bukan boolean. Solusinya, handler generik perlu membedakan tipe input:

```jsx
function handleChange(e) {
  const { name, type, value, checked } = e.target;
  const nextValue = type === "checkbox" ? checked : value;
  setForm((prev) => ({ ...prev, [name]: nextValue }));
}
```

## Validasi Langsung dari State

Inilah keuntungan terbesar controlled form: karena nilai input sudah ada di state, validasi tinggal membaca state itu. Tidak perlu `document.querySelector`, tidak perlu `ref`, dan pesan error bisa muncul seketika saat pengguna mengetik.

```jsx
import { useState } from "react";

export default function FormEmail() {
  const [email, setEmail] = useState("");
  const [touched, setTouched] = useState(false);

  const emailValid = email.includes("@") && email.includes(".");
  const showError = touched && !emailValid;

  return (
    <form>
      <label>
        Email:
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onBlur={() => setTouched(true)}
        />
      </label>
      {showError && <p style={{ color: "red" }}>Format email belum benar.</p>}
      <button type="submit" disabled={!emailValid}>
        Kirim
      </button>
    </form>
  );
}
```

State `touched` di sini mencegah pesan error muncul sebelum pengguna sempat menyentuh kolom. Tanpa `touched`, form akan langsung menampilkan error saat pertama kali dirender, padahal pengguna belum mengetik apa pun. Pola ini sederhana tapi berdampak besar pada pengalaman pengguna: error hanya muncul setelah kolom ditinggalkan, bukan sejak awal.

Tombol submit yang memakai `disabled={!emailValid}` juga hanya mungkin dilakukan dengan mudah karena nilai input ada di state. Tombol ini tidak bisa diklik selama email belum valid, sehingga kamu tidak perlu menulis logika validasi ulang di dalam `handleSubmit`.

## Kesalahan Umum Pemula dan Cara Menghindarinya

**1. Input terkunci karena lupa onChange.** Ini kesalahan nomor satu. Gejalanya persis seperti yang dibuka di awal artikel: input tampil tapi tidak bisa diketik, dan React menampilkan peringatan di console tentang komponen yang berubah dari controlled ke uncontrolled atau sebaliknya. Perbaikannya selalu sama: tambahkan `onChange` yang memperbarui state yang dipakai `value`.

**2. Menghapus kolom lain saat update state objek.** Seperti dijelaskan di atas, selalu spread state lama sebelum menimpa satu kolom. Kalau form kamu tiba-tiba mengosongkan kolom yang sudah diisi setiap kali pengguna mengetik di kolom lain, hampir pasti spread ini yang hilang.

**3. Mencampur controlled dan uncontrolled dalam satu input.** Jangan memakai `defaultValue` dan `value` bersamaan, dan jangan membiarkan `value` menjadi `undefined` di beberapa render lalu string di render lain. Nilai awal state harus konsisten, biasanya string kosong `""` untuk input teks dan `false` untuk checkbox. Nilai yang berubah dari `undefined` ke string membuat React memperingatkan bahwa komponen berubah dari uncontrolled menjadi controlled, dan perilaku inputnya menjadi tidak dapat diprediksi.

**4. Mengambil nilai dari event secara asinkron.** Di React versi lama, objek event didaur ulang sehingga `e.target.value` tidak bisa dibaca di dalam `setTimeout` atau setelah `await`. Di React 17 ke atas masalah ini sudah tidak ada, tapi kebiasaan amannya tetap sama: baca `e.target.value` ke variabel dulu di awal handler, baru pakai variabel itu di logika berikutnya. Kebiasaan ini membuat kode kamu aman di semua versi React.

**5. Memakai controlled form untuk input file.** Elemen `input type="file"` tidak bisa dikontrol lewat `value`, karena browser melarang JavaScript menetapkan file secara sembarang demi keamanan. Untuk input file, pakai uncontrolled component dengan `ref`, atau baca `e.target.files` di `onChange` tanpa menetapkan `value`. Ini satu-satunya jenis input yang memang lebih cocok dibiarkan uncontrolled.

## Kapan Controlled Form Tidak Perlu

Controlled form adalah default yang baik, tapi bukan kewajiban. Kalau form kamu sangat sederhana, tidak butuh validasi langsung, tidak butuh format otomatis, dan hanya dibaca sekali saat submit, uncontrolled component dengan `ref` justru lebih sedikit kode. Contohnya form pencarian sekali pakai atau input file yang dibahas di atas.

Aturannya praktis: kalau ada logika yang bergantung pada nilai input sebelum submit, pakai controlled. Kalau tidak ada, uncontrolled boleh dipakai dan tidak ada yang salah dengan pilihan itu. Masalah muncul ketika kamu mulai menambahkan validasi ke form uncontrolled, lalu kodenya berubah menjadi campuran `ref` dan manipulasi DOM yang sulit diuji. Di titik itu, pindahkan ke controlled form.

## Langkah Praktis yang Bisa Langsung Dicoba

1. Buat komponen form dengan satu input nama memakai pola `value` dan `onChange`, lalu tampilkan nilai state di bawah form untuk melihat lingkaran pembaruan bekerja.
2. Tambahkan kolom email dan password, gabungkan ketiganya ke satu state objek dengan handler generik berbasis atribut `name`, dan pastikan mengetik di satu kolom tidak menghapus kolom lain.
3. Tambahkan validasi email memakai pola `touched` dan tombol submit yang nonaktif selama input belum valid.
4. Tambahkan satu checkbox persetujuan memakai props `checked` dan `e.target.checked`, lalu perbarui handler generik agar membedakan checkbox dari input teks.
5. Sengaja buat kesalahan nomor satu, yaitu hapus `onChange` dari satu input, lalu baca peringatan React di console sampai kamu paham hubungan antara `value` yang terkunci dan state yang tidak berubah.

Kuasai pola `value` dan `onChange` ini, dan hampir semua form React yang kamu temui di project nyata akan terasa familiar. Form yang lebih kompleks, seperti form multi langkah atau form dinamis dengan daftar input yang bisa ditambah dan dihapus, pada dasarnya hanya menerapkan pola yang sama berulang kali, dengan state yang strukturnya lebih dalam.
