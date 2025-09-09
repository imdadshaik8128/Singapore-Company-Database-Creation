import pandas as pd
import subprocess
import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

INPUT_CSV = os.path.join(PROJECT_ROOT,"data", "output", "rrr_data_enriched.csv")
OUTPUT_CSV = os.path.join(PROJECT_ROOT, "data", "output", "rrr_data_llm.csv")


def query_ollama(text: str) -> dict:
    """Send text to Ollama and parse enrichment fields."""
    prompt = f"""
    You are an assistant that extracts structured company info.

    From the following text, extract:
    - keywords (5-10, relevant search terms)
    - normalized_industry (broad category, e.g., Finance, IT, Healthcare)
    - company_size (Small, Medium, Large based on employees/revenue hints)
    - products_offered (comma-separated list)
    - services_offered (comma-separated list)

    Respond ONLY in JSON with keys:
    ["keywords", "normalized_industry", "company_size", "products_offered", "services_offered"]

    Text:
    {text}
    """

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],  # change model if needed
            input=prompt,
            text=True,
            capture_output=True,
            timeout=60
        )
        response = result.stdout.strip()

        # Extract JSON safely
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end != -1:
            response = response[start:end]
            return json.loads(response)

    except Exception as e:
        print(f" Ollama failed: {e}")

    return {
        "keywords": None,
        "normalized_industry": None,
        "company_size": None,
        "products_offered": None,
        "services_offered": None,
    }


def run_llm_enrichment():
    df = pd.read_csv(INPUT_CSV)

    # Add enrichment columns if missing
    for col in ["keywords", "normalized_industry", "company_size", "products_offered", "services_offered"]:
        if col not in df.columns:
            df[col] = None

    for idx, row in df.iterrows():
        if pd.isna(row.get("raw_text")):
            continue

        print(f"Enriching {row.get('entity_name', 'Unknown')} ...")
        enrichment = query_ollama(row["raw_text"][:2000])  # shorten context

        for key, value in enrichment.items():
            if value:
                df.at[idx, key] = value if not isinstance(value, list) else ", ".join(value)

        if idx % 5 == 0:
            df.to_csv(OUTPUT_CSV, index=False)
            print(f" Progress saved at row {idx}")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"LLM enrichment saved to {OUTPUT_CSV}")
