---
title: Cara Backup dan Restore Database PostgreSQL Otomatis
description: Panduan lengkap backup dan restore database PostgreSQL otomatis dengan pg_dump, pg_restore, dan cron. Lengkap dengan script siap pakai dan jadwal harian.
date: 2026-11-11
tags: [postgresql, database, backup, vps, devops]
faq:
  - Berapa sering database PostgreSQL sebaiknya di-backup?
  - Untuk data yang berubah tiap hari, backup harian adalah batas minimal. Data transaksi penting sebaiknya di-backup tiap jam, atau gunakan continuous archiving dengan WAL untuk recovery sampai titik waktu tertentu.
  - Apa beda pg_dump dan pg_dumpall?
  - pg_dump membackup satu database beserta skema dan datanya. pg_dumpall membackup seluruh cluster, termasuk semua database plus role dan user. Untuk migrasi server penuh, pakai pg_dumpall.
  - Bagaimana cara restore backup PostgreSQL yang rusak sebagian?
  - Restore ke database baru dulu dengan pg_restore, lalu cek tabel mana yang bermasalah. Jangan restore langsung menimpa database produksi sebelum kamu yakin file backup-nya utuh.
  - Apakah backup otomatis dengan cron aman?
  - Aman selama file backup disimpan di lokasi terpisah dari server database, diberi permission 600, dan tidak berisi password di dalam script. Gunakan file .pgpass untuk kredensial.
---

Database yang tidak pernah di-backup itu bukan soal kalau, tapi soal kapan datanya hilang. Saya pernah melihat satu perintah `DROP TABLE` yang salah ketik menghapus tabel berisi 40 ribu baris data pelanggan. Untungnya ada backup semalam sebelumnya, jadi kerugiannya cuma data satu hari, bukan seluruh bisnis.

Artikel ini membahas cara backup dan restore database PostgreSQL yang benar, lalu mengotomatiskannya supaya kamu tidak perlu mengingatnya lagi. Semua contoh saya jalankan di Ubuntu 22.04 dengan PostgreSQL 16, tapi perintahnya sama untuk versi 14 ke atas.

## Kenapa pg_dump Jadi Standar

PostgreSQL punya beberapa cara backup, tapi `pg_dump` adalah yang paling umum dipakai untuk database ukuran kecil sampai menengah. Hasilnya berupa file SQL atau arsip custom yang berisi perintah `CREATE TABLE`, `COPY`, sampai `CREATE INDEX`. File ini bisa di-restore ke server lain, bahkan ke versi PostgreSQL yang berbeda selama tidak terlalu jauh.

Ada tiga format utama yang perlu kamu kenal:

| Format | Perintah | Kelebihan |
| --- | --- | --- |
| Plain SQL | `pg_dump db > backup.sql` | Bisa dibaca manusia, mudah diedit |
| Custom | `pg_dump -Fc db > backup.dump` | Terkompresi, restore bisa paralel dan selektif |
| Directory | `pg_dump -Fd db -f folder/` | Paling cepat untuk database besar |

Untuk kebanyakan project, format custom (`-Fc`) adalah pilihan terbaik. Ukurannya lebih kecil dan restore-nya jauh lebih fleksibel.

## Backup Manual: Perintah Dasarnya

Backup satu database ke file custom:

```bash
pg_dump -U postgres -h localhost -Fc -f backup-2026-11-11.dump nama_database
```

Restore file itu ke database baru:

```bash
createdb -U postgres -h localhost nama_database_baru
pg_restore -U postgres -h localhost -d nama_database_baru backup-2026-11-11.dump
```

Kalau kamu butuh backup seluruh cluster, termasuk semua database dan role:

```bash
pg_dumpall -U postgres -h localhost > backup-semua.sql
```

Restore-nya dengan `psql`:

```bash
psql -U postgres -h localhost -f backup-semua.sql postgres
```

Satu hal yang sering bikin bingung pemula: `pg_dump` tidak membackup role dan user. Kalau kamu membuat database baru di server lain lalu restore, kamu harus membuat ulang role-nya dulu, atau restore akan gagal di bagian kepemilikan objek. Solusinya, backup role secara terpisah:

```bash
pg_dumpall -U postgres -h localhost --globals-only > roles.sql
```

## Jangan Simpan Password di Script

Kesalahan paling umum yang saya lihat: password ditulis langsung di script backup dengan `PGPASSWORD`. Password itu akan tersimpan di history shell dan bisa dibaca siapa saja yang punya akses ke file script.

Cara yang benar adalah file `.pgpass` di home directory user yang menjalankan backup:

```bash
echo "localhost:5432:*:postgres:password_rahasia_kamu" > ~/.pgpass
chmod 600 ~/.pgpass
```

Formatnya `host:port:database:user:password`. Setelah file ini ada, `pg_dump` dan `psql` akan membaca password otomatis tanpa perlu mengetik apa pun. Permission 600 itu wajib, PostgreSQL akan menolak file `.pgpass` yang bisa dibaca orang lain.

## Script Backup Otomatis yang Siap Pakai

Ini script yang saya pakai di VPS. Simpan sebagai `/usr/local/bin/backup-postgres.sh`:

