# -*- coding: utf-8 -*-
"""
StandCheck
Wo stehe ich beruflich? Lohn anonym teilen, mit dem gleichen Beruf vergleichen
und sehen, was gut ist und was besser sein müsste.

Speicher:
- Wenn in den Streamlit Secrets ein Supabase Zugang hinterlegt ist, werden die Daten dort gespeichert.
- Sonst wird eine lokale SQLite Datei benutzt (auf Streamlit Cloud gehen die Daten beim Neustart verloren).
"""
import random
import sqlite3
from pathlib import Path

import zlib

import altair as alt
import pandas as pd
import streamlit as st

from berufe import ALLE_BERUFE, BERUF_INFO, BERUFE, BRANCHEN

st.set_page_config(page_title="StandCheck · Wo stehst du beruflich?", page_icon="🚦", layout="wide")

# ---------------------------------------------------------------------------
# Grunddaten
# ---------------------------------------------------------------------------
MIN_GRUPPE = 10  # so viele Einträge braucht es mindestens, bevor ein Vergleich angezeigt wird

ALLE_BRANCHEN = "Alle Branchen"
REGIONEN = {
    "Zürich": 1.08, "Genferseeregion": 1.06, "Nordwestschweiz": 1.02, "Espace Mittelland": 0.98,
    "Zentralschweiz": 1.00, "Ostschweiz": 0.95, "Tessin": 0.86,
}
AUSBILDUNG = ["Lehre (EFZ)", "Höhere Fachschule / Fachausweis", "Fachhochschule", "Universität", "Andere"]
FIRMENGROESSE = ["1 bis 9", "10 bis 49", "50 bis 249", "250 und mehr"]
SPALTEN = ["funktion", "branche", "region", "erfahrung", "ausbildung", "pensum", "lohn_jahr",
           "firmengroesse", "zufriedenheit", "stress", "lernen", "weiterbildung", "aufstieg", "testdaten",
           "alter_jahre"]

# Startwerte der Eingaben (in st.session_state, damit nichts verloren geht)
STARTWERTE = {
    "branche_wahl": ALLE_BRANCHEN, "funktion": "Einkäufer/in", "eigener_beruf_an": False, "eigener_beruf": "",
    "region": "Nordwestschweiz", "firmengroesse": "50 bis 249",
    "erfahrung": 5, "ausbildung": "Lehre (EFZ)", "pensum": 100,
    "lohn_monat": 6500, "dreizehnter": True, "ehrlich": False, "alter_jahre": 30,
}
for _k, _v in STARTWERTE.items():
    st.session_state[_k] = st.session_state[_k] if _k in st.session_state else _v

