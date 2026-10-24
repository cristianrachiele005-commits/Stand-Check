# -*- coding: utf-8 -*-
"""
Ordnet einen frei eingetippten Beruf (z.B. "Demand Planner" oder "Leiterin Einkauf")
den ähnlichsten Berufen aus der Liste zu. Funktioniert auf Deutsch und Englisch.
"""
import re
from difflib import SequenceMatcher
from functools import lru_cache

from berufe import ALLE_BERUFE

# Englische und deutsche Wörter auf eine gemeinsame Form bringen
SYNONYME = {
    "procurement": "einkauf", "purchasing": "einkauf", "purchase": "einkauf", "sourcing": "einkauf",
    "buyer": "einkaeufer", "einkaufer": "einkaeufer", "einkaufs": "einkauf",
    "sales": "verkauf", "vertrieb": "verkauf", "vertriebs": "verkauf", "verkaufs": "verkauf", "seller": "verkaeufer",
    "finance": "finanzen", "financial": "finanzen", "finanz": "finanzen",
    "accounting": "buchhaltung", "accountant": "buchhalter", "bookkeeper": "buchhalter",
    "controlling": "controller", "controllerin": "controller",
    "head": "leiter", "lead": "leiter", "leader": "leiter", "leitung": "leiter", "chief": "leiter",
    "director": "leiter", "direktor": "leiter", "chef": "leiter", "verantwortlicher": "leiter",
    "planner": "planer", "planning": "planer", "planung": "planer", "disponent": "planer",
    "demand": "bedarf", "bedarfs": "bedarf", "forecast": "bedarf",
    "supply": "supply", "versorgung": "supply", "versorgungs": "supply",
    "logistics": "logistik", "logistic": "logistik", "warehouse": "lager", "lagerist": "lager",
    "quality": "qualitaet", "qualitaets": "qualitaet", "qs": "qualitaet", "qa": "qualitaet",
    "production": "produktion", "manufacturing": "produktion", "produktions": "produktion",
    "engineer": "ingenieur", "engineering": "ingenieur", "ing": "ingenieur",
    "developer": "entwickler", "development": "entwicklung", "programmer": "entwickler", "programmierer": "entwickler",
    "hr": "personal", "human": "personal", "people": "personal", "personalwesen": "personal",
    "operations": "betrieb", "operation": "betrieb", "betriebs": "betrieb",
    "customer": "kunde", "kunden": "kunde", "client": "kunde",
    "assistant": "assistent", "specialist": "spezialist", "expert": "spezialist", "experte": "spezialist",
    "consultant": "berater", "advisor": "berater", "beratung": "berater",
    "nurse": "pflege", "pflegefachfrau": "pflege", "pflegefachmann": "pflege",
    "teacher": "lehrer", "lehrperson": "lehrer", "driver": "fahrer", "chauffeur": "fahrer",
    "cook": "koch", "technician": "techniker", "mechanic": "mechaniker", "electrician": "elektriker",
    "project": "projekt", "projekt": "projekt", "it": "informatik", "ict": "informatik",
    "informatiker": "informatik", "marketing": "marketing", "communication": "kommunikation",
    "communications": "kommunikation", "legal": "recht", "lawyer": "anwalt", "jurist": "recht",
    "payroll": "lohn", "lohnbuchhalter": "lohn", "treasury": "treasury", "inventory": "bestand",
    "stock": "bestand", "material": "material", "materials": "material", "master": "stammdaten",
    "office": "buero", "clerk": "sachbearbeiter", "administrator": "administrator",
    "junior": "junior", "senior": "senior", "deputy": "stellvertreter", "stv": "stellvertreter",
    "team": "team", "teamleader": "teamleiter", "abteilung": "abteilung", "abteilungs": "abteilung",
    "plant": "werk", "werks": "werk", "maintenance": "instandhaltung", "repair": "reparatur",
    "vp": "leiter", "president": "leiter", "praesident": "leiter", "commodity": "warengruppe",
    "warengruppen": "warengruppe", "category": "warengruppe", "kategorie": "warengruppe",
}
# Ganze Ausdrücke, die für einen bestimmten Beruf stehen (werden vor dem Zerlegen ersetzt)
AUSDRUECKE = {
    "chief executive officer": "ceo", "geschaeftsfuehrer": "ceo", "geschaftsfuhrer": "ceo",
    "chief operating officer": "coo", "chief financial officer": "cfo", "finanzchef": "cfo",
    "chief technology officer": "cto", "chief information officer": "cio",
    "chief human resources officer": "chro", "personalchef": "chro", "chief marketing officer": "cmo",
    "chief sales officer": "cso", "chief procurement officer": "cpo", "chief digital officer": "cdo",
    "vice president": "leiter", "supply chain": "supplychain", "key account": "keyaccount",
    "business development": "businessdevelopment", "customer service": "kundendienst",
    "krankenschwester": "pflege", "krankenpfleger": "pflege", "pflegefachperson": "pflege",
}
FUELLWOERTER = {"of", "officer", "the", "and", "und", "fuer", "for", "im", "in", "der", "die", "das", "de", "a", "an",
                "m", "w", "d", "mwd", "mw", "frau", "mann", "person", "fachperson", "mitarbeiter"}
