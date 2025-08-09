# FreeOnes Full Scraper

Scrapes:
- The first 104 listing pages of FreeOnes (names, images, bio links)
- The BIO pages for each actress (personal info + appearance)

Outputs:
- One combined CSV with all data

## Features
- Live progress feedback
- Rolling ETA
- Missing values marked as 'Unknown'
- Can reuse existing listing CSV to skip re-scraping listing pages

## Quick Start (Windows)
1. Extract ZIP to a folder
2. Double-click `run_all.bat`
3. Wait for the process to finish — CSV will be created in the same folder

## CLI Options
```bash
python combined_scraper.py --pages 104 --outfile freeones_all_104.csv --delay 1 --concurrency 3
python combined_scraper.py --reuse-list freeones_pages_1_to_104_with_images.csv --outfile freeones_all_104.csv --concurrency 3
```

## Requirements
- Python 3.9+
- Playwright

## Install manually
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

