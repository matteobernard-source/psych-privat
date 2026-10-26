#!/usr/bin/env python3
"""Führt 116117-Exporte aus data/raw/ zu data/practices.json zusammen.

Akzeptierte Eingaben (je Datei, .json oder .js):
  * Antwort von arztsuche.116117.de/api/data  -> {"arztPraxisDatas": [...]}
  * Liste solcher Antworten oder Liste von Einträgen
  * GeoJSON FeatureCollection (z. B. die alte Psychmap data.js mit window.PSYCHMAP_DATA = {...})
  * eine bereits gebaute practices.json ({"records": [...]})

Dateien werden alphabetisch gelesen; bei doppelten Einträgen gewinnt die spätere Datei.
Die IDs (uid) werden genauso berechnet wie im Browser (index.html), damit der
Outreach-Stand (state.json) über Neuimporte hinweg erhalten bleibt.
"""
import datetime
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "practices.json"

FIELDS = ["uid", "titel", "vorname", "name", "anrede", "geschlecht", "tel", "handy", "fax", "email", "web",
          "strasse", "hausnummer", "plz", "ort", "lat", "lon", "fgg", "fg", "psych", "psy", "pv", "pa",
          "fs", "bf", "zb", "src", "sources"]

VERFAHREN = [("Verhaltenstherapie", re.compile(r"verhaltenstherapie", re.I)),
             ("Tiefenpsychologisch fundierte Psychotherapie", re.compile(r"tiefenpsycholog", re.I)),
             ("Analytische Psychotherapie", re.compile(r"analytisch", re.I)),
             ("Systemische Therapie", re.compile(r"systemisch", re.I))]
PSY_GRUPPEN = {"Psychotherapie", "Kinder- und Jugendpsychiatrie"}
PSY_FACH = {"Psychiatrie und Psychotherapie", "Nervenheilkunde", "Psychosomatische Medizin und Psychotherapie"}


def s(v):
    return "" if v is None else str(v).strip()


def num(v):
    if v is None or isinstance(v, bool) or (isinstance(v, str) and not v.strip()):
        return None
    try:
        n = float(v.replace(",", ".")) if isinstance(v, str) else float(v)
    except (TypeError, ValueError, AttributeError):
        return None
    return n if math.isfinite(n) else None


def arr(v):
    if isinstance(v, list):
        return v
    return [] if v is None or v == "" else [v]


def text_list(v):
    out = []
    for x in arr(v):
        if isinstance(x, str):
            t = x
        elif isinstance(x, dict):
            t = x.get("value") or x.get("heading") or x.get("name") or x.get("text") or ""
        else:
            t = ""
        t = s(t)
        if t:
            out.append(t)
    return out


def base36(n):
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if n == 0:
        return "0"
    out = ""
    while n:
        n, r = divmod(n, 36)
        out = digits[r] + out
    return out


def hash_id(text):
    """FNV-1a 32 bit – identisch zur hashId()-Funktion in index.html."""
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return "h" + base36(h)


def uniq(xs):
    return list(dict.fromkeys(xs))


def fg_lists(v):
    """116117: [{"value": "Psychotherapie", "children": [{"value": "Psychologische Psychotherapie"}]}]"""
    grp, fach = [], []
    for x in arr(v):
        if isinstance(x, str):
            t = s(x)
            if t:
                grp.append(t)
                fach.append(t)
        elif isinstance(x, dict):
            g = s(x.get("value") or x.get("name"))
            kids = text_list(x.get("children"))
            if g:
                grp.append(g)
            if kids:
                fach.extend(kids)
            elif g:
                fach.append(g)
    return uniq(grp), uniq(fach)


def psy_lists(v):
    detail = []
    for p in arr(v):
        if isinstance(p, str):
            t = s(p)
            if t:
                detail.append(t)
        elif isinstance(p, dict):
            h = s(p.get("heading"))
            vals = text_list(p.get("values"))
            if vals:
                detail.extend(re.sub(r"\s+", " ", f"{h} {x}").strip() for x in vals)
            elif h:
                detail.append(h)
    detail = uniq(detail)
    return detail, [n for n, rx in VERFAHREN if any(rx.search(d) for d in detail)]


def first(d, *keys):
    for k in keys:
        cur = d
        for part in k.split("."):
            cur = cur.get(part) if isinstance(cur, dict) else None
        if cur not in (None, ""):
            return cur
    return None


