---
title: API Review Copilot: Minta Review PR lewat REST dan GraphQL
description: GitHub kini mengizinkan Copilot code review diminta lewat REST dan GraphQL API. Pelajari endpoint baru, level effort, dan contoh workflow Actions.
cover: /assets/img/covers/api-review-copilot-oktober-2026-rest-graphql.jpg
date: 2026-11-17
tags: [github-copilot, code-review, github-api, rest-api]
faq:
  - Bagaimana cara minta review Copilot lewat API?
  - Pakai endpoint baru POST /repos/{owner}/{repo}/pulls/{pull_number}/copilot-code-review dengan body review_effort, atau cara lama POST ke requested_reviewers dengan reviewer copilot-pull-request-reviewer[bot]. Keduanya butuh token dengan permission Pull requests: write.
  - Apa saja level effort Copilot code review?
  - Ada tiga level: Lite untuk bug umum dan hemat kredit, Balanced untuk analisis lebih dalam dan kini jadi default, serta Max untuk review paling teliti yang masih public preview sejak 28 Oktober 2026.
  - Apakah review Copilot lewat API butuh paket berbayar?
  - Ya. Fitur ini tersedia untuk Copilot Pro, Pro+, Max, Business, dan Enterprise. Paket Free tidak mendapat pull request review.
  - Apakah Copilot otomatis menyetujui PR setelah review?
  - Tidak. Secara default Copilot memberi review berjenis Comment, bukan Approve. Persetujuan otomatis adalah kemampuan terpisah yang harus dikonfigurasi organisasi.
---

Selama ini minta review Copilot berarti membuka halaman pull request dan mengklik tombol Request di samping nama Copilot. Cara itu bekerja, tapi tidak bisa dipanggil dari script, pipeline, atau tool internal. Pada 2 Oktober 2026, GitHub mengubahnya lewat changelog resmi: Copilot code review kini bisa diminta lewat REST dan GraphQL API, lengkap dengan pilihan level effort untuk setiap request.

## Dua cara minta review lewat API

GitHub sebenarnya menyediakan dua jalur REST, dan keduanya masih berlaku. Bedanya ada di apa yang bisa kamu atur dan bagaimana GitHub memperlakukan request ulang.

| | Endpoint baru | Cara lama |
| --- | --- | --- |
| Endpoint | `POST /repos/{owner}/{repo}/pulls/{pull_number}/copilot-code-review` | `POST /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` |
| Cara minta | Body JSON berisi `review_effort` | Body JSON berisi `reviewers` dengan login `copilot-pull-request-reviewer[bot]` |
| Pilih effort | Bisa, per request | Tidak bisa, pakai default repo |
| Request ulang setelah review selesai | Bisa, request baru dibuat otomatis | Tidak, reviewer sudah tidak lagi berstatus requested |
| Respons sukses | `201` dengan `node_id` dan `state` | `201 Created` |

Endpoint baru adalah jalur yang direkomendasikan kalau kamu butuh kontrol effort atau review ulang programatik. Cara lama tetap berguna untuk script yang sudah jalan.

## Level effort: Lite, Balanced, dan Max

Setiap request bisa membawa satu dari tiga level effort, dan pilihan ini langsung memengaruhi biaya serta kedalaman review.

**Lite** adalah review paling hemat. GitHub menggambarkannya sebagai review yang menyasar masalah umum seperti bug, kerentanan keamanan, dan inkonsistensi gaya. Cocok untuk PR kecil, perubahan dokumentasi, atau repo yang PR-nya banyak tapi risikonya rendah.

**Balanced** melakukan analisis lebih dalam pada logika kompleks, kode yang sensitif keamanan, dan perubahan yang menyentuh banyak service. GitHub menyebut Balanced memakai lebih banyak AI credits dan sedikit lebih banyak GitHub Actions minutes dibanding Lite.

**Max** adalah level paling teliti. GitHub menambahkannya pada 28 Oktober 2026 dan saat itu masih berstatus public preview, jadi ketersediaannya bisa berubah dan sebaiknya dicek di dokumentasi sebelum dipakai di workflow produksi.

Ada satu perubahan diam-diam yang memengaruhi tagihan. GitHub mengumumkan pada 28 Agustus 2026 bahwa level Default akan memakai Balanced, dan perubahan itu berlaku 28 September 2026 untuk repo dan organisasi baru maupun yang sudah ada. Repo yang sebelumnya sudah memilih Lite secara eksplisit tetap memakai Lite.

## Minta review lewat REST

