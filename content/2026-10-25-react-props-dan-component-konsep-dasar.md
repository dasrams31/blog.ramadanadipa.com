---
title: React Props dan Component: Konsep Dasar dengan Contoh
description: Tutorial React props dan component untuk pemula: kirim data antar komponen, destructuring props, default props, children, plus kesalahan umum pemula.
date: 2026-10-25
tags: [react, props, component, javascript]
faq:
  - Apa itu props di React?
  - Props adalah data yang dikirim dari komponen induk ke komponen anak lewat atribut JSX. Props bersifat read-only, jadi komponen anak tidak boleh mengubahnya.
  - Apa bedanya component dan props di React?
  - Component adalah fungsi yang mengembalikan JSX dan bisa dipakai ulang, sedangkan props adalah data yang masuk ke component tersebut agar tampilannya bisa berbeda-beda.
  - Apakah props di React bisa diubah oleh komponen anak?
  - Tidak. Props bersifat read-only. Kalau data perlu berubah, simpan di state komponen induk lalu kirim fungsi pengubahnya lewat props.
  - Kapan memakai props children di React?
  - Saat komponen perlu membungkus konten yang strukturnya tidak tetap, misalnya Card, Modal, atau Layout. Konten di antara tag pembuka dan penutup komponen tersedia sebagai props.children.
---

Komponen adalah unit terkecil antarmuka di React. Satu halaman web dipecah menjadi komponen-komponen kecil yang masing-masing mengurus satu bagian: header, kartu produk, tombol, formulir. Props adalah cara komponen-komponen itu berkomunikasi: komponen induk mengirim data ke komponen anak lewat props, dan komponen anak menampilkan data itu. Kalau kamu paham dua konsep ini, kamu sudah memegang fondasi React yang sesungguhnya.

## Component: Fungsi yang Mengembalikan JSX

Di React modern, komponen paling sederhana hanyalah fungsi JavaScript yang mengembalikan JSX:

```jsx
function Greeting() {
  return <h1>Halo, selamat datang!</h1>;
}
```

Ada satu aturan penamaan yang wajib dipatuhi: nama komponen harus diawali huruf kapital. Kalau kamu menulis `<greeting />`, React mengira itu tag HTML biasa, bukan komponenmu. Aturan ini sederhana, tapi saya sering melihat pemula stuck lama hanya karena menulis nama komponen dengan huruf kecil.

Komponen dipakai seperti tag HTML di komponen lain:

```jsx
function App() {
  return (
    <div>
      <Greeting />
      <Greeting />
    </div>
  );
}
```

Masalahnya langsung terlihat: kedua `Greeting` menampilkan teks yang sama persis. Komponen yang tidak menerima data luar tidak bisa dipakai ulang untuk konten yang berbeda. Di sinilah props masuk.

## Props: Data yang Dikirim ke Komponen

Props dikirim seperti atribut HTML, lalu diterima komponen sebagai satu objek parameter:

```jsx
function Greeting({ name }) {
  return <h1>Halo, {name}!</h1>;
}

function App() {
  return (
    <div>
      <Greeting name="Rama" />
      <Greeting name="Sinta" />
    </div>
  );
}
```

Di sini saya langsung memakai destructuring di parameter fungsi: `({ name })`, bukan `(props)` lalu `props.name`. Keduanya sah, tapi destructuring membuat kode jauh lebih ringkas saat props bertambah banyak. Satu komponen, dua tampilan berbeda, hanya karena props yang dikirim berbeda. Itulah inti reusability di React.

Contoh yang lebih nyata: kartu produk di toko online.

```jsx
function ProductCard({ name, price, stock }) {
  return (
    <div className="card">
      <h3>{name}</h3>
      <p>Harga: Rp {price.toLocaleString("id-ID")}</p>
      <p>{stock > 0 ? `Stok tersedia: ${stock}` : "Stok habis"}</p>
      <button disabled={stock === 0}>Beli</button>
    </div>
  );
}

function App() {
  return (
    <div>
      <ProductCard name="Keyboard Mechanical" price={750000} stock={12} />
      <ProductCard name="Mouse Wireless" price={350000} stock={0} />
    </div>
  );
}
```

