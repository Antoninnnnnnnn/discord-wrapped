# Discord Wrapped — Tableau de bord local

> 🇬🇧 [Read in English](README.md)

Un tableau de bord **autonome et respectueux de la vie privée** qui transforme
ton export Discord **« Demander mes données »** en un rapport interactif —
ton propre *Discord Wrapped*, généré entièrement sur ta machine.

Aucune donnée ne quitte ton ordinateur. L'analyseur utilise **uniquement la
bibliothèque standard de Python** (aucun paquet externe), et le rapport est un
simple fichier HTML que tu ouvres dans n'importe quel navigateur.

---

## ✨ Fonctionnalités

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

## 📦 Prérequis

- Python **3.9 ou plus récent**
- Un export de données Discord (voir ci-dessous)

## 📥 Récupérer tes données Discord

1. Ouvre Discord → **Paramètres → Données et confidentialité**.
2. Clique sur **Demander toutes mes données** et valide la demande.
3. Discord t'envoie un lien de téléchargement par e-mail (de quelques heures à
   ~30 jours).
4. Télécharge et **décompresse** l'archive. Tu obtiens un dossier contenant
   `messages/`, `account/`, `servers/`, etc.

## 🚀 Utilisation

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

### Re-générer sans re-analyser

Si tu as seulement modifié le template HTML, régénère le rapport à partir du
`data.json` existant (instantané) :

```bash
python render.py
```

## 🔒 Confidentialité

- Tout s'exécute **en local**. Rien n'est envoyé nulle part.
- Le dossier `rapport/` généré contient **tes données personnelles** et est
  exclu du versionnage via `.gitignore`. **Ne le commite jamais.**

## 📁 Structure du projet

```
analyze.py         # Analyseur : export -> rapport/data.json + rapport.html
render.py          # Génère le dashboard HTML depuis data.json
favicons/          # Icônes utilisées par le dashboard
requirements.txt   # (aucune dépendance externe)
```

## 📝 Licence

[MIT](LICENSE)