Contoh paling langsung memakai curl. Ganti `$OWNER`, `$REPO`, dan `$PR_NUMBER` dengan nilai repo kamu, dan simpan token di `$GH_TOKEN`.

```bash
curl -L -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  "https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/copilot-code-review" \
  -d '{"review_effort":"balanced"}'
```

Kalau kamu sudah memasang GitHub CLI, perintahnya lebih pendek. Opsi `-f` mengirim field sebagai JSON body.

```bash
gh api "repos/$OWNER/$REPO/pulls/$PR_NUMBER/copilot-code-review" \
  -X POST -f review_effort=balanced
```

Respons `201` berarti GitHub menerima request dan review akan dibuat. Kalau sebuah review Copilot masih berstatus pending untuk PR itu, endpoint baru menjawab `409`, jadi script yang sama tidak membuat antrean ganda. Respons `422` dengan `failure_reason` `INVALID_REVIEW_EFFORT` berarti level effort yang kamu kirim tidak dikenali atau tidak tersedia untuk repo dan akun itu. Respons `429` berarti kena rate limit, dan `503` berarti layanan review sedang tidak bisa melayani request.

Untuk token, GitHub mendokumentasikan fine-grained personal access token serta token GitHub App. Fine-grained token butuh permission repo **Pull requests: write**. Simpan token sebagai repository secret, misalnya `REVIEW_TOKEN`.

Cara lama lewat `requested_reviewers` tetap valid:

```bash
curl -L -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  "https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/requested_reviewers" \
  -d '{"reviewers":["copilot-pull-request-reviewer[bot]"]}'
```

Login `copilot-pull-request-reviewer[bot]` adalah identitas resmi Copilot sebagai reviewer. Tanpa suffix `[bot]`, GitHub tidak akan mengenalinya sebagai reviewer Copilot.

## Minta review lewat GraphQL

Tim yang sudah memakai GraphQL GitHub punya dua mutation yang relevan. Yang pertama adalah `requestReviewsByLogin`, yang menerima login bot secara langsung dan bekerja dengan node ID pull request.

```graphql
mutation {
  requestReviewsByLogin(input: {
    pullRequestId: "PR_kwDOABC123"
    botLogins: ["copilot-pull-request-reviewer[bot]"]
  }) {
    pullRequest {
      number
      title
    }
  }
}
```

Nilai `pullRequestId` adalah node ID pull request. Kamu bisa mendapatkannya dari query pull request biasa atau dari respons endpoint REST baru yang mengembalikan `node_id`.

Mutation kedua adalah `requestCopilotCodeReview`, mutation khusus yang didokumentasikan GitHub untuk meminta Copilot code review. Setiap pemanggilan mencoba memajukan lifecycle review: kalau review terakhir sudah selesai, request baru dibuat otomatis. Kalau request masih pending, mutation ini mengembalikan `failureReason` bernilai `REQUEST_CONFLICT` dan tidak membuat request ganda.

Pilih REST kalau automation kamu sudah bekerja dengan nama repo dan nomor PR. Pilih GraphQL kalau workflow kamu sudah menyimpan node ID dan memakai mutation GraphQL untuk operasi GitHub lainnya.

## Workflow GitHub Actions praktis

Contoh berikut meminta review Copilot setiap PR dibuka atau diperbarui, lalu menunggu dan memverifikasi bahwa review benar-benar masuk. Verifikasi itu penting, karena respons `201` hanya membuktikan GitHub menerima request, bukan membuktikan review sudah diproduksi.

```yaml
name: Copilot Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  request-review:
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - name: Minta review Copilot
        env:
          GH_TOKEN: ${{ secrets.REVIEW_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          gh api "repos/${{ github.repository }}/pulls/$PR_NUMBER/copilot-code-review" \
            -X POST -f review_effort=balanced
      - name: Tunggu dan verifikasi review
        env:
          GH_TOKEN: ${{ secrets.REVIEW_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          for i in $(seq 1 12); do
            sleep 10
            if gh api "repos/${{ github.repository }}/pulls/$PR_NUMBER/reviews" \
              --jq '.[] | select(.user.login == "copilot-pull-request-reviewer[bot]") | .id' \
              | grep -q .; then
              echo "Review Copilot sudah masuk."
              exit 0
            fi
          done
          echo "Review belum masuk setelah 2 menit."
          exit 1
```