Perhatikan perbedaan cara mengirim nilai: string ditulis langsung di tanda kutip (`name="Keyboard Mechanical"`), sedangkan angka dan ekspresi JavaScript dibungkus kurung kurawal (`price={750000}`, `stock={0}`). Ini jebakan klasik pemula: menulis `price="750000"` membuat harga menjadi string, dan `price.toLocaleString` tetap jalan tapi hasil operasinya bisa aneh saat kamu mulai menghitung total. Angka kirim sebagai angka, bukan string.

## Props Bisa Berupa Apa Saja

Props tidak terbatas pada string dan angka. Kamu bisa mengirim array, objek, bahkan fungsi:

```jsx
function TagList({ tags }) {
  return (
    <ul>
      {tags.map((tag) => (
        <li key={tag}>{tag}</li>
      ))}
    </ul>
  );
}

function DeleteButton({ onDelete }) {
  return <button onClick={onDelete}>Hapus</button>;
}

function App() {
  function handleDelete() {
    alert("Item dihapus!");
  }

  return (
    <div>
      <TagList tags={["react", "javascript", "pemula"]} />
      <DeleteButton onDelete={handleDelete} />
    </div>
  );
}
```

Mengirim fungsi lewat props adalah pola paling penting di React, karena ini cara komponen anak berkomunikasi balik ke induknya. Ingat aturannya: data mengalir satu arah, dari induk ke anak. Kalau anak perlu mengubah sesuatu, induk mengirim fungsi pengubahnya lewat props, lalu anak memanggil fungsi itu. Pola ini terasa berputar-putar di awal, tapi justru inilah yang membuat alur data aplikasi React mudah dilacak: tidak ada komponen yang diam-diam mengubah data komponen lain.

Satu catatan soal `key` di contoh `TagList`: setiap elemen hasil `.map()` wajib punya `key` yang unik dan stabil. React memakai `key` untuk tahu elemen mana yang berubah saat list di-render ulang. Tanpa `key`, kamu dapat warning di console dan performa render yang buruk, dan di kasus list yang bisa diurutkan atau difilter, tampilan bisa salah.

## Default Props: Nilai Cadangan Saat Props Tidak Dikirim

Tidak semua props selalu dikirim. Beri nilai default lewat destructuring supaya komponen tetap aman:

```jsx
function Avatar({ name, size = 40 }) {
  return (
    <img
      src={`https://ui-avatars.com/api/?name=${name}`}
      width={size}
      height={size}
      alt={name}
    />
  );
}

// size tidak dikirim, otomatis 40
function App() {
  return <Avatar name="Rama" />;
}
```

Nilai default hanya berlaku kalau props tidak dikirim sama sekali, atau dikirim sebagai `undefined`. Kalau kamu sengaja mengirim `null`, default tidak berlaku. Detail kecil, tapi penting saat debugging kenapa default tidak jalan.

## Children: Konten di Dalam Tag Komponen

Kadang komponen tidak butuh data, tapi butuh membungkus konten yang strukturnya tidak tetap. Misalnya komponen `Card` yang dipakai untuk banyak isi berbeda:

```jsx
function Card({ title, children }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="card-body">{children}</div>
    </div>
  );
}

function App() {
  return (
    <Card title="Profil Saya">
      <p>Nama: Rama, full stack developer.</p>
      <p>Fokus: Laravel, React, dan PostgreSQL.</p>
    </Card>
  );
}
```

Semua yang ditulis di antara `<Card>` dan `</Card>` tersedia sebagai `props.children`. Pola ini adalah dasar dari komponen layout, modal, dan pembungkus lainnya. Begitu kamu terbiasa memakai `children`, komponenmu berhenti jadi kaku dan mulai terasa seperti blok bangunan sungguhan.

## Komposisi: Susun Komponen Kecil, Bukan Satu Komponen Raksasa

Kesalahan arsitektur paling umum yang saya lihat di project pemula adalah satu komponen `App` berisi 400 baris JSX untuk seluruh halaman. Lebih baik pecah jadi komponen kecil yang masing-masing punya satu tugas:

```jsx
function Header() {
  return <header>Toko Online Saya</header>;
}

