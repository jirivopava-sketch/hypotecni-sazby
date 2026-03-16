# Hypoteční sazby CZ

Webová aplikace pro sledování hypotečních sazeb českých bank s automatickou aktualizací.

## Rychlý start

### 1. Fork / klonování
```bash
git clone https://github.com/TVOJE-JMENO/hypotecni-sazby.git
cd hypotecni-sazby
```

### 2. Nahraj počáteční data
Zkopíruj svá CSV data do složky `data/`:
- `data/cnb_sazby.csv` — data z ČNB ARAD
- `data/banky_sazby.csv` — sazby jednotlivých bank

### 3. Nastav GitHub Pages
1. GitHub → repozitář → **Settings → Pages**
2. Source: **Deploy from branch**
3. Branch: **main** / **(root)**
4. Uložit → za chvíli dostaneš URL: `https://tvoje-jmeno.github.io/hypotecni-sazby`

### 4. Nastav API klíč ČNB (volitelné)
Pro automatické stahování dat z ČNB ARAD:
1. GitHub → repozitář → **Settings → Secrets and variables → Actions**
2. **New repository secret**
3. Name: `CNB_API_KEY`, Value: tvůj klíč z cnb.cz/arad

### 5. Automatická aktualizace
GitHub Actions spustí scraper automaticky **1. každého měsíce**.

Ruční spuštění: **Actions → Aktualizace hypotečních sazeb → Run workflow**

## Struktura projektu

```
hypotecni-sazby/
├── index.html                          # Hlavní aplikace
├── scraper.py                          # Scraper sazeb (hypoindex.cz + ČNB ARAD)
├── data/
│   ├── banky_sazby.csv                 # Sazby bank (auto-aktualizace)
│   └── cnb_sazby.csv                   # ČNB průměr trhu (auto-aktualizace)
└── .github/
    └── workflows/
        └── update_rates.yml            # GitHub Actions plán
```

## Zdroje dat

| Zdroj | Co poskytuje | Frekvence |
|---|---|---|
| [hypoindex.cz](https://www.hypoindex.cz) | Sazby jednotlivých bank | měsíčně |
| [ČNB ARAD](https://www.cnb.cz/arad) | Průměr trhu dle fixace | měsíčně |

## Lokální spuštění scraperu

```bash
pip install requests beautifulsoup4
CNB_API_KEY=tvuj-klic python scraper.py
```
