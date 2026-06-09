# -*- coding: utf-8 -*-
"""
Analyseur COMPLET d'un paquet de données Discord.
Produit un fichier rapport/data.json + rapport/rapport.html (dashboard interactif).

Usage:
    python analyze.py [chemin_du_paquet] [-o dossier_sortie]

Si aucun chemin n'est fourni, le script cherche automatiquement un dossier
d'export Discord à côté du script (voir NOMS_EXPORT_PROBABLES).

Compatible Python 3.9+ (bibliothèque standard uniquement).
"""
import os
import sys
import re
import json
import glob
import argparse
import collections
import unicodedata
from datetime import datetime, timezone

# --------------------------------------------------------------------------- #
#  Configuration des chemins
# --------------------------------------------------------------------------- #
HERE = os.path.dirname(os.path.abspath(__file__))

# Noms de dossiers d'export Discord recherchés automatiquement (par défaut),
# à la fois à côté du script et dans son dossier parent.
NOMS_EXPORT_PROBABLES = (
    "mesdonnéesdiscord",
    "mesdonneesdiscord",
    "export",
    "package",
    "discord-data",
    "discord_data",
)

# Valeurs par défaut ; réellement déterminées dans main() via argparse.
PKG = None
OUT_DIR = os.path.join(HERE, "rapport")
REPORTS_DIR = os.path.join(HERE, "rapports")

# Discord epoch (snowflake) pour datation des IDs si besoin
DISCORD_EPOCH = 1420070400000


def looks_like_export(path):
    """Heuristique: un dossier ressemble à un export Discord s'il contient
    au moins un des sous-dossiers/fichiers caractéristiques."""
    if not path or not os.path.isdir(path):
        return False
    indices = ("Messages", "Compte", "Account", "Activité", "Activity", "Servers", "Serveurs")
    return any(os.path.exists(os.path.join(path, x)) for x in indices)


def find_default_pkg():
    """Cherche un dossier d'export Discord à côté du script puis dans le CWD.
    Renvoie le chemin trouvé ou None."""
    bases = [HERE, os.path.dirname(HERE), os.getcwd()]
    seen = set()
    for base in bases:
        for nom in NOMS_EXPORT_PROBABLES:
            cand = os.path.join(base, nom)
            if cand in seen:
                continue
            seen.add(cand)
            if looks_like_export(cand):
                return os.path.abspath(cand)
    # Dernier recours: un dossier voisin qui ressemble à un export.
    for base in bases:
        if not os.path.isdir(base):
            continue
        try:
            for nom in sorted(os.listdir(base)):
                cand = os.path.join(base, nom)
                if cand not in seen and looks_like_export(cand):
                    return os.path.abspath(cand)
        except OSError:
            pass
    return None


def clean_user_path(raw):
    """Nettoie un chemin collé dans le terminal (guillemets, espaces, ~, vars)."""
    if raw is None:
        return ""
    path = str(raw).strip()
    if path.startswith("& "):
        path = path[2:].strip()
    if (len(path) >= 2 and path[0] == path[-1] and path[0] in ("'", '"')):
        path = path[1:-1].strip()
    path = os.path.expandvars(os.path.expanduser(path))
    return path


def explain_export_problem(path):
    """Retourne un message clair quand le chemin fourni n'est pas exploitable."""
    if not path:
        return "Aucun chemin fourni."
    if path.lower().endswith(".zip"):
        return (
            "Tu as fourni une archive .zip. Décompresse-la d'abord, puis choisis "
            "le dossier obtenu."
        )
    if not os.path.exists(path):
        return "Ce chemin n'existe pas."
    if not os.path.isdir(path):
        return "Ce chemin existe, mais ce n'est pas un dossier."
    return (
        "Ce dossier ne ressemble pas à un export Discord. Il doit contenir au "
        "moins un dossier comme Messages, Compte/Account, Activité/Activity ou "
        "Serveurs/Servers."
    )


def validate_export_path(path):
    """Normalise et valide un dossier d'export Discord."""
    cleaned = clean_user_path(path)
    if not cleaned:
        raise ValueError(explain_export_problem(cleaned))
    path = os.path.abspath(cleaned)
    if looks_like_export(path):
        return path
    raise ValueError(explain_export_problem(path))


def slugify_name(name):
    """Transforme un nom de dossier en morceau de chemin prévisible."""
    text = unicodedata.normalize("NFKD", str(name or "export"))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return (text or "export")[:50].strip("-") or "export"


def unique_path(base_path):
    """Renvoie base_path, ou base_path_02/_03... si le dossier existe déjà."""
    if not os.path.exists(base_path):
        return base_path
    idx = 2
    while True:
        candidate = f"{base_path}_{idx:02d}"
        if not os.path.exists(candidate):
            return candidate
        idx += 1


