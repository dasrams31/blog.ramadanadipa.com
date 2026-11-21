---
title: Mengukur Kualitas AI Code Review: Metrik yang Jujur
description: Addressing rate saja tidak cukup. Pelajari cara mengukur kualitas AI code review dengan metrik jujur, plus contoh skrip Python untuk menghitungnya sendiri.
cover: /assets/img/covers/mengukur-kualitas-ai-code-review-addressing-rate-metrik-jujur.jpg
date: 2026-11-21
tags: [ai-code-review, github-copilot, code-quality, developer-tools]
faq:
  - Apa itu addressing rate di AI code review?
  - Addressing rate adalah persentase komentar review AI yang berujung perubahan kode sebelum merge. GitHub mulai menyediakan angka ini di Copilot usage metrics API sejak 5 November 2026, dihitung dari komentar pada pull request yang sudah merge.
  - Berapa addressing rate yang bagus untuk AI code review?
  - Tergantung definisi dan konteks repo. Deployment internal perusahaan besar mencatat 38 persen sampai 65 persen, sementara GitHub Actions open source umum hanya 0,9 persen sampai 19,2 persen. Bandingkan dengan angka komentar manusia di repo yang sama, bukan dengan angka perusahaan lain.
  - Kenapa komentar AI yang ditindaklanjuti belum tentu berkualitas?
  - Karena developer bisa mengubah kode untuk alasan lain, atau perubahannya trivial. Addressing rate mengukur respons, bukan kebenaran temuan. Angka ini perlu dilengkapi dismissal rate, escaped defects, dan sampling manual.
  - Bagaimana cara mengukur kualitas AI code review di repo sendiri?
  - Simpan setiap temuan ke log, catat hasilnya, diperbaiki, ditolak, atau lolos ke merge, lalu hitung addressing rate dan dismissal rate per minggu. Contoh skrip Python-nya ada di artikel ini.
---

AI code review sudah dipakai di mana-mana, tapi hampir tidak ada tim yang bisa menjawab pertanyaan paling dasar: apakah reviewer AI ini sebenarnya bagus? Tool-nya rajin memposting komentar di setiap pull request, dashboard-nya hijau, semua orang merasa produktif, lalu tidak ada yang memeriksa apakah komentar itu benar, ditindaklanjuti, atau justru menambah kerja review manusia.

GitHub membuat pertanyaan ini lebih gampang dijawab. Pada 5 November 2026, GitHub menambahkan field code review ke Copilot usage metrics API, termasuk addressing rate: persentase komentar Copilot code review yang dihitung sudah ditindaklanjuti. Angka ini berguna, tapi hanya kalau kamu paham apa yang sebenarnya dihitung.

## Addressing rate menurut GitHub

Di Copilot usage metrics API, setiap baris laporan harian per repo sekarang membawa objek `copilot_code_review` dengan dua field utama: `total_comments_evaluated` dan `total_comments_addressed`. Addressing rate adalah pembagian keduanya, dipecah lagi berdasarkan severity (high, medium, low), review tier (lite, balanced, max), dan tipe komentar (bug, security, performance, custom, dan other).

Tiga batasan yang sering dilewatkan. Pertama, yang dihitung hanya komentar pada pull request yang sudah merge. Pull request yang masih terbuka atau ditutup tanpa merge tidak masuk hitungan. Kedua, komentar dievaluasi pada hari pull request-nya merge, bukan pada hari komentar itu diposting. Ketiga, komentar pada pull request yang dibuka bot umumnya tidak dievaluasi.

Artinya addressing rate GitHub adalah metrik merge, bukan metrik review. Komentar yang benar tapi pull request-nya ditutup tanpa merge tidak pernah tercatat sebagai apapun. Kalau timmu sering menutup pull request tanpa merge, angka ini tidak menggambarkan kenyataan sehari-hari.

## Angka dari perusahaan besar

Beberapa perusahaan mempublikasikan angka mereka. Perhatikan definisinya, karena definisilah yang menentukan apakah angka itu bisa dibandingkan.

