---
title: SSL Gratis Let's Encrypt: HTTPS untuk Domain Sendiri
description: Pasang SSL gratis Let's Encrypt dengan Certbot di VPS Ubuntu: konfigurasi Nginx, auto-renewal, wildcard, dan cara memperbaiki error yang paling sering muncul.
cover: /assets/img/covers/ssl-gratis-lets-encrypt-https-untuk-domain-sendiri.jpg
date: 2026-11-25
tags: [ssl, lets-encrypt, https, nginx, vps, certbot]
faq:
  - Apakah sertifikat SSL gratis Let's Encrypt aman untuk website production?
  - Aman. Let's Encrypt menerbitkan sertifikat domain-validated yang diakui semua browser modern, sama seperti sertifikat berbayar dengan level validasi yang sama. Bedanya cuma masa berlaku 90 hari dan tidak ada garansi finansial.
  - Kenapa browser masih bilang "Not Secure" padahal sertifikat sudah terpasang?
  - Biasanya ada konten campuran: halaman dimuat lewat HTTPS tapi ada gambar, script, atau CSS yang masih di-load lewat HTTP. Periksa tab Network di DevTools dan ubah semua URL aset menjadi relatif atau HTTPS.
  - Berapa lama sertifikat Let's Encrypt berlaku dan bagaimana cara perpanjangnya?
  - Sertifikat berlaku 90 hari. Certbot memasang timer systemd yang mencoba perpanjang otomatis dua kali sehari, jadi kamu tidak perlu memperpanjang manual selama timernya jalan.
  - Bisakah satu sertifikat dipakai untuk subdomain seperti api.domain.com?
  - Bisa. Terbitkan sertifikat terpisah per subdomain, atau pakai sertifikat wildcard *.domain.com yang diterbitkan lewat validasi DNS-01.
---

Situs pertamaku di VPS sempat jalan berbulan-bulan tanpa HTTPS karena kupikir SSL itu ribet dan mahal. Sampai Chrome menandai form login di situs itu sebagai "Not Secure" dan pengunjung yang mau daftar langsung kabur. Ternyata pasang HTTPS gratis cuma butuh sepuluh menit, dan artikel ini menjelaskan caranya dari nol sampai auto-renewal jalan sendiri.

Target akhirnya: domain kamu bisa diakses lewat `https://`, dengan gembok hijau di browser, sertifikat yang diperpanjang otomatis, tanpa biaya sepeser pun.

## Kenapa HTTPS bukan lagi pilihan

HTTPS mengenkripsi lalu lintas antara browser pengunjung dan server kamu. Tanpa enkripsi, siapa pun yang berada di jaringan yang sama, misalnya WiFi publik, bisa mengintip atau mengubah data yang dikirim, termasuk password dan token login.

Selain keamanan, ada dua alasan praktis. Browser modern memblokir fitur seperti geolocation, kamera, dan service worker di situs tanpa HTTPS. Google juga menjadikan HTTPS sebagai salah satu sinyal ranking, jadi situs HTTP kalah bersaing di hasil pencarian.

Singkatnya: kalau situsmu masih HTTP, kamu kehilangan pengunjung dan kepercayaan sebelum mereka sempat membaca kontenmu.

## Cara kerja Let's Encrypt

Let's Encrypt adalah certificate authority gratis yang menerbitkan sertifikat SSL lewat protokol ACME. Alurnya sederhana: kamu membuktikan bahwa kamu mengendalikan domain tersebut, lalu Let's Encrypt menerbitkan sertifikat yang berlaku 90 hari.

Pembuktian kepemilikan domain dilakukan dengan dua cara. Cara pertama adalah HTTP-01: Let's Encrypt meminta server kamu menyajikan file token di `http://domain.com/.well-known/acme-challenge/`. Kalau file itu bisa diakses, berarti kamu memang mengendalikan domain itu. Cara kedua adalah DNS-01: kamu menambahkan record TXT ke DNS domain, dan cara ini dipakai untuk sertifikat wildcard.

Masa berlaku 90 hari memang sengaja dibuat pendek untuk mendorong otomatisasi: sertifikat diperpanjang oleh skrip, bukan oleh manusia yang bisa lupa.

## Prasyarat sebelum mulai

Siapkan tiga hal ini dulu supaya prosesnya tidak tersendat di tengah jalan.

1. **VPS Ubuntu** dengan akses root atau user sudo. Perintah di artikel ini diuji di Ubuntu 24.04, tapi caranya sama di Ubuntu 22.04.
2. **Domain** yang A record-nya sudah mengarah ke IP VPS. Cek dengan perintah `dig +short domainkamu.com`, hasilnya harus IP VPS kamu. Tunggu propagasi DNS selesai sebelum lanjut.
3. **Nginx sudah terinstall** dan sudah melayani domain itu lewat HTTP. Kalau belum, ikuti dulu panduan deploy Laravel ke VPS yang sudah terbit di blog ini.