def norm_doc(d, src):
    if not isinstance(d, dict):
        return None
    r = {
        "titel": s(d.get("titel")),
        "vorname": s(d.get("vorname")),
        "name": s(d.get("name") or d.get("nachname")),
        "anrede": s(d.get("anrede")),
        "geschlecht": s(d.get("geschlecht")),
        "tel": s(d.get("tel") or d.get("telefon")),
        "handy": s(d.get("handy")),
        "fax": s(d.get("fax")),
        "email": s(d.get("email")),
        "web": re.sub(r"^https?://(?=https?://)", "", s(d.get("web") or d.get("homepage") or d.get("url") or d.get("www")), flags=re.I),
        "strasse": s(d.get("strasse")),
        "hausnummer": s(d.get("hausnummer")),
        "plz": s(d.get("plz")),
        "ort": s(d.get("ort")),
        "lat": num(first(d, "lat", "latitude", "geo.lat", "koordinaten.lat")),
        "lon": num(first(d, "lon", "lng", "longitude", "geo.lon", "geo.lng", "koordinaten.lon")),
        "fs": text_list(d.get("fs")),
        "bf": text_list(d.get("bf")),
        "zb": text_list(d.get("zb")),
        "src": s(d.get("src")) or src,
        "sources": uniq(text_list(d.get("sources")) + [s(d.get("src")) or src]),
    }
    if not r["name"] and not r["vorname"]:
        return None
    grp, r["fg"] = fg_lists(d.get("fg") or d.get("fachgebiete") or d.get("fachrichtungen"))
    r["fgg"] = text_list(d.get("fgg")) if isinstance(d.get("fgg"), list) else grp
    r["psy"], r["pv"] = psy_lists(d.get("psy"))
    alt = " ".join(r["psy"] + r["fg"])
    r["pa"] = [n for n, rx in (("Erwachsene", r"erwachsene"), ("Kinder und Jugendliche", r"kinder|jugendl")) if re.search(rx, alt, re.I)]
    r["psych"] = any(g in PSY_GRUPPEN for g in r["fgg"]) or any(f in PSY_FACH for f in r["fg"])
    if r["lat"] is not None and not (-90 <= r["lat"] <= 90):
        r["lat"] = None
    if r["lon"] is not None and not (-180 <= r["lon"] <= 180):
        r["lon"] = None
    if r["lat"] is None or r["lon"] is None:
        r["lat"] = r["lon"] = None
    else:
        r["lat"], r["lon"] = round(r["lat"], 6), round(r["lon"], 6)
    # "id" ist in der 116117-Antwort nur eine laufende Nummer pro Suche -> nicht Teil der ID
    key = "|".join([r["titel"], r["vorname"], r["name"], r["strasse"], r["hausnummer"], r["plz"]])
    r["uid"] = s(d.get("uid")) or hash_id(key.lower())
    return {k: r[k] for k in FIELDS}


def docs_from(j):
    if isinstance(j, list):
        out = []
        for x in j:
            if isinstance(x, dict) and isinstance(x.get("arztPraxisDatas"), list):
                out.extend(x["arztPraxisDatas"])
            else:
                out.append(x)
        return out
    if isinstance(j, dict):
        if isinstance(j.get("records"), list):
            return j["records"]
        if isinstance(j.get("arztPraxisDatas"), list):
            return j["arztPraxisDatas"]
        if j.get("type") == "FeatureCollection":
            out = []
            for f in j.get("features") or []:
                p = dict(f.get("properties") or {})
                c = (f.get("geometry") or {}).get("coordinates") or []
                if len(c) >= 2:
                    p["lon"], p["lat"] = c[0], c[1]
                out.append(p)
            return out
    return []


def parse_text(text):
    t = text.strip().lstrip("\ufeff")
    if t and t[0] not in "[{":
        t = re.sub(r"^\s*(?:(?:var|let|const)\s+)?(?:window\.)?[\w$.]+\s*=\s*", "", t)
        t = re.sub(r";\s*$", "", t)
    return json.loads(t)


def merge_record(old, new):
    result = dict(old)
    for k, v in new.items():
        if isinstance(v, list):
            result[k] = uniq(arr(old.get(k)) + v)
        elif v is not None and v != "":
            result[k] = v
    return result


def main():
    files = sorted(p for p in RAW.glob("*") if p.suffix.lower() in (".json", ".js", ".txt"))
    merged, report = {}, []
    for p in files:
        try:
            parsed = parse_text(p.read_text(encoding="utf-8"))
            docs = docs_from(parsed)
        except Exception as e:  # noqa: BLE001 – eine kaputte Datei soll den Build nicht stoppen
            print(f"! {p.name}: übersprungen ({e})", file=sys.stderr)
            report.append({"file": p.name, "records": 0, "error": str(e)})
            continue
        n = 0
        for d in docs:
            r = norm_doc(d, p.name)
            if r:
                old = merged.get(r["uid"])
                merged[r["uid"]] = merge_record(old, r) if old else r
                n += 1
        report.append({"file": p.name, "records": n, "moreResults": parsed.get("moreResults") if isinstance(parsed, dict) else None})
        print(f"  {p.name}: {n} Einträge")

    records = sorted(merged.values(), key=lambda r: (r["plz"], r["name"], r["vorname"]))
    without = sum(1 for r in records if r["lat"] is None)
    psych = sum(1 for r in records if r["psych"])
    out = {
        "generated": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "source": "116117 Arztsuche (manuelle Exporte)",
        "count": len(records),
        "without_coords": without,
        "psych": psych,
        "files": report,
        "records": records,
    }
    if not files or not records:
        raise SystemExit("Keine gültigen Kontakte gefunden; vorhandene practices.json bleibt unverändert.")
    if any("error" in item for item in report):
        raise SystemExit("Mindestens eine Quelldatei ist fehlerhaft; practices.json bleibt unverändert.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"→ {OUT.relative_to(ROOT)}: {len(records)} Einträge aus {len(files)} Dateien, davon {psych} Psychotherapie/Psychiatrie, {without} ohne Koordinaten")


if __name__ == "__main__":
    main()