| Tim | Angka | Cara menghitung |
| --- | --- | --- |
| Uber, uReview, Agustus 2025 | Lebih dari 65 persen ditindaklanjuti, 75 persen dinilai berguna | Komentar dihitung ditindaklanjuti kalau lima kali re-run pada commit final tidak lagi menghasilkan komentar yang mirip |
| Atlassian, April 2026 | 38,7 persen berujung perubahan kode, dibanding 44,45 persen komentar manusia | Komentar diikuti perubahan kode di commit berikutnya; waktu siklus pull request turun 30,8 persen |
| Google, AutoCommenter | Sekitar 40 persen resolution rate | Estimasi setelah rollout bertahap sampai A/B test pada sekitar setengah developer |
| Anthropic, 9 Maret 2026 | Kurang dari 1 persen temuan ditandai salah; pull request dengan komentar substantif naik dari 16 persen ke 54 persen | Penilaian engineer Anthropic pada pull request internal |
| Studi Sun et al., 16 GitHub Actions, 178 repo, 22.326 komentar | 0,9 persen sampai 19,2 persen, dibanding 60 persen komentar manusia | File-level 0,9 sampai 4,2 persen, hunk-level 6,5 sampai 19,2 persen |
| Cursor, Bugbot, 40 eksperimen | Resolution rate naik dari 52 persen ke lebih dari 70 persen | Definisi internal Cursor |

Polanya jelas: tiga sistem yang mencapai 38 persen ke atas, Uber, Google, dan Atlassian, semuanya di-tune untuk codebase mereka sendiri dan punya tahap filter yang membuang komentar lemah sebelum sampai ke developer. Sebaliknya, GitHub Actions open source generik yang dipasang apa adanya jatuh ke kisaran satu digit sampai belasan persen.

Satu angka lain patut diingat. Survei Sonar pada Januari 2026 terhadap lebih dari 1.100 developer menemukan AI menulis 42 persen kode yang di-commit, tapi 96 persen developer mengaku tidak sepenuhnya percaya kode AI itu benar secara fungsional. Review adalah tempat ketidakpercayaan itu dibayar.

## Kenapa angka itu tidak bisa dibandingkan mentah-mentah

Masalah pertama adalah definisi. Uber memakai re-run lima kali, Atlassian memakai perubahan di commit berikutnya, GitHub memakai evaluasi saat merge. Tiga definisi ini mengukur tiga hal berbeda, dan tidak ada satu pun yang membuktikan komentar itu benar. Developer bisa mengubah kode karena alasan lain di commit berikutnya, lalu komentar AI yang salah ikut tercatat sebagai ditindaklanjuti.

Masalah kedua adalah konteks. Angka Uber berasal dari sistem yang memproses lebih dari 10.000 commit per minggu dan meninjau lebih dari 90 persen dari sekitar 65.000 diff mingguan. Angka itu bukan target yang masuk akal untuk GitHub Action generik di repo Laravel kecil milik tim tiga orang. Benchmark independen jauh lebih pesimis: SWE-PRBench melaporkan tidak ada model frontier yang mendeteksi lebih dari 31 persen isu yang ditandai manusia di 350 pull request.

Masalah ketiga adalah apa yang tidak diukur. Addressing rate tidak menghitung isu yang terlewat. Reviewer bisa mencapai 70 persen dengan hanya mengomentari hal aman seperti typo dan format, sambil melewatkan race condition di tengah diff. Di sinilah metrik tambahan menjadi wajib.

## Lima metrik yang lebih jujur

### 1. Addressing rate di repo sendiri, dibanding baseline manusia

Jangan bandingkan angka repo kamu dengan angka Uber. Bandingkan komentar AI dengan komentar manusia di repo yang sama, pada periode yang sama, dengan definisi yang sama. Kalau komentar manusia 60 persen berujung perubahan kode dan komentar AI 15 persen, itu informasi yang jujur. Kalau keduanya sama-sama sekitar 45 persen, tool itu sudah setara manusia di repo kamu.

### 2. Dismissal rate beserta alasannya

