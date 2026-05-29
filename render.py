# -*- coding: utf-8 -*-
"""Génère un rapport HTML autonome (dashboard interactif) à partir du payload."""
import json


def render_html(p):
    data_json = json.dumps(p, ensure_ascii=False)
    # On échappe </script> pour ne pas casser le bloc inline
    data_json = data_json.replace("</", "<\\/")

    return r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mon Discord — Analyse complète</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%232b2d31'/%3E%3Ccircle cx='32' cy='32' r='16' fill='none' stroke='%233f4147' stroke-width='8'/%3E%3Ccircle cx='32' cy='32' r='16' fill='none' stroke='%235865F2' stroke-width='8' stroke-dasharray='70 100' stroke-dashoffset='25' stroke-linecap='round' transform='rotate(-90 32 32)'/%3E%3Ccircle cx='32' cy='32' r='16' fill='none' stroke='%23eb459e' stroke-width='8' stroke-dasharray='25 100' stroke-dashoffset='-45' stroke-linecap='round' transform='rotate(-90 32 32)'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg-main:#313338; --bg-side:#2b2d31; --bg-darkest:#1e1f22;
  --card:#383a40; --card-hover:#404249;
  --accent:#5865F2; --accent-hover:#4752c4; --accent2:#c2c9ff;
  --green:#23a55a; --pink:#eb459e; --yellow:#f0b232; --red:#ed4245;
  --text:#f2f3f5; --muted:#b5bac1; --faint:#949ba4; --border:#3f4147;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{font-family:'Inter',system-ui,'Segoe UI',sans-serif;background:var(--bg-darkest);
  color:var(--text);line-height:1.5;display:flex;overflow:hidden;-webkit-font-smoothing:antialiased}

/* ===== Rail des serveurs ===== */
.guild-rail{width:72px;background:var(--bg-darkest);display:flex;flex-direction:column;align-items:center;
  padding:12px 0;gap:8px;flex-shrink:0}
.guild-icon{width:48px;height:48px;border-radius:50%;background:var(--bg-side);display:flex;align-items:center;
  justify-content:center;font-size:20px;cursor:pointer;position:relative;transition:border-radius .15s,background .15s}
