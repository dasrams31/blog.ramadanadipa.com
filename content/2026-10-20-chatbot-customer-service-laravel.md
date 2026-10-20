---
title: Chatbot Customer Service di Laravel: Bikin CS AI Sendiri
description: Tutorial bikin chatbot customer service di Laravel: database percakapan, knowledge base FAQ, widget chat, eskalasi ke manusia, plus data tren CS AI 2026.
date: 2026-10-20
tags: [laravel, ai, chatbot, php]
faq:
  - Berapa biaya menjalankan chatbot AI untuk customer service?
  - Dengan model murah seperti GPT-4o mini atau model lokal, biaya per percakapan biasanya di bawah Rp100 untuk toko kecil sampai menengah. Pasang rate limit dan batas maksimal pesan per sesi agar tagihan tidak membengkak.
  - Apakah chatbot AI bisa menggantikan CS manusia sepenuhnya?
  - Tidak. Data Comm100 2026 menunjukkan chatbot hanya menyelesaikan 44,8 persen chat tanpa bantuan manusia, dan 87 persen pelanggan tetap ingin akses ke manusia (Gartner, Agustus 2026). Pola terbaik adalah hybrid: AI menangani pertanyaan rutin, manusia menangani kasus kompleks.
  - Bagaimana cara membuat chatbot menjawab sesuai info bisnis saya?
  - Masukkan knowledge base (FAQ, daftar harga, kebijakan) ke system prompt atau ambil dari database sebelum memanggil API AI. Tanpa konteks bisnis, chatbot akan menjawab ngawur atau mengarang info yang salah.
  - Apa bedanya chatbot AI dengan chatbot rule-based lama?
  - Chatbot rule-based hanya cocok kalau kata kunci cocok persis, tingkat resolusinya sekitar 52 persen. Chatbot AI memahami maksud kalimat bebas dan mencapai resolusi sekitar 78 persen (data EBI.AI, Mei 2026).
---

Kalau kamu punya toko online atau jasa, pertanyaan yang masuk ke CS itu-itu saja: jam berapa buka, ongkir ke Bandung berapa, cara retur gimana. Data Feedough (September 2026) mencatat waktu respons pertama layanan pelanggan turun dari lebih dari 6 jam jadi di bawah 4 menit setelah memakai AI, dan waktu resolusi turun dari hampir 32 jam jadi 32 menit. Gartner memproyeksikan penghematan biaya tenaga kerja contact center global mencapai 80 miliar dolar AS tahun ini.

Kabar baiknya: kamu tidak perlu langganan platform mahal untuk mulai. Dengan Laravel dan API AI, chatbot customer service sederhana bisa jadi dalam satu akhir pekan. Artikel ini membahas arsitekturnya yang benar, bukan sekadar tempel API key lalu berharap.

## Arsitektur yang Benar

Chatbot CS yang bagus punya lima komponen:

1. **Widget chat** di frontend: kotak chat yang bisa dibuka pengunjung.
2. **API endpoint** di Laravel: menerima pesan, memanggil AI, menyimpan riwayat.
3. **Knowledge base**: FAQ dan info bisnis yang disuntik ke prompt.
4. **Riwayat percakapan**: disimpan di database supaya AI ingat konteks.
5. **Eskalasi**: tombol atau trigger yang meneruskan ke manusia.

Tanpa komponen nomor 3 dan 5, yang kamu punya cuma mainan, bukan CS.

## Langkah 1: Database Percakapan

AI butuh ingat konteks. Kalau setiap pesan diperlakukan sebagai percakapan baru, user harus mengulang info terus. Buat dua tabel:

```php
// database/migrations/2026_10_20_000000_create_conversations_table.php
Schema::create('conversations', function (Blueprint $table) {
    $table->id();
    $table->string('session_id')->index();
    $table->string('visitor_name')->nullable();
    $table->enum('status', ['open', 'escalated', 'closed'])->default('open');
    $table->timestamps();
});

Schema::create('messages', function (Blueprint $table) {
    $table->id();
    $table->foreignId('conversation_id')->constrained()->cascadeOnDelete();
    $table->enum('role', ['user', 'assistant']);
    $table->text('content');
    $table->timestamps();
});
```