def make_default_output_dir(export_path):
    """Crée le nom de sortie par défaut sans l'écrire sur disque."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    export_name = slugify_name(os.path.basename(os.path.normpath(export_path)))
    return unique_path(os.path.join(REPORTS_DIR, f"discord_{stamp}_{export_name}"))


def ask_yes_no(prompt, default=False):
    suffix = "O/n" if default else "o/N"
    while True:
        answer = input(f"{prompt} [{suffix}] ").strip().lower()
        if not answer:
            return default
        if answer in ("o", "oui", "y", "yes"):
            return True
        if answer in ("n", "non", "no"):
            return False
        log("Réponds par oui ou non.")


def open_in_browser(html_path):
    """Ouvre le rapport dans le navigateur par défaut."""
    from pathlib import Path
    import webbrowser
    return webbrowser.open(Path(html_path).resolve().as_uri())


MSG_INTROUVABLE = (
    "ERREUR: impossible de trouver le dossier d'export Discord.\n\n"
    "Comment obtenir tes données Discord :\n"
    "  1. Discord > Paramètres > Confidentialité et sécurité > "
    "« Demander toutes mes données ».\n"
    "  2. Tu recevras par e-mail un fichier .zip (« package »).\n"
    "  3. Décompresse-le.\n\n"
    "Place ensuite le dossier décompressé à côté de ce script "
    "(par ex. nomme-le « export » ou « mesdonnéesdiscord »), "
    "ou indique son chemin explicitement :\n"
    "    python analyze.py /chemin/vers/mon/export\n"
)


def log(msg):
    print(msg, flush=True)


def snowflake_to_dt(sid):
    try:
        sid = int(sid)
        ms = (sid >> 22) + DISCORD_EPOCH
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    except Exception:
        return None


# --------------------------------------------------------------------------- #
#  Stopwords (FR + EN) pour l'analyse de mots
# --------------------------------------------------------------------------- #
STOPWORDS = set("""
au aux avec ce ces dans de des du elle en et eux il ils je la le les leur lui ma mais
me même mes moi mon ne nos notre nous on ou où par pas pour qu que qui sa se ses son sur
ta te tes toi ton tu un une vos votre vous c d j l à m n s t y été étée étées étés étant
suis es est sommes êtes sont serai seras sera serons serez seront étais était étions
étiez étaient ai as avons avez ont aurai auras aura aurons aurez auront avais avait avions
aviez avaient eu eus eut eûmes eûtes eurent fais fait faisons faites font ça cette cet
mes tes ses nos vos leurs comme plus moins très bien aussi alors donc car si oui non
ok okay ya yo wsh wesh bah ben ouais nan jsuis jai cest cmt jpp mdr ptdr lol xd the to of
and a in is it you that he was for on are with as i his they be at one have this from or
had by hot but some what there we can out other were all your when up use word how said
an each she which do their time if will way about many then them would these so my get
me no thats just got dont im like yeah ah oh hey vraiment trop déjà fait faire faut peux
peut être avoir tout tous toute toutes rien quoi quand chez sans sous entre vers depuis
""".split())

URL_RE = re.compile(r'https?://[^\s<>"\')]+', re.IGNORECASE)
CUSTOM_EMOJI_RE = re.compile(r'<a?:(\w+):(\d+)>')
MENTION_RE = re.compile(r'<@!?(\d+)>')
WORD_RE = re.compile(r"[a-zàâäéèêëïîôöùûüÿçœæ]+", re.IGNORECASE)
# Plage unicode emoji (approx, large)
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u2700-\u27bf\u2600-\u26ff]",
    flags=re.UNICODE,
)


def parse_ts(s):
    """Parse divers formats de timestamps Discord -> datetime aware (UTC)."""
    if not s:
        return None
    if not isinstance(s, str):
        s = str(s)
    # certains champs d'événements sont des chaînes JSON doublement encodées
    # ex: '"2025-07-22T10:07:51Z"' -> on retire les guillemets / espaces
    s = s.strip().strip('"').strip()
    if not s:
        return None
    try:
        # format messages.json: "2024-07-20 12:59:22"
        if " " in s and "T" not in s:
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        # ISO 8601 (events) ex "2025-07-06T17:24:03.426+02:00"
        ss = s.replace("Z", "+00:00")
        return datetime.fromisoformat(ss)
    except Exception:
        try:
            return datetime.fromisoformat(s[:19])
        except Exception:
            return None


# =========================================================================== #
#  1. MESSAGES
# =========================================================================== #
def analyze_messages(pkg):
    log(">> Analyse des messages…")
    msg_dir = os.path.join(pkg, "Messages")
    index_path = os.path.join(msg_dir, "index.json")
    index = {}
    if os.path.exists(index_path):
        try:
            with open(index_path, encoding="utf-8", errors="ignore") as f:
                index = json.load(f)
        except Exception as e:
            log(f"   ! index.json illisible ({e}); les noms de salons seront 'Unknown'")
            index = {}

    R = {
        "total_messages": 0,
        "total_chars": 0,
        "total_words": 0,        # mots significatifs (>=3 lettres, hors stopwords)
        "total_words_raw": 0,    # tous les mots écrits (KPI "mots écrits")
        "total_attachments": 0,
        "total_links": 0,
        "total_mentions": 0,
        "total_custom_emojis": 0,
        "total_unicode_emojis": 0,
        "edited_or_empty": 0,
        "by_year": collections.Counter(),
        "by_month": collections.Counter(),   # YYYY-MM
        "by_weekday": collections.Counter(),  # 0=lundi
        "by_hour": collections.Counter(),
        "by_date": collections.Counter(),     # YYYY-MM-DD
        "heatmap": collections.Counter(),     # (weekday, hour)
        "words": collections.Counter(),
        "custom_emojis": collections.Counter(),
        "unicode_emojis": collections.Counter(),
        "domains": collections.Counter(),
        "channel_type": collections.Counter(),
        "per_channel": [],         # liste de dicts
        "per_server": collections.Counter(),  # serveur -> nb messages
        "dm_counter": collections.Counter(),  # nom DM -> nb messages
        "first_ts": None,
        "last_ts": None,
        "msg_lengths": [],         # pour distribution / moyenne (échantillonné)
        # --- analyses enrichies ---
        "length_buckets": collections.Counter(),  # tranche de longueur -> nb
        "msgs_with_link": 0,
        "msgs_with_attachment": 0,
        "msgs_with_mention": 0,
        "msgs_with_emoji": 0,
        "msgs_pure_text": 0,
        "msgs_empty": 0,
        "night_msgs": 0,        # messages entre 0h et 5h59
        "laugh_msgs": 0,        # messages contenant un rire (mdr/ptdr/lol/😂…)
        "question_msgs": 0,     # messages contenant '?'
        "exclaim_msgs": 0,      # messages contenant '!'
        "caps_msgs": 0,         # messages majoritairement en MAJUSCULES
        "longest_msg": {"len": 0, "text": ""},
        "dm_by_month": {},      # nom DM -> Counter(YYYY-MM)
    }

    channel_dirs = [d for d in glob.glob(os.path.join(msg_dir, "c*")) if os.path.isdir(d)]
    log(f"   {len(channel_dirs)} salons trouvés")

    for cdir in channel_dirs:
        cid = os.path.basename(cdir).lstrip("c")
        ch_path = os.path.join(cdir, "channel.json")
        msgs_path = os.path.join(cdir, "messages.json")
        if not os.path.exists(msgs_path):
            continue
        ctype = "UNKNOWN"
        if os.path.exists(ch_path):
            try:
                with open(ch_path, encoding="utf-8") as f:
                    cj = json.load(f)
                ctype = cj.get("type", "UNKNOWN")
            except Exception:
                pass

        label = index.get(cid, index.get(str(cid), "Unknown"))
        # Déterminer serveur / DM à partir du label
        server_name = None
        is_dm = label.startswith("Direct Message with") or ctype in ("DM", "GROUP_DM")
        if " in " in label and not is_dm:
            server_name = label.rsplit(" in ", 1)[-1].strip()

        try:
            with open(msgs_path, encoding="utf-8") as f:
                msgs = json.load(f)
        except Exception:
            continue

        ch_count = len(msgs)
        if ch_count == 0:
            continue
        R["channel_type"][ctype] += ch_count
        R["total_messages"] += ch_count

        ch_chars = 0
        ch_first = None
        ch_last = None
        for m in msgs:
            content = m.get("Contents", "") or ""
            ts = parse_ts(m.get("Timestamp"))
            atts = m.get("Attachments", "") or ""

            clen = len(content)
            ch_chars += clen
            R["total_chars"] += clen

            # composition du message
            has_att = bool(atts.strip())
            if has_att:
                R["total_attachments"] += atts.count("http") if "http" in atts else 1
                R["msgs_with_attachment"] += 1

            # histogramme de longueur
            if clen == 0:
                R["msgs_empty"] += 1
                bucket = "0 (vide)"
            elif clen <= 10:
                bucket = "1-10"
            elif clen <= 50:
                bucket = "11-50"
            elif clen <= 100:
                bucket = "51-100"
            elif clen <= 300:
                bucket = "101-300"
            else:
                bucket = "300+"
            R["length_buckets"][bucket] += 1
            if clen > R["longest_msg"]["len"]:
                R["longest_msg"] = {"len": clen, "text": content[:280]}

            # liens / domaines
            urls = URL_RE.findall(content)
            if urls:
                R["msgs_with_link"] += 1
            for url in urls:
                R["total_links"] += 1
                try:
                    dom = re.sub(r"^www\.", "", url.split("/")[2].lower())
                    R["domains"][dom] += 1
                except Exception:
                    pass
            # mentions
            n_ment = len(MENTION_RE.findall(content))
            R["total_mentions"] += n_ment
            if n_ment:
                R["msgs_with_mention"] += 1
            # emojis custom
            n_emo = 0
            for name, eid in CUSTOM_EMOJI_RE.findall(content):
                R["custom_emojis"][name] += 1
                R["total_custom_emojis"] += 1
                n_emo += 1
            # emojis unicode
            for e in EMOJI_RE.findall(content):
                R["unicode_emojis"][e] += 1
                R["total_unicode_emojis"] += 1
                n_emo += 1
            if n_emo:
                R["msgs_with_emoji"] += 1
            if clen and not (urls or has_att or n_ment or n_emo):
                R["msgs_pure_text"] += 1

            # ton / expressions
            low = content.lower()
            if ("mdr" in low or "ptdr" in low or "lol" in low or "xptdr" in low
                    or "\U0001F602" in content or "\U0001F923" in content):
                R["laugh_msgs"] += 1
            if "?" in content:
                R["question_msgs"] += 1
            if "!" in content:
                R["exclaim_msgs"] += 1
            letters = [c for c in content if c.isalpha()]
            if len(letters) >= 5 and sum(1 for c in letters if c.isupper()) / len(letters) > 0.7:
                R["caps_msgs"] += 1
            # mots
            clean = CUSTOM_EMOJI_RE.sub(" ", content)
            clean = URL_RE.sub(" ", clean)
            clean = MENTION_RE.sub(" ", clean)
            seen_words = set()
            for w in WORD_RE.findall(clean.lower()):
                R["total_words_raw"] += 1   # vrai total de mots écrits (KPI)
                if len(w) >= 3 and w not in STOPWORDS:
                    R["total_words"] += 1   # mots significatifs (pour le classement)
                    seen_words.add(w)
            # classement: chaque mot compté une seule fois par message
            # (évite qu'un message "spam spam spam…" fausse le top)
            for w in seen_words:
                R["words"][w] += 1
            if len(R["msg_lengths"]) < 200000:
                R["msg_lengths"].append(len(content))

            if ts:
                R["by_year"][ts.year] += 1
                R["by_month"][f"{ts.year:04d}-{ts.month:02d}"] += 1
                R["by_weekday"][ts.weekday()] += 1
                R["by_hour"][ts.hour] += 1
                R["by_date"][ts.strftime("%Y-%m-%d")] += 1
                R["heatmap"][(ts.weekday(), ts.hour)] += 1
                if ts.hour <= 5:
                    R["night_msgs"] += 1
                if R["first_ts"] is None or ts < R["first_ts"]:
                    R["first_ts"] = ts
                if R["last_ts"] is None or ts > R["last_ts"]:
                    R["last_ts"] = ts
                if ch_first is None or ts < ch_first:
                    ch_first = ts
                if ch_last is None or ts > ch_last:
                    ch_last = ts

        R["per_channel"].append({
            "id": cid,
            "label": label,
            "type": ctype,
            "server": server_name,
            "is_dm": is_dm,
            "count": ch_count,
            "chars": ch_chars,
            "first": ch_first.isoformat() if ch_first else None,
            "last": ch_last.isoformat() if ch_last else None,
        })
        if is_dm:
            name = label.replace("Direct Message with", "").strip() or "Inconnu"
            R["dm_counter"][name] += ch_count
        elif server_name:
            R["per_server"][server_name] += ch_count

    return R


# =========================================================================== #
#  2. ÉVÉNEMENTS ANALYTICS (dédupliqués par event_id)
# =========================================================================== #
VOICE_TYPES = {
    "voice_channel_join", "voice_channel_leave", "voice_connection_success",
    "voice_disconnect", "join_voice_channel", "leave_voice_channel",
    "call_started", "call_ended", "ring", "join_call", "leave_call",
}


def analyze_events(pkg):
    log(">> Analyse des événements (Activité)… (peut prendre 1-2 min)")
    act_dir = os.path.join(pkg, "Activité")
    files = glob.glob(os.path.join(act_dir, "*", "*.json"))

    seen = set()  # dedup global par event_id
    E = {
        "total_events": 0,
        "unique_events": 0,
        "event_types": collections.Counter(),
        "by_date": collections.Counter(),
        "by_hour": collections.Counter(),
        "by_weekday": collections.Counter(),
        "by_month": collections.Counter(),
        "heatmap": collections.Counter(),
        "os": collections.Counter(),
        "device": collections.Counter(),
        "browser": collections.Counter(),
        "client_version": collections.Counter(),
        "release_channel": collections.Counter(),
        "city": collections.Counter(),
        "country": collections.Counter(),
        "region": collections.Counter(),
        "isp": collections.Counter(),
        "timezone": collections.Counter(),
        "geo_first_last": {},     # "Ville, Pays" -> [first, last]
        "reactions": collections.Counter(),
        "session_count": 0,
        "active_buckets": set(),  # tranches de 10 min avec activité
        "notif_received": 0,
        "notif_clicked": 0,
        "messages_edited": 0,
        "messages_deleted": 0,
        "experiments": set(),
        "app_opens": 0,
        "logins": 0,
        "guild_joined": 0,
        "searches": 0,
        "ad_decisions": 0,
        "net_bytes": 0,
        "cpu_samples": [],
        "mem_samples": [],
        "first_ts": None,
        "last_ts": None,
        "screens": collections.Counter(),
        "voice_events": 0,
        "locale": collections.Counter(),
        "net_by_month": collections.Counter(),  # YYYY-MM -> octets
        "reactions_removed": 0,
    }

    n_lines = 0
    for fp in files:
        with open(fp, encoding="utf-8", errors="ignore") as f:
            for line in f:
                n_lines += 1
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                eid = ev.get("event_id")
                if eid is not None:
                    if eid in seen:
                        continue
                    seen.add(eid)
                E["unique_events"] += 1

                et = ev.get("event_type", "?")
                E["event_types"][et] += 1

                # timestamp: champ 'timestamp' / 'client_track_timestamp' (ISO)
                ts = parse_ts(ev.get("timestamp") or ev.get("client_track_timestamp")
                              or ev.get("_day_utc"))
                if ts is not None and ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)

                if ts:
                    dkey = ts.strftime("%Y-%m-%d")
                    E["by_date"][dkey] += 1
                    E["by_hour"][ts.hour] += 1
                    E["by_weekday"][ts.weekday()] += 1
                    E["by_month"][f"{ts.year:04d}-{ts.month:02d}"] += 1
                    E["heatmap"][(ts.weekday(), ts.hour)] += 1
                    secs = ts.timestamp()
                    E["active_buckets"].add(int(secs // 600))
                    if E["first_ts"] is None or ts < E["first_ts"]:
                        E["first_ts"] = ts
                    if E["last_ts"] is None or ts > E["last_ts"]:
                        E["last_ts"] = ts

                # device / client
                if ev.get("os"):
                    E["os"][ev["os"]] += 1
                if ev.get("device"):
                    E["device"][ev["device"]] += 1
                if ev.get("browser"):
                    E["browser"][ev["browser"]] += 1
                if ev.get("client_version"):
                    E["client_version"][str(ev["client_version"])] += 1
                if ev.get("release_channel"):
                    E["release_channel"][ev["release_channel"]] += 1

                # géo
                city = ev.get("city")
                country = ev.get("country_code")
                if city:
                    E["city"][city] += 1
                if country:
                    E["country"][country] += 1
                if ev.get("region_code"):
                    E["region"][str(ev["region_code"])] += 1
                if ev.get("isp"):
                    E["isp"][ev["isp"]] += 1
                if ev.get("time_zone"):
                    E["timezone"][ev["time_zone"]] += 1
                if city and country:
                    key = f"{city}, {country}"
                    if ts:
                        rec = E["geo_first_last"].get(key)
                        iso = ts.strftime("%Y-%m-%d")
                        if rec is None:
                            E["geo_first_last"][key] = [iso, iso]
                        else:
                            if iso < rec[0]:
                                rec[0] = iso
                            if iso > rec[1]:
                                rec[1] = iso

                # par type d'événement, métriques spécifiques
                # NB: une session émet à la fois session_start ET session_start_success.
                # On ne compte que session_start_success pour éviter de doubler le total.
                if et == "session_start_success":
                    E["session_count"] += 1
                elif et == "add_reaction":
                    emo = ev.get("emoji_name") or ev.get("emoji") or ev.get("name")
                    if emo:
                        E["reactions"][str(emo)] += 1
                elif et == "notification_request_received":
                    # vraies notifications reçues (les autres types sont des étapes
                    # internes du pipeline : published/sent/processed/canceled...)
                    E["notif_received"] += 1
                elif et in ("notification_clicked", "push_notification_clicked"):
                    E["notif_clicked"] += 1
                elif et == "message_edited":
                    E["messages_edited"] += 1
                elif et == "message_deleted":
                    E["messages_deleted"] += 1
                elif et.startswith("experiment_"):
                    name = ev.get("experiment_name") or ev.get("name")
                    if name:
                        E["experiments"].add(str(name))
                elif et in ("app_opened", "app_launched"):
                    E["app_opens"] += 1
                elif et in ("login_successful", "login_success"):
                    E["logins"] += 1
                elif et in ("guild_joined", "join_guild", "guild_joined_pending"):
                    E["guild_joined"] += 1
                elif et in ("search_started", "search_results_viewed", "guild_search"):
                    E["searches"] += 1
                elif et.startswith("ad_decision"):
                    E["ad_decisions"] += 1
                elif et == "app_network_usage":
                    nb = 0
                    for k in ("total_receive_bytes", "total_send_bytes"):
                        try:
                            nb += int(ev.get(k) or 0)
                        except Exception:
                            pass
                    E["net_bytes"] += nb
                    if ts and nb:
                        E["net_by_month"][f"{ts.year:04d}-{ts.month:02d}"] += nb
                elif et == "remove_reaction":
                    E["reactions_removed"] += 1
                elif et == "app_ui_viewed":
                    sn = ev.get("screen_name") or ev.get("screen")
                    if sn:
                        E["screens"][str(sn)] += 1
                if et in VOICE_TYPES or "voice" in et:
                    E["voice_events"] += 1

                # langue (locale)
                loc = ev.get("chosen_locale") or ev.get("detected_locale") or ev.get("system_locale")
                if loc:
                    E["locale"][str(loc)] += 1

                # perfs
                if ev.get("client_performance_cpu") is not None and len(E["cpu_samples"]) < 200000:
                    try:
                        E["cpu_samples"].append(float(ev["client_performance_cpu"]))
                    except Exception:
                        pass
                if ev.get("client_performance_memory") is not None and len(E["mem_samples"]) < 200000:
                    try:
                        E["mem_samples"].append(float(ev["client_performance_memory"]))
                    except Exception:
                        pass

    E["total_events"] = n_lines
    E["experiments"] = len(E["experiments"])
    log(f"   {n_lines} lignes lues, {E['unique_events']} événements uniques")
    return E


# =========================================================================== #
#  3. COMPTE (user.json)
# =========================================================================== #
# Noms de jeux/applications connus (résolus via l'API publique Discord).
KNOWN_GAMES = {
    "432980957394370572": "Fortnite",
    "1402418703554842694": "Fortnite",
    "477175586805252107": "Among Us",
    "363445589247131668": "ROBLOX",
    "356875570916753438": "Minecraft",
    "700136079562375258": "VALORANT",
    "1158877933042143272": "Counter-Strike 2",
    "1124352162890264686": "Metro Exodus Enhanced Edition",
    "1124351807645302905": "Combat Master",
    "1334672060328443984": "EA Sports FC 25",
    "1364888648839073802": "Clair Obscur: Expedition 33",
    "1450685090098315376": "Comet",
    "787443973538971748": "Cyberpunk 2077",
    "363431197960962049": "Planet Coaster",
    "425778678723510302": "Goat Simulator",
    "1124357900933025882": "MyDockFinder",
}

# --------------------------------------------------------------------------
#  Noms de code matériels Android -> modèles commerciaux lisibles
#  (codenames Samsung/Pixel/Xiaomi les plus courants ; repli = code brut)
# --------------------------------------------------------------------------
DEVICE_CODENAMES = {
    # Samsung Galaxy S25 / S24 / S23 / S22 / S21 series (Snapdragon "q")
    "pa3q": "Galaxy S25 Ultra", "pa2q": "Galaxy S25+", "pa1q": "Galaxy S25",
    "e3q": "Galaxy S24 Ultra", "e2q": "Galaxy S24+", "e1q": "Galaxy S24",
    "dm3q": "Galaxy S23 Ultra", "dm2q": "Galaxy S23+", "dm1q": "Galaxy S23",
    "b0q": "Galaxy S22 Ultra", "g0q": "Galaxy S22+", "r0q": "Galaxy S22",
    "p3q": "Galaxy S21 Ultra", "t2q": "Galaxy S21+", "o1q": "Galaxy S21",
    # variantes Exynos (suffixe "s") du même modèle
    "b0s": "Galaxy S22 Ultra", "g0s": "Galaxy S22+", "r0s": "Galaxy S22",
    "p3s": "Galaxy S21 Ultra", "t2s": "Galaxy S21+", "o1s": "Galaxy S21",
    "e3s": "Galaxy S24 Ultra", "e2s": "Galaxy S24+", "e1s": "Galaxy S24",
    # Galaxy Z / Note / A / Tab
    "q5q": "Galaxy Z Fold4", "b4q": "Galaxy Z Flip4",
    "q6q": "Galaxy Z Fold5", "b5q": "Galaxy Z Flip5",
    "a52q": "Galaxy A52", "a53x": "Galaxy A53", "a54x": "Galaxy A54",
    "gts8": "Galaxy Tab S8", "gts9": "Galaxy Tab S9",
    # Google Pixel
    "oriole": "Pixel 6", "raven": "Pixel 6 Pro", "bluejay": "Pixel 6a",
    "panther": "Pixel 7", "cheetah": "Pixel 7 Pro", "lynx": "Pixel 7a",
    "shiba": "Pixel 8", "husky": "Pixel 8 Pro",
    # Xiaomi
    "lisa": "Xiaomi 11 Lite 5G NE",
    # Noms d'installations de bureau (PC) identifiés par l'utilisateur
    "ktor": "PC Windows", "rain": "PC Windows",
}
# Identifiants matériels Apple -> modèle commercial
IPHONE_MODELS = {
    "iPhone13,1": "iPhone 12 mini", "iPhone13,2": "iPhone 12",
    "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
    "iPhone14,4": "iPhone 13 mini", "iPhone14,5": "iPhone 13",
    "iPhone14,2": "iPhone 13 Pro", "iPhone14,3": "iPhone 13 Pro Max",
    "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus",
    "iPhone15,2": "iPhone 14 Pro", "iPhone15,3": "iPhone 14 Pro Max",
    "iPhone15,4": "iPhone 15", "iPhone15,5": "iPhone 15 Plus",
    "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max",
    "iPhone17,3": "iPhone 16", "iPhone17,4": "iPhone 16 Plus",
    "iPhone17,1": "iPhone 16 Pro", "iPhone17,2": "iPhone 16 Pro Max",
}
# Préfixes de modèles Samsung (SM-XXXX) -> nom commercial
SM_MODELS = {
    "SM-S938": "Galaxy S25 Ultra", "SM-S931": "Galaxy S25",
    "SM-S928": "Galaxy S24 Ultra", "SM-S921": "Galaxy S24",
    "SM-S918": "Galaxy S23 Ultra", "SM-S916": "Galaxy S23+", "SM-S911": "Galaxy S23",
    "SM-S908": "Galaxy S22 Ultra", "SM-S906": "Galaxy S22+", "SM-S901": "Galaxy S22",
    "SM-G998": "Galaxy S21 Ultra", "SM-G996": "Galaxy S21+", "SM-G991": "Galaxy S21",
}


def resolve_device_name(raw):
    """Traduit un code matériel en modèle commercial lisible (repli = code brut)."""
    if not raw:
        return raw
    s = str(raw).strip()
    # Apple : identifiant complet (contient une virgule), à tester en premier
    if s in IPHONE_MODELS:
        return IPHONE_MODELS[s]
    # cas "SM-S908U1, b0quew" -> on tente le préfixe SM- puis le codename
    for token in re.split(r"[,\s]+", s):
        tk = token.strip()
        # retire les suffixes régionaux courants (_global, _eea, _in, w, x...)
        base = re.sub(r"(_global|_eea|_in|_nao|_row)$", "", tk)
        if tk in DEVICE_CODENAMES:
            return DEVICE_CODENAMES[tk]
        if base in DEVICE_CODENAMES:
            return DEVICE_CODENAMES[base]
        for pref, name in SM_MODELS.items():
            if tk.upper().startswith(pref):
                return name
    if s in DEVICE_CODENAMES:
        return DEVICE_CODENAMES[s]
    return s


def _resolve_device_counter(counter):
    """Réagrège un Counter de codes matériels par modèle commercial lisible."""
    agg = collections.Counter()
    for raw, n in counter.items():
        agg[resolve_device_name(raw)] += n
    return agg


_GAME_CACHE_PATH = os.path.join(OUT_DIR, "games_cache.json")


def _load_game_cache():
    cache = dict(KNOWN_GAMES)
    if os.path.exists(_GAME_CACHE_PATH):
        try:
            with open(_GAME_CACHE_PATH, encoding="utf-8") as f:
                cache.update(json.load(f))
        except Exception:
            pass
    return cache


def resolve_game_name(app_id, cache):
    """Résout un application_id -> nom. Cache local + repli réseau (best-effort)."""
    aid = str(app_id)
    if aid in cache:
        return cache[aid]
    name = None
    try:
        import urllib.request
        url = f"https://discord.com/api/v10/applications/{aid}/rpc"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            name = json.load(r).get("name")
    except Exception:
        name = None
    cache[aid] = name
    return name


def analyze_account(pkg):
    log(">> Analyse du compte…")
    path = os.path.join(pkg, "Compte", "user.json")
    A = {}
    if not os.path.exists(path):
        return A
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            u = json.load(f)
    except Exception as e:
        log(f"   ! user.json illisible ({e}); section compte ignorée")
        return A

    A["username"] = u.get("username")
    A["global_name"] = u.get("global_name")
    A["id"] = u.get("id")
    A["email"] = u.get("email")
    A["verified"] = u.get("verified")
    A["has_phone"] = bool(u.get("phone"))
    A["premium_until"] = u.get("premium_until")
    A["created"] = None
    dt = snowflake_to_dt(u.get("id"))
    if dt:
        A["created"] = dt.isoformat()
    A["orbs"] = u.get("current_orbs_balance")

    rels = u.get("relationships", []) or []
    rel_types = collections.Counter()
    friends = []
    name_map = {}  # username -> pseudo affiché (global_name)
    for r in rels:
        t = {1: "Ami", 2: "Bloqué", 3: "Demande reçue", 4: "Demande envoyée"}.get(r.get("type"), r.get("type"))
        if isinstance(r.get("type"), str):
            t = r.get("type")
        rel_types[str(t)] += 1
        usr = r.get("user", {}) or {}
        un = usr.get("username")
        gn = usr.get("global_name")
        if un:
            name_map[un] = gn or un
        nm = gn or un or usr.get("id")
        if str(t).upper() in ("FRIEND", "AMI", "1") or r.get("type") == 1:
            friends.append(nm)
    A["name_map"] = name_map
    A["relationship_types"] = dict(rel_types)
    A["friends_count"] = len(friends)
    A["friends_sample"] = friends[:60]

    conns = u.get("connections", []) or []
    A["connections"] = [{"type": c.get("type"), "name": c.get("name"),
                         "verified": c.get("verified")} for c in conns]

    stats = u.get("user_activity_application_statistics", []) or []
    games = []
    game_cache = _load_game_cache()
    for s in stats:
        aid = s.get("application_id")
        games.append({
            "app_id": aid,
            "name": resolve_game_name(aid, game_cache) or f"App {aid}",
            "total_duration": s.get("total_duration"),
            "first": s.get("first_played_at"),
            "last": s.get("last_played_at"),
        })
    games.sort(key=lambda x: x["total_duration"] or 0, reverse=True)
    A["games"] = games
    try:
        # ne persister que les entrées non encore connues
        extra = {k: v for k, v in game_cache.items() if k not in KNOWN_GAMES}
        with open(_GAME_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(extra, f, ensure_ascii=False)
    except Exception:
        pass

    gs = u.get("guild_settings", {})
    if isinstance(gs, dict):
        A["guild_settings_count"] = len(gs)
    elif isinstance(gs, list):
        A["guild_settings_count"] = len(gs)
    else:
        A["guild_settings_count"] = 0

    A["payments_note"] = u.get("premium_until")
    return A


# =========================================================================== #
#  4. SERVEURS
# =========================================================================== #
def analyze_servers(pkg):
    log(">> Analyse des serveurs…")
    sdir = os.path.join(pkg, "Serveurs")
    servers = []
    total_audit = 0
    for d in glob.glob(os.path.join(sdir, "*")):
        if not os.path.isdir(d):
            continue
        gj = os.path.join(d, "guild.json")
        name = os.path.basename(d)
        audit = 0
        if os.path.exists(gj):
            try:
                with open(gj, encoding="utf-8") as f:
                    name = json.load(f).get("name", name)
            except Exception:
                pass
        aj = os.path.join(d, "audit-log.json")
        if os.path.exists(aj):
            try:
                with open(aj, encoding="utf-8") as f:
                    al = json.load(f)
                audit = len(al) if isinstance(al, list) else 0
            except Exception:
                pass
        total_audit += audit
        servers.append({"name": name, "audit": audit})
    servers.sort(key=lambda x: x["name"].lower())
    return {"count": len(servers), "servers": servers, "total_audit": total_audit}


# =========================================================================== #
#  5. PUBLICITÉS / TRAITS
# =========================================================================== #
def analyze_ads(pkg):
    log(">> Analyse des publicités / traits…")
    res = {"traits": [], "quests": 0}
    tp = os.path.join(pkg, "Publicités", "traits.json")
    if os.path.exists(tp):
        try:
            with open(tp, encoding="utf-8") as f:
                t = json.load(f)
            if isinstance(t, list):
                for item in t[:400]:
                    if isinstance(item, dict):
                        res["traits"].append({
                            "name": item.get("trait_name") or item.get("name") or str(list(item.keys())[:2]),
                            "value": item.get("value") or item.get("trait_value"),
                        })
            elif isinstance(t, dict):
                for k, v in list(t.items())[:400]:
                    res["traits"].append({"name": k, "value": v if not isinstance(v, (dict, list)) else json.dumps(v)[:80]})
        except Exception:
            pass
    qp = os.path.join(pkg, "Publicités", "quests_user_status.json")
    if os.path.exists(qp):
        try:
            with open(qp, encoding="utf-8") as f:
                q = json.load(f)
            res["quests"] = len(q) if isinstance(q, list) else (len(q) if isinstance(q, dict) else 0)
        except Exception:
            pass
    return res


# --------------------------------------------------------------------------- #
#  Helpers de sérialisation
# --------------------------------------------------------------------------- #
def counter_top(counter, n=30):
    return counter.most_common(n)


def stats_list(values):
    if not values:
        return {"count": 0, "avg": 0, "median": 0, "max": 0, "min": 0}
    vs = sorted(values)
    n = len(vs)
    return {
        "count": n,
        "avg": sum(vs) / n,
        "median": vs[n // 2],
        "max": vs[-1],
        "min": vs[0],
    }


def _pretty_top_dms(rows, A):
    """Remplace le nom d'utilisateur (mehdi7869#0) par le pseudo affiché
    quand il est connu via la liste d'amis, et retire le discriminateur."""
    name_map = (A or {}).get("name_map", {}) or {}
    out = []
    for name, count in rows:
        base = str(name).split("#")[0].strip()
        pretty = name_map.get(base) or base
        out.append([pretty, count])
    return out


