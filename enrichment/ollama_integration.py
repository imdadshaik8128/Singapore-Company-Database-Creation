import pandas as pd
import subprocess
import json

INPUT_CSV = "data/output/rrr_data_enriched.csv"
OUTPUT_CSV = "data/output/rrr_data_llm.csv"


def query_ollama(text: str) -> dict:
    """Send excess data to Ollama to extract structured info."""
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
            ["ollama", "run", "mistral"],  # you can switch model
            input=prompt,
            text=True,
            capture_output=True,
            timeout=60,
            encoding="utf-8",   
            errors="ignore"
        )
        response = result.stdout.strip()

        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(response[start:end])

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

    for col in ["keywords", "normalized_industry", "company_size", "products_offered", "services_offered"]:
        if col not in df.columns:
            df[col] = None

    for idx, row in df.iterrows():
        if pd.isna(row.get("excess_data")):
            continue

        print(f"✨ Enriching {row.get('company_name', 'Unknown')} ...")
        enrichment = query_ollama(row["excess_data"][:2000])  # truncate for prompt length

        for key, value in enrichment.items():
            if value:
                df.at[idx, key] = value if not isinstance(value, list) else ", ".join(value)

        if idx % 5 == 0:
            df.to_csv(OUTPUT_CSV, index=False)
            print(f" Progress saved at row {idx}")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"LLM enrichment saved to {OUTPUT_CSV}")


