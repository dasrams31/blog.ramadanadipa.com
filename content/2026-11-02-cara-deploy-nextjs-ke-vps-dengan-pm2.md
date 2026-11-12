---
title: Cara Deploy Next.js ke VPS dengan PM2, Langkah Demi Langkah
description: Deploy Next.js ke VPS dengan PM2 dan Nginx: build production, ecosystem config, reverse proxy, dan HTTPS gratis. Tetap jalan setelah reboot.
cover: /assets/img/covers/cara-deploy-nextjs-ke-vps-dengan-pm2.jpg
date: 2026-11-02
tags: [nextjs, pm2, nginx, vps, deployment]
faq:
  - Apa itu PM2 dan kenapa dipakai untuk deploy Next.js di VPS?
  - PM2 adalah process manager untuk aplikasi Node.js. Ia menjaga aplikasi tetap jalan, me-restart otomatis saat crash, menampilkan log, dan menghidupkan kembali aplikasi setelah VPS reboot bila sudah disimpan dengan pm2 save dan pm2 startup.
  - Berapa RAM minimal VPS untuk menjalankan Next.js?
  - Untuk aplikasi kecil sampai menengah, VPS 1 GB RAM biasanya cukup, tapi proses build butuh RAM lebih besar daripada saat aplikasi jalan. Kalau build sering gagal karena kehabisan memori, naikkan ke 2 GB RAM atau tambahkan swap sementara selama proses build.
  - Kenapa aplikasi Next.js berhenti setelah terminal SSH ditutup?
  - Karena proses yang dijalankan langsung dari terminal adalah anak dari sesi SSH itu. Saat sesi ditutup, proses ikut dihentikan. PM2 menjalankan aplikasi sebagai daemon terpisah, jadi aplikasi tetap jalan walau kamu sudah logout dari SSH.
  - Bagaimana cara update aplikasi Next.js yang sudah jalan di PM2?
  - Tarik kode terbaru, jalankan npm ci, build ulang dengan npm run build, lalu jalankan pm2 reload ecosystem.config.js. Setelah itu cek status dan log dengan pm2 status dan pm2 logs untuk memastikan versi baru sudah aktif.
---

Deploy Next.js ke Vercel memang paling gampang. Tapi ada saatnya kamu butuh VPS sendiri, misalnya aplikasinya butuh proses background atau kamu mau menghemat biaya dengan satu VPS untuk beberapa aplikasi. Di VPS, Next.js tidak bisa sekadar dijalankan dari terminal lalu ditinggal begitu saja. Kamu butuh process manager supaya aplikasi tetap hidup, dan reverse proxy supaya domain bisa diakses lewat HTTPS dengan rapi.

Pola yang aku pakai di sini sederhana: Nginx menerima request dari internet, meneruskannya ke aplikasi Next.js yang dijalankan PM2 di port lokal, dan Certbot mengurus HTTPS gratis dari Let's Encrypt. Tidak ada panel hosting. Setiap bagiannya bisa kamu cek sendiri dari terminal.

## Cara Kerja Deploy Ini

Alurnya begini. Pengunjung membuka domain lewat HTTPS. Nginx menerima request di port 443, lalu meneruskannya ke `http://127.0.0.1:3000`, alamat lokal tempat Next.js berjalan. PM2 menjaga proses itu tetap hidup, me-restart otomatis saat crash, dan menghidupkan kembali aplikasi setelah VPS reboot. Port 3000 tidak perlu dibuka ke internet, karena pengunjung yang mengaksesnya langsung akan melewati Nginx dan HTTPS.

Bedakan juga dua mode Next.js. Mode development (`npm run dev`) tidak dioptimasi dan boros resource. Mode production (`npm run build` lalu `npm start`) jauh lebih cepat. Di VPS, selalu pakai mode production.

## Persiapan di VPS

Contoh di sini memakai Ubuntu 22.04 atau 24.04 dengan user `sudo`. Domain sudah diarahkan ke IP VPS lewat DNS record A, karena Certbot butuh domain itu untuk menerbitkan sertifikat.

Pertama, perbarui paket dan pasang Nginx, yang akan menjadi pintu masuk semua request.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx curl git
sudo systemctl enable --now nginx
```

Lalu pasang Node.js versi LTS. Di sini aku pakai Node.js 20 dari NodeSource, karena versi dari repository default Ubuntu sering ketinggalan dan bisa menimbulkan masalah kompatibilitas dengan Next.js terbaru.

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node -v
npm -v
```

