#!/usr/bin/env python3
"""
Scraper hypotečních sazeb z hypoindex.cz
Spouští se automaticky přes GitHub Actions každý měsíc.
Výstup: data/banky_sazby.csv
"""

import urllib.request
import urllib.error
import re
import csv
import os
import json
from datetime import datetime, date

BANKY_MAP = {
    "česká spořitelna": "Česká spořitelna",
    "čsob": "ČSOB",
    "komerční banka": "Komerční banka",
    "raiffeisenbank": "Raiffeisenbank",
    "moneta": "Moneta",
    "moneta money bank": "Moneta",
}

FIXACE_MAP = {
    "1 rok": "1 rok",
    "3 roky": "3 roky",
    "5 let": "5 let",
    "10 let": "10 let",
}

def fetch_url(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; HypoScraper/1.0)"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")

def parse_hypoindex(html):
    """Parsuje tabulku sazeb z hypoindex.cz"""
    records = []
    today = date.today().replace(day=1).isoformat()

    # Najdi tabulku s daty
    table_match = re.search(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
    if not table_match:
        print("WARN: Tabulka nenalezena v HTML")
        return records

    table_html = table_match.group(1)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)

    # Zjisti hlavičku — pořadí sloupců (fixace)
    header_cells = []
    if rows:
        header_cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', rows[0], re.DOTALL | re.IGNORECASE)
        header_cells = [re.sub(r'<[^>]+>', '', c).strip().lower() for c in header_cells]

    fixace_cols = {}
    for i, cell in enumerate(header_cells):
        for fix_key in FIXACE_MAP:
            if fix_key in cell:
                fixace_cols[i] = FIXACE_MAP[fix_key]

    print(f"Fixace ve sloupcích: {fixace_cols}")

    for row in rows[1:]:
        cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL | re.IGNORECASE)
        cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        if not cells:
            continue

        banka_raw = cells[0].lower().strip()
        banka = None
        for key, val in BANKY_MAP.items():
            if key in banka_raw:
                banka = val
                break
        if not banka:
            continue

        for col_idx, fix_label in fixace_cols.items():
            if col_idx >= len(cells):
                continue
            rate_str = cells[col_idx].replace(",", ".").replace("%", "").strip()
            try:
                rate = float(rate_str)
            except ValueError:
                continue
            records.append({
                "Datum": today,
                "Banka": banka,
                "Fixace": fix_label,
                "Sazba (%)": rate,
                "Zdroj": "manual",
                "Odkaz": "hypoindex.cz"
            })

    return records

def load_existing(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_csv(records, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = ["Datum", "Banka", "Fixace", "Sazba (%)", "Zdroj", "Odkaz"]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

def main():
    out_path = "data/banky_sazby.csv"
    url = "https://www.hypoindex.cz/hypoindex-vyvoj/"

    print(f"Stahuji: {url}")
    try:
        html = fetch_url(url)
    except Exception as e:
        print(f"CHYBA při stahování: {e}")
        # Fallback — zkus přímý článek
        try:
            url2 = "https://www.hypoindex.cz/clanky/"
            html = fetch_url(url2)
        except Exception as e2:
            print(f"CHYBA fallback: {e2}")
            return

    new_records = parse_hypoindex(html)
    print(f"Nalezeno {len(new_records)} nových záznamů")

    existing = load_existing(out_path)
    today = date.today().replace(day=1).isoformat()

    # Odstraň dnešní záznamy (přepíšeme je)
    existing = [r for r in existing if r.get("Datum", "") != today]

    all_records = existing + new_records
    all_records.sort(key=lambda r: (r.get("Datum",""), r.get("Banka",""), r.get("Fixace","")), reverse=True)

    save_csv(all_records, out_path)
    print(f"Uloženo {len(all_records)} záznamů do {out_path}")

    # Zápis metadata
    meta = {"last_update": today, "records": len(all_records), "new": len(new_records)}
    with open("data/meta.json", "w") as f:
        json.dump(meta, f)
    print(f"Metadata: {meta}")

if __name__ == "__main__":
    main()