Dari semua temuan yang diposting, berapa persen yang ditolak tanpa tindakan, dan kenapa? Catat alasannya dengan kosakata tetap: false positive, wont fix, sudah ditangani, dan tidak berlaku untuk service ini. False positive yang tinggi berarti aturan atau prompt harus diperketat. Wont fix yang tinggi berarti reviewer mengomentari hal yang tim sengaja biarkan. Tanpa alasan, dismissal rate hanya angka keluhan.

### 3. Escaped defects

Ini metrik yang paling tidak nyaman dan paling penting: apa yang lolos ke merge padahal reviewer sudah menandainya, atau apa yang lolos tanpa ditandai sama sekali. Setiap minggu, ambil sampel pull request yang sudah merge, terutama yang komentarnya ditolak manusia, lalu periksa apakah isu yang ditandai itu nyata. Setiap escape yang terkonfirmasi adalah sinyal ganda: reviewer benar, dan proses membiarkannya lolos.

### 4. Signal ratio

Dari temuan yang tidak ditolak, berapa banyak yang berkategori HIGH dibanding noise. Reviewer yang sehat diam sebagian besar waktu dan berisik soal hal yang penting. Kalau 90 persen komentar berkategori low dan medium, tim akan belajar mengabaikan semuanya, termasuk yang high. Pantau rasio ini dari waktu ke waktu, bukan jumlah komentar per pull request.

### 5. Time-to-merge delta dan biaya per komentar berguna

Bandingkan waktu merge pull request sebelum dan sesudah reviewer AI, dan pisahkan pull request yang punya temuan dengan yang tidak. Reviewer yang bagus memangkas waktu review manusia, reviewer yang berisik menambahnya. Terakhir, hitung biaya per komentar berguna: total biaya tool dan token dibagi jumlah komentar yang benar-benar berujung perbaikan. Angka ini yang akan ditanya atasanmu, dan lebih jujur daripada biaya per pull request.

## Cara mengukurnya di repo sendiri

Kamu tidak butuh dashboard mahal untuk mulai. Yang dibutuhkan hanya satu file log: satu baris JSON per temuan, ditambahkan oleh job reviewer di CI. Lima field sudah cukup: `rule_id`, `severity`, `outcome` (fixed, dismissed, atau merged-as-flagged), `dismissal_reason`, dan `pr_number`.

Skrip Python berikut membaca log itu dan menghitung metrik di atas. Simpan sebagai `scripts/review_metrics.py` dan jalankan tiap minggu:

```python
import json
import sys
from collections import Counter, defaultdict

def load_findings(path):
    findings = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                findings.append(json.loads(line))
    return findings

def main(path):
    findings = load_findings(path)
    total = len(findings)
    if total == 0:
        print("Belum ada temuan di log.")
        return

    fixed = sum(1 for f in findings if f["outcome"] == "fixed")
    dismissed = sum(1 for f in findings if f["outcome"] == "dismissed")
    escaped = sum(1 for f in findings if f["outcome"] == "merged-as-flagged")

    print(f"Total temuan: {total}")
    print(f"Addressing rate: {fixed / total:.1%}")
    print(f"Dismissal rate: {dismissed / total:.1%}")
    print(f"Escaped defects: {escaped}")

    reasons = Counter(
        f.get("dismissal_reason", "tanpa-alasan")
        for f in findings
        if f["outcome"] == "dismissed"
    )
    print("Alasan penolakan:")
    for reason, count in reasons.most_common():
        print(f"  {reason}: {count}")

    by_severity = defaultdict(lambda: {"total": 0, "fixed": 0})
    for f in findings:
        bucket = by_severity[f["severity"]]
        bucket["total"] += 1
        if f["outcome"] == "fixed":
            bucket["fixed"] += 1

    print("Signal ratio per severity:")
    for severity in ("high", "medium", "low"):
        bucket = by_severity.get(severity, {"total": 0, "fixed": 0})
        if bucket["total"]:
            rate = bucket["fixed"] / bucket["total"]
            print(f"  {severity}: {bucket['total']} temuan, {rate:.1%} ditindaklanjuti")

if __name__ == "__main__":
    main(sys.argv[1])
```