# ---------------------------------------------------------------------------
# Design (gleicher Stil wie AutoBudget)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, [class*="css"], button, input, textarea { font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* ---------- Animierter Aurora Hintergrund ---------- */
[data-testid="stAppViewContainer"] { background: #F3F6FB; isolation: isolate; }
[data-testid="stAppViewContainer"]::before {
    content: ""; position: fixed; inset: -25%; z-index: -1; pointer-events: none;
    background:
        radial-gradient(38% 38% at 20% 20%, rgba(45,212,191,.40), transparent 70%),
        radial-gradient(34% 34% at 82% 12%, rgba(99,102,241,.28), transparent 70%),
        radial-gradient(40% 40% at 72% 82%, rgba(56,189,248,.30), transparent 70%),
        radial-gradient(30% 30% at 12% 88%, rgba(244,114,182,.20), transparent 70%);
    filter: blur(50px);
    animation: aurora 24s ease-in-out infinite alternate;
}
[data-testid="stAppViewContainer"]::after {
    content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
    background-image: linear-gradient(rgba(15,23,42,.035) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(15,23,42,.035) 1px, transparent 1px);
    background-size: 44px 44px;
    -webkit-mask-image: radial-gradient(ellipse at 50% 0%, #000 30%, transparent 75%);
            mask-image: radial-gradient(ellipse at 50% 0%, #000 30%, transparent 75%);
}
@keyframes aurora {
    0%   { transform: translate(0, 0) rotate(0deg) scale(1); }
    50%  { transform: translate(4%, -3%) rotate(10deg) scale(1.08); }
    100% { transform: translate(-4%, 3%) rotate(-8deg) scale(1); }
}
[data-testid="stHeader"] { background: transparent; }
html { font-size: 17px; }
.block-container, [data-testid="stMainBlockContainer"] { padding: 1.4rem 2.5rem 2rem !important; max-width: 100% !important; }
[data-testid="stMain"] [data-testid="stWidgetLabel"] p { font-size: .95rem !important; font-weight: 600; color: #334155; }
[data-testid="stMain"] p, [data-testid="stMain"] li { font-size: 1rem; }
#MainMenu, footer, [data-testid="stToolbarActions"] { visibility: hidden; }

/* ---------- Seitenleiste ---------- */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0B1220 0%, #111C2E 55%, #0F2A2E 100%); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] small, [data-testid="stSidebar"] li,
[data-testid="stSidebar"] [data-testid="stMetricValue"] div,
[data-testid="stSidebar"] [data-testid="stMetricLabel"] div { color: #E2E8F0 !important; }
[data-testid="stSidebar"] h2 { font-size: .95rem !important; margin-top: .8rem; letter-spacing: .01em; }
[data-testid="stSidebar"] hr { border-color: #24344F; }
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(45,212,191,.16), rgba(99,102,241,.10));
    border: 1px solid rgba(45,212,191,.35); box-shadow: none; }
.brand { display: flex; align-items: center; gap: 10px; font-size: 1.25rem; font-weight: 800; color: #FFFFFF; padding: 4px 0 6px; }
.brand .logo { width: 36px; height: 36px; border-radius: 11px; display: inline-flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #2DD4BF, #6366F1); box-shadow: 0 6px 18px rgba(45,212,191,.35); }
.brand span.acc { color: #2DD4BF; }
.sb-schritt { display: flex; gap: 10px; align-items: flex-start; margin: 10px 0; color: #CBD5E1; font-size: .88rem; line-height: 1.4; }
.sb-schritt .n { flex: none; width: 24px; height: 24px; border-radius: 999px; background: rgba(45,212,191,.18);
    border: 1px solid rgba(45,212,191,.45); color: #5EEAD4; font-weight: 800; font-size: .78rem;
    display: inline-flex; align-items: center; justify-content: center; }
.sb-box { background: rgba(255,255,255,.05); border: 1px solid #24344F; border-radius: 14px; padding: 12px 14px;
    color: #CBD5E1; font-size: .84rem; line-height: 1.45; margin-top: 8px; }
.sb-box b { color: #5EEAD4; }

/* ---------- Kopfbereich ---------- */
.hero {
    position: relative; overflow: hidden; display: flex; justify-content: space-between; align-items: center; gap: 24px;
    background: linear-gradient(120deg, #0B1220 0%, #0F2A2E 45%, #0E7490 80%, #0EA5A4 100%);
    background-size: 200% 200%; animation: shift 14s ease infinite;
    border-radius: 24px; padding: 22px 30px; color: #FFFFFF; margin-bottom: 16px;
    box-shadow: 0 20px 50px -12px rgba(15,23,42,.45);
}
.hero::before { content: ""; position: absolute; width: 380px; height: 380px; right: -90px; top: -140px; border-radius: 50%;
    background: radial-gradient(circle, rgba(45,212,191,.45), transparent 65%); }
.hero::after { content: ""; position: absolute; inset: 0; pointer-events: none;
    background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,.08) 50%, transparent 60%);
    background-size: 250% 100%; animation: shine 7s ease-in-out infinite; }
@keyframes shift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@keyframes shine { 0% { background-position: 150% 0; } 100% { background-position: -100% 0; } }
.hero .left { position: relative; z-index: 1; }
.hero .badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,.12); padding: 6px 12px;
    border: 1px solid rgba(255,255,255,.18); border-radius: 999px; font-size: .78rem; font-weight: 600; }
.hero .dot { width: 8px; height: 8px; border-radius: 50%; background: #34D399; box-shadow: 0 0 0 0 rgba(52,211,153,.7); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(52,211,153,.6); } 70% { box-shadow: 0 0 0 10px rgba(52,211,153,0); } 100% { box-shadow: 0 0 0 0 rgba(52,211,153,0); } }
.hero .title { font-size: 1.9rem; font-weight: 800; margin: 8px 0 0; line-height: 1.12; letter-spacing: -.02em; }
.hero .title span { background: linear-gradient(90deg, #5EEAD4, #A5B4FC); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero .text { color: #CBD5E1; font-size: .93rem; max-width: 640px; margin-top: 6px; }
.hero .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.hero .chip { background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.16); padding: 6px 12px; border-radius: 10px; font-size: .8rem; }
.hero .chip b { color: #FFFFFF; }
.ring { position: relative; z-index: 1; flex: 0 0 auto; width: 112px; height: 112px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; }
.ring .inner { width: 88px; height: 88px; border-radius: 50%; background: #0B1220; display: flex; flex-direction: column;
    align-items: center; justify-content: center; box-shadow: inset 0 0 20px rgba(0,0,0,.4); }
.ring .pct { font-size: 1.35rem; font-weight: 800; }
.ring .lbl { font-size: .58rem; color: #94A3B8; text-align: center; line-height: 1.2; padding: 0 6px; }

/* ---------- Grosser Knopf «Teilen» ---------- */
.st-key-teilen_knopf button {
    min-height: 58px; border-radius: 14px !important; border: none !important;
    background: linear-gradient(135deg, #0EA5A4, #6366F1) !important; color: #FFFFFF !important;
    box-shadow: 0 10px 24px -8px rgba(14,165,164,.7) !important; transition: transform .2s ease, box-shadow .2s ease; }
.st-key-teilen_knopf button:hover { transform: translateY(-2px); box-shadow: 0 14px 30px -8px rgba(14,165,164,.8) !important; }
.st-key-teilen_knopf button p { font-size: 1.05rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
.st-key-teilen_knopf button:disabled { opacity: .45; transform: none; }

/* ---------- Kennzahl Karten (Glas) ---------- */
.kpi { position: relative; overflow: hidden; background: rgba(255,255,255,.72); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border-radius: 20px; padding: 18px 20px; height: 100%; border: 1px solid rgba(255,255,255,.8);
    box-shadow: 0 10px 30px -12px rgba(15,23,42,.18); transition: transform .25s ease, box-shadow .25s ease; }
.kpi:hover { transform: translateY(-4px); box-shadow: 0 18px 40px -14px rgba(15,23,42,.28); }
.kpi .label { font-size: .92rem; color: #64748B; font-weight: 600; display: flex; gap: 10px; align-items: center; }
.kpi .icon { width: 36px; height: 36px; border-radius: 11px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.05rem; }
.kpi .value { font-size: 2.15rem; font-weight: 800; color: #0F172A; margin-top: 12px; letter-spacing: -.02em; }
.kpi .sub { font-size: .86rem; color: #94A3B8; margin-top: 4px; font-weight: 600; }
.kpi .bar { height: 6px; border-radius: 999px; background: #E2E8F0; margin-top: 10px; overflow: hidden; }
.kpi .bar > div { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #2DD4BF, #6366F1); }
.kpi.accent { background: linear-gradient(135deg, #0EA5A4 0%, #0E7490 60%, #4F46E5 130%); border: none;
    box-shadow: 0 16px 36px -12px rgba(14,165,164,.6); }
.kpi.accent .label, .kpi.accent .sub { color: #CCFBF1; }
.kpi.accent .value { color: #FFFFFF; }
.kpi.accent .bar { background: rgba(255,255,255,.2); }
.kpi.accent .bar > div { background: #FFFFFF; }

/* ---------- Karten für Abschnitte ---------- */
[class*="st-key-card"] {
    background: rgba(255,255,255,.74); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,.85); border-radius: 24px;
    padding: 24px 26px; box-shadow: 0 12px 34px -14px rgba(15,23,42,.18);
}
.sec { font-size: 1.25rem; font-weight: 800; color: #0F172A; display: flex; gap: 10px; align-items: center; letter-spacing: -.01em; }
.sec .ic { width: 32px; height: 32px; border-radius: 10px; display: inline-flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #CCFBF1, #E0E7FF); font-size: .95rem; }
.secsub { color: #64748B; font-size: .92rem; margin: 4px 0 14px 42px; }
.abschnitt { display: flex; align-items: center; gap: 12px; margin: 30px 0 14px; }
.abschnitt:first-child { margin-top: 4px; }
.abschnitt .num { width: 28px; height: 28px; border-radius: 999px; background: linear-gradient(135deg, #0B1220, #0F4C4F);
    color: #FFFFFF; font-weight: 800; font-size: .85rem; display: inline-flex; align-items: center; justify-content: center; flex: none; }
.abschnitt .txt { font-weight: 800; font-size: 1.05rem; color: #0F172A; letter-spacing: -.01em; white-space: nowrap; }
.abschnitt .sub { color: #64748B; font-size: .82rem; white-space: nowrap; }
.abschnitt .line { height: 1px; background: linear-gradient(90deg, #CBD5E1, transparent); flex: 1; }
.trenner { margin: 18px 0 14px; border: none; border-top: 1px solid #E2E8F0; }

/* ---------- Slider ---------- */
[data-testid="stSlider"] [role="slider"] { width: 20px !important; height: 20px !important; background: #FFFFFF !important;
    border: 4px solid #0EA5A4 !important; box-shadow: 0 0 0 6px rgba(14,165,164,.16), 0 4px 10px rgba(15,23,42,.25) !important;
    transition: box-shadow .2s ease; }
[data-testid="stSlider"] [role="slider"]:hover { box-shadow: 0 0 0 10px rgba(14,165,164,.2), 0 4px 12px rgba(15,23,42,.3) !important; }
[data-testid="stSliderThumbValue"] { background: #0B1220; color: #FFFFFF !important; padding: 2px 9px; border-radius: 999px;
    font-weight: 700; font-size: .72rem !important; }
[data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] { color: #94A3B8 !important; font-size: .72rem; }

/* ---------- Eingaben ---------- */
[data-testid="stMain"] [data-testid="stNumberInputContainer"], [data-testid="stMain"] [data-baseweb="select"] > div {
    border-radius: 12px !important; border: 1.5px solid #0EA5A4 !important; transition: box-shadow .2s ease, border-color .2s ease; }
[data-testid="stMain"] [data-testid="stNumberInputContainer"]:focus-within, [data-testid="stMain"] [data-baseweb="select"] > div:focus-within {
    border-color: #0F766E !important; box-shadow: 0 0 0 3px rgba(14,165,164,.18) !important; }
[data-testid="stMain"] [data-testid="stSelectbox"] [role="group"],
[data-testid="stMain"] [data-testid="stMultiSelect"] [role="group"],
[data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMain"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    border: 1.5px solid #0EA5A4 !important; border-radius: 12px !important; background: #FFFFFF !important;
    transition: box-shadow .2s ease, border-color .2s ease; }
[data-testid="stMain"] [data-testid="stSelectbox"] [role="group"]:focus-within,
[data-testid="stMain"] [data-testid="stMultiSelect"] [role="group"]:focus-within,
[data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
[data-testid="stMain"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
    border-color: #0F766E !important; box-shadow: 0 0 0 3px rgba(14,165,164,.18) !important; }
[data-testid="stMain"] [data-testid="stNumberInputContainer"] { background: #FFFFFF; }
[data-testid="stMain"] [data-testid="stButtonGroup"] button { border-radius: 12px !important; font-weight: 600; }
[data-testid="stMain"] [data-testid="stCheckbox"] label p { font-weight: 600; color: #334155; }
[data-testid="stMetric"] { background: rgba(248,250,252,.85); border: 1px solid #E2E8F0; border-radius: 16px; padding: 14px 16px; }
[data-testid="stMetricValue"] { font-weight: 800; color: #0F172A; letter-spacing: -.02em; }
[data-testid="stExpander"] details { background: rgba(255,255,255,.6); border-radius: 16px; border: 1px solid #E2E8F0; }
[data-testid="stAlert"] { border-radius: 16px; backdrop-filter: blur(8px); }

/* ---------- Jahreslohn Feld (türkis) ---------- */
.jahreslohn { background: linear-gradient(135deg, #0EA5A4, #0E7490); border-radius: 14px; padding: 12px 16px; color: #FFFFFF;
    box-shadow: 0 8px 20px -8px rgba(14,165,164,.7); margin-top: 2px; }
.jahreslohn span { display: block; font-size: .8rem; color: #CCFBF1; font-weight: 600; }
.jahreslohn b { font-size: 1.45rem; font-weight: 800; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }

/* ---------- Ergebnis Schild ---------- */
.verdict { display: flex; align-items: center; gap: 18px; border-radius: 20px; padding: 20px 24px; margin: 4px 0 16px; }
.verdict .vi { font-size: 2.2rem; }
.verdict .vt { font-size: 1.45rem; font-weight: 800; letter-spacing: -.01em; }
.verdict .vx { font-size: 1rem; margin-top: 2px; }
.verdict .vp { margin-left: auto; text-align: right; }
.verdict .vl { font-size: .8rem; opacity: .8; }
.verdict .vv { font-size: 1.6rem; font-weight: 800; }
.verdict.ok { background: linear-gradient(120deg, #ECFDF5, #CCFBF1); border: 1.5px solid #5EEAD4; color: #065F46; }
.verdict.knapp { background: linear-gradient(120deg, #FFFBEB, #FEF3C7); border: 1.5px solid #FCD34D; color: #92400E; }
.verdict.nein { background: linear-gradient(120deg, #FFF1F2, #FFE4E6); border: 1.5px solid #FDA4AF; color: #9F1239; }

/* ---------- Kacheln: Spanne der Löhne ---------- */
.tiles3 { display: flex; gap: 14px; margin-top: 4px; }
.tiles3 .t { flex: 1 1 0; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 16px; padding: 14px 16px; }
.tiles3 .t span { display: block; font-size: .8rem; color: #64748B; font-weight: 600; }
.tiles3 .t b { display: block; font-size: 1.35rem; color: #0F172A; font-weight: 800; letter-spacing: -.02em;
    margin-top: 6px; font-variant-numeric: tabular-nums; }
.tiles3 .t.mitte { background: linear-gradient(135deg, #CCFBF1, #E0E7FF); border-color: #99F6E4; }

/* ---------- Ampel Balken ---------- */
.hbars .hb { margin: 0 0 16px; }
.hbars .hb .top { display: flex; justify-content: space-between; gap: 10px; font-size: .95rem; color: #334155; font-weight: 700; }
.hbars .hb .top b { font-weight: 800; white-space: nowrap; }
.hbars .hb .top small { color: #94A3B8; font-weight: 600; margin-left: 6px; }
.hbars .hb .trk { height: 12px; border-radius: 999px; background: #E2E8F0; margin-top: 8px; overflow: hidden; }
.hbars .hb .trk > div { height: 100%; border-radius: 999px; }
.hbars .hb .hint { font-size: .78rem; color: #94A3B8; margin-top: 5px; }
.hbars .hb.ich .top span { color: #0F766E; }

/* ---------- Tipp Karten ---------- */
.tipp { position: relative; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px; padding: 18px 20px; height: 100%;
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease; }
.tipp:hover { transform: translateY(-4px); box-shadow: 0 18px 36px -16px rgba(15,23,42,.3); border-color: #99F6E4; }
.tipp.wichtig { border: 2px solid transparent;
    background: linear-gradient(#FFFFFF, #FFFFFF) padding-box, linear-gradient(135deg, #2DD4BF, #6366F1) border-box; }
.tipp .rank { display: inline-block; font-size: .7rem; font-weight: 800; letter-spacing: .06em; text-transform: uppercase;
    color: #0F766E; background: #CCFBF1; padding: 4px 10px; border-radius: 999px; }
.tipp.wichtig .rank { color: #FFFFFF; background: linear-gradient(135deg, #0EA5A4, #6366F1); }
.tipp .name { font-size: 1.2rem; font-weight: 800; color: #0F172A; margin: 10px 0 6px; letter-spacing: -.01em; }
.tipp .txt { font-size: .92rem; color: #475569; line-height: 1.45; }

/* ---------- Gesperrt ---------- */
.gesperrt { display: flex; align-items: center; gap: 16px; background: linear-gradient(120deg, #0B1220, #0F4C4F);
    border-radius: 20px; padding: 20px 24px; color: #E2E8F0; box-shadow: 0 14px 32px -14px rgba(15,23,42,.5); }
.gesperrt .i { font-size: 2rem; }
.gesperrt .t { font-weight: 800; font-size: 1.1rem; color: #FFFFFF; }
.gesperrt .s { font-size: .9rem; color: #94A3B8; margin-top: 2px; }

/* ---------- Handy: kompakt ---------- */
@media (max-width: 700px) {
    html { font-size: 15px; }
    .block-container, [data-testid="stMainBlockContainer"] { padding: 4.2rem .7rem 1.5rem !important; }
    .abschnitt { margin: 22px 0 10px; }
    .abschnitt .sub { display: none; }
    .hero { padding: 16px 18px; border-radius: 20px; gap: 12px; margin-bottom: 10px; }
    .hero .badge, .hero .text, .hero .chips { display: none; }
    .hero .title { font-size: 1.35rem; margin: 0; }
    .ring { width: 80px; height: 80px; }
    .ring .inner { width: 64px; height: 64px; }
    .ring .pct { font-size: 1.05rem; }
    .ring .lbl { display: none; }
    .st-key-eingaben [data-testid="stHorizontalBlock"], .st-key-kpis [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important; gap: .6rem !important; }
    .st-key-eingaben [data-testid="stColumn"], .st-key-eingaben [data-testid="column"],
    .st-key-kpis [data-testid="stColumn"], .st-key-kpis [data-testid="column"] {
        width: calc(50% - .3rem) !important; flex: 1 1 calc(50% - .3rem) !important; min-width: calc(50% - .3rem) !important; }
    .kpi { padding: 12px 12px; border-radius: 16px; }
    .kpi .icon { display: none; }
    .kpi .label { font-size: .74rem; }
    .kpi .value { font-size: 1.25rem; margin-top: 6px; }
    .kpi .sub, .kpi .bar { display: none; }
    [class*="st-key-card"] { padding: 16px 14px; border-radius: 18px; }
    .secsub { margin-left: 0; }
    .verdict { flex-wrap: wrap; padding: 16px; }
    .verdict .vt { font-size: 1.2rem; }
    .verdict .vx { font-size: .9rem; }
    .verdict .vp { margin-left: 0; text-align: left; }
    .tiles3 { flex-wrap: wrap; }
    .tiles3 .t { flex: 1 1 calc(50% - 7px); }
    .gesperrt { padding: 16px; }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Kleine Bausteine
# ---------------------------------------------------------------------------
def titel(icon, text, sub=""):
    html = f'<div class="sec"><span class="ic">{icon}</span>{text}</div>'
    if sub:
        html += f'<div class="secsub">{sub}</div>'
    st.markdown(html, unsafe_allow_html=True)


def abschnitt(nummer, text, sub=""):
    st.markdown(
        f'<div class="abschnitt"><span class="num">{nummer}</span>'
        f'<span class="txt">{text}</span>' + (f'<span class="sub">{sub}</span>' if sub else "") +
        f'<span class="line"></span></div>', unsafe_allow_html=True)


def kpi(icon, farbe, label, wert, sub="", accent=False, anteil=None, rand="#2DD4BF"):
    klasse = "kpi accent" if accent else "kpi"
    stil = "" if accent else (f'style="border:1.5px solid {rand}55;box-shadow:0 0 0 4px {rand}10,'
                              f'0 14px 32px -16px {rand}90"')
    bar = ""
    if anteil is not None:
        bar = (f'<div class="bar"><div style="width:{max(0, min(anteil, 1)) * 100:.0f}%;'
               f'{"" if accent else "background:" + rand}"></div></div>')
    sub_stil = "" if accent else f'style="color:{rand}"'
    return (f'<div class="{klasse}" {stil}><div class="label"><span class="icon" style="background:{farbe}">{icon}</span>'
            f'{label}</div><div class="value">{wert}</div>{bar}<div class="sub" {sub_stil}>{sub}</div></div>')


def chf(x):
    return f"CHF {x:,.0f}".replace(",", "'")


def stufe(wert, rot_bis, gelb_bis):
    """Ampel: gibt (Text, Klasse, Farbverlauf, Farbe) zurück."""
    if wert < rot_bis:
        return "schlecht", "nein", "linear-gradient(90deg, #FB7185, #EF4444)", "#E11D48"
    if wert < gelb_bis:
        return "mittel", "knapp", "linear-gradient(90deg, #FBBF24, #F59E0B)", "#D97706"
    return "gut", "ok", "linear-gradient(90deg, #2DD4BF, #10B981)", "#059669"


def altersgruppe(alter):
    if alter is None or pd.isna(alter):
        return None
    alter = int(alter)
    if alter < 25:
        return "unter 25"
    if alter < 35:
        return "25 bis 34"
    if alter < 45:
        return "35 bis 44"
    if alter < 55:
        return "45 bis 54"
    return "55 und älter"


def erfahrungsstufe(jahre):
    if jahre < 5:
        return "0 bis 4 Jahre"
    if jahre < 10:
        return "5 bis 9 Jahre"
    if jahre < 20:
        return "10 bis 19 Jahre"
    return "20 Jahre und mehr"


# ---------------------------------------------------------------------------
# Speicher (Supabase oder SQLite)
# ---------------------------------------------------------------------------
def supabase_client():
    try:
        if "supabase" not in st.secrets:
            return None
        from supabase import create_client
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except Exception:
        return None


DB_DATEI = Path(__file__).parent / "standcheck.db"


def sqlite_verbindung():
    con = sqlite3.connect(DB_DATEI)
    con.execute(
        """CREATE TABLE IF NOT EXISTS loehne (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funktion TEXT, branche TEXT, region TEXT, erfahrung INTEGER, ausbildung TEXT,
            pensum INTEGER, lohn_jahr REAL, firmengroesse TEXT, zufriedenheit INTEGER,
            stress INTEGER, lernen INTEGER, weiterbildung INTEGER, aufstieg INTEGER,
            testdaten INTEGER DEFAULT 0, alter_jahre INTEGER
        )""")
    spalten = [z[1] for z in con.execute("PRAGMA table_info(loehne)")]
    if "alter_jahre" not in spalten:
        con.execute("ALTER TABLE loehne ADD COLUMN alter_jahre INTEGER")
    # Ältere Testdaten ohne Alter: grob aus der Erfahrung schätzen (nur erfundene Werte)
    con.execute("UPDATE loehne SET alter_jahre = MIN(erfahrung + 19 + (id % 7), 64) "
                "WHERE testdaten = 1 AND alter_jahre IS NULL")
    con.commit()
    return con


def zeilen_speichern(zeilen):
    """Speichert Einträge und gibt die ID des letzten zurück."""
    sb = supabase_client()
    if sb is not None:
        letzte_id = None
        for start in range(0, len(zeilen), 200):
            teil = zeilen[start:start + 200]
            try:
                antwort = sb.table("loehne").insert(teil).execute()
            except Exception:
                # Tabelle noch ohne Spalte alter_jahre (siehe supabase_tabelle.sql)
                antwort = sb.table("loehne").insert(
                    [{k: v for k, v in z.items() if k != "alter_jahre"} for z in teil]).execute()
            if antwort.data:
                letzte_id = antwort.data[-1].get("id")
        return letzte_id
    con = sqlite_verbindung()
    platzhalter = ",".join("?" for _ in SPALTEN)
    cur = con.cursor()
    for z in zeilen:
        cur.execute(f"INSERT INTO loehne ({','.join(SPALTEN)}) VALUES ({platzhalter})",
                    [int(z[s]) if isinstance(z[s], bool) else z[s] for s in SPALTEN])
    letzte_id = cur.lastrowid
    con.commit()
    con.close()
    return letzte_id


@st.cache_data(ttl=60)
def alle_eintraege():
    sb = supabase_client()
    if sb is not None:
        daten, start = [], 0
        while True:
            antwort = sb.table("loehne").select("*").range(start, start + 999).execute()
            daten.extend(antwort.data)
            if len(antwort.data) < 1000:
                break
            start += 1000
        df = pd.DataFrame(daten)
    else:
        con = sqlite_verbindung()
        df = pd.read_sql("SELECT * FROM loehne", con)
        con.close()
    if df.empty:
        return pd.DataFrame(columns=["id"] + SPALTEN + ["lohn_100"])
    df["testdaten"] = df["testdaten"].fillna(False).astype(bool)
    if "alter_jahre" not in df.columns:
        df["alter_jahre"] = None
    df["lohn_100"] = df["lohn_jahr"].astype(float) / df["pensum"].astype(float) * 100
    return df


TESTDATEN_PRO_BERUF = 80
TESTDATEN_VERSION = "3"   # erhöhen, wenn sich die Art der Testdaten ändert (alte Testdaten werden dann ersetzt)


def alte_testdaten_ersetzen():
    """Nur lokal (SQLite): Testdaten einer älteren Version löschen, damit sie neu erzeugt werden."""
    if supabase_client() is not None:
        return
    con = sqlite_verbindung()
    con.execute("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)")
    zeile = con.execute("SELECT v FROM meta WHERE k = 'testdaten_version'").fetchone()
    if zeile is None or zeile[0] != TESTDATEN_VERSION:
        con.execute("DELETE FROM loehne WHERE testdaten = 1")
        con.execute("INSERT OR REPLACE INTO meta (k, v) VALUES ('testdaten_version', ?)", (TESTDATEN_VERSION,))
        con.commit()
        alle_eintraege.clear()
    con.close()


def testdaten_anlegen():
    """Legt erfundene Testdaten an, damit jeder Beruf sofort Vergleichswerte hat.
    Hat ein Beruf weniger als TESTDATEN_PRO_BERUF Testwerte (z.B. weil er neu ist), wird aufgefüllt."""
    alte_testdaten_ersetzen()
    df = alle_eintraege()
    anzahl = df.loc[df["testdaten"], "funktion"].value_counts() if not df.empty else pd.Series(dtype=int)
    zeilen = []
    for beruf in ALLE_BERUFE:
        schon_da = int(anzahl.get(beruf, 0))
        if schon_da >= TESTDATEN_PRO_BERUF:
            continue
        branche, basis = BERUF_INFO[beruf]
        zufall = random.Random(zlib.crc32(beruf.encode("utf-8")) + schon_da)
        for _ in range(TESTDATEN_PRO_BERUF - schon_da):
            region = zufall.choices(list(REGIONEN), weights=[22, 14, 16, 18, 10, 14, 6])[0]
            pensum = zufall.choices([100, 90, 80, 60], weights=[70, 10, 15, 5])[0]
            ausbildung = zufall.choice(AUSBILDUNG[:4])
            startalter = {"Lehre (EFZ)": 18, "Höhere Fachschule / Fachausweis": 22,
                          "Fachhochschule": 24, "Universität": 26}[ausbildung]
            alter = zufall.randint(startalter, 64)        # Alter gleichmässig verteilt
            erfahrung = max(0, alter - startalter - zufall.randint(0, 3))
            lohn_100 = basis * REGIONEN[region] * (1 + 0.025 * min(erfahrung, 20)) * zufall.gauss(1, 0.09)
            zeilen.append({
                "funktion": beruf, "branche": branche, "region": region, "erfahrung": erfahrung,
                "ausbildung": ausbildung, "pensum": pensum,
                "lohn_jahr": round(lohn_100 * pensum / 100, -2), "firmengroesse": zufall.choice(FIRMENGROESSE),
                "zufriedenheit": None, "stress": None, "lernen": None,
                "weiterbildung": None, "aufstieg": None, "testdaten": True, "alter_jahre": alter,
            })
    if not zeilen:
        return
    zeilen_speichern(zeilen)
    alle_eintraege.clear()


def vergleichsgruppe(df, ich):
    """Sucht die genaueste Gruppe mit genug Einträgen: gleicher Beruf und gleiches Alter zuerst.
    Gibt es zu wenige Einträge, wird die Gruppe schrittweise grösser."""
    if df.empty:
        return None, None
    df = df.copy()
    df["altersgruppe"] = df["alter_jahre"].apply(altersgruppe)
    ag = altersgruppe(ich.get("alter_jahre"))
    beruf = df["funktion"] == ich["funktion"]
    branche = df["branche"] == ich["branche"]
    versuche = []
    if ag:
        alter = df["altersgruppe"] == ag
        versuche += [
            (f"{ich['funktion']} · {ich['region']} · Alter {ag}", beruf & (df["region"] == ich["region"]) & alter),
            (f"{ich['funktion']} · ganze Schweiz · Alter {ag}", beruf & alter),
        ]
    if ag:
        a = int(ich["alter_jahre"])
        for breite in (7, 10):   # zuerst höchstens 7, dann 10 Jahre jünger oder älter
            von, bis = max(a - breite, 15), a + breite
            fenster = df["alter_jahre"].astype(float).between(von, bis)
            versuche.append((f"{ich['funktion']} · ganze Schweiz · Alter {von} bis {bis}", beruf & fenster))
    versuche.append((f"{ich['funktion']} · ganze Schweiz · alle Altersgruppen", beruf))
    if ag:
        versuche.append((f"Branche {ich['branche']} · Alter {ag}", branche & (df["altersgruppe"] == ag)))
    versuche.append((f"Branche {ich['branche']} · alle Altersgruppen", branche))
    for beschreibung, maske in versuche:
        gruppe = df[maske]
        if len(gruppe) >= MIN_GRUPPE:
            return beschreibung, gruppe
    return None, None
    df = df.copy()
    df["stufe"] = df["erfahrung"].astype(int).apply(erfahrungsstufe)
    s = erfahrungsstufe(ich["erfahrung"])
    versuche = [
        (f"{ich['funktion']} · {ich['region']} · {s} Erfahrung",
         (df["funktion"] == ich["funktion"]) & (df["region"] == ich["region"]) & (df["stufe"] == s)),
        (f"{ich['funktion']} · ganze Schweiz · {s} Erfahrung",
         (df["funktion"] == ich["funktion"]) & (df["stufe"] == s)),
        (f"{ich['funktion']} · ganze Schweiz", df["funktion"] == ich["funktion"]),
        (f"Branche {ich['branche']} · ganze Schweiz", df["branche"] == ich["branche"]),
    ]
    for beschreibung, maske in versuche:
        gruppe = df[maske]
        if len(gruppe) >= MIN_GRUPPE:
            return beschreibung, gruppe
    return None, None


# ---------------------------------------------------------------------------
# Daten laden
# ---------------------------------------------------------------------------
testdaten_anlegen()
daten = alle_eintraege()
ich = st.session_state.get("ich")

# ---------------------------------------------------------------------------
# Seitenleiste
# ---------------------------------------------------------------------------
st.sidebar.markdown('<div class="brand"><span class="logo">🚦</span>Stand<span class="acc">Check</span></div>',
                    unsafe_allow_html=True)
st.sidebar.header("So funktioniert es")
st.sidebar.markdown(
    '<div class="sb-schritt"><span class="n">1</span><span>Job und Lohn anonym eingeben</span></div>'
    '<div class="sb-schritt"><span class="n">2</span><span>Teilen und damit den Vergleich freischalten</span></div>'
    '<div class="sb-schritt"><span class="n">3</span><span>Ampel ansehen und Tipps umsetzen</span></div>',
    unsafe_allow_html=True)
st.sidebar.header("Datenschutz")
st.sidebar.markdown(
    f'<div class="sb-box">Kein Name, keine Firma, keine E-Mail. Vergleiche werden erst ab '
    f'<b>{MIN_GRUPPE} Einträgen</b> gezeigt, damit niemand erkannt werden kann.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Kopfbereich
# ---------------------------------------------------------------------------
hero_platz = st.container()
if not daten.empty and daten["testdaten"].any():
    st.info("Testversion: Die Vergleichswerte enthalten erfundene Testdaten, keine echten Löhne.")

# ---------------------------------------------------------------------------
# 1. Eingaben
# ---------------------------------------------------------------------------
abschnitt(1, "Deine Angaben", "anonym, ohne Name und Firma")
with st.container(key="card_eingaben"):
    eingaben = st.container(key="eingaben")
    with eingaben:
        titel("💼", "Dein Job", "Damit wir dich mit den richtigen Leuten vergleichen")
        eigener_beruf_an = st.session_state.get("eigener_beruf_an", False)
        j1, j2, j3, j0 = st.columns(4, gap="medium")
        with j1:
            branche_wahl = st.selectbox("Branche", [ALLE_BRANCHEN] + BRANCHEN, key="branche_wahl")
        with j2:
            if eigener_beruf_an:
                eigener_beruf = st.text_input("Dein Beruf", key="eigener_beruf", placeholder="z.B. Orgelbauer/in")
                funktion = " ".join(eigener_beruf.split())
            else:
                berufe_auswahl = (ALLE_BERUFE if branche_wahl == ALLE_BRANCHEN
                                  else sorted((b for b, _ in BERUFE[branche_wahl]), key=str.casefold))
                if st.session_state.get("funktion") not in berufe_auswahl:
                    st.session_state["funktion"] = berufe_auswahl[0]   # Beruf passt nicht zur gewählten Branche
                funktion = st.selectbox("Beruf", berufe_auswahl, key="funktion",
                                        help="Tippe ins Feld, um nach deinem Beruf zu suchen.")
        with j3:
            region = st.selectbox("Region", list(REGIONEN), key="region")
        with j0:
            firmengroesse = st.selectbox("Mitarbeitende in der Firma", FIRMENGROESSE, key="firmengroesse")
        st.checkbox("Mein Beruf ist nicht in der Liste", key="eigener_beruf_an")
        if eigener_beruf_an and branche_wahl == ALLE_BRANCHEN:
            st.caption("Wähle bitte noch die Branche, die am besten zu deinem Beruf passt.")
        j7, j4, j5, j6 = st.columns(4, gap="medium")
        with j7:
            alter_jahre = st.number_input("Alter", min_value=15, max_value=70, step=1, key="alter_jahre")
        with j4:
            erfahrung = st.number_input("Jahre Berufserfahrung", min_value=0, max_value=50, step=1, key="erfahrung")
        with j5:
            ausbildung = st.selectbox("Höchste Ausbildung", AUSBILDUNG, key="ausbildung")
        with j6:
            pensum = st.select_slider("Pensum in %", options=list(range(10, 101, 10)), key="pensum")

        st.markdown('<hr class="trenner">', unsafe_allow_html=True)
        titel("💰", "Dein Lohn", "Brutto, so wie er auf der Lohnabrechnung steht, ohne Bonus")
        l1, l2, l3 = st.columns(3, gap="medium")
        with l1:
            lohn_monat = st.number_input("Bruttolohn pro Monat (CHF)", min_value=500, max_value=100000,
                                         step=100, key="lohn_monat")
        with l2:
            st.write("")
            dreizehnter = st.checkbox("Ich bekomme einen 13. Monatslohn", key="dreizehnter")
        lohn_jahr = lohn_monat * (13 if dreizehnter else 12)
        with l3:
            st.markdown(f'<div class="jahreslohn"><span>Dein Jahreslohn</span><b>{chf(lohn_jahr)}</b></div>',
                        unsafe_allow_html=True)

    st.markdown('<hr class="trenner">', unsafe_allow_html=True)
    ehrlich = st.checkbox("Meine Angaben stimmen. Ehrliche Daten helfen allen.", key="ehrlich")

    if funktion in BERUF_INFO:
        branche = BERUF_INFO[funktion][0]
    else:
        branche = branche_wahl if branche_wahl != ALLE_BRANCHEN else ""
    beruf_ok = bool(funktion) and bool(branche)
    alter_ok = erfahrung <= alter_jahre - 14   # Berufserfahrung frühestens ab etwa 14 Jahren

    aktuell = {
        "funktion": funktion, "branche": branche, "region": region,
        "erfahrung": int(erfahrung), "alter_jahre": int(alter_jahre), "ausbildung": ausbildung, "pensum": int(pensum),
        "lohn_jahr": float(lohn_jahr), "firmengroesse": firmengroesse,
        # Die Fragen zur Zufriedenheit wurden entfernt, die Spalten bleiben für später leer
        "zufriedenheit": None, "stress": None, "lernen": None,
        "weiterbildung": None, "aufstieg": None, "testdaten": False,
    }

    def _teilen():
        eintrag = dict(aktuell)
        if st.session_state.get("ich_id") is None:
            # Pro Besuch wird nur einmal gespeichert, spätere Änderungen aktualisieren nur den Check
            st.session_state["ich_id"] = zeilen_speichern([eintrag])
            alle_eintraege.clear()
        st.session_state["ich"] = eintrag

    knopf_text = "Lohn anonym teilen und Vergleich sehen" if ich is None else "Check mit neuen Angaben aktualisieren"
    with st.container(key="teilen_knopf"):
        st.button(knopf_text, use_container_width=True, disabled=not (ehrlich and beruf_ok and alter_ok), on_click=_teilen)
    if not alter_ok:
        st.caption("Die Jahre Berufserfahrung passen nicht zu deinem Alter. Bitte prüfe beide Felder.")
    elif not beruf_ok:
        st.caption("Bitte gib deinen Beruf ein und wähle die passende Branche.")
    elif not ehrlich:
        st.caption("Bitte zuerst bestätigen, dass deine Angaben stimmen.")
    elif ich is not None and ich != aktuell:
        st.caption("Du hast etwas geändert. Klicke auf den Knopf, damit dein Check neu berechnet wird.")

ich = st.session_state.get("ich")
daten = alle_eintraege()

# ---------------------------------------------------------------------------
# 2. StandCheck
# ---------------------------------------------------------------------------
abschnitt(2, "Dein StandCheck", "Ampel, Vergleich und Tipps")
perzentil, ring_text = None, "?"

if ich is None:
    st.markdown(
        '<div class="gesperrt"><span class="i">🔒</span><div><div class="t">Dein Check ist noch gesperrt</div>'
        '<div class="s">Wer seinen Lohn anonym teilt, sieht die Löhne der anderen. '
        'Fülle oben alles aus und tippe auf den Knopf.</div></div></div>', unsafe_allow_html=True)
else:
    eigene_id = st.session_state.get("ich_id")
    andere = daten[daten["id"] != eigene_id] if eigene_id is not None else daten
    beschreibung, gruppe = vergleichsgruppe(andere, ich)

    if gruppe is None:
        st.warning("Für deinen Beruf gibt es noch zu wenige Einträge. Schau bald wieder vorbei.")
    else:
        mein_100 = ich["lohn_jahr"] / ich["pensum"] * 100
        median = gruppe["lohn_100"].median()
        p25, p75 = gruppe["lohn_100"].quantile([0.25, 0.75])
        perzentil = (gruppe["lohn_100"] < mein_100).mean() * 100
        differenz = mein_100 - median
        perzentil = min(perzentil, 99)
        ring_text = f"{perzentil:.0f}%"

        l_text, l_klasse, _, _ = stufe(perzentil, 30, 60)
        v_icon, v_titel, v_text = {
            "ok": ("✅", "Dein Lohn ist gut", "Du verdienst mehr als die meisten in deinem Beruf."),
            "knapp": ("⚠️", "Dein Lohn ist im Mittelfeld", "Mit dem richtigen Vorgehen liegt noch mehr drin."),
            "nein": ("❗", "Dein Lohn liegt unter dem Markt", "Es lohnt sich, das anzusprechen. Schau dir die Tipps an."),
        }[l_klasse]
        st.markdown(
            f'<div class="verdict {l_klasse}"><span class="vi">{v_icon}</span>'
            f'<div><div class="vt">{v_titel}</div><div class="vx">{v_text}</div></div>'
            f'<div class="vp"><div class="vl">Du verdienst mehr als</div><div class="vv">{perzentil:.0f}%</div></div></div>',
            unsafe_allow_html=True)

        # Vergleichsdaten für Ampel und Tipps
        vgl = andere.copy()
        vgl["stufe"] = vgl["erfahrung"].astype(int).apply(erfahrungsstufe)
        gleicher_beruf = vgl[vgl["funktion"] == ich["funktion"]]
        meine_stufe = erfahrungsstufe(ich["erfahrung"])
        meine_altersgruppe = altersgruppe(ich.get("alter_jahre"))

        # Kennzahlen
        with st.container(key="kpis"):
            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(kpi("💰", "#E0F2FE", "Dein Lohn (100%)", chf(mein_100),
                            f"bei {ich['pensum']}% Pensum: {chf(ich['lohn_jahr'])}", rand="#0EA5E9"),
                        unsafe_allow_html=True)
            k2.markdown(kpi("👥", "#EDE9FE", "Mittelwert Gruppe", chf(median),
                            f"{len(gruppe)} Einträge", rand="#8B5CF6"), unsafe_allow_html=True)
            k3.markdown(kpi("📈", "rgba(255,255,255,.2)", "Du verdienst mehr als", f"{perzentil:.0f}%",
                            "der Vergleichsgruppe", accent=True, anteil=perzentil / 100), unsafe_allow_html=True)
            abstand_farbe = "#10B981" if differenz >= 0 else "#F43F5E"
            k4.markdown(kpi("⚖️", "#FFEDD5", "Abstand zum Mittelwert",
                            ("+ " if differenz >= 0 else "− ") + chf(abs(differenz))[4:],
                            f"{differenz / median * 100:+.0f}% pro Jahr", rand=abstand_farbe), unsafe_allow_html=True)
        st.write("")

        links, rechts = st.columns([1.25, 1], gap="medium")
        with links:
            with st.container(key="card_vergleich"):
                titel("📊", "Dein Lohn im Vergleich", f"Verglichen mit: {beschreibung}. Löhne auf 100% Pensum umgerechnet.")
                verteilung = alt.Chart(gruppe).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6,
                                                        color="#2DD4BF", opacity=.85).encode(
                    x=alt.X("lohn_100:Q", bin=alt.Bin(maxbins=18), title="Jahreslohn bei 100% (CHF)",
                            axis=alt.Axis(format=",.0f", labelColor="#64748B", titleColor="#64748B",
                                          grid=False, domain=False, tickColor="#CBD5E1")),
                    y=alt.Y("count():Q", title=None, axis=None),
                    tooltip=[alt.Tooltip("count():Q", title="Anzahl")],
                )
                marke = pd.DataFrame({"x": [mein_100], "label": ["Du"]})
                linie = alt.Chart(marke).mark_rule(color="#6366F1", strokeWidth=3).encode(x="x:Q")
                text = alt.Chart(marke).mark_text(align="left", dx=6, dy=-8, fontSize=13, fontWeight=800,
                                                  color="#4F46E5").encode(x="x:Q", y=alt.value(12), text="label:N")
                st.altair_chart((verteilung + linie + text).properties(height=230, background="transparent")
                                .configure_view(strokeWidth=0, fill=None), use_container_width=True)
                st.markdown(
                    f'<div class="tiles3"><div class="t"><span>Unteres Viertel bis</span><b>{chf(p25)}</b></div>'
                    f'<div class="t mitte"><span>Mittelwert</span><b>{chf(median)}</b></div>'
                    f'<div class="t"><span>Oberes Viertel ab</span><b>{chf(p75)}</b></div></div>',
                    unsafe_allow_html=True)

        with rechts:
            with st.container(key="card_ampel"):
                titel("🚦", "Deine Ampel", "So schneidet dein Lohn in verschiedenen Vergleichen ab")
                vergleiche = [
                    ("📍 Gleicher Beruf, deine Region", gleicher_beruf[gleicher_beruf["region"] == ich["region"]]),
                    ("🇨🇭 Gleicher Beruf, ganze Schweiz", gleicher_beruf),
                    ("⏳ Gleicher Beruf, ähnliche Erfahrung", gleicher_beruf[gleicher_beruf["stufe"] == meine_stufe]),
                    (f"🎂 Gleicher Beruf, Alter {meine_altersgruppe}" if meine_altersgruppe
                     else "🎂 Gleicher Beruf, gleiches Alter",
                     gleicher_beruf[gleicher_beruf["alter_jahre"].apply(altersgruppe) == meine_altersgruppe]
                     if meine_altersgruppe else gleicher_beruf.iloc[0:0]),
                    ("🏢 Gleicher Beruf, gleiche Firmengrösse",
                     gleicher_beruf[gleicher_beruf["firmengroesse"] == ich["firmengroesse"]]),
                    ("🏭 Deine ganze Branche", vgl[vgl["branche"] == ich["branche"]]),
                ]
                html = ""
                for name, g in vergleiche:
                    if len(g) >= MIN_GRUPPE:
                        wert = min((g["lohn_100"] < mein_100).mean() * 100, 99)
                        text, _, verlauf, farbe = stufe(wert, 30, 60)
                        html += (f'<div class="hb"><div class="top"><span>{name}</span>'
                                 f'<b style="color:{farbe}">{text}<small>mehr als {wert:.0f}%</small></b></div>'
                                 f'<div class="trk"><div style="width:{max(wert, 4):.0f}%;background:{verlauf}"></div></div>'
                                 f'<div class="hint">Mittelwert {chf(g["lohn_100"].median())} · {len(g)} Einträge</div></div>')
                    else:
                        html += (f'<div class="hb"><div class="top"><span>{name}</span>'
                                 f'<b style="color:#94A3B8">offen<small>{len(g)} von {MIN_GRUPPE}</small></b></div>'
                                 f'<div class="trk"><div style="width:0%"></div></div>'
                                 f'<div class="hint">Noch zu wenige Einträge für diesen Vergleich</div></div>')
                st.markdown(f'<div class="hbars">{html}</div>', unsafe_allow_html=True)

        # Tipps
        st.write("")
        with st.container(key="card_tipps"):
            titel("💡", "Was besser sein müsste", "Konkrete nächste Schritte, das Wichtigste zuerst")
            tipps = []
            if differenz < 0:
                tipps.append((True, "Lohn", "Lohngespräch vorbereiten",
                              f"Du liegst rund {chf(-differenz)} pro Jahr unter dem Mittelwert. Nenne im Gespräch "
                              "diese Zahl, deine Erfolge der letzten 12 Monate und einen konkreten Betrag."))
            else:
                tipps.append((False, "Lohn", "Gut verhandelt",
                              "Du liegst über dem Mittelwert. Achte darauf, dass dein Lohn jedes Jahr mitwächst."))
            # Region: wo verdient man im gleichen Beruf mehr?
            nach_region = gleicher_beruf.groupby("region")["lohn_100"].agg(["count", "median"])
            nach_region = nach_region[(nach_region["count"] >= MIN_GRUPPE) & (nach_region.index != ich["region"])]
            if not nach_region.empty and nach_region["median"].max() > mein_100:
                beste = nach_region["median"].idxmax()
                tipps.append((False, "Region", f"In {beste} verdient man mehr",
                              f"Im gleichen Beruf liegt der Mittelwert in {beste} bei {chf(nach_region['median'].max())}, "
                              f"rund {chf(nach_region['median'].max() - mein_100)} mehr als du."))
            # Perspektive: was verdient man im gleichen Beruf ein paar Jahre älter?
            gruppen = ["unter 25", "25 bis 34", "35 bis 44", "45 bis 54", "55 und älter"]
            if meine_altersgruppe and meine_altersgruppe != gruppen[-1]:
                naechste = gruppen[gruppen.index(meine_altersgruppe) + 1]
                g = gleicher_beruf[gleicher_beruf["alter_jahre"].apply(altersgruppe) == naechste]
                if len(g) >= MIN_GRUPPE and g["lohn_100"].median() > mein_100:
                    tipps.append((False, "Perspektive", "So wächst dein Lohn",
                                  f"Mit {naechste} Jahren verdient man in deinem Beruf im Mittel "
                                  f"{chf(g['lohn_100'].median())}. Achte darauf, dass dein Lohn mitwächst."))
            if ich["ausbildung"] in ("Lehre (EFZ)", "Andere"):
                tipps.append((False, "Weiterbildung", "Marktwert steigern",
                              "Ein Fachausweis oder eine höhere Fachschule kann deinen Lohn deutlich steigern. "
                              "Frag, ob dein Arbeitgeber die Weiterbildung mitfinanziert."))
            if len(tipps) < 3:
                tipps.append((False, "Weiter so", "Regelmässig vergleichen",
                              "Mach in 6 Monaten wieder einen StandCheck, damit du siehst, ob dein Lohn mithält."))
            for start in range(0, len(tipps), 3):
                spalten = st.columns(3, gap="medium")
                for spalte, (wichtig, rang, name, text) in zip(spalten, tipps[start:start + 3]):
                    spalte.markdown(
                        f'<div class="tipp{" wichtig" if wichtig else ""}"><span class="rank">{rang}</span>'
                        f'<div class="name">{name}</div><div class="txt">{text}</div></div>',
                        unsafe_allow_html=True)
                st.write("")
            st.caption("Nächster StandCheck in 6 Monaten empfohlen, damit du deine Entwicklung siehst.")

        # Kurzfassung in der Seitenleiste
        st.sidebar.divider()
        st.sidebar.subheader("Dein Ergebnis")
        st.sidebar.markdown(f"Beruf: **{ich['funktion']}**  \nRegion: **{ich['region']}**  \n"
                            f"Alter: **{ich.get('alter_jahre', '')}**  \n"
                            f"Mittelwert Gruppe: **{chf(median)}**")
        st.sidebar.metric("Dein Lohn (100%)", chf(mein_100), f"{differenz / median * 100:+.0f}% zum Mittelwert")

# ---------------------------------------------------------------------------
# 3. Lohnübersicht
# ---------------------------------------------------------------------------
abschnitt(3, "Lohnübersicht", "alle Berufe auf einen Blick")
if ich is None:
    st.markdown(
        '<div class="gesperrt"><span class="i">🔒</span><div><div class="t">Lohnübersicht gesperrt</div>'
        '<div class="s">Die Übersicht siehst du, nachdem du deinen eigenen Lohn geteilt hast.</div></div></div>',
        unsafe_allow_html=True)
else:
    with st.container(key="card_uebersicht"):
        titel("🗂️", "Was verdienen andere?", "Mittelwert pro Jahr bei 100% Pensum, mit der Spanne der mittleren Hälfte")
        u1, u2 = st.columns([1, 2], gap="medium")
        with u1:
            branchen_liste = [ALLE_BRANCHEN] + BRANCHEN
            u_branche = st.selectbox("Branche", branchen_liste,
                                     index=branchen_liste.index(ich["branche"]) if ich["branche"] in branchen_liste else 0)
        with u2:
            regionen_auswahl = st.multiselect("Regionen", list(REGIONEN), default=list(REGIONEN))
        auswahl = daten[daten["region"].isin(regionen_auswahl)]
        if u_branche != ALLE_BRANCHEN:
            auswahl = auswahl[auswahl["branche"] == u_branche]
        if auswahl.empty:
            st.warning("Bitte mindestens eine Region wählen.")
        else:
            uebersicht = (auswahl.groupby("funktion")["lohn_100"]
                          .agg(anzahl="count", mitte="median",
                               von=lambda s: s.quantile(0.25), bis=lambda s: s.quantile(0.75))
                          .reset_index())
            uebersicht = uebersicht[uebersicht["anzahl"] >= MIN_GRUPPE].sort_values("mitte", ascending=False)
            if uebersicht.empty:
                st.warning("Noch zu wenige Einträge für eine Übersicht.")
            else:
                hoechster = uebersicht["mitte"].max()
                html = "".join(
                    f'<div class="hb{" ich" if r.funktion == ich["funktion"] else ""}"><div class="top">'
                    f'<span>{"👉 " if r.funktion == ich["funktion"] else ""}{r.funktion}</span>'
                    f'<b>{chf(r.mitte)}<small>{r.anzahl} Einträge</small></b></div>'
                    f'<div class="trk"><div style="width:{r.mitte / hoechster * 100:.0f}%;'
                    f'background:{"linear-gradient(90deg, #6366F1, #A5B4FC)" if r.funktion == ich["funktion"] else "linear-gradient(90deg, #2DD4BF, #0EA5A4)"}">'
                    f'</div></div><div class="hint">Mittlere Hälfte: {chf(r.von)} bis {chf(r.bis)}</div></div>'
                    for r in uebersicht.itertuples())
                st.markdown(f'<div class="hbars">{html}</div>', unsafe_allow_html=True)
                st.caption(f"Gruppen mit weniger als {MIN_GRUPPE} Einträgen werden zum Schutz der Anonymität nicht gezeigt.")

# ---------------------------------------------------------------------------
# Kopfbereich nachträglich füllen (Ring zeigt die Position, sobald der Check da ist)
# ---------------------------------------------------------------------------
if perzentil is None:
    ring_grad, ring_farbe, ring_lbl = 0, "#2DD4BF", "Teile deinen Lohn"
else:
    ring_farbe = "#2DD4BF" if perzentil >= 60 else "#FBBF24" if perzentil >= 30 else "#FB7185"
    ring_grad, ring_lbl = perzentil * 3.6, "verdienst du mehr als andere"
with hero_platz:
    st.markdown(
        f'<div class="hero"><div class="left">'
        f'<span class="badge"><span class="dot"></span>Anonym · Schweiz · gratis</span>'
        f'<div class="title">Wo stehst du <span>beruflich?</span></div>'
        f'<div class="text">Teile deinen Lohn anonym, vergleiche dich mit Leuten im gleichen Beruf '
        f'und erfahre, was gut ist und was besser sein müsste.</div>'
        f'<div class="chips"><span class="chip">💼 <b>{len(ALLE_BERUFE)}</b> Berufe</span>'
        f'<span class="chip">👥 <b>{len(daten)}</b> Einträge</span>'
        f'<span class="chip">🔒 ab <b>{MIN_GRUPPE}</b> Einträgen sichtbar</span>'
        f'<span class="chip">⏱️ <b>2 Minuten</b></span></div>'
        f'</div>'
        f'<div class="ring" style="background:conic-gradient({ring_farbe} {ring_grad:.0f}deg, rgba(255,255,255,.12) 0)">'
        f'<div class="inner"><div class="pct">{ring_text}</div><div class="lbl">{ring_lbl}</div></div></div></div>',
        unsafe_allow_html=True)

st.write("")
