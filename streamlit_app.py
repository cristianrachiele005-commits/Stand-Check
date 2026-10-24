"""
StandCheck – Wo stehe ich beruflich?
Erste Testversion: Lohn anonym eintragen, mit anderen vergleichen, Ampel und Tipps.

Speicher:
- Wenn in den Streamlit Secrets ein Supabase Zugang hinterlegt ist, werden die Daten dort gespeichert (bleiben dauerhaft).
- Sonst wird eine lokale SQLite Datei benutzt (gut zum Testen, auf Streamlit Cloud gehen die Daten beim Neustart verloren).
"""

import random
import sqlite3
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Grundeinstellungen
# ---------------------------------------------------------------------------

st.set_page_config(page_title="StandCheck", page_icon="🚦", layout="centered")

MIN_GRUPPE = 10  # so viele Einträge braucht es mindestens, bevor ein Vergleich angezeigt wird

FUNKTIONEN = {
    # Funktion: (Branche, Basislohn pro Jahr bei 100% und 0 Jahren Erfahrung) – nur für Testdaten
    "Einkäufer/in": ("Industrie", 72000),
    "Sachbearbeiter/in kaufmännisch": ("Dienstleistung", 62000),
    "Projektleiter/in": ("Industrie", 92000),
    "Logistiker/in": ("Logistik", 56000),
    "Polymechaniker/in": ("Industrie", 62000),
    "Software Entwickler/in": ("Informatik", 90000),
    "Pflegefachperson": ("Gesundheit", 72000),
    "Detailhandelsfachperson": ("Handel", 50000),
    "Buchhalter/in": ("Dienstleistung", 70000),
    "Marketing Fachperson": ("Dienstleistung", 72000),
}

REGIONEN = {
    # Region: Faktor für Testdaten
    "Zürich": 1.08,
    "Genferseeregion": 1.06,
    "Nordwestschweiz": 1.02,
    "Espace Mittelland": 0.98,
    "Zentralschweiz": 1.00,
    "Ostschweiz": 0.95,
    "Tessin": 0.86,
}

AUSBILDUNG = ["Lehre (EFZ)", "Höhere Fachschule / Fachausweis", "Fachhochschule", "Universität", "Andere"]
FIRMENGROESSE = ["1 bis 9", "10 bis 49", "50 bis 249", "250 und mehr"]

