# Psych Outreach · Resilience

Kartenbasiertes Outreach-Tool für psychotherapeutische und psychiatrische Praxen in Deutschland – aufgebaut wie das DKG-/Oncomap-Tool (ohne Waves). Datengrundlage sind Suchergebnisse aus der **116117 Arztsuche** (KBV).

## Funktionen

| Tab | Zweck |
| :-- | :-- |
| **Suchen** | Region als Mittelpunkt + Radius (z. B. Berlin, 200 km; Städte-Presets oder frei auf der Karte gewählter Punkt), PLZ-Bereich, Fachgebiet, Therapieverfahren, Status, Kontaktdaten. Treffer nach Entfernung sortiert. |
| **Standort** | Alle Einträge an einer Adresse, mit Telefon, E-Mail, Website, Verfahren, Sprachen. Status, Owner und Notiz pro Person, wird sofort gespeichert. |
| **Outreach** | Auswahl nach Status, Status/Owner gesammelt setzen, **HubSpot-CSV-Export**. |
| **Daten** | Team-Stand (`state.json`) teilen/laden, 116117-Exporte importieren, `practices.json` exportieren. |

Status: Neu · Kontaktiert · Antwort · Termin · Kein Interesse. Gespeichert wird im Browser (localStorage), geteilt über `data/state.json`.

## Repo-Struktur

```
index.html                    Das Tool (statisch, Leaflet)
data/raw/                     116117-Exporte (JSON) – hier neue Daten ablegen
data/practices.json           Zusammengeführte Daten (wird von der Action gebaut)
data/state.json               Geteilter Outreach-Stand des Teams
tools/build_data.py           Führt data/raw/* zu data/practices.json zusammen
.github/workflows/deploy.yml  Baut die Daten und veröffentlicht auf GitHub Pages
```

## Einrichten (einmalig)

1. Alle Dateien in ein Repo hochladen (z. B. `Team-Germany/Psychmap`), Branch `main`.
2. **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Unter **Actions** den Workflow „Daten bauen & Pages deployen“ einmal manuell starten (oder einfach pushen).

## Daten aus der 116117 Arztsuche holen

Die Schnittstelle `arztsuche.116117.de/api/data` ist nicht öffentlich dokumentiert und beantwortet Anfragen nur noch innerhalb einer echten Browser-Sitzung (Session-Cookies und ein vom Seitenskript erzeugter `req-val`-Header). Ein automatischer Abruf per GitHub Action – wie bei Oncomap – funktioniert deshalb nicht zuverlässig. Der Weg ist darum: im Browser suchen, Ergebnis exportieren, ins Repo legen.

1. Auf [arztsuche.116117.de](https://arztsuche.116117.de/) suchen (Ort/PLZ, Umkreis, Fachgebiet z. B. Psychotherapie bzw. Psychiatrie und Psychotherapie).
2. Ergebnis als JSON sichern – eine der beiden Varianten:
   - Userscript **„116117 Arztsuche – Data Export (JSON)“** von Bergiu (MIT, [GitHub](https://github.com/Bergiu/Aerztesuche-Scripts)) in Tampermonkey/Violentmonkey installieren; neben „PDF ausdrucken“ erscheint „Exportieren (JSON)“.
   - Oder ohne Erweiterung: Entwicklertools → Netzwerk → Anfrage `data` anklicken → Antwort kopieren und als `.json` speichern.
3. Datei mit sprechendem Namen nach `data/raw/` legen, z. B. `2026-10-26_berlin-50km_psychotherapie.json`, und committen. Die Action baut `practices.json` neu und veröffentlicht die Seite.

Für einen Blick ohne Commit: Tab **Daten → 116117-Export importieren** (mehrere Dateien möglich; gilt bis zum Neuladen).

Hinweise:
- Größere Regionen in mehrere Suchen aufteilen (z. B. pro Stadt/Fachgebiet). Doppelte Einträge werden beim Zusammenführen entfernt; bei Dubletten gewinnt die alphabetisch spätere Datei.
- Die alte Psychmap-`data.js` (GeoJSON, `window.PSYCHMAP_DATA = …`) kann ebenfalls einfach nach `data/raw/` gelegt werden.
- Einträge ohne Koordinaten erscheinen nur in der Liste, nicht auf der Karte und nicht im Radiusfilter.
- Nutzungsbedingungen der 116117-Arztsuche vor größeren Abrufen prüfen. Die Daten sind kein vollständiges Versorgungsverzeichnis und sagen nichts über freie Therapieplätze aus.

Lokal bauen: `python tools/build_data.py`. Lokal ansehen: `python -m http.server` im Repo-Ordner, dann `http://localhost:8000` (per Doppelklick auf `index.html` kann der Browser `data/` nicht laden).

## Team-Stand teilen

- **state.json exportieren** → Datei im Repo unter `data/state.json` ersetzen und committen.
- **Team-Stand aus dem Repo laden** → übernimmt `data/state.json`; bei Konflikten gewinnt die neuere Änderung, die Auswahl wird ergänzt.

Achtung: Bei einem öffentlichen Repo/Pages-Site sind `state.json` (Owner, Notizen) öffentlich lesbar. Notizen entsprechend knapp halten oder das Repo privat führen.

## HubSpot-CSV

Spalten: `firstname, lastname, salutation, academic_title, email, phone, mobilephone, website, company, address, zip, city, country, specialty, therapy_methods, languages, region, distance_km, outreach_status, owner, note, lead_source, source_id`.
`company` wird als „Praxis {Titel Vorname Name}“ gebildet. `source_id` ist die stabile interne ID, über die auch `state.json` zugeordnet wird.
