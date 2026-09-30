<div align="center">
  <img src="logo.jpeg" alt="Sarah Agent" width="220">

  # Sarah Agent

  **Agen AI otonom untuk lingkungan Linux**

  ACTION &rarr; OBSERVATION loop &middot; Multi-step reasoning &middot; Autonomous shell agent
</div>

---

## Deskripsi

**Sarah Agent** adalah agen AI otonom yang dirancang untuk membantu berbagai tugas di lingkungan Linux. Agen ini bekerja dengan siklus **Action &rarr; Observation**: menerima sebuah tujuan, merancang langkah berikutnya secara mandiri, mengeksekusi perintah shell, lalu membaca output untuk menentukan langkah berikutnya — hingga tujuan tercapai.

Sarah Agent dibangun sebagai agen **single-file** berbasis Python dengan model bahasa (LLM) sebagai otak. Tidak ada API atau layanan eksternal tambahan yang wajib dipasang, selain endpoint LLM yang dikonfigurasi melalui environment variable.

## Fitur Utama

| Fitur | Keterangan |
| :--- | :--- |
| 🔁 Action–Observation Loop | siklus `rencana → eksekusi → observasi → rencana berikutnya` secara otomatis |
| 🧠 Multi-step reasoning | langkah berpikir mandiri hingga 150 langkah eksekusi per sesi tugas |
| 🛡️ Anti-loop protection | deteksi perintah berulang, output JSON rusak, dan kondisi "macet" |
| ⏱️ Rate limit & retry | throttle antar-request, exponential backoff, dan cooldown otomatis |
| 📉 Manajemen konteks | riwayat pesan dipangkas, token budget opsional, ringkasan observasi panjang |
| 📄 Laporan akhir | transkrip alasan, perintah, dan hasil setiap langkah dicetak saat selesai |
| 🎛️ Sepenuhnya konfigurabel | seluruh perilaku diatur lewat environment variable, tanpa hardcode API key |

## Kemampuan

<details open>
<summary><b>🖥️ Eksekusi Perintah Linux</b></summary>

- Menjalankan perintah shell (`bash`, `sh`)
- Mengelola proses (`start`, `stop`, `kill`)
- Mengelola layanan sistem (`systemctl`)

</details>

<details>
<summary><b>📁 Manajemen File</b></summary>

- Membuat, membaca, menulis, dan menghapus file
- Mengelola direktori
- Mengubah izin file (`chmod`, `chown`)
- Mencari file (`find`, `grep`)

</details>

<details>
<summary><b>🌐 Jaringan &amp; Web</b></summary>

- Mengunduh file (`curl`, `wget`)
- Mengirim permintaan HTTP (GET, POST, PUT, DELETE)
- Mengelola koneksi jaringan
- Debugging masalah jaringan

</details>

<details>
<summary><b>💻 Pemrograman &amp; Skrip</b></summary>

- Menulis dan menjalankan skrip Python, Bash, JavaScript
- Debugging kode
- Manajemen dependensi (`pip`, `npm`, `apt`)

</details>

<details>
<summary><b>🗄️ Database</b></summary>

- Interaksi dengan database (MySQL, PostgreSQL, SQLite)
- Menjalankan query SQL
- Backup dan restore database

</details>

<details>
<summary><b>⏰ Otomasi &amp; Skeduling</b></summary>

- Membuat dan mengelola cron jobs
- Otomasi tugas berulang
- Monitoring sistem

</details>

<details>
<summary><b>🔐 Keamanan</b></summary>

- Manajemen pengguna dan grup
- Konfigurasi firewall (`iptables`, `ufw`)
- Audit log keamanan

</details>

<details>
<summary><b>🌐 Pengembangan Web</b></summary>

- Menjalankan server web (nginx, Apache)
- Manajemen container (Docker)
- Deployment aplikasi

</details>

<details>
<summary><b>📊 Analisis Data</b></summary>

- Pemrosesan data (`awk`, `sed`, `sort`)
- Visualisasi data dasar
- Analisis log

</details>

<details>
<summary><b>📝 Dokumentasi</b></summary>

- Membuat dan mengelola file Markdown
- Dokumentasi proyek
- Penulisan laporan

</details>

---

## Persyaratan

- **Python 3.9+** (diuji pada Python 3.12)
- **Endpoint LLM** yang mendukung OpenAI Chat Completions API
- **Koneksi internet** untuk instalasi dependensi

### Dependensi

```bash
pip install requests
```

## Instalasi

```bash
# 1. Clone repository
git clone <url-repository>.git
cd model

# 2. (Opsional) Buat virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Instal dependensi
pip install requests
```

## Cara Penggunaan

### 1. Konfigurasi Environment

Sarah Agent dikonfigurasi sepenuhnya melalui **environment variable**. API key tidak pernah ditulis di dalam kode.

| Variabel | Default | Keterangan |
| :--- | :--- | :--- |
| `API_URL` | `https://gateway.dahono.com/v1/chat/completions` | Endpoint chat completions |
| `API_KEY` | *(kosong)* | API key LLM — wajib diisi |
| `MODEL` | `dahono/auto` | Model yang digunakan |
| `MIN_LLM_INTERVAL` | `7` | Jeda minimum antar-request (detik) |
| `AGENT_MAX_TOKENS` | `600` | Batas token per respons (`0` = tanpa batas) |
| `TOKEN_BUDGET` | `0` | Batas total token per sesi (`0` = tanpa batas) |
| `MAX_OUTPUT_CHARS` | `4000` | Batas output command yang dikirim ke model |
| `SUMMARY_LONG_OUTPUT` | `false` | Aktifkan ringkasan untuk observasi panjang |
| `SUMMARY_MODEL` | *(kosong)* | Model khusus untuk ringkasan |