Jalankan `php artisan migrate`. Tabel ini juga jadi bahan evaluasi: kamu bisa baca ulang percakapan yang gagal dan memperbaiki knowledge base.

## Langkah 2: Knowledge Base dari Database

Jangan hardcode FAQ di prompt. Simpan di tabel supaya tim non-teknis bisa update lewat admin panel nanti:

```php
// database/migrations/2026_10_20_000001_create_faqs_table.php
Schema::create('faqs', function (Blueprint $table) {
    $table->id();
    $table->string('question');
    $table->text('answer');
    $table->boolean('is_active')->default(true);
    $table->timestamps();
});
```

Lalu service yang merangkai konteks. Ini bagian paling penting:

```php
// app/Services/CsChatService.php
namespace App\Services;

use App\Models\Faq;
use App\Models\Message;
use Illuminate\Support\Facades\Http;

class CsChatService
{
    public function reply(string $sessionId, string $userMessage): string
    {
        $conversation = \App\Models\Conversation::firstOrCreate(
            ['session_id' => $sessionId]
        );

        $conversation->messages()->create([
            'role'    => 'user',
            'content' => $userMessage,
        ]);

        $knowledge = Faq::where('is_active', true)
            ->get()
            ->map(fn ($f) => "Q: {$f->question}\nA: {$f->answer}")
            ->implode("\n\n");

        $history = $conversation->messages()
            ->latest()->limit(10)->get()->reverse()
            ->map(fn ($m) => ['role' => $m->role, 'content' => $m->content])
            ->values()->all();

        $response = Http::withToken(config('services.openai.key'))
            ->timeout(45)
            ->post('https://api.openai.com/v1/chat/completions', [
                'model'       => config('services.openai.model', 'gpt-4o-mini'),
                'temperature' => 0.3,
                'max_tokens'  => 400,
                'messages'    => array_merge([
                    ['role' => 'system', 'content' =>
                        "Kamu CS TokoRama, ramah dan singkat. " .
                        "Jawab HANYA berdasarkan info berikut. " .
                        "Kalau info tidak ada, bilang akan diteruskan ke tim manusia, jangan mengarang.\n\n" .
                        $knowledge],
                ], $history),
            ]);

        $answer = $response->json('choices.0.message.content', 'Maaf, ada gangguan. Coba lagi ya.');

        $conversation->messages()->create([
            'role'    => 'assistant',
            'content' => $answer,
        ]);

        return $answer;
    }
}
```

Tiga keputusan penting di kode ini: `temperature` 0.3 supaya jawaban konsisten dan tidak kreatif mengarang, `max_tokens` 400 untuk hemat biaya, dan instruksi eksplisit "jangan mengarang" di system prompt. Itu baris yang menyelamatkan reputasimu.

## Langkah 3: Endpoint API dengan Rate Limit

Tanpa rate limit, satu orang bisa spam 500 pesan dan menghabiskan budget API-mu dalam sejam. Laravel punya middleware throttle bawaan, pakai:

```php
// routes/api.php
use App\Http\Controllers\ChatController;

Route::middleware('throttle:20,1')->post('/chat', [ChatController::class, 'send']);
Route::post('/chat/escalate', [ChatController::class, 'escalate']);
```

```php
// app/Http/Controllers/ChatController.php
namespace App\Http\Controllers;

use App\Models\Conversation;
use App\Services\CsChatService;
use Illuminate\Http\Request;

class ChatController extends Controller
{
    public function send(Request $request, CsChatService $chat)
    {
        $validated = $request->validate([
            'session_id' => 'required|string|max:64',
            'message'    => 'required|string|max:1000',
        ]);

        return response()->json([
            'reply' => $chat->reply($validated['session_id'], $validated['message']),
        ]);
    }

    public function escalate(Request $request)
    {
        $conversation = Conversation::where('session_id', $request->session_id)->firstOrFail();
        $conversation->update(['status' => 'escalated']);

        // TODO: kirim notifikasi ke Telegram/Slack tim CS di sini

        return response()->json([
            'reply' => 'Siap, saya teruskan ke tim kami. Mohon tunggu sebentar ya.',
        ]);
    }
}
```