def _pretty_channel_label(label, is_dm, A):
    """Pour les canaux DM, remplace le nom d'utilisateur par le pseudo."""
    name_map = (A or {}).get("name_map", {}) or {}
    if not label:
        return label
    if label.startswith("Direct Message with"):
        nm = label.replace("Direct Message with", "").strip()
        base = nm.split("#")[0].strip()
        pretty = name_map.get(base) or base
        return "DM avec " + pretty
    if is_dm:
        base = str(label).split("#")[0].strip()
        return name_map.get(base) or base
    return label


def build_payload(M, E, A, S, ADS):
    # streaks (jours consécutifs avec message)
    dates = sorted(M["by_date"].keys())
    best_streak = cur = 0
    prev = None
    for d in dates:
        dd = datetime.strptime(d, "%Y-%m-%d")
        if prev and (dd - prev).days == 1:
            cur += 1
        else:
            cur = 1
        best_streak = max(best_streak, cur)
        prev = dd

    busiest_day = M["by_date"].most_common(1)[0] if M["by_date"] else ("-", 0)
    active_days = len(M["by_date"])

    span_days = 0
    if M["first_ts"] and M["last_ts"]:
        span_days = (M["last_ts"] - M["first_ts"]).days + 1

    msg_len = stats_list(M["msg_lengths"])
    cpu = stats_list(E["cpu_samples"])
    mem = stats_list(E["mem_samples"])

    # comparaison par année (messages, jours actifs, moy./jour)
    year_active = collections.Counter()
    for d in M["by_date"]:
        year_active[int(d[:4])] += 1
    per_year = []
    for y, cnt in sorted(M["by_year"].items()):
        ad = year_active.get(y, 0)
        per_year.append({
            "year": y,
            "messages": cnt,
            "active_days": ad,
            "avg_per_day": round(cnt / ad, 1) if ad else 0,
        })

    # Temps en ligne estimé : nombre de tranches de 10 min contenant au moins
    # un événement (proxy réaliste du temps réellement actif sur Discord).
    online_sec = len(E["active_buckets"]) * 600
    online_days = len(E["by_date"])
    online_avg_min = (online_sec / online_days / 60) if online_days else 0

    payload = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "package": PKG,
        "messages": {
            "total": M["total_messages"],
            "chars": M["total_chars"],
            "words": M["total_words_raw"],
            "words_significant": M["total_words"],
            "attachments": M["total_attachments"],
            "links": M["total_links"],
            "mentions": M["total_mentions"],
            "custom_emojis": M["total_custom_emojis"],
            "unicode_emojis": M["total_unicode_emojis"],
            "avg_len": round(msg_len["avg"], 1),
            "first": M["first_ts"].isoformat() if M["first_ts"] else None,
            "last": M["last_ts"].isoformat() if M["last_ts"] else None,
            "span_days": span_days,
            "active_days": active_days,
            "best_streak": best_streak,
            "busiest_day": {"date": busiest_day[0], "count": busiest_day[1]},
            "channels_count": len(M["per_channel"]),
            "dm_count": sum(1 for c in M["per_channel"] if c["is_dm"]),
            "by_year": sorted(M["by_year"].items()),
            "per_year": per_year,
            "by_month": sorted(M["by_month"].items()),
            "by_weekday": [M["by_weekday"].get(i, 0) for i in range(7)],
            "by_hour": [M["by_hour"].get(i, 0) for i in range(24)],
            "by_date": sorted(M["by_date"].items()),
            "heatmap": [[M["heatmap"].get((wd, h), 0) for h in range(24)] for wd in range(7)],
            "channel_type": counter_top(M["channel_type"], 20),
            "top_dms": _pretty_top_dms(counter_top(M["dm_counter"], 40), A),
            "top_servers": counter_top(M["per_server"], 40),
            "top_words": counter_top(M["words"], 60),
            "top_custom_emojis": counter_top(M["custom_emojis"], 40),
            "top_unicode_emojis": counter_top(M["unicode_emojis"], 40),
            "top_domains": counter_top(M["domains"], 40),
            "top_channels": sorted(
                [{"label": _pretty_channel_label(c["label"], c["is_dm"], A), "count": c["count"], "type": c["type"],
                  "server": c["server"], "is_dm": c["is_dm"]} for c in M["per_channel"]],
                key=lambda x: x["count"], reverse=True)[:50],
            # --- analyses enrichies ---
            "length_buckets": [[k, M["length_buckets"].get(k, 0)] for k in
                               ("0 (vide)", "1-10", "11-50", "51-100", "101-300", "300+")],
            "msgs_with_link": M["msgs_with_link"],
            "msgs_with_attachment": M["msgs_with_attachment"],
            "msgs_with_mention": M["msgs_with_mention"],
            "msgs_with_emoji": M["msgs_with_emoji"],
            "msgs_pure_text": M["msgs_pure_text"],
            "msgs_empty": M["msgs_empty"],
            "night_msgs": M["night_msgs"],
            "laugh_msgs": M["laugh_msgs"],
            "question_msgs": M["question_msgs"],
            "exclaim_msgs": M["exclaim_msgs"],
            "caps_msgs": M["caps_msgs"],
            "longest_msg": M["longest_msg"],
            "unique_words": len(M["words"]),
            "peak_hour": (max(range(24), key=lambda h: M["by_hour"].get(h, 0))
                          if M["by_hour"] else 0),
            "avg_per_active_day": round(M["total_messages"] / active_days, 1) if active_days else 0,
        },
        "events": {
            "total": E["total_events"],
            "unique": E["unique_events"],
            "types": counter_top(E["event_types"], 60),
            "by_date": sorted(E["by_date"].items()),
            "by_hour": [E["by_hour"].get(i, 0) for i in range(24)],
            "by_weekday": [E["by_weekday"].get(i, 0) for i in range(7)],
            "by_month": sorted(E["by_month"].items()),
            "heatmap": [[E["heatmap"].get((wd, h), 0) for h in range(24)] for wd in range(7)],
            "os": counter_top(E["os"], 15),
            "device": counter_top(_resolve_device_counter(E["device"]), 20),
            "browser": counter_top(E["browser"], 15),
            "client_version": counter_top(E["client_version"], 15),
            "release_channel": counter_top(E["release_channel"], 10),
            "city": counter_top(E["city"], 30),
            "country": counter_top(E["country"], 30),
            "region": counter_top(E["region"], 20),
            "isp": counter_top(E["isp"], 20),
            "timezone": counter_top(E["timezone"], 15),
            "geo_first_last": sorted(
                [{"place": k, "first": v[0], "last": v[1]} for k, v in E["geo_first_last"].items()],
                key=lambda x: x["first"]),
            "reactions": counter_top(E["reactions"], 40),
            "screens": counter_top(E["screens"], 30),
            "session_count": E["session_count"],
            "session_total_hours": round(online_sec / 3600, 1),
            "session_avg_min": round(online_avg_min, 1),
            "session_median_min": 0,
            "online_days": online_days,
            "notif_received": E["notif_received"],
            "notif_clicked": E["notif_clicked"],
            "messages_edited": E["messages_edited"],
            "messages_deleted": E["messages_deleted"],
            "experiments": E["experiments"],
            "app_opens": E["app_opens"],
            "logins": E["logins"],
            "guild_joined": E["guild_joined"],
            "searches": E["searches"],
            "ad_decisions": E["ad_decisions"],
            "voice_events": E["voice_events"],
            "net_bytes": E["net_bytes"],
            "net_by_month": sorted(E["net_by_month"].items()),
            "locale": counter_top(E["locale"], 12),
            "reactions_removed": E["reactions_removed"],
            "cpu_avg": round(cpu["avg"], 1) if cpu["count"] else 0,
            "mem_avg_mb": round(mem["avg"] / 1024, 1) if mem["count"] and mem["avg"] > 10000 else round(mem["avg"], 1),
            "first": E["first_ts"].isoformat() if E["first_ts"] else None,
            "last": E["last_ts"].isoformat() if E["last_ts"] else None,
        },
        "account": A,
        "servers": S,
        "ads": ADS,
    }
    return payload


