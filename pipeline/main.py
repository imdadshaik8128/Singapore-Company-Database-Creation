import os
import sys
import subprocess

# Ensure project root is on sys.path so root-level modules import correctly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scraping.google_search import run_google_search
from scraping.site_scraper import run_site_scraper
from enrichment.ollama_integration import run_llm_enrichment


INPUT_CSV = "data/input/rrr_data.csv"
GOOGLE_OUTPUT_CSV = "data/output/rrr_data_with_websites.csv"


def main():
    #os.makedirs("output", exist_ok=True)

    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"Input CSV not found at {INPUT_CSV}")

    print("[1/4] Running Google search to find company websites...")
    #run_google_search(INPUT_CSV, GOOGLE_OUTPUT_CSV)

    print("[2/4] Scraping company websites for contact and social data...")
    run_site_scraper()

    print("[3/4] Enriching data via LLM (Ollama)...")
    run_llm_enrichment()

    print("[4/4] Loading enriched CSV into the database...")
    try:
        subprocess.run([sys.executable, os.path.join("db", "load_csv_to_db.py")], check=True)
        print("Database load completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Database load failed with exit code {e.returncode}.")

    print("Pipeline complete. Final output CSV: output/rrr_data_llm.csv")


if __name__ == "__main__":
    main()