SPALTEN = [
    "funktion", "branche", "region", "erfahrung", "ausbildung", "pensum", "lohn_jahr",
    "firmengroesse", "zufriedenheit", "stress", "lernen", "weiterbildung", "aufstieg", "testdaten",
]


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
            testdaten INTEGER DEFAULT 0
        )"""
    )
    return con


def eintraege_speichern(zeilen: list[dict]):
    sb = supabase_client()
    if sb is not None:
        for start in range(0, len(zeilen), 200):
            sb.table("loehne").insert(zeilen[start:start + 200]).execute()
        return
    con = sqlite_verbindung()
    platzhalter = ",".join("?" for _ in SPALTEN)
    con.executemany(
        f"INSERT INTO loehne ({','.join(SPALTEN)}) VALUES ({platzhalter})",
        [[int(z[s]) if isinstance(z[s], bool) else z[s] for s in SPALTEN] for z in zeilen],
    )
    con.commit()
    con.close()


@st.cache_data(ttl=60)
def alle_eintraege() -> pd.DataFrame:
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
        return pd.DataFrame(columns=SPALTEN)
    df["weiterbildung"] = df["weiterbildung"].astype(bool)
    df["aufstieg"] = df["aufstieg"].astype(bool)
    df["testdaten"] = df["testdaten"].astype(bool)
    df["lohn_100"] = df["lohn_jahr"] / df["pensum"] * 100
    return df


def testdaten_anlegen():
    """Legt einmalig erfundene Testdaten an, damit man die App ausprobieren kann."""
    df = alle_eintraege()
    if not df.empty and df["testdaten"].any():
        return
    zufall = random.Random(42)
    zeilen = []
    for _ in range(600):
        funktion = zufall.choice(list(FUNKTIONEN))
        branche, basis = FUNKTIONEN[funktion]
        region = zufall.choices(list(REGIONEN), weights=[22, 14, 16, 18, 10, 14, 6])[0]
        erfahrung = min(int(zufall.expovariate(1 / 9)), 40)
        pensum = zufall.choices([100, 90, 80, 60], weights=[70, 10, 15, 5])[0]
        lohn_100 = basis * REGIONEN[region] * (1 + 0.025 * min(erfahrung, 20)) * zufall.gauss(1, 0.09)
        zeilen.append({
            "funktion": funktion, "branche": branche, "region": region, "erfahrung": erfahrung,
            "ausbildung": zufall.choice(AUSBILDUNG[:4]), "pensum": pensum,
            "lohn_jahr": round(lohn_100 * pensum / 100, -2),
            "firmengroesse": zufall.choice(FIRMENGROESSE),
            "zufriedenheit": zufall.randint(1, 5), "stress": zufall.randint(1, 5),
            "lernen": zufall.randint(1, 5),
            "weiterbildung": zufall.random() < 0.5, "aufstieg": zufall.random() < 0.45,
            "testdaten": True,
        })
    eintraege_speichern(zeilen)
    alle_eintraege.clear()


# ---------------------------------------------------------------------------
# Auswertung
# ---------------------------------------------------------------------------

def erfahrungsstufe(jahre: int) -> str:
    if jahre < 5:
        return "0 bis 4 Jahre"
    if jahre < 10:
        return "5 bis 9 Jahre"
    if jahre < 20:
        return "10 bis 19 Jahre"
    return "20 Jahre und mehr"


def vergleichsgruppe(df: pd.DataFrame, ich: dict):
    """Sucht die genaueste Gruppe mit genug Einträgen. Wird sonst schrittweise grösser."""
    df = df.copy()
    df["stufe"] = df["erfahrung"].apply(erfahrungsstufe)
    stufe = erfahrungsstufe(ich["erfahrung"])
    versuche = [
        (f"{ich['funktion']}, {ich['region']}, {stufe} Erfahrung",
         (df["funktion"] == ich["funktion"]) & (df["region"] == ich["region"]) & (df["stufe"] == stufe)),
        (f"{ich['funktion']}, ganze Schweiz, {stufe} Erfahrung",
         (df["funktion"] == ich["funktion"]) & (df["stufe"] == stufe)),
        (f"{ich['funktion']}, ganze Schweiz",
         df["funktion"] == ich["funktion"]),
        (f"Branche {ich['branche']}, ganze Schweiz",
         df["branche"] == ich["branche"]),
    ]
    for beschreibung, maske in versuche:
        gruppe = df[maske]
        if len(gruppe) >= MIN_GRUPPE:
            return beschreibung, gruppe
    return None, None


def ampel(wert: float, rot_bis: float, gelb_bis: float):
    if wert < rot_bis:
        return "🔴", "schlecht"
    if wert < gelb_bis:
        return "🟡", "mittel"
    return "🟢", "gut"


def chf(betrag: float) -> str:
    return f"CHF {betrag:,.0f}".replace(",", "'")


# ---------------------------------------------------------------------------
# Oberfläche
# ---------------------------------------------------------------------------

testdaten_anlegen()
daten = alle_eintraege()

st.title("🚦 StandCheck")
st.caption("Wo stehe ich beruflich? Lohn anonym eintragen, vergleichen und erfahren, was besser sein könnte.")

if daten["testdaten"].any():
    st.info("Testversion: Die Vergleichswerte enthalten erfundene Testdaten, keine echten Löhne.")

tab_eintragen, tab_check, tab_uebersicht = st.tabs(["1. Eintragen", "2. Mein StandCheck", "3. Lohnübersicht"])

# --- 1. Eintragen -----------------------------------------------------------
with tab_eintragen:
    st.subheader("Dein Job, anonym")
    st.write("Kein Name, keine Firma. Wer seinen Lohn teilt, sieht die Löhne der anderen.")

    with st.form("eintrag"):
        col1, col2 = st.columns(2)
        funktion = col1.selectbox("Funktion", list(FUNKTIONEN))
        region = col2.selectbox("Region", list(REGIONEN))
        erfahrung = col1.number_input("Jahre Berufserfahrung", 0, 50, 5)
        ausbildung = col2.selectbox("Höchste Ausbildung", AUSBILDUNG)
        pensum = col1.slider("Pensum in %", 10, 100, 100, step=10)
        firmengroesse = col2.selectbox("Mitarbeitende in der Firma", FIRMENGROESSE)
        lohn_jahr = st.number_input(
            "Bruttolohn pro Jahr in CHF (inkl. 13. Monatslohn, ohne Bonus)",
            min_value=10000, max_value=1000000, value=80000, step=1000,
        )

        st.markdown("**Wie geht es dir im Job?** (1 = gar nicht, 5 = sehr)")
        col3, col4, col5 = st.columns(3)
        zufriedenheit = col3.slider("Zufrieden", 1, 5, 3)
        stress = col4.slider("Gestresst", 1, 5, 3)
        lernen = col5.slider("Lerne Neues", 1, 5, 3)

        weiterbildung = st.checkbox("Mein Arbeitgeber unterstützt Weiterbildungen")
        aufstieg = st.checkbox("Ich habe realistische Aufstiegschancen")
        echte_angabe = st.checkbox("Meine Angaben stimmen (ehrliche Daten helfen allen)")

        abschicken = st.form_submit_button("Eintragen und Vergleich freischalten", type="primary")

    if abschicken:
        if not echte_angabe:
            st.warning("Bitte bestätige, dass deine Angaben stimmen.")
        else:
            eintrag = {
                "funktion": funktion, "branche": FUNKTIONEN[funktion][0], "region": region,
                "erfahrung": int(erfahrung), "ausbildung": ausbildung, "pensum": int(pensum),
                "lohn_jahr": float(lohn_jahr), "firmengroesse": firmengroesse,
                "zufriedenheit": zufriedenheit, "stress": stress, "lernen": lernen,
                "weiterbildung": weiterbildung, "aufstieg": aufstieg, "testdaten": False,
            }
            eintraege_speichern([eintrag])
            alle_eintraege.clear()
            st.session_state["ich"] = eintrag
            st.success("Danke! Dein StandCheck ist jetzt im Tab «2. Mein StandCheck» bereit.")

# --- 2. StandCheck ----------------------------------------------------------
with tab_check:
    ich = st.session_state.get("ich")
    if ich is None:
        st.info("🔒 Trage zuerst im Tab «1. Eintragen» deinen Lohn ein, dann siehst du hier deinen StandCheck.")
    else:
        daten = alle_eintraege()
        andere = daten[~((daten["lohn_jahr"] == ich["lohn_jahr"]) & (daten["funktion"] == ich["funktion"])
                         & (daten["region"] == ich["region"]) & (~daten["testdaten"]))]
        beschreibung, gruppe = vergleichsgruppe(andere, ich)

        if gruppe is None:
            st.warning("Für deine Funktion gibt es noch zu wenige Einträge. Schau bald wieder vorbei.")
        else:
            mein_lohn_100 = ich["lohn_jahr"] / ich["pensum"] * 100
            median = gruppe["lohn_100"].median()
            p25, p75 = gruppe["lohn_100"].quantile([0.25, 0.75])
            perzentil = (gruppe["lohn_100"] < mein_lohn_100).mean() * 100
            differenz = mein_lohn_100 - median

            # Ampeln
            lohn_symbol, lohn_text = ampel(perzentil, 30, 60)
            entwicklung_punkte = (ich["lernen"] - 1) / 4 * 50 + (25 if ich["weiterbildung"] else 0) + (25 if ich["aufstieg"] else 0)
            entw_symbol, entw_text = ampel(entwicklung_punkte, 40, 70)
            zufrieden_punkte = ((ich["zufriedenheit"] - 1) / 4 * 60) + ((5 - ich["stress"]) / 4 * 40)
            zufr_symbol, zufr_text = ampel(zufrieden_punkte, 40, 70)
            gesamt = (perzentil + entwicklung_punkte + zufrieden_punkte) / 3
            ges_symbol, ges_text = ampel(gesamt, 40, 65)

            st.subheader(f"{ges_symbol} Dein Gesamtstand: {ges_text}")
            st.caption(f"Verglichen mit: {beschreibung} ({len(gruppe)} Einträge). Löhne auf 100% Pensum umgerechnet.")

            c1, c2, c3 = st.columns(3)
            c1.metric(f"{lohn_symbol} Lohn", lohn_text, f"{differenz / median * 100:+.0f}% zum Mittelwert")
            c2.metric(f"{entw_symbol} Entwicklung", entw_text)
            c3.metric(f"{zufr_symbol} Zufriedenheit", zufr_text)

            st.markdown("#### Dein Lohn im Vergleich")
            st.write(
                f"Dein Lohn (auf 100%): **{chf(mein_lohn_100)}**. "
                f"Der Mittelwert liegt bei **{chf(median)}**, die mittlere Hälfte verdient "
                f"zwischen {chf(p25)} und {chf(p75)}. "
                f"Du verdienst mehr als **{perzentil:.0f}%** der Vergleichsgruppe."
            )

            balken = alt.Chart(gruppe).mark_bar(opacity=0.7).encode(
                x=alt.X("lohn_100:Q", bin=alt.Bin(maxbins=20), title="Jahreslohn bei 100% (CHF)"),
                y=alt.Y("count():Q", title="Anzahl"),
            )
            linie = alt.Chart(pd.DataFrame({"x": [mein_lohn_100]})).mark_rule(color="red", size=3).encode(x="x:Q")
            st.altair_chart(balken + linie, width="stretch")
            st.caption("Rote Linie = du")

            st.markdown("#### Was besser sein müsste")
            tipps = []
            if differenz < 0:
                tipps.append(
                    f"💰 **Lohn:** Du liegst rund {chf(-differenz)} pro Jahr unter dem Mittelwert. "
                    "Das ist ein gutes Argument fürs nächste Lohngespräch. Nenne die Zahl, deine Erfolge "
                    "der letzten 12 Monate und einen konkreten Betrag."
                )
            else:
                tipps.append("💰 **Lohn:** Du liegst über dem Mittelwert. Gut verhandelt! Achte darauf, dass der Lohn jedes Jahr mitwächst.")
            if not ich["weiterbildung"]:
                tipps.append("🎓 **Weiterbildung:** Frag deinen Arbeitgeber, ob er eine Weiterbildung mitfinanziert. Das steigert deinen Marktwert.")
            if not ich["aufstieg"]:
                tipps.append("📈 **Aufstieg:** Ohne Aufstiegschancen bleibt der Lohn oft stehen. Sprich das an oder schau dich nach Stellen mit mehr Verantwortung um.")
            if ich["stress"] >= 4:
                tipps.append("😮‍💨 **Belastung:** Dein Stress ist hoch. Prüfe, ob Lohn und Belastung zusammenpassen.")
            if ich["lernen"] <= 2:
                tipps.append("🧠 **Lernen:** Du lernst wenig Neues. Ein neues Projekt oder eine neue Aufgabe kann helfen.")
            for tipp in tipps:
                st.markdown(tipp)

            st.caption("Nächster StandCheck in 6 Monaten empfohlen, damit du deine Entwicklung siehst.")

# --- 3. Lohnübersicht -------------------------------------------------------
with tab_uebersicht:
    if st.session_state.get("ich") is None:
        st.info("🔒 Die Lohnübersicht siehst du, nachdem du deinen eigenen Lohn eingetragen hast.")
    else:
        daten = alle_eintraege()
        regionen_auswahl = st.multiselect("Regionen", list(REGIONEN), default=list(REGIONEN))
        auswahl = daten[daten["region"].isin(regionen_auswahl)]
        uebersicht = (
            auswahl.groupby("funktion")["lohn_100"]
            .agg(Einträge="count", Mittelwert="median",
                 Von=lambda s: s.quantile(0.25), Bis=lambda s: s.quantile(0.75))
            .reset_index()
        )
        uebersicht = uebersicht[uebersicht["Einträge"] >= MIN_GRUPPE].sort_values("Mittelwert", ascending=False)
        if uebersicht.empty:
            st.warning("Noch zu wenige Einträge für eine Übersicht.")
        else:
            for spalte in ["Mittelwert", "Von", "Bis"]:
                uebersicht[spalte] = uebersicht[spalte].apply(chf)
            uebersicht = uebersicht.rename(columns={"funktion": "Funktion"})
            st.dataframe(uebersicht, hide_index=True, width="stretch")
            st.caption(f"Jahreslöhne bei 100% Pensum. Gruppen mit weniger als {MIN_GRUPPE} Einträgen werden zum Schutz der Anonymität nicht gezeigt.")
