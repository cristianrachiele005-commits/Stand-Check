# StandCheck

Wo stehe ich beruflich? Lohn anonym eintragen, mit ähnlichen Funktionen vergleichen und sehen, was besser sein könnte.

## Starten
Die App läuft auf Streamlit Community Cloud mit der Datei `streamlit_app.py`.

## Dauerhafte Daten mit Supabase
1. Projekt auf supabase.com anlegen
2. Im SQL Editor den Inhalt von `supabase_tabelle.sql` ausführen
3. In Streamlit unter Settings, Secrets eintragen:

```
[supabase]
url = "deine URL"
key = "dein anon Schlüssel"
```

Ohne Supabase speichert die App lokal. Auf Streamlit Cloud gehen die Einträge dann beim Neustart verloren.