Satu hal lagi: pastikan port 80 dan 443 terbuka di firewall VPS. Kalau kamu memakai UFW, jalankan perintah berikut.

```bash
sudo ufw allow 'Nginx Full'
sudo ufw status
```

Profil `Nginx Full` membuka port 80 dan 443 sekaligus. Kalau kamu hanya membuka port 80, validasi HTTP-01 bisa jalan, tapi pengunjung tidak akan bisa mengakses HTTPS.

## Langkah 1: install Certbot

Certbot adalah client resmi Let's Encrypt. Di Ubuntu, install dari repository resmi bersama plugin Nginx supaya Certbot bisa mengubah konfigurasi Nginx secara otomatis.

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

Jangan install Certbot dari snap kalau Nginx sudah diinstall lewat apt, karena dua jalur instalasi itu bisa bentrok soal path konfigurasi.

## Langkah 2: terbitkan sertifikat

Satu perintah ini cukup untuk menerbitkan sertifikat dan mengaktifkan HTTPS di konfigurasi Nginx kamu.

```bash
sudo certbot --nginx -d domainkamu.com -d www.domainkamu.com
```

Certbot akan bertanya alamat email untuk notifikasi kedaluwarsa, lalu menanyakan apakah kamu setuju dengan Terms of Service. Setelah itu Certbot melakukan validasi HTTP-01, mengunduh sertifikat, lalu menambahkan blok SSL ke konfigurasi Nginx kamu.

Di akhir, Certbot menanyakan apakah semua request HTTP harus di-redirect ke HTTPS. Pilih opsi redirect supaya tidak ada pengunjung yang mendarat di versi HTTP yang tidak terenkripsi.

Kalau sertifikat berhasil diterbitkan, outputnya kira-kira seperti ini.

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/domainkamu.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/domainkamu.com/privkey.pem
```

Perhatikan dua file itu. `fullchain.pem` adalah sertifikat lengkap beserta rantai intermediate, sedangkan `privkey.pem` adalah private key. Private key hanya boleh dibaca oleh root. Jangan pernah meng-commit atau membagikan file ini.

## Langkah 3: periksa konfigurasi Nginx hasil Certbot

Setelah Certbot selesai, buka konfigurasi Nginx dan lihat apa yang berubah.

```bash
sudo nano /etc/nginx/sites-available/domainkamu.com
```

Bagian HTTPS-nya kurang lebih akan terlihat seperti ini.

```nginx
server {
    listen 443 ssl;
    server_name domainkamu.com www.domainkamu.com;

    ssl_certificate /etc/letsencrypt/live/domainkamu.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domainkamu.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    root /var/www/domainkamu.com/public;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.3-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }
}

server {
    listen 80;
    server_name domainkamu.com www.domainkamu.com;
    return 301 https://$host$request_uri;
}
```

Ada dua server block di sini. Block pertama melayani HTTPS di port 443 dan menunjuk ke sertifikat Let's Encrypt. Block kedua melayani port 80 dan hanya melakukan redirect permanen ke HTTPS. File `options-ssl-nginx.conf` berisi pengaturan SSL yang aman, seperti protokol TLS 1.2 dan 1.3 saja, jadi kamu tidak perlu mengutak-atik cipher sendiri.

Uji sintaksnya, lalu reload Nginx.

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Buka `https://domainkamu.com` di browser. Kalau gemboknya muncul, sertifikat kamu sudah aktif. Klik gembok itu dan periksa tanggal kedaluwarsanya, seharusnya sekitar 90 hari dari sekarang.

## Langkah 4: pastikan auto-renewal jalan

Sertifikat Let's Encrypt hanya berlaku 90 hari, jadi perpanjangan otomatis adalah bagian terpenting dari setup ini. Paket Certbot dari Ubuntu memasang timer systemd yang menjalankan `certbot renew` dua kali sehari. Timer ini hanya memperpanjang sertifikat yang masa berlakunya kurang dari 30 hari, jadi tidak ada beban yang sia-sia.

Cek apakah timernya aktif.

```bash
sudo systemctl list-timers | grep certbot
```

Output yang sehat terlihat seperti ini.

```
Tue 2026-11-25 00:00:00 WIB  12h left  certbot.timer  certbot.service
```

Kalau timer tidak muncul, aktifkan manual.

```bash
sudo systemctl enable --now certbot.timer
```

Jangan cuma percaya timernya ada, tapi uji juga proses perpanjangannya. Perintah berikut menjalankan perpanjangan dalam mode simulasi tanpa mengubah sertifikat yang sudah ada.

```bash
sudo certbot renew --dry-run
```

Kalau dry run berhasil, berarti proses renewal di dunia nyata juga akan berhasil. Kalau dry run gagal, perbaiki sekarang selagi sertifikat masih berlaku, jangan menunggu sampai hari kedaluwarsa.

