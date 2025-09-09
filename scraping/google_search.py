import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import re

# ---------------------- Chrome Setup ----------------------
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# ---------------------- Helper Functions ----------------------
def clean_company_name(company_name):
    """Remove suffixes for search query"""
    return re.sub(r'\b(pte ltd|ltd|pty ltd|private limited|company limited|co ltd)\b',
                  '', company_name, flags=re.I).strip()

def is_company_match(url, company_name):
    if not url or not company_name:
        return False

    clean_url = url.lower().strip()

    # Reject blacklisted sites
    blacklist = [
        "companies", "google", "facebook", "linkedin", "youtube", "wikipedia",
        "yellowpages", "sgpbusiness", "carousell", "shopee", "streetdirectory",
        "seair", "abillion", "scam", "tradegecko", "kompass"
    ]
    if any(bad in clean_url for bad in blacklist):
        return False

    # Extract domain part (between // and first /)
    try:
        domain_start = clean_url.find("://") + 3 if "://" in clean_url else 0
        slash_pos = clean_url.find("/", domain_start)
        domain = clean_url[domain_start:slash_pos] if slash_pos > 0 else clean_url[domain_start:]
        path = clean_url[slash_pos:] if slash_pos > 0 else ""
    except Exception:
        return False

    # Check requirement: must contain .sg in domain OR /sg in path
    if ".sg" not in domain:
        return False

    # Clean company name
    cleaned_name = re.sub(
        r"\b(pte ltd|ltd|pty ltd|private limited|company limited|co ltd|&|and)\b",
        "",
        company_name,
        flags=re.I
    ).strip()
    company_words = [w.lower() for w in cleaned_name.split() if len(w) > 2]

    if not company_words:
        return False

    # Check if any company word appears in domain or path
    for word in company_words:
        if word in domain or word in path:
            return True

    return False



def find_website(driver, company_name):
    """Perform Google search and return best website"""
    try:
        driver.get("https://www.google.com")
        time.sleep(1)

        # Accept cookies if needed
        try:
            accept_btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//button[contains(text(), 'Accept') or contains(text(), 'I agree')]"))
            )
            accept_btn.click()
            time.sleep(1)
        except:
            pass

        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.clear()
        search_box.send_keys(f'"{company_name}"')
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

        found_urls = set()
        try:
            links = driver.find_elements(By.CSS_SELECTOR, "a[href^='http']")
            for link in links:
                href = link.get_attribute("href")
                if href:
                    found_urls.add(href)
        except:
            pass

        for url in found_urls:
            if is_company_match(url, company_name):
                return url
        return None

    except Exception as e:
        print(f"Error searching {company_name}: {e}")
        return None

# ---------------------- Main ----------------------
def run_google_search(input_csv, output_csv):
    df = pd.read_csv(input_csv, low_memory=False)

    if "website" not in df.columns:
        df["website"] = None

    driver = init_driver()
    found = 0
    processed = 0

    try:
        for index, row in df.iterrows():
            company_name = row["entity_name"]
            if pd.isna(company_name) or pd.notna(row["website"]):
                continue

            print(f"Searching website for: {company_name}")
            website = find_website(driver, company_name)
            df.at[index, "website"] = website

            if website:
                found += 1
                print(f" Found: {website}")
            else:
                print(" Not found")

            processed += 1
            if processed % 5 == 0:
                df.to_csv(output_csv, index=False)
                print(f"Progress saved: {found}/{processed}")

            time.sleep(random.uniform(8, 15))

        df.to_csv(output_csv, index=False)
        print(f"Finished: {found}/{processed} websites found")

    finally:
        driver.quit()