ANREDE_ENDUNG = re.compile(r"(erin|orin|eurin|istin|antin|entin)$")


def _woerter(text):
    text = text.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("é", "e"), ("è", "e"), ("à", "a"), ("&", " und ")):
        text = text.replace(a, b)
    text = re.sub(r"/in\b|/innen\b|/r\b|/e\b|\(m/w/d\)|\(w/m/d\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = f" {' '.join(text.split())} "
    for ausdruck, ersatz in AUSDRUECKE.items():
        text = text.replace(f" {ausdruck} ", f" {ersatz} ")
        text = text.replace(f" {ausdruck}in ", f" {ersatz} ")
    woerter = []
    for w in text.split():
        if w in FUELLWOERTER:
            continue
        if len(w) > 6 and ANREDE_ENDUNG.search(w):
            w = w[:-2]                       # Planerin -> Planer, Leiterin -> Leiter
        w = SYNONYME.get(w, w)
        # Zusammengesetzte Wörter wie "Einkaufsleiter" in Teile zerlegen
        teile = [w]
        for stamm in ("leiter", "planer", "einkaeufer", "einkauf", "manager", "spezialist", "berater",
                      "ingenieur", "techniker", "entwickler", "assistent", "sachbearbeiter", "controller",
                      "disponent", "chef"):
            if w != stamm and w.endswith(stamm) and len(w) - len(stamm) >= 3:
                vorne = w[: -len(stamm)].rstrip("s")
                teile = [SYNONYME.get(vorne, vorne), SYNONYME.get(stamm, stamm)]
                break
        woerter.extend(t for t in teile if t)
    return woerter


@lru_cache(maxsize=None)
def _beruf_woerter(beruf):
    return tuple(dict.fromkeys(_woerter(beruf)))


def _wort_aehnlich(a, b):
    if a == b:
        return 1.0
    if len(a) >= 4 and len(b) >= 4 and (a in b or b in a):
        return 0.8
    r = SequenceMatcher(None, a, b).ratio()
    return r if r >= 0.8 else 0.0


def _punkte(anfrage, beruf):
    q = list(dict.fromkeys(_woerter(anfrage)))
    b = list(_beruf_woerter(beruf))
    if not q or not b:
        return 0.0
    treffer_q = sum(max(_wort_aehnlich(x, y) for y in b) for x in q) / len(q)
    treffer_b = sum(max(_wort_aehnlich(y, x) for x in q) for y in b) / len(b)
    wortwert = 2 * treffer_q * treffer_b / (treffer_q + treffer_b) if treffer_q + treffer_b else 0.0
    textwert = SequenceMatcher(None, " ".join(q), " ".join(b)).ratio()
    return 0.75 * wortwert + 0.25 * textwert


def aehnlichste_berufe(anfrage, anzahl=5):
    """Gibt die ähnlichsten Berufe als Liste von (Beruf, Punkte 0 bis 1) zurück."""
    anfrage = (anfrage or "").strip()
    if not anfrage:
        return []
    exakt = [b for b in ALLE_BERUFE if b.casefold() == anfrage.casefold()]
    if exakt:
        return [(exakt[0], 1.0)]
    roh = anfrage.casefold()
    bewertet = sorted(((b, _punkte(anfrage, b)) for b in ALLE_BERUFE),
                      key=lambda x: (-round(x[1], 3), roh not in x[0].casefold(),
                                     -SequenceMatcher(None, roh, x[0].casefold()).ratio()))
    return bewertet[:anzahl]