`throttle:20,1` artinya maksimal 20 pesan per menit per IP. Cukup longgar untuk manusia, cukup ketat untuk bot spam.

## Langkah 4: Widget Chat Sederhana

Frontend tidak perlu framework berat. Vanilla JS cukup:

```html
<div id="chat-box" style="display:none">
  <div id="chat-messages"></div>
  <input id="chat-input" placeholder="Tanya apa saja...">
</div>
<button id="chat-toggle">Chat dengan kami</button>

<script>
const sessionId = localStorage.getItem('chat_session') || crypto.randomUUID();
localStorage.setItem('chat_session', sessionId);

async function sendChat() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';

  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message: text }),
  });
  const data = await res.json();
  appendMessage('assistant', data.reply);
}
</script>
```

Tambahkan tombol "Bicara dengan manusia" yang memanggil `/api/chat/escalate`. Di Indonesia, konteksnya kuat: Udesk mencatat tren 2026 adalah model hybrid AI plus manusia sebagai yang paling optimal, dan platform lokal seperti Qiscus serta Kata.ai sudah terintegrasi WhatsApp dan marketplace. Kalau bisnismu hidup di WhatsApp, pertimbangkan WhatsApp Business API sebagai kanal berikutnya setelah widget web jalan.

## Kesalahan Umum Pemula

**1. Tidak membatasi konteks bisnis.** Chatbot tanpa knowledge base akan menjawab pertanyaan soal harga dengan angka karangan. Selalu suntik info resmi ke system prompt dan larang mengarang.

**2. Menyimpan API key di JavaScript.** Panggilan ke OpenAI harus selalu lewat backend Laravel. Key yang bocor di frontend bisa dipakai orang lain dan tagihanmu yang jebol.

**3. Tidak menyimpan riwayat.** Tanpa tabel messages, setiap pesan adalah awal baru. User yang bilang "kalau yang warna merah?" setelah tanya soal sepatu akan dapat jawaban ngawur.

**4. Tidak ada jalur eskalasi.** 87 persen pelanggan menganggap akses ke manusia itu penting (Gartner, Agustus 2026). Chatbot yang tidak bisa menyerah adalah chatbot yang bikin pelanggan marah.

**5. Lupa rate limit dan batas biaya.** Pasang throttle di route dan spending limit di dashboard OpenAI. Ini bukan opsional.

## Langkah Praktis yang Bisa Dicoba Hari Ini

1. Buat migration conversations, messages, dan faqs, lalu migrate.
2. Isi 10 FAQ paling sering ditanyakan pelangganmu ke tabel faqs.
3. Buat `CsChatService` seperti contoh di atas, dengan instruksi anti-mengarang.
4. Pasang route `/api/chat` dengan `throttle:20,1`.
5. Tempel widget di satu halaman dulu, uji dengan 20 pertanyaan nyata, baca riwayatnya, perbaiki FAQ yang jawabannya meleset.

Ulangi langkah 5 tiap minggu. Akurasi chatbot CS bukan ditentukan sekali saat coding, tapi dari siklus evaluasi mingguan: baca percakapan gagal, tambahkan ke knowledge base, ulangi. Itulah yang membedakan chatbot yang benar-benar dipakai dengan yang cuma jadi pajangan di pojok kanan bawah.

---

**Sumber data tren:** statistik chatbot customer service 2026 dari Feedough (diperbarui September 2026, merujuk benchmark Comm100 atas 220 juta interaksi); data adopsi dan resolusi dari EBI.AI (Mei 2026, merujuk riset Gartner); proyeksi integrasi CX berbasis AI di Indonesia dari Tek.id (2026); tren CS pintar Indonesia dari Udesk (2026).