Format tiap baris log terlihat seperti ini:

```json
{"rule_id": "sql-injection", "severity": "high", "outcome": "fixed", "dismissal_reason": "", "pr_number": 142}
{"rule_id": "naming-style", "severity": "low", "outcome": "dismissed", "dismissal_reason": "wont-fix", "pr_number": 143}
```

Jalankan skrip ini tiap Jumat sore selama empat minggu sebelum memutuskan nasib tool. Empat minggu cukup untuk melewati variasi jenis pull request, tapi cukup pendek untuk menghentikan tool yang jelas-jelas berisik sebelum tim kehilangan kepercayaan. Yang penting adalah tren: dismissal rate turun, escape datar atau turun, signal ratio stabil, dan addressing rate mendekati baseline manusia di repo yang sama.

## Kesalahan umum pemula

**Membandingkan angka antar perusahaan.** Angka Uber, Atlassian, dan GitHub Actions open source dihitung dengan definisi berbeda di codebase berbeda. Satu-satunya pembanding yang sah adalah komentar manusia di repo kamu sendiri.

**Menghitung komentar di pull request bot dan draft.** Pull request dari bot dan draft sering memicu komentar yang tidak pernah ditindaklanjuti siapa pun. Kalau masuk ke perhitungan, addressing rate jatuh bukan karena reviewer buruk, tapi karena datanya kotor. Saring dulu sebelum menghitung.

**Hanya melihat jumlah komentar.** Tool yang memposting 30 komentar per pull request terlihat rajin di dashboard, tapi volume adalah metrik yang paling gampang dimanipulasi. Tiga puluh komentar yang 25 di antaranya ditolak lebih buruk daripada tiga komentar yang semuanya ditindaklanjuti.

**Mengabaikan biaya.** Lisensi tool, token model, dan menit CI semuanya ada harganya. Reviewer yang murah tapi berisik bisa lebih mahal daripada reviewer yang mahal tapi tepat, karena biaya terbesarnya adalah jam engineer yang membaca komentar yang salah. Selalu hitung biaya per komentar berguna, bukan biaya per bulan.

**Tidak pernah sampling manual.** Tidak ada metrik otomatis yang bisa menggantikan membaca 20 komentar acak dan menilai sendiri apakah komentar itu benar, berguna, dan pantas diposting. Sampling manual adalah satu-satunya cara menangkap false negative, yaitu isu nyata yang tidak pernah dikomentari. Jadwalkan 30 menit seminggu untuk ini.

## Langkah praktis yang bisa langsung dicoba

Mulai minggu ini, tanpa mengganti tool apapun. Pertama, buat file log temuan dan isi secara manual untuk 20 pull request terakhir: catat tiap komentar AI, hasilnya, dan alasannya kalau ditolak. Kedua, hitung addressing rate dan dismissal rate repo kamu dengan skrip di atas, lalu hitung angka yang sama untuk komentar manusia di periode yang sama. Ketiga, ambil 10 pull request yang sudah merge dan periksa apakah ada isu yang lolos.

Setelah empat minggu data terkumpul, keputusannya jadi sederhana. Kalau addressing rate AI mendekati manusia, dismissal rate turun, dan escape tidak naik, pertahankan dan tune aturannya. Kalau dismissal rate didominasi false positive, perketat prompt dan aturan. Kalau addressing rate mentok di bawah 20 persen sementara manusia di atas 50 persen, matikan tool itu dan coba pendekatan lain. Angka yang jujur memang kadang menyakitkan, tapi lebih murah daripada setahun membayar tool yang hanya menambah kebisingan di pull request.

Sumber angka yang dikutip: GitHub Changelog dan dokumentasi Copilot usage metrics, 5 November 2026; Uber Engineering tentang uReview, Agustus 2025; Atlassian tentang RovoDev Code Reviewer, April 2026; Anthropic tentang peluncuran Code Review, 9 Maret 2026; studi Sun et al. tentang 16 GitHub Actions di 178 repository; survei Sonar, Januari 2026; dan ringkasan statistik AI code review 2026 dari QuashBugs.