Ada tiga detail yang sengaja dibuat seperti itu. Pertama, draft PR dilewati, karena mereview kode yang masih berubah hanya menambah noise. Kedua, permission job dibatasi ke `pull-requests: write`. Ketiga, langkah verifikasi memakai endpoint daftar review dan mencari login bot Copilot, karena begitu Copilot mengirim review, ia tidak lagi muncul di daftar requested reviewers. GitHub menyebut review biasanya selesai kurang dari 30 detik, jadi polling dua menit sudah cukup longgar.

Kamu juga bisa menyesuaikan effort dengan jenis perubahan. PR yang menyentuh file autentikasi atau pembayaran pantas memakai `balanced` atau `max`, sementara PR yang hanya mengubah teks cukup memakai `lite`. GitHub Actions menyediakan `paths` filter di trigger workflow untuk memisahkan keduanya.

Sejak 6 November 2026, GitHub juga menambahkan pengelolaan setting Copilot code review lewat API, termasuk pengaturan default effort di level organisasi dan repo.

## Biaya dan batasan yang perlu dihitung

Fitur API ini tersedia untuk Copilot Pro, Pro+, Max, Business, dan Enterprise. Paket Free tidak mendapat pull request review, jadi workflow di atas akan gagal dengan `422` kalau paketnya tidak memenuhi syarat.

Biaya mengikuti model AI credits ditambah GitHub Actions minutes untuk repo privat. Balanced lebih mahal dari Lite, dan Max tentu lebih mahal lagi, jadi jangan memakai effort tertinggi untuk semua PR. Aturan praktisnya: Lite untuk PR rutin, Balanced untuk perubahan logika dan keamanan, Max untuk PR yang menyentuh data sensitif atau arsitektur inti. Ukur dulu di satu repo selama seminggu sebelum menetapkan kebijakan effort untuk semua repo.

Secara default hasil review berupa komentar, bukan approval, dan kemampuan approval otomatis adalah konfigurasi terpisah yang masih berstatus public preview. Pisahkan tiga status ini di workflow kamu: review diminta, review diterima, dan keputusan merge. Keputusan merge tetap dipegang test, static analysis, dan manusia.

## Kesalahan umum pemula dan cara menghindarinya

Pertama, menganggap respons `201` berarti kode sudah direview. Respons itu hanya berarti request diterima. Selalu verifikasi lewat endpoint daftar review.

Kedua, memakai effort yang sama untuk semua PR. Tagihan membengkak diam-diam, terutama setelah default berubah ke Balanced pada 28 September 2026. Periksa setting default repo kamu dan tetapkan kebijakan effort berdasarkan jenis perubahan.

Ketiga, meminta review ulang dengan endpoint lama setelah Copilot selesai mereview. Cara lama tidak membuat request baru karena reviewer sudah tidak berstatus requested. Pakai endpoint baru `copilot-code-review` atau mutation `requestCopilotCodeReview` untuk re-review.

Keempat, memakai token tanpa permission yang benar lalu bingung melihat `403`. Token fine-grained butuh **Pull requests: write**. Uji token di satu PR percobaan dulu.

Kelima, membiarkan workflow meminta review untuk setiap push tanpa jeda. Setiap push baru yang memicu review baru memakan kredit dan Actions minutes. Pertimbangkan memicu review hanya saat PR dibuka atau saat label tertentu ditambahkan.

## Langkah pertama hari ini

Ambil satu repo kecil yang PR-nya kamu kenal baik. Buat fine-grained token dengan permission **Pull requests: write**, simpan sebagai secret `REVIEW_TOKEN`, lalu jalankan perintah curl endpoint baru di satu PR percobaan dengan `review_effort` bernilai `lite`. Cek responsnya, tunggu sekitar satu menit, lalu ambil daftar review dan pastikan komentar Copilot masuk. Setelah satu PR berhasil, salin workflow YAML di atas ke repo itu dan buka PR percobaan dengan satu bug yang jelas.

API review Copilot Oktober 2026 mengubah review dari tombol yang harus diingat menjadi langkah yang bisa dipanggil software. Dipakai dengan benar, PR tidak lagi menunggu seseorang sempat mengklik Request. Dipakai sembarangan, ia menjadi mesin komentar berbayar yang tidak ada yang membaca. Bedanya ada di effort yang kamu pilih, verifikasi yang kamu pasang, dan keputusan merge yang tetap kamu pegang sendiri.

Sumber: GitHub Changelog 2 Oktober 2026; GitHub Changelog 28 Oktober 2026; GitHub Changelog 6 November 2026; GitHub Docs, REST API endpoints for Copilot code review; GitHub Docs, referensi GraphQL.