def build_parser():
    parser = argparse.ArgumentParser(
        description="Analyse un export « Mes données » Discord et génère "
                    "un rapport HTML interactif.",
    )
    parser.add_argument(
        "export",
        nargs="?",
        default=None,
        help="Chemin vers le dossier d'export Discord décompressé. "
             "Si omis sans autre option, un menu interactif s'ouvre.",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output",
        default=None,
        help="Dossier de sortie exact pour data.json / rapport.html. "
             "Si omis, un dossier daté est créé dans ./rapports/.",
    )
    return parser


def run_analysis(export_path, output_dir):
    global PKG, OUT_DIR, _GAME_CACHE_PATH

    PKG = validate_export_path(export_path)
    OUT_DIR = os.path.abspath(output_dir)
    os.makedirs(OUT_DIR, exist_ok=True)
    _GAME_CACHE_PATH = os.path.join(OUT_DIR, "games_cache.json")

    log(f"Paquet analysé: {PKG}")
    log(f"Dossier de sortie: {OUT_DIR}")
    M = analyze_messages(PKG)
    A = analyze_account(PKG)
    S = analyze_servers(PKG)
    ADS = analyze_ads(PKG)
    E = analyze_events(PKG)

    payload = build_payload(M, E, A, S, ADS)

    data_path = os.path.join(OUT_DIR, "data.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    log(f">> data.json écrit ({os.path.getsize(data_path)//1024} Ko)")

    # Générer le HTML
    from render import render_html
    html_out = render_html(payload)
    html_path = os.path.join(OUT_DIR, "rapport.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    log(f">> rapport.html écrit -> {html_path}")
    log("")
    log("Terminé.")
    log(f"Rapport HTML : {html_path}")
    log(f"Données JSON  : {data_path}")
    return data_path, html_path


def print_menu():
    log("")
    log("=== Discord Wrapped - lanceur ===")
    log("1. Analyser un export")
    log("2. Détecter automatiquement un export")
    log("3. Afficher l'aide")
    log("4. Quitter")


def confirm_and_run(export_path, output_dir):
    log("")
    log("Résumé avant génération")
    log(f"  Export : {export_path}")
    log(f"  Sortie : {output_dir}")
    log("  Fichiers générés : data.json, rapport.html")
    if not ask_yes_no("Lancer l'analyse ?", default=True):
        log("Analyse annulée.")
        return
    _, html_path = run_analysis(export_path, output_dir)
    if ask_yes_no("Ouvrir le rapport dans le navigateur ?", default=True):
        if open_in_browser(html_path):
            log("Ouverture demandée au navigateur.")
        else:
            log("Impossible d'ouvrir automatiquement le navigateur.")


def interactive_main(parser):
    while True:
        print_menu()
        choice = input("Choix > ").strip()

        if choice == "1":
            raw = input("Chemin du dossier d'export Discord > ")
            cleaned = clean_user_path(raw)
            try:
                export_path = validate_export_path(cleaned)
            except ValueError as exc:
                log(f"Erreur : {exc}")
                continue
            output_dir = make_default_output_dir(export_path)
            confirm_and_run(export_path, output_dir)
            return

        if choice == "2":
            export_path = find_default_pkg()
            if not export_path:
                log(MSG_INTROUVABLE)
                continue
            output_dir = make_default_output_dir(export_path)
            confirm_and_run(export_path, output_dir)
            return

        if choice == "3":
            log("")
            parser.print_help()
            continue

        if choice == "4":
            log("À bientôt.")
            return

        log("Choix invalide. Entre 1, 2, 3 ou 4.")


def main():
    parser = build_parser()
    if len(sys.argv) == 1:
        interactive_main(parser)
        return

    args = parser.parse_args()

    if args.export:
        export_path = args.export
    else:
        export_path = find_default_pkg()

    if not export_path:
        log(MSG_INTROUVABLE)
        sys.exit(1)

    try:
        export_path = validate_export_path(export_path)
    except ValueError as exc:
        log(f"ERREUR: {exc}")
        if args.export:
            log(f"(chemin fourni: {args.export})")
        sys.exit(1)

    output_dir = os.path.abspath(args.output) if args.output else make_default_output_dir(export_path)
    run_analysis(export_path, output_dir)


if __name__ == "__main__":
    main()
