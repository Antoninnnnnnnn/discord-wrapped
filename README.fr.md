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
# Lance le menu interactif :
python analyze.py

# Mode direct : indique le chemin de ton export :
python analyze.py "/chemin/vers/ton/export/discord"

# Optionnel : choisir le dossier de sortie exact
python analyze.py "/chemin/vers/export" -o ./mon_rapport
```

Sans `-o`, chaque analyse crée automatiquement un dossier prévisible dans
`rapports/`, par exemple :

```text
rapports/discord_2026-06-10_0024_mesdonneesdiscord/
```

Cela génère :

- `data.json` — les statistiques calculées
- `rapport.html` — le tableau de bord interactif

Le script affiche le chemin complet du rapport à la fin et peut te proposer de
l'ouvrir automatiquement depuis le menu interactif. 🎉

### Re-générer sans re-analyser

Si tu as seulement modifié le template HTML, régénère le rapport à partir du
`data.json` existant (instantané) :

```bash
# Régénère le dernier rapport trouvé dans ./rapports/
python render.py

# Ou régénère un rapport précis
python render.py "./rapports/discord_2026-06-10_0024_mesdonneesdiscord"
```

## 🔒 Confidentialité

- Tout s'exécute **en local**. Rien n'est envoyé nulle part.
- Les dossiers `rapport/` et `rapports/` générés contiennent **tes données personnelles** et sont
  exclus du versionnage via `.gitignore`. **Ne les commite jamais.**

## 📁 Structure du projet

```
analyze.py         # Analyseur : export -> rapport/data.json + rapport.html
render.py          # Génère le dashboard HTML depuis data.json
favicons/          # Icônes utilisées par le dashboard
requirements.txt   # (aucune dépendance externe)
```

## 📝 Licence

[MIT](LICENSE)

---

> 🤖 **Soyons honnêtes :** ce projet a été fait par [@Antoninnnnnnnn](https://github.com/Antoninnnnnnnn) qui admet volontiers ne comprendre aucune ligne de ce code. Le vrai MVP ici c'est la programmation en duo avec une IA. Apparemment, pas besoin de savoir coder pour shipper du code. Bienvenue en 2026.
