<div align="center">
  <img src="logo.png" alt="Sarah Agent" width="220">

  # Sarah Agent

  **Agen AI otonom untuk lingkungan Linux**

  ACTION &rarr; OBSERVATION loop &middot; Autonomous shell agent
</div>

---

## Deskripsi

**Sarah Agent** adalah agen AI otonom berbasis Python untuk tugas-tugas di Linux. Agen menerima satu tujuan, lalu menjalankan siklus **Action &rarr; Observation**: merancang langkah berikutnya, mengeksekusi perintah shell, membaca output, dan mengulangi sampai tujuan tercapai.

Seluruhnya *single-file* — cukup satu endpoint LLM yang dikonfigurasi lewat environment variable.

## Fitur

| Fitur | Keterangan |
| :--- | :--- |
| 🔁 Action–Observation Loop | `rencana → eksekusi → observasi → rencana berikutnya` otomatis |
| 🧠 Multi-step reasoning | hingga 150 langkah eksekusi per sesi tugas |
| 🛡️ Anti-loop protection | deteksi perintah berulang dan respons rusak |
| ⏱️ Rate limit & retry | throttle, exponential backoff, cooldown |
| 📉 Manajemen konteks | riwayat dipangkas, token budget opsional |
| 📄 Laporan akhir | transkrip langkah dicetak saat selesai |

## Kemampuan

<details open>
<summary><b>🖥️ Sistem & Shell</b></summary>

- Perintah shell (`bash`, `sh`), proses, dan layanan (`systemctl`)
- Manajemen file, direktori, izin (`chmod`, `chown`), pencarian (`find`, `grep`)

</details>

<details>
<summary><b>🌐 Jaringan &amp; Web</b></summary>

- Unduh file (`curl`, `wget`) dan permintaan HTTP (GET/POST/PUT/DELETE)
- Menjalankan server web (nginx, Apache) dan container (Docker)

</details>

<details>
<summary><b>💻 Kode &amp; Data</b></summary>

- Menulis & menjalankan skrip (Python, Bash, JavaScript), termasuk `pip`/`npm`/`apt`
- Database (MySQL, PostgreSQL, SQLite), query SQL, backup
- Pemrosesan data (`awk`, `sed`, `sort`) dan analisis log

</details>

<details>
<summary><b>🔐 Keamanan &amp; Otomasi</b></summary>

- Manajemen user/grup, firewall (`iptables`, `ufw`), audit log
- Cron jobs, monitoring sistem, penulisan dokumentasi Markdown

</details>

## Persyaratan

- **Python 3.9+** (diuji pada 3.12)
- Endpoint LLM yang mendukung OpenAI Chat Completions API

```bash
pip install requests
```

## Instalasi

```bash
git clone <url-repository>.git
cd model
pip install requests
```

## Konfigurasi

Semua perilaku diatur lewat environment variable — API key tidak pernah ditulis di kode.

| Variabel | Default | Keterangan |
| :--- | :--- | :--- |
| `API_URL` | `https://gateway.dahono.com/v1/chat/completions` | Endpoint chat completions |
| `API_KEY` | *(kosong)* | API key LLM — wajib diisi |
| `MODEL` | `dahono/auto` | Model yang digunakan |
| `MIN_LLM_INTERVAL` | `7` | Jeda minimum antar-request (detik) |
| `AGENT_MAX_TOKENS` | `600` | Batas token per respons (`0` = tanpa batas) |
| `TOKEN_BUDGET` | `0` | Batas total token per sesi (`0` = tanpa batas) |
| `MAX_OUTPUT_CHARS` | `4000` | Batas output command yang dikirim ke model |
| `SUMMARY_LONG_OUTPUT` | `false` | Ringkasan otomatis untuk observasi panjang |
| `SUMMARY_MODEL` | *(kosong)* | Model khusus untuk ringkasan |

```bash
export API_URL="https://gateway.dahono.com/v1/chat/completions"
export API_KEY="sk-xxxxxxxxxxxxxxxx"
export MODEL="dahono/auto"
```

## Penggunaan

```bash
python3 agent.py
```

Jika variabel di atas belum diisi, nilainya akan diminta secara interaktif:

```text
API URL > https://gateway.dahono.com/v1/chat/completions
API KEY > sk-xxxxxxxxxxxxxxxx
MODEL > dahono/auto
Prompt > Analisis pemakaian disk pada direktori home saya
```

Contoh sesi:

```text
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

Mengambil dan membaca konten halaman web langsung.

```bash
python3 skills/webfetch.py <URL> [-f markdown|text|html] [--max-chars 6000] [--timeout 30]
```

| Argumen | Keterangan |
| :--- | :--- |
| `URL` | Alamat halaman (wajib) |
| `-f`, `--format` | `markdown` (default), `text`, atau `html` |
| `--max-chars` | Batas karakter keluaran (default `6000`) |
| `--timeout` | Batas waktu permintaan (default `30`) |

## Cara Kerja

1. **Planner** — LLM menghasilkan JSON berisi alasan dan perintah.
2. **Eksekusi** — perintah dijalankan via `subprocess` dengan timeout.
3. **Observasi** — output + `returncode` dikirim kembali sebagai konteks langkah berikutnya.
4. **Penjaga** — kondisi macet dan JSON rusak ditangani guard internal.
5. **Laporan** — transkrip langkah demi langkah dicetak saat selesai.

## Struktur Proyek

```text
.
├── agent.py          # loop Action–Observation, konfigurasi, laporan
├── logo.png          # logo proyek (rounded)
├── README.md
└── skills/
    └── webfetch.py   # skill pengambilan konten web
```

## Tuning Lanjutan

Nilai constant berikut dapat diubah di bagian `CONFIG` pada `agent.py`:

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

---

<div align="center">
  <p><b>Sarah Agent</b> &mdash; autonomous Linux agent, Version 1.0.0</p>
</div>
