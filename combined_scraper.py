import asyncio
import csv
import argparse
import time
from playwright.async_api import async_playwright

# --- Helpers ---
def clean(text):
    return text.strip().replace('\n', ' ') if text else "Unknown"

async def scrape_listing(page, page_num):
    url = f"https://www.freeones.com/babes?page={page_num}"
    await page.goto(url)
    await page.wait_for_selector('[data-test="teaser-card"]')
    cards = await page.query_selector_all('[data-test="teaser-card"]')
    results = []
    for card in cards:
        name_el = await card.query_selector('[data-test="teaser-name"]')
        name = clean(await name_el.inner_text()) if name_el else "Unknown"
        link_el = await card.query_selector('a')
        link = "https://www.freeones.com" + await link_el.get_attribute('href') if link_el else "Unknown"
        img_el = await card.query_selector('img')
        img_url = await img_el.get_attribute('src') if img_el else ""
        bio_url = link.replace('/videos', '/bio') if link else ""
        results.append({"name": name, "url": link, "image_url": img_url, "bio_url": bio_url})
    return results

async def scrape_bio(page, entry):
    try:
        await page.goto(entry["bio_url"], timeout=60000)
        await page.wait_for_selector("body")
        # Summary
        summary_el = await page.query_selector("article p")
        entry["summary"] = clean(await summary_el.inner_text()) if summary_el else "Unknown"
        # Info table
        info_pairs = await page.query_selector_all("ul.profile-meta-list li")
        for pair in info_pairs:
            label_el = await pair.query_selector("span")
            value_el = await pair.query_selector("a, span.font-size-xs")
            label = clean(await label_el.inner_text()) if label_el else ""
            value = clean(await value_el.inner_text()) if value_el else ""
            if label and label.endswith(":"):
                label = label[:-1]
            entry[label] = value or "Unknown"
    except Exception as e:
        print(f"[ERR] Bio scrape failed for {entry['name']}: {e}")
    return entry

async def main(pages, outfile, delay, concurrency, reuse_list):
    start_time = time.time()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        if not reuse_list:
            all_listings = []
            for p in range(1, pages+1):
                listings = await scrape_listing(page, p)
                all_listings.extend(listings)
                elapsed = time.time() - start_time
                eta = (elapsed / p) * (pages - p)
                print(f"[LIST] Page {p}/{pages} scraped. ETA: {eta/60:.1f} min")
                await asyncio.sleep(delay)
        else:
            with open(reuse_list, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                all_listings = list(reader)

        # Scrape bios
        bios = []
        sem = asyncio.Semaphore(concurrency)

        async def worker(entry, idx, total):
            async with sem:
                elapsed = time.time() - start_time
                eta = (elapsed / max(1, idx)) * (total - idx)
                print(f"[BIO ] {idx}/{total} {entry['name']} ETA: {eta/60:.1f} min")
                bios.append(await scrape_bio(page, entry))

        tasks = [worker(e, i+1, len(all_listings)) for i, e in enumerate(all_listings)]
        await asyncio.gather(*tasks)

        await browser.close()

    # Write output
    keys = set()
    for row in bios:
        keys.update(row.keys())
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(keys))
        writer.writeheader()
        writer.writerows(bios)
    print(f"[DONE] Saved {len(bios)} entries to {outfile}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=104)
    ap.add_argument("--outfile", type=str, default="freeones_all_104.csv")
    ap.add_argument("--delay", type=float, default=1)
    ap.add_argument("--concurrency", type=int, default=3)
    ap.add_argument("--reuse-list", type=str, default=None)
    args = ap.parse_args()
    asyncio.run(main(args.pages, args.outfile, args.delay, args.concurrency, args.reuse_list))