```bash
#!/bin/bash
set -e

DB_NAME="nama_database"
DB_USER="postgres"
BACKUP_DIR="/var/backups/postgres"
RETENTION_DAYS=14
DATE=$(date +%Y-%m-%d_%H-%M)

mkdir -p "$BACKUP_DIR"

# Backup dalam format custom, terkompresi
pg_dump -U "$DB_USER" -h localhost -Fc \
  -f "$BACKUP_DIR/${DB_NAME}_${DATE}.dump" "$DB_NAME"

# Hapus backup yang lebih tua dari masa retensi
find "$BACKUP_DIR" -name "${DB_NAME}_*.dump" \
  -mtime +$RETENTION_DAYS -delete

echo "Backup selesai: ${DB_NAME}_${DATE}.dump"
```

Jadikan executable, lalu jadwalkan dengan cron:

```bash
chmod +x /usr/local/bin/backup-postgres.sh
crontab -e
```

Tambahkan baris ini untuk backup tiap hari jam 2 pagi:

```cron
0 2 * * * /usr/local/bin/backup-postgres.sh >> /var/log/postgres-backup.log 2>&1
```

Kenapa jam 2 pagi? Karena biasanya itu jam trafik paling rendah. Dan kenapa log-nya ditulis ke file? Karena kalau backup gagal di tengah malam, kamu butuh bukti untuk debugging, bukan sekadar cron yang diam-diam gagal.

## Restore: Latihan yang Sering Dilewatkan

Backup yang tidak pernah diuji restore-nya sama saja dengan tidak punya backup. Saya sarankan jadwalkan latihan restore minimal sebulan sekali. Caranya sederhana, restore ke database baru lalu cek jumlah baris di tabel penting:

```bash
createdb -U postgres -h localhost restore_test
pg_restore -U postgres -h localhost -d restore_test \
  /var/backups/postgres/nama_database_2026-11-11_02-00.dump

psql -U postgres -h localhost -d restore_test -c \
  "SELECT count(*) FROM users;"
```

Bandingkan angka itu dengan database produksi. Kalau sama, backup kamu sehat. Kalau `pg_restore` mengeluarkan error soal role yang tidak ada, itu tanda kamu lupa membackup `roles.sql` seperti yang dibahas di atas.

Untuk restore sebagian, misalnya cuma satu tabel, format custom memungkinkan itu:

```bash
pg_restore -U postgres -h localhost -d nama_database \
  -t users backup-2026-11-11.dump
```

Opsi `-t` ini alasan lain kenapa format custom lebih unggul dari plain SQL.

## Kesalahan Umum Pemula

**1. Backup disimpan di server yang sama, tanpa salinan di tempat lain.**

Hard disk rusak, backup ikut hilang. Minimal salin file backup ke object storage seperti S3 atau ke VPS lain dengan `rsync`. Tambahkan satu baris ini di akhir script backup:

```bash
rsync -avz "$BACKUP_DIR/" user@server-cadangan:/backups/postgres/
```

**2. Tidak ada retensi, disk penuh diam-diam.**

Backup harian tanpa penghapusan akan mengisi disk dalam beberapa minggu. PostgreSQL akan berhenti menulis saat disk penuh, dan itu lebih buruk daripada tidak ada backup. Baris `find ... -mtime +14 -delete` di script di atas mencegah hal ini.

**3. Backup jalan saat database sedang di-vacuum atau di-migrasi besar.**

`pg_dump` mengambil snapshot konsisten, jadi secara teknis aman. Tapi beban I/O-nya bisa memperlambat migrasi yang sedang jalan. Jadwalkan backup di jam sepi dan jangan bersamaan dengan deploy besar.

**4. Mengandalkan snapshot VPS sebagai satu-satunya backup.**

Snapshot itu backup seluruh disk, bukan backup database. Restore snapshot berarti mengembalikan seluruh server ke kondisi lama, termasuk data yang sudah berubah setelah snapshot diambil. Snapshot bagus sebagai pelengkap, bukan pengganti `pg_dump`.

**5. Tidak pernah mengecek ukuran file backup.**

File backup yang tiba-tiba mengecil drastis biasanya tanda ada yang salah, misalnya tabel gagal ter-dump. Tambahkan pengecekan ukuran di script:

```bash
SIZE=$(stat -c%s "$BACKUP_DIR/${DB_NAME}_${DATE}.dump")
if [ "$SIZE" -lt 1024 ]; then
  echo "Backup mencurigakan, ukuran hanya $SIZE byte" >&2
  exit 1
fi
```

## Langkah Praktis Hari Ini

Kalau kamu belum pernah membackup database PostgreSQL, ini urutan yang bisa langsung kamu kerjakan dalam 30 menit:

1. Buat file `.pgpass` dan set permission 600.
2. Jalankan `pg_dump` manual sekali, lalu restore ke database `restore_test` dan cek jumlah barisnya.
3. Simpan script backup di `/usr/local/bin/backup-postgres.sh`, sesuaikan nama database dan direktori.
4. Tambahkan cron jam 2 pagi dan cek log keesokan harinya.
5. Salin satu file backup ke tempat lain, minimal ke laptop kamu, sebagai bukti konsep offsite backup.

Backup itu seperti asuransi: terasa buang-buang waktu sampai hari ketika kamu membutuhkannya. Dan hari itu pasti datang, entah karena perintah yang salah ketik, update yang gagal, atau disk yang tiba-tiba mati. Bedanya cuma satu, apakah kamu sudah siap atau belum.