Satu detail yang sering terlewat: setelah sertifikat diperpanjang, Nginx perlu reload supaya memakai sertifikat baru. Certbot versi terbaru sudah menambahkan hook reload otomatis untuk plugin Nginx, tapi kalau kamu memakai web server lain atau konfigurasi khusus, tambahkan hook sendiri di `/etc/letsencrypt/renewal-hooks/deploy/` atau jalankan renew dengan flag `--deploy-hook "systemctl reload nginx"`.

## Sertifikat wildcard untuk semua subdomain

Kalau kamu punya banyak subdomain, misalnya `api.domainkamu.com`, `blog.domainkamu.com`, dan `app.domainkamu.com`, menerbitkan satu sertifikat per subdomain akan cepat merepotkan. Solusinya adalah sertifikat wildcard `*.domainkamu.com` yang berlaku untuk semua subdomain tingkat satu.

Wildcard tidak bisa divalidasi lewat HTTP-01, karena Let's Encrypt tidak bisa menebak semua subdomain yang kamu punya. Validasi memakai DNS-01: kamu menambahkan record TXT ke DNS domain, lalu Let's Encrypt memeriksa record itu.

```bash
sudo certbot certonly --manual --preferred-challenges dns \
  -d domainkamu.com -d *.domainkamu.com
```

Certbot akan menampilkan nilai TXT yang harus kamu tambahkan di panel DNS provider kamu, lalu menunggu sampai kamu menekan Enter. Setelah record TXT terdeteksi, sertifikat diterbitkan dan disimpan di `/etc/letsencrypt/live/domainkamu.com/`.

Kelemahan mode manual: renewal tidak bisa otomatis karena record TXT harus ditambahkan ulang setiap kali perpanjang. Kalau butuh wildcard dengan auto-renewal, pakai plugin DNS provider kamu, misalnya `python3-certbot-dns-cloudflare`, yang menambah dan menghapus record TXT lewat API.

## Kesalahan umum pemula dan cara menghindarinya

**DNS belum mengarah ke VPS saat menjalankan Certbot.** Ini penyebab error paling sering. Let's Encrypt memeriksa domain dari internet, bukan dari dalam VPS kamu. Kalau A record masih mengarah ke IP lama atau belum terpropagasi, validasi gagal dengan pesan `DNS problem: NXDOMAIN` atau `connection refused`. Tunggu propagasi selesai, cek dengan `dig`, baru jalankan Certbot.

**Port 80 tertutup firewall.** Validasi HTTP-01 memakai port 80, bukan 443. Banyak orang membuka 443 tapi lupa membuka 80, lalu heran kenapa Certbot gagal padahal situsnya bisa dibuka lewat HTTPS. Pastikan profil `Nginx Full` aktif di UFW, atau buka kedua port di firewall provider VPS kamu.

**Terlalu banyak percobaan gagal sampai kena rate limit.** Let's Encrypt membatasi 5 sertifikat gagal per akun per jam dan 50 sertifikat per minggu per domain. Kalau kamu mencoba berkali-kali tanpa memperbaiki penyebabnya, kamu akan terkunci sementara. Untuk latihan, pakai flag `--dry-run` atau `--staging` supaya tidak menghabiskan kuota production.

**Konten campuran, mixed content.** Sertifikat sudah terpasang tapi browser tetap memberi peringatan. Penyebabnya hampir selalu aset yang masih di-load lewat HTTP: gambar, font, atau script dengan URL `http://` absolut. Ubah semua URL aset menjadi relatif, atau pakai `https://` secara eksplisit. Di Laravel, pastikan `APP_URL` di file `.env` sudah memakai `https://`, karena helper `asset()` mengikuti nilai itu.

**Lupa reload Nginx setelah sertifikat diperpanjang.** Ini jarang terjadi dengan plugin Nginx, tapi sering terjadi kalau sertifikat diterbitkan dengan mode `certonly` lalu dikonfigurasi manual. Nginx membaca sertifikat saat start atau reload, bukan setiap request. Kalau sertifikat baru sudah terbit tapi Nginx belum di-reload, pengunjung tetap menerima sertifikat lama yang sudah kedaluwarsa.

## Checklist verifikasi akhir

Sebelum menutup terminal, jalankan checklist ini.

1. Buka `https://domainkamu.com` di browser dan pastikan gemboknya muncul.
2. Buka `http://domainkamu.com` dan pastikan diarahkan ke HTTPS.
3. Cek skor SSL di SSL Labs, `https://www.ssllabs.com/ssltest/`, idealnya dapat nilai A.
4. Jalankan `sudo certbot renew --dry-run` dan pastikan tidak ada error.
5. Cek timer dengan `sudo systemctl list-timers | grep certbot`.

Kalau lima poin itu lolos, HTTPS kamu sudah beres dan auto-renewal akan mengurus sisanya. Lain kali deploy aplikasi baru ke VPS, pasang SSL di awal, bukan di akhir.
