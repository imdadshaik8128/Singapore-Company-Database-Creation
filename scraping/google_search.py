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
    """Check if a URL matches company name rules"""
    if not url or not company_name:
        return False

    clean_url = url.lower()
    if ".sg" not in clean_url:
        return False
    if "companies" in clean_url or "google" in clean_url:
        return False

    # Basic heuristic: company word must appear in domain
    cleaned_name = clean_company_name(company_name)
    company_words = [w.lower() for w in cleaned_name.split() if len(w) > 2]

    for word in company_words:
        if word in clean_url:
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
        search_box.send_keys(f'"{clean_company_name(company_name)}" Singapore site:.sg')
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