function ProductList() {
  return (
    <div>
      <ProductCard name="Keyboard Mechanical" price={750000} stock={12} />
      <ProductCard name="Mouse Wireless" price={350000} stock={0} />
    </div>
  );
}

function Footer() {
  return <footer>Copyright 2026</footer>;
}

function App() {
  return (
    <div>
      <Header />
      <ProductList />
      <Footer />
    </div>
  );
}
```

Aturan praktisnya: kalau satu komponen mulai terasa sulit dibaca dalam sekali pandang, pecah. Komponen kecil lebih mudah diuji, lebih mudah dipakai ulang, dan lebih mudah dibaca orang lain. Ini bukan soal gaya semata, ini soal biaya perawatan project dalam jangka panjang.

## Kesalahan Umum Pemula dan Cara Menghindarinya

**1. Mengubah props di dalam komponen anak.** Props bersifat read-only. Menulis `props.name = "baru"` tidak akan bekerja seperti yang kamu kira dan merusak asumsi satu arah alur data React. Kalau nilai perlu berubah, angkat state ke komponen induk dan kirim fungsi pengubahnya lewat props.

**2. Mengirim angka atau boolean sebagai string.** `stock="0"` adalah string, dan string `"0"` bernilai truthy di JavaScript. Akibatnya kondisi `stock > 0` atau `stock === 0` berperilaku aneh. Selalu kirim angka dengan kurung kurawal: `stock={0}`.

**3. Menamai komponen dengan huruf kecil.** React membedakan komponen dan tag HTML dari huruf pertamanya. `<productcard />` tidak akan dirender sebagai komponenmu. Selalu PascalCase: `ProductCard`.

**4. Lupa key saat render list.** Tanpa `key` yang stabil, React kesulitan melacak elemen list dan tampilan bisa salah saat list berubah. Jangan pakai index array sebagai key kalau urutan list bisa berubah, pakai ID yang unik dari datanya.

**5. Props drilling yang dibiarkan berlapis-lapis.** Kalau data harus melewati lima komponen perantara yang sebenarnya tidak memakainya, itu tanda struktur perlu dipikirkan ulang. Untuk kasus sederhana, angkat state ke komponen terdekat yang masih masuk akal. Untuk aplikasi besar, barulah pertimbangkan Context atau state management, bukan sejak hari pertama.

## Langkah Praktis yang Bisa Langsung Dicoba

1. Buat project React dengan Vite: `npm create vite@latest latihan-props -- --template react`, lalu `npm install` dan `npm run dev`.
2. Buat komponen `ProductCard` seperti contoh di atas dengan props `name`, `price`, dan `stock`, lalu render tiga produk berbeda dari satu komponen yang sama.
3. Tambahkan props `onBuy` berupa fungsi yang menampilkan alert nama produk saat tombol diklik, dan kirim fungsi itu dari `App`.
4. Bungkus daftar produk di dalam komponen `Card` memakai `children`, lengkap dengan judulnya.
5. Sengaja buat satu kesalahan dari daftar di atas, misalnya kirim `stock="0"` sebagai string, lalu amati perilaku tombolnya. Memahami kenapa bug itu muncul lebih berharga daripada sekadar menghafal aturannya.

Kuasai component dan props sampai terasa alami, karena semua konsep React berikutnya, mulai dari state, hooks, sampai Context, dibangun di atas fondasi ini. Kalau fondasinya goyah, setiap konsep lanjutan akan terasa sulit tanpa alasan yang jelas.