Terakhir, pasang PM2 secara global dan atur firewall. Urutan firewall ini penting: izinkan SSH dulu, baru aktifkan firewall, supaya kamu tidak mengunci diri sendiri keluar dari VPS.

```bash
sudo npm install -g pm2
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

Cek hasil tiap langkah. `node -v` harus menampilkan `v20.x.x` dan `sudo ufw status` harus menunjukkan SSH serta Nginx Full dalam keadaan allow. Kalau salah satu gagal di sini, jangan lanjut dulu.

## Siapkan Aplikasi Next.js untuk Production

Aplikasi bisa dibawa ke VPS dengan `git clone` atau `rsync`, tapi yang paling mudah dilacak adalah Git. Clone repository ke `/var/www`, misalnya `/var/www/aplikasi`.

```bash
sudo mkdir -p /var/www
cd /var/www
sudo git clone https://github.com/namamu/aplikasi-next.git aplikasi
cd aplikasi
```

Cek script standar di `package.json`:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

`next start` mendengarkan port 3000 secara default dan menghormati variabel `PORT`. Pola di bawah berlaku untuk deploy standar, bukan untuk `output: "standalone"`.

Simpan variabel environment di `.env.production` dan jangan masukkan file itu ke Git. Nilai `NEXT_PUBLIC_` disematkan ke dalam build, jadi mengubahnya berarti build harus diulang. Pasang dependency dan build di server, bukan dengan mengunggah folder `.next` dari laptop.

```bash
npm ci
npm run build
```

`npm ci` memasang dependency persis sesuai `package-lock.json`. `npm install` di server bisa mengubah lock file dan menghasilkan environment yang berbeda dari yang kamu uji di laptop.

## Jalankan Aplikasi dengan PM2

PM2 bisa menjalankan perintah npm secara langsung, tapi menyuruh PM2 menjalankan `npm run dev` di production adalah jebakan. Yang benar adalah menjalankan `npm start` lewat file konfigurasi ecosystem, supaya semua pengaturan tersimpan di satu file dan mudah diulang di deploy berikutnya. Buat file `ecosystem.config.js` di folder aplikasi:

```javascript
module.exports = {
  apps: [
    {
      name: "aplikasi-next",
      cwd: "/var/www/aplikasi",
      script: "npm",
      args: "start",
      instances: 1,
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      env: {
        NODE_ENV: "production",
        PORT: 3000,
      },
    },
  ],
};
```

`instances: 1` cukup untuk VPS kecil. `max_memory_restart` me-restart proses kalau memorinya melewati batas. `watch: false` berarti restart saat deploy kamu kendalikan sendiri.

Jalankan aplikasi dari file konfigurasi itu, lalu cek status dan lognya:

```bash
pm2 start ecosystem.config.js
pm2 status
pm2 logs aplikasi-next --lines 50
```

`pm2 status` harus menunjukkan status `online`. Kalau log menampilkan error `EADDRINUSE`, port 3000 sudah dipakai proses lain. Cari pelakunya dengan `sudo ss -tlnp | grep 3000`, hentikan proses yang tidak perlu, lalu restart PM2.

Tes dari dalam VPS: `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000` harus mengembalikan `200`.

Agar aplikasi hidup lagi setelah VPS reboot, simpan daftar proses PM2 dan aktifkan startup script:

```bash
pm2 save
pm2 startup systemd
```

Perintah `pm2 startup` akan mencetak satu perintah `sudo` panjang yang harus kamu jalankan persis seperti tampilannya. Perintah itu mendaftarkan PM2 ke systemd. Setelah dijalankan, ulangi `pm2 save` sekali lagi. Langkah ini sering dilewati, dan akibatnya aplikasi hilang begitu VPS reboot.

## Nginx sebagai Reverse Proxy

Sekarang buat konfigurasi Nginx untuk domain kamu. Ganti `contoh.com` dengan domain asli. Simpan file ini di `/etc/nginx/sites-available/aplikasi`:

```nginx
server {
    listen 80;
    server_name contoh.com www.contoh.com;

    client_max_body_size 10m;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Header `Host` dan `X-Forwarded-Proto` menjaga Next.js tidak salah mengenali host dan protokol.

Aktifkan konfigurasi, uji sintaksnya, lalu reload Nginx. Jangan pernah reload tanpa `nginx -t`, karena satu kesalahan ketik bisa membuat semua situs di VPS itu ikut terganggu.

```bash
sudo ln -s /etc/nginx/sites-available/aplikasi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Pada titik ini, domain kamu seharusnya sudah bisa dibuka lewat HTTP. Kalau yang muncul adalah halaman default Nginx, periksa apakah file konfigurasi sudah ter-link di `sites-enabled`.

## HTTPS Gratis dengan Certbot

HTTP saja tidak cukup untuk production. Pasang Certbot dan plugin Nginx, lalu minta sertifikat untuk domain kamu:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d contoh.com -d www.contoh.com
```

Certbot akan bertanya alamat email, lalu otomatis mengubah konfigurasi Nginx untuk redirect HTTP ke HTTPS. Pilih opsi redirect saat ditanya. Setelah selesai, cek dengan `curl -I https://contoh.com` dan pastikan sertifikatnya valid di browser.

Sertifikat Let's Encrypt berlaku 90 hari dan diperpanjang otomatis. Uji perpanjangannya dengan `sudo certbot renew --dry-run` sebelum sertifikat kedaluwarsa.

## Alur Update: Deploy Ulang dengan Aman

Deploy ulang tidak perlu menghentikan Nginx. Urutannya selalu sama: tarik kode, pasang dependency, build, lalu reload PM2. Untuk satu instance, tetap ada jeda singkat saat proses berganti, jadi lakukan update di jam sepi kalau aplikasimu ramai.

```bash
cd /var/www/aplikasi
git pull
npm ci
npm run build
pm2 reload ecosystem.config.js
pm2 status
pm2 logs aplikasi-next --lines 30
```

Jangan menjalankan `pm2 reload` sebelum build selesai. Kalau build gagal dan kamu tetap reload, proses baru akan gagal start. Biasakan membaca 30 baris log terakhir setelah reload, dan buka satu halaman penting di browser untuk memastikan versi baru benar benar tampil. Kalau update bermasalah, kembalikan kode ke commit sebelumnya, build ulang, dan reload lagi.

## Kesalahan Umum Pemula

Pertama, menjalankan `npm run dev` di VPS. Lambat dan boros memori, selalu pakai `npm start` lewat PM2.

Kedua, lupa `pm2 save` dan `pm2 startup`. Aplikasi hilang begitu VPS reboot, jadi aktifkan keduanya di hari pertama.

Ketiga, membuka port 3000 ke publik. Ini melewati HTTPS dan Nginx, biarkan port itu hanya bisa diakses dari dalam VPS.

Keempat, memakai `npm install` di server dan mengunggah folder `.next` dari laptop. Pakai `npm ci` dan build langsung di VPS.

Kelima, mengubah variabel `NEXT_PUBLIC_` lalu hanya me-restart PM2. Nilai itu disematkan saat build, jadi build ulang baru reload.

Keenam, tidak membaca log saat error. Hampir semua masalah deploy terlihat di `pm2 logs`.

Ketujuh, mengedit Nginx langsung di `sites-enabled` atau reload tanpa `nginx -t`. Selalu uji sintaks sebelum reload.

## Langkah Praktis yang Bisa Langsung Dicoba

Coba alur lengkap ini dalam satu sesi: siapkan domain yang mengarah ke IP VPS, jalankan persiapan Node.js, Nginx, dan PM2, clone project, build, jalankan lewat ecosystem config, pasang reverse proxy, terbitkan sertifikat, lalu buka domain lewat HTTPS. Uji ketahanannya:

```bash
curl -I https://contoh.com
pm2 status
sudo reboot
```

Setelah VPS hidup lagi, login lewat SSH dan jalankan `pm2 status` sekali lagi. Aplikasi harus kembali online tanpa perintah start manual. Kalau tidak kembali, periksa apakah perintah dari `pm2 startup` sudah dijalankan dan apakah `pm2 save` sudah dilakukan.

Terakhir, latih alur update sekali. Ubah satu teks kecil di halaman utama, commit, lalu jalankan `git pull`, `npm ci`, `npm run build`, dan `pm2 reload`. Refresh browser dan pastikan teks baru muncul.

Kuasai tiga lapisan ini, PM2, Nginx, dan Certbot, dan kamu bisa memakai pola yang sama untuk project berikutnya.
