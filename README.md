# Discord Wrapped — Local Dashboard

> 🇫🇷 [Lire en français](README.fr.md)

A self-contained, privacy-friendly dashboard that turns your personal
**"Request my Data"** Discord export into a beautiful interactive report —
your own *Discord Wrapped*, generated entirely on your machine.

No data ever leaves your computer. The analyzer uses the **Python standard
library only** (no third-party packages), and the report is a single HTML file
you open in any browser.

---

## ✨ Features

- **12 themed tabs**: Overview, Records, Messages, People, Time, Words,
  Activity, Devices, Geography, Account, Servers, Ads.
- **Rich visualizations** powered by Chart.js: line/bar/doughnut charts, an
  hourly × weekday **heatmap**, and a GitHub-style **contribution calendar**.
- **Key stats**: total messages, words written, longest streak, busiest day,
  top servers, top DMs, most used words & emojis, peak hours, devices, cities…
- **Bilingual UI**: switch between **FR / EN** at any time (your choice is
  remembered).
- **100% local & offline-friendly** — your export is read on your machine, and
  the dashboard is a single self-contained `rapport.html`.
- **No dependencies**: pure Python 3.9+ standard library.

## 📦 Requirements

- Python **3.9 or newer**
- A Discord data export (see below)

## 📥 Getting your Discord data

1. Open Discord → **User Settings → Data & Privacy**.
2. Click **Request all of my Data** and submit the request.
3. Discord emails you a download link (it can take a few hours to ~30 days).
4. Download and **unzip** the archive. You should get a folder containing
   `messages/`, `account/`, `servers/`, etc.

## 🚀 Usage

```bash
# Auto-detect an export folder next to the script:
python analyze.py

# Or point to your export folder:
python analyze.py "/path/to/your/discord/export"

# Optional: choose the output directory (default: ./rapport)
python analyze.py "/path/to/export" -o ./my_report
```

This generates:

- `rapport/data.json` — the computed statistics
- `rapport/rapport.html` — the interactive dashboard

Open `rapport/rapport.html` in your browser and enjoy. 🎉

### Re-rendering without re-analyzing

If you only tweaked the HTML template, regenerate the report from the existing
`data.json` (instant):

```bash
python render.py
```

## 🔒 Privacy

- Everything runs **locally**. Nothing is uploaded anywhere.
- The generated `rapport/` folder contains **your personal data** and is
  excluded from version control via `.gitignore`. **Never commit it.**

## 📁 Project structure

```
analyze.py         # Streaming analyzer: export -> rapport/data.json + rapport.html
render.py          # Builds the self-contained HTML dashboard from data.json
favicons/          # Icon set used by the dashboard
requirements.txt   # (no third-party dependencies)
```

## 📝 License

[MIT](LICENSE)
