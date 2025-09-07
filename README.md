### Singapore Company ETL and LLM Enrichment Pipeline

### How to Run

1. **Prerequisites**:
   * Install **ChromeDriver** to match your Chrome browser version.
   * Set up a local **PostgreSQL** instance.
   * Install **Ollama** and download the **Mistral** model:
     ```
     ollama run mistral
     ```
   * Ensure your `config/settings.py` file contains the correct `DB_URI`.
   * Place your seed data in `data/input/rrr_data.csv`.
2. **Execution**:


### Solution Summary
- **Approach**: End-to-end ETL pipeline that enriches a seed CSV of Singapore companies, discovers official websites via automated Google search, scrapes contact/social/meta data, performs LLM-based enrichment, and loads structured results into PostgreSQL using SQLAlchemy.
- **Flow**: Seed CSV → Google Search (Selenium) → Website Scraping (Requests/BS4) → LLM Enrichment (Ollama mistral) → DB Load (SQLAlchemy) → PostgreSQL.

### Market Study Insights
- **Web presence**: Most Singapore-registered entities have a `.sg` domain or Singapore-specific landing pages; heuristic matching via name tokens works for many SMEs.
- **Contact discoverability**: Contact emails/phones are frequently available on landing/contact pages; social links (LinkedIn especially) are common and easy to extract.
- **Industry cues**: Meta descriptions and first-paragraph content reliably hint broad industries; precise verticals often need LLM normalization.
- **LLM value-add**: Useful for normalizing industries, deriving company size hints, and extracting product/service descriptors from unstructured text.

### Sources of Information
- **Seed data**: `data/input/rrr_data.csv` (local CSV).
- **Website discovery**: Live Google Search via Selenium WebDriver (headless Chrome); access by automated browsing.
- **Website content**: Company sites fetched with `requests` and parsed via `BeautifulSoup`.
- **LLM enrichment**: Local `ollama` runtime using the `mistral` model; accessed by shelling out with `subprocess` and parsing JSON response.
- **Database**: PostgreSQL `company_db` at `config/settings.py: DB_URI`; accessed via SQLAlchemy.

### AI Model Used & Rationale
- **Model**: `mistral` via Ollama (open-source, local inference).
- **Why**:
  - Runs on local hardware (no data egress), low latency, zero external dependency risks.
  - Strong instruction-following for short JSON extraction tasks.
- **Prompt style** (example extract):
```text
You are an assistant that extracts structured company info.
From the following text, extract:
- keywords (5–10)
- normalized_industry
- company_size
- products_offered
- services_offered
Respond ONLY in JSON keys:
["keywords","normalized_industry","company_size","products_offered","services_offered"]
Text:
{excess_data_snippet}
```
- **API interaction**:
```bash
ollama run mistral
```
Invoked via Python `subprocess.run`, then parse first/last JSON braces and `json.loads`.

### Technology Justification
- **ETL orchestration**: Simple Python script (`pipeline/main.py`) is sufficient and transparent for a linear batch pipeline; no heavy scheduler needed yet.
- **Web discovery**: Selenium WebDriver handles dynamic consent/Google pages robustly compared to plain HTTP.
- **Scraping**: `requests` + `BeautifulSoup` are reliable for static content extraction with light heuristics for social/contact info.
- **LLM**: Ollama with `mistral` offers private, reproducible enrichment without external API limits or costs.
- **Database**: PostgreSQL provides strong relational integrity and indexing; SQLAlchemy ORM makes idempotent upsert-like flows simpler.

### Architecture Diagram
[See diagram above; if not visible, here’s the flow text]
- Seed CSV → Google Search → CSV with websites → Site Scraper → Enriched CSV → LLM Enrichment → Final CSV → DB Loader → PostgreSQL
- Config (`DB_URI`, `OLLAMA_MODEL`) parameterizes components.

### Entity-Relationship Diagram (ERD)
[See ERD above; if not visible, key entities]
- `companies` 1—* `company_contacts`
- `companies` 1—* `company_socials`
- `companies` 1—* `company_keywords`

### Brief Documentation
- **Entity matching**:
  - Website discovery: Clean company names by removing suffixes (e.g., “Pte Ltd”); require `.sg` domain and exclude generic `google`, `companies` URLs; ensure at least one company word appears in domain.
  - DB loading: Prefer matching by `uen` if present; fallback to `company_name`. Insert if not found; append related contacts/socials/keywords.
- **Data quality strategies**:
  - Defensive scraping: Normalize URLs, handle timeouts, and restrict to HTTPS; basic validation on extracted emails/phones.
  - Incremental saves: CSV checkpoints during Google search and scraping to avoid loss; periodic writes during LLM enrichment.
  - Normalization: LLM consolidates free text into controlled fields; keywords deduplicated when splitting comma-separated values.
  - Observability: Console progress logs per stage; clear failure messages for DB load, with pipeline step numbering.

`
- **Outputs**:
  - `rrr_data_with_websites.csv` (intermediate)
  - `output/rrr_data_enriched.csv`
  - `output/rrr_data_llm.csv`
  - Database: tables populated via `db/models.py` mappings.

- **Extensibility**:
  - Swap LLM model via `config/settings.py: OLLAMA_MODEL`.
  - Add more extractors in `site_scraper.py` (e.g., Twitter, YouTube).
  - Introduce retry/backoff or proxy rotation in Google search if needed.

- **Risks**:
  - Google automation may rate-limit; throttle and randomize sleeps.
  - Some sites are JS-heavy; consider headless browser scraping for such cases.
  - LLM JSON parsing may fail; current code extracts JSON substring defensively.

- **Next steps**:
  - Add idempotent upserts to avoid duplicate socials/keywords.
  - Centralize logging/metrics.
  - Optionally move to a workflow tool (e.g., Airflow) if scheduling/monitoring becomes necessary.