.guild-icon:hover,.guild-icon.active,.guild-icon.home{border-radius:16px;background:var(--accent)}
.guild-icon.active::before,.guild-icon.home::before{content:"";position:absolute;left:-12px;width:4px;
  border-radius:0 4px 4px 0;background:#fff;height:40px}
.guild-sep{width:32px;height:2px;background:var(--border);border-radius:1px;margin:2px 0}

/* ===== Sidebar ===== */
.sidebar{width:240px;background:var(--bg-side);display:flex;flex-direction:column;flex-shrink:0}
.sidebar-header{height:48px;padding:0 16px;display:flex;align-items:center;font-weight:700;font-size:15px;
  box-shadow:0 1px 0 rgba(0,0,0,.2);flex-shrink:0;gap:8px}
.sidebar-nav{padding:8px;overflow-y:auto;flex:1}
.nav-label{color:var(--faint);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.02em;
  padding:14px 8px 4px}
.nav-item{display:flex;align-items:center;gap:12px;padding:8px;margin:1px 0;border-radius:4px;color:var(--faint);
  font-size:14.5px;font-weight:500;cursor:pointer;transition:background .12s,color .12s}
.nav-item:hover{background:rgba(255,255,255,.04);color:var(--muted)}
.nav-item.active{background:rgba(255,255,255,.08);color:var(--text)}
.nav-item .ico{width:20px;text-align:center;font-size:16px;flex-shrink:0}
.sidebar-footer{min-height:52px;background:#232428;display:flex;align-items:center;gap:8px;padding:0 8px;flex-shrink:0}
.avatar{width:32px;height:32px;border-radius:50%;background:var(--accent);display:flex;align-items:center;
  justify-content:center;font-weight:700;font-size:14px;position:relative}
.avatar::after{content:"";position:absolute;bottom:-2px;right:-2px;width:12px;height:12px;border-radius:50%;
  background:var(--green);border:3px solid #232428}
.user-meta .name{font-size:14px;font-weight:600;line-height:1.2}
.user-meta .tag{font-size:12px;color:var(--faint)}

/* ===== Main ===== */
.main{flex:1;background:var(--bg-main);display:flex;flex-direction:column;min-width:0}
.topbar{height:48px;flex-shrink:0;display:flex;align-items:center;gap:8px;padding:0 16px;
  box-shadow:0 1px 0 rgba(0,0,0,.2);z-index:10}
.topbar .hash{color:var(--faint);font-size:22px;font-weight:400}
.topbar .title{font-size:16px;font-weight:700}
.topbar .divider{width:1px;height:24px;background:var(--border);margin:0 8px}
.topbar .desc{font-size:13px;color:var(--faint);font-weight:500}
.content{overflow-y:auto;flex:1;padding:24px 32px 64px}
.wrap{max-width:1180px;margin:0 auto}

section{display:none;animation:fade .35s}
section.active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

h2{margin:30px 0 14px;font-size:1.15rem;font-weight:700;letter-spacing:-.01em;display:flex;align-items:center;gap:10px}
h2 .dot{width:8px;height:8px;border-radius:50%;background:var(--accent)}
.grid{display:grid;gap:16px}
.kpis{grid-template-columns:repeat(auto-fit,minmax(185px,1fr))}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:20px}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:18px;position:relative;
  transition:background .12s,transform .12s,border-color .12s}
.kpi:hover{background:var(--card-hover);transform:translateY(-2px);border-color:rgba(88,101,242,.45)}
.kpi .v{font-size:1.65rem;font-weight:800;letter-spacing:-.5px}
.kpi .l{color:var(--faint);font-size:.8rem;margin-top:5px}
.cols2{grid-template-columns:1fr 1fr}
.cols3{grid-template-columns:repeat(3,1fr)}
@media(max-width:820px){.cols2,.cols3{grid-template-columns:1fr}}
canvas{max-width:100%}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--border)}
th{color:var(--faint);font-weight:600;font-size:.78rem;text-transform:uppercase}
td.num{text-align:right;font-variant-numeric:tabular-nums;color:#dbdee1;font-weight:600}
.bar{height:6px;border-radius:4px;background:linear-gradient(90deg,var(--accent),#7984f5);margin-top:4px;opacity:.9}
.tag{display:inline-block;background:var(--bg-main);border:1px solid var(--border);border-radius:14px;
  padding:4px 10px;margin:3px;font-size:.82rem}
.muted{color:var(--muted)}
.heat{display:grid;grid-template-columns:auto repeat(24,1fr);gap:2px;font-size:.62rem}
.heat .cell{aspect-ratio:1;border-radius:3px;background:#2b2d31}
.heat .lab{color:var(--faint);display:flex;align-items:center;justify-content:center}
.scroll{max-height:430px;overflow:auto}
.scroll::-webkit-scrollbar,.content::-webkit-scrollbar,.sidebar-nav::-webkit-scrollbar{width:8px}
.scroll::-webkit-scrollbar-thumb,.content::-webkit-scrollbar-thumb,.sidebar-nav::-webkit-scrollbar-thumb{background:var(--bg-darkest);border-radius:8px}
.title-sm{font-size:.95rem;font-weight:700;margin-bottom:10px;color:#fff}
.flex{display:flex;flex-wrap:wrap;gap:8px}
.pill{font-size:.78rem;padding:3px 9px;border-radius:10px;background:var(--bg-main);border:1px solid var(--border)}
.emoji{font-size:1.3rem}
.cal{display:grid;grid-auto-flow:column;grid-template-rows:repeat(7,11px);gap:3px}
.cal .d{width:11px;height:11px;border-radius:2px;background:#2b2d31}
.calmonths{display:flex;gap:3px;font-size:.62rem;color:var(--faint);margin-bottom:4px;padding-left:2px}
footer{color:var(--faint);font-size:.8rem;margin-top:40px;text-align:center}
a{color:var(--accent2)}
@media(max-width:820px){.guild-rail{display:none}.sidebar{width:200px}.content{padding:18px}}
@media(max-width:620px){.sidebar{display:none}}
.lang-switch{margin-left:auto;display:flex;align-items:center;gap:4px;font-size:12.5px;font-weight:700;color:var(--faint)}
.lang-switch span[data-lang]{cursor:pointer;padding:3px 8px;border-radius:5px;transition:background .12s,color .12s}
.lang-switch span[data-lang]:hover{color:var(--text);background:rgba(255,255,255,.06)}
.lang-switch span[data-lang].active{color:#fff;background:var(--accent)}
.lang-switch .sep{opacity:.35;cursor:default}
</style>
</head>
<body>
<nav class="guild-rail">
  <div class="guild-icon home" data-i18n-title="tab_overview" title="Vue d'ensemble">📊</div>
  <div class="guild-sep"></div>
  <div class="guild-icon active" data-i18n-title="rail_mydata" title="Mes données">🦀</div>
  <div class="guild-icon" data-i18n-title="rail_convos" title="Conversations">💬</div>
  <div class="guild-icon" data-i18n-title="tab_servers" title="Serveurs">🌐</div>
</nav>
<aside class="sidebar">
  <div class="sidebar-header" data-i18n="app_title">📈 Mon Récap Discord</div>
  <nav class="sidebar-nav" id="nav"></nav>
  <div class="sidebar-footer">
    <div class="avatar" id="navAvatar">?</div>
    <div class="user-meta"><div class="name" id="navName">Mes données</div><div class="tag" data-i18n="status_online">En ligne</div></div>
  </div>
</aside>
<main class="main">
  <header class="topbar">
    <span class="hash">#</span>
    <span class="title" id="topTitle">vue-d-ensemble</span>
    <span class="divider"></span>
    <span class="desc" id="subtitle"></span>
    <div class="lang-switch" id="langSwitch">
      <span data-lang="fr">FR</span><span class="sep">|</span><span data-lang="en">EN</span>
    </div>
  </header>
  <div class="content">
    <div class="wrap">
      <section id="tab-overview"></section>
      <section id="tab-records"></section>
      <section id="tab-messages"></section>
      <section id="tab-people"></section>
      <section id="tab-time"></section>
      <section id="tab-words"></section>
      <section id="tab-activity"></section>
      <section id="tab-devices"></section>
      <section id="tab-geo"></section>
      <section id="tab-account"></section>
      <section id="tab-servers"></section>
      <section id="tab-ads"></section>
      <footer><span data-i18n="footer">Généré localement • Aucune donnée envoyée en ligne • </span><span id="gen"></span></footer>
    </div>
  </div>
</main>

<script id="payload" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('payload').textContent);
const M = D.messages, E = D.events, A = D.account||{}, S = D.servers||{}, ADS = D.ads||{};
const fmt = n => (n==null?'—':n.toLocaleString('fr-FR'));
const fmtH = h => { if(h==null)return '—'; const d=new Date(h); return d.toLocaleDateString('fr-FR'); };
const fmtGo = b => b? (b/1073741824).toFixed(2)+' '+t('unit_gb') : '—';
const C = ['#5865F2','#949cf7','#3ba55d','#f0b232','#5bc0de','#eb459e','#a78bfa','#1abc9c','#e67e8a','#7289da'];
Chart.defaults.color = '#b5bac1';
Chart.defaults.borderColor = '#3f414733';
Chart.defaults.font.family = "'Inter',sans-serif";

const I18N = {
  fr: {
    page_title:"Mon Discord — Analyse complète",
    app_title:"📈 Mon Récap Discord",
    status_online:"En ligne",
    footer:"Généré localement • Aucune donnée envoyée en ligne • ",
    nav_default_name:"Mes données",
    rail_mydata:"Mes données", rail_convos:"Conversations",
    nav_label:"Analyse",
    weekdays:["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"],
    months:["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Aoû","Sep","Oct","Nov","Déc"],
    sub_messages:"messages", sub_events:"événements", sub_days:"jours d'historique",
    unit_h:"h", unit_d_short:"j", unit_gb:"Go", unit_msg:"msg", unit_messages:"messages",
    unit_chars:"caractères", unit_chars_short:"car.", unit_days:"jours", unit_events:"événements",
    unit_times:"fois", unit_min:"min", unit_mb:"Mo",
    txt_none:"Aucun", txt_none_f:"Aucune", txt_yes:"Oui", txt_no:"Non", tbl_nodata:"Aucune donnée",
    tab_overview:"Vue d'ensemble", tab_records:"Records", tab_messages:"Messages",
    tab_people:"Contacts & serveurs", tab_time:"Temps & rythme", tab_words:"Mots & emojis",
    tab_activity:"Activité Discord", tab_devices:"Appareils", tab_geo:"Géolocalisation",
    tab_account:"Compte & amis", tab_servers:"Serveurs", tab_ads:"Pub & traits",
    ov_h_kpis:"Chiffres clés",
    kpi_messages_sent:"Messages envoyés", kpi_words_written:"Mots écrits", kpi_chars:"Caractères",
    kpi_channels:"Salons / conversations", kpi_dms:"Conversations privées (DM)", kpi_servers:"Serveurs",
    kpi_friends:"Amis", kpi_time_discord:"Temps sur Discord", kpi_active_days:"Jours actifs",
    kpi_best_streak:"Plus longue série", kpi_links_shared:"Liens partagés", kpi_attachments:"Pièces jointes",
    ov_h_month:"Évolution des messages par mois",
    ov_facts_title:"📌 Faits marquants", ov_type_title:"🥧 Répartition par type de salon",
    fact_first:"Premier message", fact_last:"Dernier message", fact_busiest_day:"Jour le plus actif",
    fact_avg_len:"Longueur moyenne", fact_mentions:"Mentions envoyées", fact_emojis:"Emojis (perso + unicode)",
    fact_edited:"Messages modifiés", fact_deleted:"Messages supprimés", fact_sessions:"Sessions ouvertes",
    fact_notifs:"Notifications reçues", fact_experiments:"Expériences (A/B tests)",
    fact_ad_decisions:"Décisions de ciblage pub",
    rec_h:"🏆 Tes records sur Discord", rec_sub:"Un condensé de tes temps forts, façon rétrospective.",
    rec_streak_l:"Plus longue série", rec_streak_s:"Jours consécutifs avec au moins un message",
    rec_busiest_l:"Jour le plus actif", rec_busiest_s:"messages ce jour-là",
    rec_month_l:"Mois le plus actif", rec_peak_l:"Heure de pointe", rec_peak_s:"Le moment où tu écris le plus",
    rec_wd_l:"Jour de semaine favori", rec_dm_l:"Ton/ta n°1 en DM", rec_dm_s:"messages échangés",
    rec_srv_l:"Serveur n°1", rec_word_l:"Mot fétiche", rec_word_s_pre:"Dans",
    rec_uni_l:"Emoji favori", rec_uni_s:"Le plus utilisé dans tes messages",
    rec_custom_l:"Emoji perso favori", rec_custom_s_pre:"Emoji de serveur le plus utilisé",
    rec_dev_l:"Appareil principal", rec_city_l:"Lieu principal",
    rec_words_l:"Mots écrits au total", rec_words_s:"mots / message",
    rec_long_l:"Message le plus long", rec_long_s:"Ton record de longueur",
    msg_h_stats:"Statistiques des messages",
    msg_kpi_total:"Total messages", msg_kpi_avglen:"Longueur moy. (car.)", msg_kpi_perday:"Msg / jour actif",
    msg_kpi_unique_words:"Mots uniques", msg_kpi_peak:"Heure de pointe", msg_kpi_links:"Liens",
    msg_kpi_mentions:"Mentions", msg_kpi_custom_emojis:"Emojis perso",
    msg_dist_title:"📏 Distribution de la longueur des messages", msg_comp_title:"🧩 Composition des messages",
    msg_h_tone:"Ton & style",
    msg_kpi_laugh:"Messages avec rire 😂", msg_kpi_question:"Messages avec « ? »",
    msg_kpi_exclaim:"Messages avec « ! »", msg_kpi_caps:"Messages en MAJUSCULES",
    msg_kpi_night:"Messages la nuit (0-6h)", msg_kpi_puretext:"Texte pur (sans média)",
    msg_h_longest:"Message le plus long", msg_h_year:"Messages par année", msg_h_compare:"Comparaison année par année",
    msg_h_topchannels:"Top 50 salons / conversations",
    th_year:"Année", th_messages:"Messages", th_active_days:"Jours actifs", th_avg_perday:"Moy. / jour actif",
    th_channel:"Salon", th_type:"Type", th_server:"Serveur", th_person:"Personne", th_word:"Mot",
    th_domain:"Domaine", th_links:"Liens", th_count:"Nombre", th_place:"Lieu", th_first:"Première",
    th_last:"Dernière", th_attribute:"Attribut", th_value:"Valeur", th_game:"Jeu / application",
    th_duration:"Durée totale",
    ppl_h_dm:"Avec qui tu parles le plus (DM)", ppl_h_srv:"Serveurs où tu écris le plus",
    ppl_topdm_title:"Top contacts (DM)", ppl_topsrv_title:"Top serveurs",
    rt_daynight_title:"🌞 Jour vs 🌙 Nuit", rt_day:"Jour (7h–22h)", rt_night:"Nuit (22h–7h)",
    rt_night_note:"de ton activité a lieu la nuit.",
    rt_week_title:"🗓️ Semaine vs Week-end", rt_weekdays:"Lun–Ven", rt_weekend:"Sam–Dim",
    rt_avg_pre:"Moyenne/jour :", rt_avg_week:"en semaine", rt_avg_wend:"le week-end",
    rt_moments_title:"🕐 Moments de la journée", rt_morning:"Matin (6h–12h)", rt_afternoon:"Après-midi (12h–18h)",
    rt_evening:"Soirée (18h–23h)", rt_latenight:"Nuit profonde (23h–6h)",
    tm_h_when:"Quand es-tu actif ?", tm_byhour:"Par heure de la journée", tm_byweek:"Par jour de la semaine",
    tm_h_heatmap:"Carte de chaleur (jour × heure) — messages", tm_h_rhythm:"Rythme de vie",
    tm_h_calendar:"Calendrier d'activité (style contributions)",
    tm_cal_note:"Chaque carré = un jour. Plus c'est clair, plus tu as écrit de messages.",
    tm_h_daily:"Activité quotidienne (messages dans le temps)",
    wd_kpi_total:"Mots écrits (total)", wd_kpi_signif:"Mots significatifs",
    wd_note1:"« Mots écrits » = tous les mots tapés. « Mots significatifs » = hors mots vides (je, le, et…) et mots de moins de 3 lettres ; c'est cette base qui sert au classement ci-dessous.",
    wd_h_top:"Mots les plus utilisés",
    wd_note2:"Nombre de messages contenant chaque mot (compté une fois par message, pour ne pas être faussé par les messages répétitifs).",
    wd_uni_title:"🙂 Emojis unicode favoris", wd_custom_title:"😎 Emojis personnalisés favoris",
    wd_h_domains:"Domaines / liens les plus partagés",
    act_h_main:"Activité Discord (depuis les journaux analytics)",
    act_kpi_unique:"Événements uniques", act_kpi_sessions:"Sessions", act_kpi_total_time:"Temps total",
    act_kpi_avg_session:"Session moyenne", act_kpi_app_opens:"Ouvertures app", act_kpi_logins:"Connexions",
    act_kpi_notifs:"Notifs reçues", act_kpi_voice:"Événements vocaux", act_kpi_abtests:"A/B tests",
    act_kpi_ad_decisions:"Décisions pub", act_kpi_cpu:"CPU moyen", act_kpi_mem:"Mémoire moy.",
    act_h_types:"Types d'événements les plus fréquents", act_h_daily:"Activité (événements par jour)",
    act_h_month:"Activité par mois", act_h_heatmap:"Carte de chaleur de l'activité (jour × heure)",
    act_h_net_pre:"Données réseau consommées par mois", act_h_net_post:"au total",
    act_h_locale:"Langues détectées", act_h_reactions:"Réactions ajoutées",
    act_h_screens:"Écrans / pages les plus consultés",
    dev_h_main:"Appareils & clients utilisés", dev_os:"Systèmes d'exploitation", dev_browser:"Navigateurs",
    dev_models:"Modèles d'appareils", dev_versions:"Versions du client", dev_h_channel:"Canal de version",
    geo_h_main:"Où tu te connectes", geo_cities:"🏙️ Villes", geo_countries:"🌍 Pays",
    geo_isp:"📡 Fournisseurs d'accès (ISP)", geo_tz:"🕐 Fuseaux horaires",
    geo_h_history:"Historique des lieux (première / dernière connexion)",
    acc_h_main:"Mon compte", acc_username:"Nom d'utilisateur", acc_globalname:"Nom global", acc_id:"ID",
    acc_email:"Email", acc_email_verified:"Email vérifié", acc_phone:"Téléphone lié",
    acc_created:"Compte créé le", acc_nitro:"Nitro jusqu'au", acc_orbs:"Solde Orbs",
    acc_guild_settings:"Serveurs configurés", acc_h_friends:"Amis", acc_more:"autres",
    acc_h_relations:"Relations", acc_h_connections:"Connexions externes",
    acc_h_games:"Applications / jeux les plus joués", acc_games_tracked:"Jeux / apps suivis",
    acc_games_time:"Temps de jeu total",
    srv_h_main:"Serveurs dont je suis membre", srv_audit:"Entrées journal d'audit",
    ads_h_main:"Ce que Discord sait pour cibler la pub", ads_kpi_decisions:"Décisions de ciblage",
    ads_kpi_traits:"Traits publicitaires", ads_kpi_quests:"Quêtes",
    ads_h_traits:"Traits / attributs publicitaires",
    chart_messages:"Messages", chart_messages_day:"Messages/jour", chart_events_day:"Événements/jour",
    chart_gb:"Go",
    comp_puretext:"Texte pur", comp_link:"Avec lien", comp_attachment:"Avec pièce jointe",
    comp_mention:"Avec mention", comp_emoji:"Avec emoji"
  },
  en: {
    page_title:"My Discord — Full analysis",
    app_title:"📈 My Discord Recap",
    status_online:"Online",
    footer:"Generated locally • No data sent online • ",
    nav_default_name:"My data",
    rail_mydata:"My data", rail_convos:"Conversations",
    nav_label:"Analysis",
    weekdays:["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
    months:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    sub_messages:"messages", sub_events:"events", sub_days:"days of history",
    unit_h:"h", unit_d_short:"d", unit_gb:"GB", unit_msg:"msg", unit_messages:"messages",
    unit_chars:"characters", unit_chars_short:"chars", unit_days:"days", unit_events:"events",
    unit_times:"times", unit_min:"min", unit_mb:"MB",
    txt_none:"None", txt_none_f:"None", txt_yes:"Yes", txt_no:"No", tbl_nodata:"No data",
    tab_overview:"Overview", tab_records:"Records", tab_messages:"Messages",
    tab_people:"Contacts & servers", tab_time:"Time & rhythm", tab_words:"Words & emojis",
    tab_activity:"Discord activity", tab_devices:"Devices", tab_geo:"Geolocation",
    tab_account:"Account & friends", tab_servers:"Servers", tab_ads:"Ads & traits",
    ov_h_kpis:"Key figures",
    kpi_messages_sent:"Messages sent", kpi_words_written:"Words written", kpi_chars:"Characters",
    kpi_channels:"Channels / conversations", kpi_dms:"Direct messages (DMs)", kpi_servers:"Servers",
    kpi_friends:"Friends", kpi_time_discord:"Time on Discord", kpi_active_days:"Active days",
    kpi_best_streak:"Longest streak", kpi_links_shared:"Links shared", kpi_attachments:"Attachments",
    ov_h_month:"Messages over time (monthly)",
    ov_facts_title:"📌 Highlights", ov_type_title:"🥧 Breakdown by channel type",
    fact_first:"First message", fact_last:"Last message", fact_busiest_day:"Busiest day",
    fact_avg_len:"Average length", fact_mentions:"Mentions sent", fact_emojis:"Emojis (custom + unicode)",
    fact_edited:"Messages edited", fact_deleted:"Messages deleted", fact_sessions:"Sessions opened",
    fact_notifs:"Notifications received", fact_experiments:"Experiments (A/B tests)",
    fact_ad_decisions:"Ad targeting decisions",
    rec_h:"🏆 Your Discord records", rec_sub:"A recap of your highlights, wrapped-style.",
    rec_streak_l:"Longest streak", rec_streak_s:"Consecutive days with at least one message",
    rec_busiest_l:"Busiest day", rec_busiest_s:"messages that day",
    rec_month_l:"Busiest month", rec_peak_l:"Peak hour", rec_peak_s:"When you write the most",
    rec_wd_l:"Favorite weekday", rec_dm_l:"Your #1 DM", rec_dm_s:"messages exchanged",
    rec_srv_l:"#1 server", rec_word_l:"Signature word", rec_word_s_pre:"In",
    rec_uni_l:"Favorite emoji", rec_uni_s:"The one you use the most",
    rec_custom_l:"Favorite custom emoji", rec_custom_s_pre:"Most used server emoji",
    rec_dev_l:"Main device", rec_city_l:"Main location",
    rec_words_l:"Total words written", rec_words_s:"words / message",
    rec_long_l:"Longest message", rec_long_s:"Your length record",
    msg_h_stats:"Message statistics",
    msg_kpi_total:"Total messages", msg_kpi_avglen:"Avg. length (chars)", msg_kpi_perday:"Msg / active day",
    msg_kpi_unique_words:"Unique words", msg_kpi_peak:"Peak hour", msg_kpi_links:"Links",
    msg_kpi_mentions:"Mentions", msg_kpi_custom_emojis:"Custom emojis",
    msg_dist_title:"📏 Message length distribution", msg_comp_title:"🧩 Message composition",
    msg_h_tone:"Tone & style",
    msg_kpi_laugh:"Messages with laughter 😂", msg_kpi_question:"Messages with « ? »",
    msg_kpi_exclaim:"Messages with « ! »", msg_kpi_caps:"Messages in CAPS",
    msg_kpi_night:"Messages at night (0-6h)", msg_kpi_puretext:"Plain text (no media)",
    msg_h_longest:"Longest message", msg_h_year:"Messages per year", msg_h_compare:"Year-by-year comparison",
    msg_h_topchannels:"Top 50 channels / conversations",
    th_year:"Year", th_messages:"Messages", th_active_days:"Active days", th_avg_perday:"Avg. / active day",
    th_channel:"Channel", th_type:"Type", th_server:"Server", th_person:"Person", th_word:"Word",
    th_domain:"Domain", th_links:"Links", th_count:"Count", th_place:"Place", th_first:"First",
    th_last:"Last", th_attribute:"Attribute", th_value:"Value", th_game:"Game / application",
    th_duration:"Total duration",
    ppl_h_dm:"Who you talk to the most (DM)", ppl_h_srv:"Servers where you write the most",
    ppl_topdm_title:"Top contacts (DM)", ppl_topsrv_title:"Top servers",
    rt_daynight_title:"🌞 Day vs 🌙 Night", rt_day:"Day (7h–22h)", rt_night:"Night (22h–7h)",
    rt_night_note:"of your activity happens at night.",
    rt_week_title:"🗓️ Weekdays vs Weekend", rt_weekdays:"Mon–Fri", rt_weekend:"Sat–Sun",
    rt_avg_pre:"Average/day:", rt_avg_week:"on weekdays", rt_avg_wend:"on weekends",
    rt_moments_title:"🕐 Times of day", rt_morning:"Morning (6h–12h)", rt_afternoon:"Afternoon (12h–18h)",
    rt_evening:"Evening (18h–23h)", rt_latenight:"Late night (23h–6h)",
    tm_h_when:"When are you active?", tm_byhour:"By hour of the day", tm_byweek:"By day of the week",
    tm_h_heatmap:"Heatmap (day × hour) — messages", tm_h_rhythm:"Life rhythm",
    tm_h_calendar:"Activity calendar (contributions style)",
    tm_cal_note:"Each square = one day. The lighter it is, the more messages you wrote.",
    tm_h_daily:"Daily activity (messages over time)",
    wd_kpi_total:"Words written (total)", wd_kpi_signif:"Significant words",
    wd_note1:"« Words written » = every word typed. « Significant words » = excluding stop words (I, the, and…) and words shorter than 3 letters; this is the basis for the ranking below.",
    wd_h_top:"Most used words",
    wd_note2:"Number of messages containing each word (counted once per message, to avoid being skewed by repetitive messages).",
    wd_uni_title:"🙂 Favorite unicode emojis", wd_custom_title:"😎 Favorite custom emojis",
    wd_h_domains:"Most shared domains / links",
    act_h_main:"Discord activity (from analytics logs)",
    act_kpi_unique:"Unique events", act_kpi_sessions:"Sessions", act_kpi_total_time:"Total time",
    act_kpi_avg_session:"Average session", act_kpi_app_opens:"App opens", act_kpi_logins:"Logins",
    act_kpi_notifs:"Notifications received", act_kpi_voice:"Voice events", act_kpi_abtests:"A/B tests",
    act_kpi_ad_decisions:"Ad decisions", act_kpi_cpu:"Average CPU", act_kpi_mem:"Avg. memory",
    act_h_types:"Most frequent event types", act_h_daily:"Activity (events per day)",
    act_h_month:"Activity per month", act_h_heatmap:"Activity heatmap (day × hour)",
    act_h_net_pre:"Network data used per month", act_h_net_post:"total",
    act_h_locale:"Detected languages", act_h_reactions:"Reactions added",
    act_h_screens:"Most visited screens / pages",
    dev_h_main:"Devices & clients used", dev_os:"Operating systems", dev_browser:"Browsers",
    dev_models:"Device models", dev_versions:"Client versions", dev_h_channel:"Release channel",
    geo_h_main:"Where you connect from", geo_cities:"🏙️ Cities", geo_countries:"🌍 Countries",
    geo_isp:"📡 Internet providers (ISP)", geo_tz:"🕐 Time zones",
    geo_h_history:"Location history (first / last connection)",
    acc_h_main:"My account", acc_username:"Username", acc_globalname:"Global name", acc_id:"ID",
    acc_email:"Email", acc_email_verified:"Email verified", acc_phone:"Phone linked",
    acc_created:"Account created on", acc_nitro:"Nitro until", acc_orbs:"Orbs balance",
    acc_guild_settings:"Configured servers", acc_h_friends:"Friends", acc_more:"more",
    acc_h_relations:"Relationships", acc_h_connections:"External connections",
    acc_h_games:"Most played apps / games", acc_games_tracked:"Games / apps tracked",
    acc_games_time:"Total play time",
    srv_h_main:"Servers I am a member of", srv_audit:"Audit log entries",
    ads_h_main:"What Discord knows to target ads", ads_kpi_decisions:"Targeting decisions",
    ads_kpi_traits:"Ad traits", ads_kpi_quests:"Quests",
    ads_h_traits:"Ad traits / attributes",
    chart_messages:"Messages", chart_messages_day:"Messages/day", chart_events_day:"Events/day",
    chart_gb:"GB",
    comp_puretext:"Plain text", comp_link:"With link", comp_attachment:"With attachment",
    comp_mention:"With mention", comp_emoji:"With emoji"
  }
};
let LANG = (function(){ try{ const s=localStorage.getItem('lang'); return (s==='en'||s==='fr')?s:'fr'; }catch(e){ return 'fr'; } })();
let activeTab = 'overview';
let _charts = [];
const t = k => { const o=I18N[LANG]; if(o && o[k]!=null) return o[k]; return (I18N.fr[k]!=null?I18N.fr[k]:k); };

function applyLang(lang){
  LANG = (lang==='en')?'en':'fr';
  try{ localStorage.setItem('lang', LANG); }catch(e){}
  document.documentElement.lang = LANG;
  document.title = t('page_title');
  document.querySelectorAll('[data-i18n]').forEach(function(el){ const v=t(el.getAttribute('data-i18n')); if(v!=null) el.textContent=v; });
  document.querySelectorAll('[data-i18n-title]').forEach(function(el){ const v=t(el.getAttribute('data-i18n-title')); if(v!=null) el.title=v; });
  document.querySelectorAll('#langSwitch span[data-lang]').forEach(function(s){ s.classList.toggle('active', s.dataset.lang===LANG); });
  buildUI();
}

function buildUI(){
const WD = t('weekdays');
const MN = t('months');
_charts.forEach(function(c){ try{ c.destroy(); }catch(e){} });
_charts = [];

document.getElementById('subtitle').textContent =
  fmt(M.total)+' '+t('sub_messages')+' • '+fmt(E.unique)+' '+t('sub_events')+' • '+fmt(M.span_days)+' '+t('sub_days');
document.getElementById('gen').textContent = D.generated;
(function(){ const nm=(A.username||A.name||t('nav_default_name')); document.getElementById('navName').textContent=nm;
  document.getElementById('navAvatar').textContent=(nm[0]||'?').toUpperCase(); })();

const TABS = [
  ['overview',t('tab_overview'),'🏠'],['records',t('tab_records'),'🏆'],['messages',t('tab_messages'),'💬'],
  ['people',t('tab_people'),'🫂'],['time',t('tab_time'),'⏱️'],['words',t('tab_words'),'🔤'],
  ['activity',t('tab_activity'),'📡'],['devices',t('tab_devices'),'📱'],['geo',t('tab_geo'),'📍'],
  ['account',t('tab_account'),'👤'],['servers',t('tab_servers'),'🌐'],['ads',t('tab_ads'),'📢']
];
const nav = document.getElementById('nav');
nav.innerHTML = `<div class="nav-label">${t('nav_label')}</div>`;
TABS.forEach(([id,label,ico])=>{
  const b=document.createElement('div');
  b.className='nav-item'+(id===activeTab?' active':'');
  b.dataset.tab=id;
  b.innerHTML = `<span class="ico">${ico}</span> ${label}`;
  b.onclick=()=>{activeTab=id;
    document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('section').forEach(x=>x.classList.remove('active'));
    b.classList.add('active'); document.getElementById('tab-'+id).classList.add('active');
    document.getElementById('topTitle').textContent = id.replace(/[^a-z0-9]/gi,'-').toLowerCase();
    document.querySelector('.content').scrollTo({top:0,behavior:'smooth'});};
  nav.appendChild(b);
});
document.getElementById('topTitle').textContent = activeTab.replace(/[^a-z0-9]/gi,'-').toLowerCase();

function kpi(v,l){return `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div></div>`;}
function card(inner,cls=''){return `<div class="card ${cls}">${inner}</div>`;}
function h2(t){return `<h2><span class="dot"></span>${t}</h2>`;}
function tableRows(arr,maxv){ if(!arr||!arr.length)return `<tr><td class="muted">${t('tbl_nodata')}</td></tr>`;
  const mx=maxv||Math.max(...arr.map(x=>x[1]))||1;
  return arr.map(([k,v])=>`<tr><td>${esc(k)}<div class="bar" style="width:${Math.max(4,v/mx*100)}%"></div></td><td class="num">${fmt(v)}</td></tr>`).join('');}
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function cv(id){return `<canvas id="${id}"></canvas>`;}

// ---------- OVERVIEW ----------
document.getElementById('tab-overview').innerHTML =
  h2(t('ov_h_kpis')) +
  `<div class="grid kpis">
    ${kpi(fmt(M.total),t('kpi_messages_sent'))}
    ${kpi(fmt(M.words),t('kpi_words_written'))}
    ${kpi(fmt(M.chars),t('kpi_chars'))}
    ${kpi(fmt(M.channels_count),t('kpi_channels'))}
    ${kpi(fmt(M.dm_count),t('kpi_dms'))}
    ${kpi(fmt(S.count),t('kpi_servers'))}
    ${kpi(fmt(A.friends_count),t('kpi_friends'))}
    ${kpi(fmt(E.session_total_hours)+' '+t('unit_h'),t('kpi_time_discord'))}
    ${kpi(fmt(M.active_days),t('kpi_active_days'))}
    ${kpi(fmt(M.best_streak)+' '+t('unit_d_short'),t('kpi_best_streak'))}
    ${kpi(fmt(M.links),t('kpi_links_shared'))}
    ${kpi(fmt(M.total_attachments||M.attachments),t('kpi_attachments'))}
   </div>` +
  h2(t('ov_h_month')) +
  card(cv('ovMonth')) +
  `<div class="grid cols2" style="margin-top:16px">
    ${card(`<div class="title-sm">${t('ov_facts_title')}</div>`+factsHtml())}
    ${card(`<div class="title-sm">${t('ov_type_title')}</div>`+cv('ovType'))}
   </div>`;

function factsHtml(){
  const e=[];
  e.push([t('fact_first'), fmtH(M.first)]);
  e.push([t('fact_last'), fmtH(M.last)]);
  e.push([t('fact_busiest_day'), `${M.busiest_day.date} (${fmt(M.busiest_day.count)} ${t('unit_msg')})`]);
  e.push([t('fact_avg_len'), `${M.avg_len} ${t('unit_chars')}`]);
  e.push([t('fact_mentions'), fmt(M.mentions)]);
  e.push([t('fact_emojis'), fmt((M.custom_emojis||0)+(M.unicode_emojis||0))]);
  e.push([t('fact_edited'), fmt(E.messages_edited)]);
  e.push([t('fact_deleted'), fmt(E.messages_deleted)]);
  e.push([t('fact_sessions'), fmt(E.session_count)]);
  e.push([t('fact_notifs'), fmt(E.notif_received)]);
  e.push([t('fact_experiments'), fmt(E.experiments)]);
  e.push([t('fact_ad_decisions'), fmt(E.ad_decisions)]);
  return '<table>'+e.map(([k,v])=>`<tr><td>${k}</td><td class="num">${v}</td></tr>`).join('')+'</table>';
}

// ---------- RECORDS (récap façon "Wrapped") ----------
function bigStat(emoji,value,label,sub){
  return `<div class="card" style="text-align:center;padding:22px 16px">
    <div style="font-size:2rem;line-height:1">${emoji}</div>
    <div style="font-size:1.7rem;font-weight:800;margin:6px 0;color:#fff;word-break:break-word">${value}</div>
    <div class="muted" style="font-size:.85rem">${label}</div>
    ${sub?`<div class="muted" style="font-size:.72rem;margin-top:4px;opacity:.7">${sub}</div>`:''}
   </div>`;
}
(function renderRecords(){
  const topWord = (M.top_words&&M.top_words[0])||['—',0];
  const topDm = (M.top_dms&&M.top_dms[0])||['—',0];
  const topSrv = (M.top_servers&&M.top_servers[0])||['—',0];
  const topUni = (M.top_unicode_emojis&&M.top_unicode_emojis[0])||['—',0];
  const topCustom = (M.top_custom_emojis&&M.top_custom_emojis[0])||null;
  const topDev = (E.device&&E.device[0])||['—',0];
  const topCity = (E.city&&E.city[0])||['—',0];
  const topMonth = (M.by_month&&M.by_month.length)? M.by_month.reduce((a,b)=>b[1]>a[1]?b:a) : ['—',0];
  const peak = M.peak_hour;
  const wkd = M.by_weekday||[0,0,0,0,0,0,0];
  const topWd = wkd.indexOf(Math.max(...wkd));
  const grid = id=>document.getElementById(id);
  grid('tab-records').innerHTML =
    h2(t('rec_h')) +
    `<div class="muted" style="margin-bottom:14px;font-size:.85rem">${t('rec_sub')}</div>`+
    `<div class="grid kpis">
      ${bigStat('🔥', fmt(M.best_streak)+' '+t('unit_days'), t('rec_streak_l'), t('rec_streak_s'))}
      ${bigStat('📅', M.busiest_day.date, t('rec_busiest_l'), fmt(M.busiest_day.count)+' '+t('rec_busiest_s'))}
      ${bigStat('🗓️', topMonth[0], t('rec_month_l'), fmt(topMonth[1])+' '+t('unit_messages'))}
      ${bigStat('⏰', peak+t('unit_h'), t('rec_peak_l'), t('rec_peak_s'))}
      ${bigStat('📆', WD[topWd]||'—', t('rec_wd_l'), fmt(wkd[topWd])+' '+t('unit_messages'))}
      ${bigStat('💬', esc(topDm[0]), t('rec_dm_l'), fmt(topDm[1])+' '+t('rec_dm_s'))}
      ${bigStat('🏰', esc(topSrv[0]), t('rec_srv_l'), fmt(topSrv[1])+' '+t('unit_messages'))}
      ${bigStat('🗣️', esc(topWord[0]), t('rec_word_l'), t('rec_word_s_pre')+' '+fmt(topWord[1])+' '+t('unit_messages'))}
      ${bigStat(esc(topUni[0]), fmt(topUni[1]), t('rec_uni_l'), t('rec_uni_s'))}
      ${topCustom?bigStat('🎭', ':'+esc(topCustom[0])+':', t('rec_custom_l'), t('rec_custom_s_pre')+' ('+fmt(topCustom[1])+' '+t('unit_times')+')'):''}
      ${bigStat('📱', esc(topDev[0]), t('rec_dev_l'), fmt(topDev[1])+' '+t('unit_events'))}
      ${bigStat('📍', esc(topCity[0]), t('rec_city_l'), fmt(topCity[1])+' '+t('unit_events'))}
      ${bigStat('✍️', fmt(M.words), t('rec_words_l'), '≈ '+fmt(Math.round(M.words/Math.max(1,M.total)))+' '+t('rec_words_s'))}
      ${bigStat('📏', fmt(M.longest_msg.len)+' '+t('unit_chars_short'), t('rec_long_l'), t('rec_long_s'))}
     </div>`;
})();

// ---------- MESSAGES ----------
document.getElementById('tab-messages').innerHTML =
  h2(t('msg_h_stats')) +
  `<div class="grid kpis">
    ${kpi(fmt(M.total),t('msg_kpi_total'))}
    ${kpi(fmt(M.avg_len),t('msg_kpi_avglen'))}
    ${kpi(fmt(M.avg_per_active_day),t('msg_kpi_perday'))}
    ${kpi(fmt(M.unique_words),t('msg_kpi_unique_words'))}
    ${kpi(fmt(M.peak_hour)+t('unit_h'),t('msg_kpi_peak'))}
    ${kpi(fmt(M.total_attachments||M.attachments),t('kpi_attachments'))}
    ${kpi(fmt(M.links),t('msg_kpi_links'))}
    ${kpi(fmt(M.mentions),t('msg_kpi_mentions'))}
    ${kpi(fmt(M.custom_emojis),t('msg_kpi_custom_emojis'))}
   </div>`+
  `<div class="grid cols2" style="margin-top:16px">
    ${card(`<div class="title-sm">${t('msg_dist_title')}</div>`+cv('msgLen'))}
    ${card(`<div class="title-sm">${t('msg_comp_title')}</div>`+cv('msgComp'))}
   </div>`+
  h2(t('msg_h_tone')) +
  `<div class="grid kpis">
    ${kpi(fmt(M.laugh_msgs),t('msg_kpi_laugh'))}
    ${kpi(fmt(M.question_msgs),t('msg_kpi_question'))}
    ${kpi(fmt(M.exclaim_msgs),t('msg_kpi_exclaim'))}
    ${kpi(fmt(M.caps_msgs),t('msg_kpi_caps'))}
    ${kpi(fmt(M.night_msgs),t('msg_kpi_night'))}
    ${kpi(fmt(M.msgs_pure_text),t('msg_kpi_puretext'))}
   </div>`+
  (M.longest_msg && M.longest_msg.len ?
    h2(t('msg_h_longest')+' ('+fmt(M.longest_msg.len)+' '+t('unit_chars')+')') +
    card('<div class="muted" style="white-space:pre-wrap;word-break:break-word">'+esc(M.longest_msg.text)+(M.longest_msg.len>280?' …':'')+'</div>') : '')+
  h2(t('msg_h_year')) + card(cv('msgYear')) +
  h2(t('msg_h_compare')) +
  card(`<table><thead><tr><th>${t('th_year')}</th><th>${t('th_messages')}</th><th>${t('th_active_days')}</th><th>${t('th_avg_perday')}</th></tr></thead><tbody>`+
    (M.per_year||[]).map(y=>`<tr><td>${y.year}</td><td class="num">${fmt(y.messages)}</td><td class="num">${fmt(y.active_days)}</td><td class="num">${fmt(y.avg_per_day)}</td></tr>`).join('')+
    '</tbody></table>')+
  h2(t('msg_h_topchannels')) +
  card(`<div class="scroll"><table><thead><tr><th>${t('th_channel')}</th><th>${t('th_type')}</th><th>${t('th_server')}</th><th>${t('th_messages')}</th></tr></thead><tbody>`+
    M.top_channels.map(c=>`<tr><td>${esc(c.label)}</td><td><span class="pill">${c.is_dm?'DM':esc(c.type)}</span></td><td class="muted">${esc(c.server||'—')}</td><td class="num">${fmt(c.count)}</td></tr>`).join('')+
    '</tbody></table></div>');

// ---------- PEOPLE ----------
document.getElementById('tab-people').innerHTML =
  h2(t('ppl_h_dm')) +
  card(`<div class="scroll"><table><thead><tr><th>${t('th_person')}</th><th>${t('th_messages')}</th></tr></thead><tbody>`+tableRows(M.top_dms)+'</tbody></table></div>')+
  h2(t('ppl_h_srv')) +
  card(`<div class="scroll"><table><thead><tr><th>${t('th_server')}</th><th>${t('th_messages')}</th></tr></thead><tbody>`+tableRows(M.top_servers)+'</tbody></table></div>')+
  `<div class="grid cols2" style="margin-top:16px">
    ${card(`<div class="title-sm">${t('ppl_topdm_title')}</div>`+cv('peopleDM'))}
    ${card(`<div class="title-sm">${t('ppl_topsrv_title')}</div>`+cv('peopleSrv'))}
   </div>`;

// ---------- TIME ----------
function rythmeHtml(){
  const byH = M.by_hour||[]; const byW = M.by_weekday||[];
  const sum = a => a.reduce((x,y)=>x+y,0);
  const tot = sum(byH)||1;
  // jour (7h-22h) vs nuit (22h-7h)
  let night=0; for(let h=0;h<byH.length;h++){ if(h<7||h>=22) night+=byH[h]; }
  const day = tot-night;
  // semaine (lun-ven) vs week-end (sam-dim)  -- WD: 0=lun..6=dim
  const week = (byW[0]||0)+(byW[1]||0)+(byW[2]||0)+(byW[3]||0)+(byW[4]||0);
  const wend = (byW[5]||0)+(byW[6]||0);
  const totW = (week+wend)||1;
  const pct = (n,t)=>Math.round(n/t*100);
  // tranches de la journée
  const slice=(a,b)=>{let s=0;for(let h=a;h<b;h++)s+=byH[h]||0;return s;};
  const matin=slice(6,12), aprem=slice(12,18), soir=slice(18,23), nuit2=slice(23,24)+slice(0,6);
  const bar=(label,n,t,col)=>`<div style="margin:6px 0">
     <div style="display:flex;justify-content:space-between;font-size:.82rem"><span>${label}</span><span class="muted">${fmt(n)} (${pct(n,t)}%)</span></div>
     <div style="background:#2c3050;border-radius:6px;height:10px;overflow:hidden"><div style="height:100%;width:${pct(n,t)}%;background:${col}"></div></div>
   </div>`;
  return `<div class="grid cols2">
    ${card(`<div class="title-sm">${t('rt_daynight_title')}</div>`+
      bar(t('rt_day'),day,tot,'#faa61a')+bar(t('rt_night'),night,tot,'#5865F2')+
      `<div class="muted" style="font-size:.75rem;margin-top:6px">${pct(night,tot)}% ${t('rt_night_note')}</div>`)}
    ${card(`<div class="title-sm">${t('rt_week_title')}</div>`+
      bar(t('rt_weekdays'),week,totW,'#3ba55d')+bar(t('rt_weekend'),wend,totW,'#eb459e')+
      `<div class="muted" style="font-size:.75rem;margin-top:6px">${t('rt_avg_pre')} ${fmt(Math.round(week/5))} ${t('rt_avg_week')}, ${fmt(Math.round(wend/2))} ${t('rt_avg_wend')}.</div>`)}
    ${card(`<div class="title-sm">${t('rt_moments_title')}</div>`+
      bar(t('rt_morning'),matin,tot,'#00d4ff')+bar(t('rt_afternoon'),aprem,tot,'#faa61a')+
      bar(t('rt_evening'),soir,tot,'#eb459e')+bar(t('rt_latenight'),nuit2,tot,'#9b59b6'))}
   </div>`;
}
// ---------- TIME ----------
document.getElementById('tab-time').innerHTML =
  h2(t('tm_h_when')) +
  `<div class="grid cols2">
    ${card(`<div class="title-sm">${t('tm_byhour')}</div>`+cv('timeHour'))}
    ${card(`<div class="title-sm">${t('tm_byweek')}</div>`+cv('timeWeek'))}
   </div>`+
  h2(t('tm_h_heatmap')) +
  card('<div id="heatmap"></div>')+
  h2(t('tm_h_rhythm')) +
  rythmeHtml() +
  h2(t('tm_h_calendar')) +
  card('<div id="calwrap" class="scroll"></div>'+`<div class="muted" style="margin-top:8px;font-size:.78rem">${t('tm_cal_note')}</div>`)+
  h2(t('tm_h_daily')) +
  card(cv('timeDaily'));

// ---------- WORDS ----------
document.getElementById('tab-words').innerHTML =
  `<div class="grid kpis">
    ${kpi(fmt(M.words),t('wd_kpi_total'))}
    ${kpi(fmt(M.words_significant),t('wd_kpi_signif'))}
    ${kpi(fmt(M.unique_words),t('msg_kpi_unique_words'))}
   </div>`+
  `<div class="muted" style="margin:8px 0 14px;font-size:.8rem">${t('wd_note1')}</div>`+
  h2(t('wd_h_top')) +
  `<div class="muted" style="margin-bottom:10px;font-size:.82rem">${t('wd_note2')}</div>`+
  card(`<div class="scroll"><table><thead><tr><th>${t('th_word')}</th><th>${t('th_messages')}</th></tr></thead><tbody>`+tableRows(M.top_words)+'</tbody></table></div>')+
  `<div class="grid cols2" style="margin-top:16px">
   ${card(`<div class="title-sm">${t('wd_uni_title')}</div><div class="flex">`+
     (M.top_unicode_emojis.length?M.top_unicode_emojis.map(([k,v])=>`<span class="tag"><span class="emoji">${esc(k)}</span> ${fmt(v)}</span>`).join(''):`<span class="muted">${t('txt_none')}</span>`)+'</div>')}
   ${card(`<div class="title-sm">${t('wd_custom_title')}</div><div class="flex">`+
     (M.top_custom_emojis.length?M.top_custom_emojis.map(([k,v])=>`<span class="tag">:${esc(k)}: ${fmt(v)}</span>`).join(''):`<span class="muted">${t('txt_none')}</span>`)+'</div>')}
   </div>`+
  h2(t('wd_h_domains')) +
  card(`<div class="scroll"><table><thead><tr><th>${t('th_domain')}</th><th>${t('th_links')}</th></tr></thead><tbody>`+tableRows(M.top_domains)+'</tbody></table></div>');

// ---------- ACTIVITY ----------
document.getElementById('tab-activity').innerHTML =
  h2(t('act_h_main')) +
  `<div class="grid kpis">
    ${kpi(fmt(E.unique),t('act_kpi_unique'))}
    ${kpi(fmt(E.session_count),t('act_kpi_sessions'))}
    ${kpi(fmt(E.session_total_hours)+' '+t('unit_h'),t('act_kpi_total_time'))}
    ${kpi(fmt(E.session_avg_min)+' '+t('unit_min'),t('act_kpi_avg_session'))}
    ${kpi(fmt(E.app_opens),t('act_kpi_app_opens'))}
    ${kpi(fmt(E.logins),t('act_kpi_logins'))}
    ${kpi(fmt(E.notif_received),t('act_kpi_notifs'))}
    ${kpi(fmt(E.voice_events),t('act_kpi_voice'))}
    ${kpi(fmt(E.experiments),t('act_kpi_abtests'))}
    ${kpi(fmt(E.ad_decisions),t('act_kpi_ad_decisions'))}
    ${kpi(fmt(E.cpu_avg)+'%',t('act_kpi_cpu'))}
    ${kpi(fmt(E.mem_avg_mb)+' '+t('unit_mb'),t('act_kpi_mem'))}
   </div>`+
  h2(t('act_h_types')) +
  card(`<div class="scroll"><table><thead><tr><th>${t('th_type')}</th><th>${t('th_count')}</th></tr></thead><tbody>`+tableRows(E.types)+'</tbody></table></div>')+
  h2(t('act_h_daily')) +
  card(cv('actDaily'))+
  h2(t('act_h_month')) +
  card(cv('actMonth'))+
  h2(t('act_h_heatmap')) +
  card('<div id="heatmapEv"></div>')+
  (E.net_by_month && E.net_by_month.length ?
    h2(t('act_h_net_pre')+' ('+fmtGo(E.net_bytes)+' '+t('act_h_net_post')+')')+
    card(cv('actNet')) : '')+
  (E.locale && E.locale.length ?
    h2(t('act_h_locale'))+
    card('<div class="flex">'+E.locale.map(([k,v])=>`<span class="tag">${esc(k)} : ${fmt(v)}</span>`).join('')+'</div>') : '')+
  h2(t('act_h_reactions')) +
  card('<div class="flex">'+(E.reactions.length?E.reactions.map(([k,v])=>`<span class="tag"><span class="emoji">${esc(k)}</span> ${fmt(v)}</span>`).join(''):`<span class="muted">${t('txt_none_f')}</span>`)+'</div>')+
  (E.screens.length? h2(t('act_h_screens'))+card('<div class="scroll"><table><tbody>'+tableRows(E.screens)+'</tbody></table></div>'):'');

// ---------- DEVICES ----------
document.getElementById('tab-devices').innerHTML =
  h2(t('dev_h_main')) +
  `<div class="grid cols2">
    ${card(`<div class="title-sm">${t('dev_os')}</div>`+cv('devOS'))}
    ${card(`<div class="title-sm">${t('dev_browser')}</div>`+cv('devBrowser'))}
   </div>`+
  `<div class="grid cols2" style="margin-top:16px">
    ${card(`<div class="title-sm">${t('dev_models')}</div><div class="scroll"><table><tbody>`+tableRows(E.device)+'</tbody></table></div>')}
    ${card(`<div class="title-sm">${t('dev_versions')}</div><div class="scroll"><table><tbody>`+tableRows(E.client_version)+'</tbody></table></div>')}
   </div>`+
  h2(t('dev_h_channel')) + card('<div class="flex">'+E.release_channel.map(([k,v])=>`<span class="tag">${esc(k)} : ${fmt(v)}</span>`).join('')+'</div>');

// ---------- GEO ----------
document.getElementById('tab-geo').innerHTML =
  h2(t('geo_h_main')) +
  `<div class="grid cols2">
    ${card(`<div class="title-sm">${t('geo_cities')}</div><div class="scroll"><table><tbody>`+tableRows(E.city)+'</tbody></table></div>')}
    ${card(`<div class="title-sm">${t('geo_countries')}</div><div class="scroll"><table><tbody>`+tableRows(E.country)+'</tbody></table></div>')}
   </div>`+
  `<div class="grid cols2" style="margin-top:16px">
    ${card(`<div class="title-sm">${t('geo_isp')}</div><div class="scroll"><table><tbody>`+tableRows(E.isp)+'</tbody></table></div>')}
    ${card(`<div class="title-sm">${t('geo_tz')}</div><div class="scroll"><table><tbody>`+tableRows(E.timezone)+'</tbody></table></div>')}
   </div>`+
  h2(t('geo_h_history')) +
  card(`<div class="scroll"><table><thead><tr><th>${t('th_place')}</th><th>${t('th_first')}</th><th>${t('th_last')}</th></tr></thead><tbody>`+
    (E.geo_first_last.length?E.geo_first_last.map(g=>`<tr><td>${esc(g.place)}</td><td class="muted">${g.first}</td><td class="muted">${g.last}</td></tr>`).join(''):`<tr><td class="muted">${t('tbl_nodata')}</td></tr>`)+
    '</tbody></table></div>');

// ---------- ACCOUNT ----------
document.getElementById('tab-account').innerHTML =
  h2(t('acc_h_main')) +
  card('<table>'+
    [[t('acc_username'),A.username],[t('acc_globalname'),A.global_name],[t('acc_id'),A.id],
     [t('acc_email'),A.email],[t('acc_email_verified'),A.verified?t('txt_yes'):t('txt_no')],[t('acc_phone'),A.has_phone?t('txt_yes'):t('txt_no')],
     [t('acc_created'),fmtH(A.created)],[t('acc_nitro'),A.premium_until?fmtH(A.premium_until):'—'],
     [t('acc_orbs'),fmt(A.orbs)],[t('acc_guild_settings'),fmt(A.guild_settings_count)]]
    .map(([k,v])=>`<tr><td>${k}</td><td class="num">${esc(String(v==null?'—':v))}</td></tr>`).join('')+'</table>')+
  h2(t('acc_h_friends')+` (${fmt(A.friends_count)})`) +
  card('<div class="flex">'+((A.friends_sample||[]).length?A.friends_sample.map(f=>`<span class="tag">${esc(f)}</span>`).join(''):'<span class="muted">—</span>')+
    (A.friends_count>(A.friends_sample||[]).length?`<span class="pill">+${A.friends_count-A.friends_sample.length} ${t('acc_more')}</span>`:'')+'</div>')+
  h2(t('acc_h_relations')) +
  card('<div class="flex">'+Object.entries(A.relationship_types||{}).map(([k,v])=>`<span class="tag">${esc(k)} : ${fmt(v)}</span>`).join('')+'</div>')+
  h2(t('acc_h_connections')) +
  card('<div class="flex">'+((A.connections||[]).length?A.connections.map(c=>`<span class="tag">${esc(c.type)} — ${esc(c.name||'')} ${c.verified?'✔️':''}</span>`).join(''):`<span class="muted">${t('txt_none_f')}</span>`)+'</div>')+
  h2(t('acc_h_games')) +
  (function(){
    const g=A.games||[];
    const totMin=g.reduce((s,x)=>s+Math.round((x.total_duration||0)/60),0);
    const totH=(totMin/60).toFixed(1);
    return `<div class="grid kpis"><div class="kpi"><div class="v">${fmt(g.length)}</div><div class="l">${t('acc_games_tracked')}</div></div><div class="kpi"><div class="v">${fmt(totH)} ${t('unit_h')}</div><div class="l">${t('acc_games_time')}</div></div></div>`+
    card(`<div class="scroll"><table><thead><tr><th>${t('th_game')}</th><th>${t('th_duration')}</th><th>${t('th_first')}</th><th>${t('th_last')}</th></tr></thead><tbody>`+
    (g.length?g.map(x=>{const m=Math.round((x.total_duration||0)/60); const disp=m>=60?(m/60).toFixed(1)+' '+t('unit_h'):m+' '+t('unit_min'); return `<tr><td>${esc(x.name||x.app_id)}</td><td class="num">${disp}</td><td class="muted">${(x.first||'').slice(0,10)}</td><td class="muted">${(x.last||'').slice(0,10)}</td></tr>`;}).join(''):`<tr><td class="muted">${t('txt_none_f')}</td></tr>`)+
    '</tbody></table></div>');
  })();

// ---------- SERVERS ----------
document.getElementById('tab-servers').innerHTML =
  h2(t('srv_h_main')+` (${fmt(S.count)})`) +
  card(`<div class="scroll"><table><thead><tr><th>${t('th_server')}</th><th>${t('srv_audit')}</th></tr></thead><tbody>`+
    (S.servers||[]).map(s=>`<tr><td>${esc(s.name)}</td><td class="num">${fmt(s.audit)}</td></tr>`).join('')+
    '</tbody></table></div>');

// ---------- ADS ----------
document.getElementById('tab-ads').innerHTML =
  h2(t('ads_h_main')) +
  `<div class="grid kpis">${kpi(fmt(E.ad_decisions),t('ads_kpi_decisions'))}${kpi(fmt((ADS.traits||[]).length),t('ads_kpi_traits'))}${kpi(fmt(ADS.quests),t('ads_kpi_quests'))}</div>`+
  h2(t('ads_h_traits')) +
  card(`<div class="scroll"><table><thead><tr><th>${t('th_attribute')}</th><th>${t('th_value')}</th></tr></thead><tbody>`+
    ((ADS.traits||[]).length?ADS.traits.map(at=>`<tr><td>${esc(at.name)}</td><td class="muted">${esc(String(at.value==null?'':at.value))}</td></tr>`).join(''):`<tr><td class="muted">${t('txt_none')}</td></tr>`)+
    '</tbody></table></div>');

// =================== CHARTS ===================
function mkLine(id,labels,data,label,color){
  _charts.push(new Chart(document.getElementById(id),{type:'line',data:{labels,datasets:[{label,data,
    borderColor:color,backgroundColor:color+'22',fill:true,tension:.3,pointRadius:0,borderWidth:2}]},
    options:{plugins:{legend:{display:false}},scales:{x:{ticks:{maxTicksLimit:12}}}}}));}
function mkBar(id,labels,data,color,horizontal){
  _charts.push(new Chart(document.getElementById(id),{type:'bar',data:{labels,datasets:[{data,backgroundColor:color}]},
    options:{indexAxis:horizontal?'y':'x',plugins:{legend:{display:false}}}}));}
function mkDoughnut(id,labels,data){
  _charts.push(new Chart(document.getElementById(id),{type:'doughnut',data:{labels,datasets:[{data,backgroundColor:C}]},
    options:{plugins:{legend:{position:'right',labels:{boxWidth:12}}}}}));}

mkLine('ovMonth', M.by_month.map(x=>x[0]), M.by_month.map(x=>x[1]),t('chart_messages'),'#5865F2');
mkDoughnut('ovType', M.channel_type.map(x=>x[0]), M.channel_type.map(x=>x[1]));
mkBar('msgYear', M.by_year.map(x=>x[0]), M.by_year.map(x=>x[1]),'#00d4ff');
mkBar('peopleDM', M.top_dms.slice(0,12).map(x=>x[0]), M.top_dms.slice(0,12).map(x=>x[1]),'#eb459e',true);
mkBar('peopleSrv', M.top_servers.slice(0,12).map(x=>x[0]), M.top_servers.slice(0,12).map(x=>x[1]),'#3ba55d',true);
mkBar('timeHour', [...Array(24).keys()].map(h=>h+t('unit_h')), M.by_hour,'#faa61a');
mkBar('timeWeek', WD, M.by_weekday,'#00d4ff');
mkLine('timeDaily', M.by_date.map(x=>x[0]), M.by_date.map(x=>x[1]),t('chart_messages_day'),'#eb459e');
mkDoughnut('devOS', E.os.map(x=>x[0]), E.os.map(x=>x[1]));
mkDoughnut('devBrowser', E.browser.map(x=>x[0]), E.browser.map(x=>x[1]));
if(document.getElementById('actDaily'))
  mkLine('actDaily', E.by_date.map(x=>x[0]), E.by_date.map(x=>x[1]),t('chart_events_day'),'#00d4ff');
if(document.getElementById('msgLen'))
  mkBar('msgLen', M.length_buckets.map(x=>x[0]), M.length_buckets.map(x=>x[1]),'#5865F2');
if(document.getElementById('msgComp'))
  mkDoughnut('msgComp', [t('comp_puretext'),t('comp_link'),t('comp_attachment'),t('comp_mention'),t('comp_emoji')],
    [M.msgs_pure_text, M.msgs_with_link, M.msgs_with_attachment, M.msgs_with_mention, M.msgs_with_emoji]);
if(document.getElementById('actNet') && E.net_by_month)
  mkLine('actNet', E.net_by_month.map(x=>x[0]), E.net_by_month.map(x=>(x[1]/1073741824).toFixed(2)),t('chart_gb'),'#3ba55d');

// Heatmap
(function(){
  const hm=M.heatmap; let mx=1;
  hm.forEach(r=>r.forEach(v=>{if(v>mx)mx=v;}));
  const el=document.getElementById('heatmap'); if(!el)return;
  let html='<div class="heat"><div class="lab"></div>';
  for(let h=0;h<24;h++) html+=`<div class="lab">${h}</div>`;
  for(let wd=0;wd<7;wd++){
    html+=`<div class="lab">${WD[wd]}</div>`;
    for(let h=0;h<24;h++){
      const v=hm[wd][h], a=v/mx;
      const col=`rgba(88,101,242,${0.08+a*0.92})`;
      html+=`<div class="cell" title="${WD[wd]} ${h}${t('unit_h')} : ${v} ${t('unit_msg')}" style="background:${v?col:'#24273f'}"></div>`;
    }
  }
  html+='</div>';
  el.innerHTML=html;
})();

// Heatmap événements
(function(){
  const hm=E.heatmap; if(!hm) return; let mx=1;
  hm.forEach(r=>r.forEach(v=>{if(v>mx)mx=v;}));
  const el=document.getElementById('heatmapEv'); if(!el)return;
  let html='<div class="heat"><div class="lab"></div>';
  for(let h=0;h<24;h++) html+=`<div class="lab">${h}</div>`;
  for(let wd=0;wd<7;wd++){
    html+=`<div class="lab">${WD[wd]}</div>`;
    for(let h=0;h<24;h++){
      const v=hm[wd][h], a=v/mx;
      const col=`rgba(0,212,255,${0.08+a*0.92})`;
      html+=`<div class="cell" title="${WD[wd]} ${h}${t('unit_h')} : ${v}" style="background:${v?col:'#24273f'}"></div>`;
    }
  }
  html+='</div>';
  el.innerHTML=html;
})();

// Calendrier de contributions (style GitHub)
(function(){
  const el=document.getElementById('calwrap'); if(!el||!M.by_date||!M.by_date.length)return;
  const map={}; let mx=1;
  M.by_date.forEach(([d,v])=>{map[d]=v; if(v>mx)mx=v;});
  const first=new Date(M.by_date[0][0]+'T00:00:00');
  const last=new Date(M.by_date[M.by_date.length-1][0]+'T00:00:00');
  // commencer au lundi de la semaine du premier jour
  const start=new Date(first); start.setDate(start.getDate()-((start.getDay()+6)%7));
  let cells='', months='', lastMonth=-1, weeks=0;
  for(let dt=new Date(start); dt<=last; dt.setDate(dt.getDate()+1)){
    const iso=dt.toISOString().slice(0,10);
    const v=map[iso]||0, a=v/mx;
    const col=v?`rgba(88,101,242,${0.18+a*0.82})`:'#24273f';
    cells+=`<div class="d" title="${iso} : ${v} ${t('unit_msg')}" style="background:${col}"></div>`;
  }
  // étiquettes de mois (approx, une par ~4 semaines)
  for(let dt=new Date(start); dt<=last; dt.setDate(dt.getDate()+7)){
    if(dt.getMonth()!==lastMonth){ months+=`<span style="min-width:46px">${MN[dt.getMonth()]} ${String(dt.getFullYear()).slice(2)}</span>`; lastMonth=dt.getMonth(); }
    else { months+=`<span style="min-width:14px"></span>`; }
  }
  el.innerHTML=`<div class="calmonths">${months}</div><div class="cal">${cells}</div>`;
})();

// Activité par mois (événements)
if(document.getElementById('actMonth') && E.by_month)
  mkBar('actMonth', E.by_month.map(x=>x[0]), E.by_month.map(x=>x[1]),'#9b59b6');

document.querySelectorAll('section').forEach(x=>x.classList.remove('active'));
const _act=document.getElementById('tab-'+activeTab); if(_act) _act.classList.add('active');
} // end buildUI

document.querySelectorAll('#langSwitch span[data-lang]').forEach(function(s){
  s.addEventListener('click', function(){ applyLang(s.dataset.lang); });
});
applyLang(LANG);
</script>
</body>
</html>
""".replace("__DATA__", data_json)


def _regen():
    """Régénère rapport/rapport.html à partir de rapport/data.json.

    Permet d'exécuter directement `python render.py` sans relancer
    l'analyse complète (utile après une modification du template).
    """
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "rapport")
    data_path = os.path.join(out_dir, "data.json")
    html_path = os.path.join(out_dir, "rapport.html")
    if not os.path.exists(data_path):
        print("data.json introuvable. Lance d'abord : python analyze.py")
        raise SystemExit(1)
    with open(data_path, encoding="utf-8") as f:
        payload = json.load(f)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(render_html(payload))
    print(">> rapport.html régénéré ->", html_path)


if __name__ == "__main__":
    _regen()