Contoh:

```bash
export API_URL="https://gateway.dahono.com/v1/chat/completions"
export API_KEY="sk-xxxxxxxxxxxxxxxx"
export MODEL="dahono/auto"
```

### 2. Menjalankan Agent

```bash
python3 agent.py
```

Jika variabel di atas belum diisi, Sarah Agent akan meminta nilainya secara interaktif:

```text
API URL > https://gateway.dahono.com/v1/chat/completions
API KEY > sk-xxxxxxxxxxxxxxxx
MODEL > dahono/auto
Prompt > Analisis pemakaian disk pada direktori home saya
```

### 3. Contoh Sesi

```text
$ python3 agent.py
Prompt > Temukan file log lebih besar dari 100MB, lalu tampilkan 10 baris terakhir

─── Langkah 1 ─────────────────────────────────────
Reason: Mencari file log berukuran lebih dari 100MB
$ find ~ -name "*.log" -size +100M
─── Output (0.4s) ─────────────────────────────────
/home/user/app/debug.log
/home/user/nginx/access.log
─── Selesai (returncode: 0) ───────────────────────
```

## Skill: `webfetch`

Repository ini menyertakan skill tambahan untuk mengambil dan membaca konten halaman web secara langsung.

```bash
python3 skills/webfetch.py <URL> [-f markdown|text|html] [--max-chars 6000] [--timeout 30]
```

| Argumen | Keterangan |
| :--- | :--- |
| `URL` | Alamat halaman yang akan diambil (wajib) |
| `-f`, `--format` | Format keluaran: `markdown` (default), `text`, atau `html` |
| `--max-chars` | Batas jumlah karakter yang ditampilkan (default `6000`) |
| `--timeout` | Batas waktu permintaan dalam detik (default `30`) |

Contoh:

```bash
python3 skills/webfetch.py https://example.com
python3 skills/webfetch.py https://github.com/rafixxp -f text --max-chars 3000
```

## Struktur Proyek

```text
.
├── agent.py          # Otak agen: loop Action–Observation, konfigurasi, laporan
├── logo.jpeg         # Logo proyek Sarah Agent
├── README.md         # Dokumentasi proyek
└── skills/
    └── webfetch.py   # Skill pengambilan konten web
```

## Cara Kerja

```text
        Prompt pengguna
               │
               ▼
      ┌─────────────────┐
      │     Planner     │  menghasilkan JSON:
      │    (LLM step)   │  { reason, command }
      └────────┬────────┘
               │ perintah
               ▼
      ┌─────────────────┐
      │    Eksekusi     │  subprocess + timeout
      │     (shell)     │
      └────────┬────────┘
               │ output + returncode
               ▼
      ┌─────────────────┐
      │   Observasi     │  kirim balik ke model
      └────────┬────────┘
               │ ulangi (maks. MAX_STEPS)
               ▼
      ┌─────────────────┐
      │ Laporan Akhir   │  transkrip langkah
      └─────────────────┘
```

1. **Planner** — model diminta menghasilkan JSON berisi alasan dan perintah yang akan dijalankan.
2. **Eksekusi** — perintah dijalankan melalui `subprocess` dengan batas waktu (`COMMAND_TIMEOUT`).
3. **Observasi** — output dan `returncode` dikirim kembali ke model sebagai konteks langkah berikutnya.
4. **Penjaga** — kondisi macet, perintah berulang, dan respons JSON rusak ditangani otomatis oleh guard internal.
5. **Laporan** — saat tugas selesai, transkrip langkah demi langkah dicetak.

## Konfigurasi Lanjutan

Agen sengaja dibuat **sederhana dan transparan**. Perilaku lanjutan dapat disesuaikan pada bagian `CONFIG` di `agent.py`:

| Konstanta | Nilai | Fungsi |
| :--- | :--- | :--- |
| `MAX_STEPS` | `150` | Batas maksimum langkah eksekusi |
| `MAX_REPEAT_ACTIONS` | `2` | Batas perintah identik berturut-turut |
| `MAX_STALLED_ATTEMPTS` | `4` | Batas percobaan "arah macet" |
| `MAX_CONSECUTIVE_BAD_REPLIES` | `6` | Batas respons JSON rusak |
| `COMMAND_TIMEOUT` | `120` | Timeout eksekusi perintah (detik) |
| `REQUEST_TIMEOUT` | `120` | Timeout permintaan LLM (detik) |
| `MAX_RETRIES` | `8` | Maksimum retry untuk error sementara |
| `FINAL_REPORT` | `True` | Cetak laporan akhir saat selesai |

## Roadmap

- [ ] Antarmuka web (dashboard) untuk memantau sesi agen
- [ ] Dukungan multi-provider (OpenAI, Anthropic, Ollama)
- [ ] Mode *dry-run* untuk simulasi tanpa eksekusi
- [ ] Sandbox eksekusi perintah (container / user terbatas)
- [ ] Riwayat sesi persisten dan pencarian

<div align="center">
  <p><b>Sarah Agent</b> &mdash; autonomous Linux agent, Version 1.0.0</p>
</div>
