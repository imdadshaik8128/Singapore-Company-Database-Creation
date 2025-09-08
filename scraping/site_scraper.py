import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

INPUT_CSV = "data/output/rrr_data_with_websites.csv"
OUTPUT_CSV = "data/output/rrr_data_enriched.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36"
}


def scrape_website(url: str) -> dict:
    """Scrape company website and split structured vs excess data."""
    result = {
        "contact_email": None,
        "contact_phone": None,
        "linkedin": None,
        "facebook": None,
        "instagram": None,
        "meta_description": None,
        "excess_data": None,
    }

    if not isinstance(url, str) or not url.strip():
        return result

    if not url.startswith("http"):
        url = "https://" + url.strip()

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f" Failed to fetch {url}: {e}")
        return result

    soup = BeautifulSoup(resp.text, "html.parser")
    text = resp.text

    # Extract emails & phones
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"\+?\d[\d\s\-]{7,15}", text)
    result["contact_email"] = emails[0] if emails else None
    result["contact_phone"] = phones[0] if phones else None

    # Extract social links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "linkedin.com" in href and not result["linkedin"]:
            result["linkedin"] = href
        elif "facebook.com" in href and not result["facebook"]:
            result["facebook"] = href
        elif "instagram.com" in href and not result["instagram"]:
            result["instagram"] = href

    # Meta description
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        result["meta_description"] = meta["content"]

    # Excess text (everything else useful for LLM)
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    excess_text = " ".join(paragraphs)
    result["excess_data"] = re.sub(r"\s+", " ", excess_text)[:8000]  # keep size safe

    return result


def run_site_scraper():
    df = pd.read_csv(INPUT_CSV)

    # Add new columns if missing
    for col in ["contact_email", "contact_phone", "linkedin", "facebook",
                "instagram", "meta_description", "excess_data"]:
        if col not in df.columns:
            df[col] = None

    for idx, row in df.iterrows():
        website = row.get("website")
        if pd.isna(website) or not website.strip():
            continue

        print(f" Scraping {website} ...")
        details = scrape_website(website)
        for key, value in details.items():
            df.at[idx, key] = value

        if idx % 10 == 0:
            df.to_csv(OUTPUT_CSV, index=False)
            print(f" Progress saved at row {idx}")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f" Enriched data saved to {OUTPUT_CSV}")



