# Psych – lokale Korrektur, 26.10.2026

Noch nicht veröffentlichen. Die Datennutzung und die Versandgrundlage sind nicht freigegeben.

## Installation
1. Eine Kopie deines bisherigen lokalen Ordners Psych-main als Sicherung behalten.
2. index.html aus diesem Paket ersetzt Psych-main/index.html.
3. build_data.py aus diesem Paket ersetzt Psych-main/tools/build_data.py.
4. practices.json aus diesem Paket ersetzt Psych-main/data/practices.json.
5. data/state.json und data/raw/ bleiben unverändert.

Die practices.json ist bereits aus den beiden übermittelten Originalexporten gebaut: 240 Personen-/Standorteinträge. Keine Vollständigkeitsbehauptung. Beide Quellen melden moreResults=true. Die identische zweite Berlin-Datei wurde nicht hinzugefügt.

## Start
Terminal öffnen, `cd ` eingeben (mit Leerzeichen), den Ordner Psych-main aus dem Finder ins Terminal ziehen, Enter. Dann:

python3 -m http.server 8001 --bind 127.0.0.1

Browser: http://127.0.0.1:8001/index.html
Terminal geöffnet lassen; mit Ctrl+C stoppen. Nur auf dem eigenen Rechner erreichbar.

## Weitere lokale Imports
.txt, .json und .js werden unterstützt. Um neue Rohdateien dauerhaft zusammenzuführen: Dateien in data/raw ablegen und im Projektordner `python3 tools/build_data.py` ausführen. Vorhandene JSON-Ausgabe wird bei leeren oder fehlerhaften Quellen nicht überschrieben. Browser-Importe sind bis zum Neuladen vorhanden; für dauerhafte Übernahme practices.json exportieren bzw. Rohdaten neu bauen.

## Behobene Punkte
Python- und Browsernormalisierung stimmen für die beiden Originalexporte überein. Suchlokale id ist nicht mehr Teil der Browserkennung. Fachgebiets-Untergruppen und Therapieverfahren bleiben erhalten. Fehlende Koordinaten bleiben leer. Gleichzeitige Wiederimporte erzeugen im Test keine zusätzlichen Kontakte; Teststatus, Notiz und Auswahl bleiben erhalten. Quellen-Dateinamen werden mitgeführt. Leere Felder eines neuen Imports überschreiben keine bestehenden Angaben.

## Grenzen
Kennungen hängen weiterhin von Titel, Name und Adresse ab. Umzüge, Namens-/Titeländerungen sowie Schreibvarianten erfordern eine manuelle Dublettenprüfung. Keine behauptete globale Personenkennung. Neue Browser-Speicherbereiche v2 vermeiden eine automatische Vermischung mit älteren v1-Ständen. Alte Speicherstände werden nicht gelöscht, aber nicht automatisch migriert. Vor Nutzung älterer state.json-Dateien gesonderte Zuordnung prüfen.

CSV bleibt ein RECHERCHEEXPORT, kein versandfertiger Export. Zusätzliche Spalten kennzeichnen gemeinsame Postfächer (nach gleicher Schreibweise ohne Groß-/Kleinschreibung), ungeprüften Status, fehlende Versandfreigabe und Kein-Interesse-Markierung. Keine automatische Postfachverifikation oder rechtliche Einwilligungsprüfung; nicht direkt in einen Versandprozess importieren. Die Firmenbezeichnung bleibt leer, statt einen Praxisnamen zu erfinden.

Die erneute Python-Aufbereitung überschreibt practices.json, nicht state.json. Team-Stand bleibt manueller Dateiaustausch, kein gleichzeitiges Mehrbenutzer-CRM.

## Tests
Syntaxprüfung, Vergleich beider Normalisierungen an 240 Originaleinträgen und zwei künstlichen Testfällen, identischer Wiederaufbau, wiederholte Browserimporte, Erhalt von Testnotiz/Status/Auswahl, Berlin-/Hamburg-Radiusfilter und Recherche-CSV-Export geprüft. Oberfläche in Desktop- und Mobilgröße im Offline-Fallback betrachtet. Echten Kartenhintergrund und Browserberechtigungen auf deinem Rechner testen. Kein Zugriff auf externe Datenquellen im Test; kein GitHub-Upload oder Deployment.
