# Discord Data Recap

A self-contained, privacy-friendly dashboard that turns your personal
**"Request my Data"** Discord export into a beautiful interactive report —
think *Discord Wrapped*, but generated entirely on your own machine.

No data ever leaves your computer. The analyzer uses the **Python standard
library only** (no third-party packages), and the report is a single HTML file
you open in any browser.

> 🇬🇧 English below &nbsp;·&nbsp; 🇫🇷 [Version française plus bas](#-français)

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
# 1. Place the unzipped export folder next to the scripts (auto-detected),
#    OR pass its path explicitly.

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

---

## 🇫🇷 Français

Un tableau de bord **autonome et respectueux de la vie privée** qui transforme
ton export Discord **« Demander mes données »** en un rapport interactif —
un peu comme un *Discord Wrapped*, mais généré entièrement sur ta machine.

Aucune donnée ne quitte ton ordinateur. L'analyseur utilise **uniquement la
bibliothèque standard de Python** (aucun paquet externe), et le rapport est un
simple fichier HTML que tu ouvres dans n'importe quel navigateur.

### ✨ Fonctionnalités

- **12 onglets thématiques** : Vue d'ensemble, Records, Messages, Personnes,
  Temps, Mots, Activité, Appareils, Géographie, Compte, Serveurs, Pubs.
- **Visualisations riches** avec Chart.js : courbes, barres, anneaux, une
  **heatmap** heure × jour, et un **calendrier de contributions** façon GitHub.
- **Statistiques clés** : messages totaux, mots écrits, plus longue série,
  jour le plus actif, top serveurs, top DMs, mots & emojis les plus utilisés,
  heures de pointe, appareils, villes…
- **Interface bilingue** : bascule **FR / EN** à tout moment (ton choix est
  mémorisé).
- **100 % local et hors-ligne** — ton export est lu sur ta machine, et le
  rapport est un unique fichier `rapport.html`.
- **Sans dépendances** : Python 3.9+, bibliothèque standard uniquement.

### 📦 Prérequis

- Python **3.9 ou plus récent**
- Un export de données Discord (voir ci-dessous)

### 📥 Récupérer tes données Discord

1. Ouvre Discord → **Paramètres → Données et confidentialité**.
2. Clique sur **Demander toutes mes données** et valide la demande.
3. Discord t'envoie un lien de téléchargement par e-mail (de quelques heures à
   ~30 jours).
4. Télécharge et **décompresse** l'archive. Tu obtiens un dossier contenant
   `messages/`, `account/`, `servers/`, etc.

### 🚀 Utilisation

```bash
# Détection automatique d'un dossier d'export à côté du script :
python analyze.py

# Ou indique le chemin de ton export :
python analyze.py "/chemin/vers/ton/export/discord"

# Optionnel : choisir le dossier de sortie (défaut : ./rapport)
python analyze.py "/chemin/vers/export" -o ./mon_rapport
```

Cela génère :

- `rapport/data.json` — les statistiques calculées
- `rapport/rapport.html` — le tableau de bord interactif

Ouvre `rapport/rapport.html` dans ton navigateur. 🎉

#### Re-générer sans re-analyser

Si tu as seulement modifié le template HTML, régénère le rapport à partir du
`data.json` existant (instantané) :

```bash
python render.py
```

### 🔒 Confidentialité

- Tout s'exécute **en local**. Rien n'est envoyé nulle part.
- Le dossier `rapport/` généré contient **tes données personnelles** et est
  exclu du versionnage via `.gitignore`. **Ne le commite jamais.**

### 📝 Licence

[MIT](LICENSE)
