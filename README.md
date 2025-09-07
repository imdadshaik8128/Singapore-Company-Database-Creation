        ## **Singapore Company ETL and LLM Enrichment Pipeline**
Overview
This project implements a comprehensive, end-to-end Extract, Transform, and Load (ETL) pipeline designed to enrich a seed dataset of Singaporean companies. The pipeline automates the discovery of official company websites, scrapes publicly available contact and social media information, and utilizes a local Large Language Model (LLM) for advanced data enrichment and normalization. The final, structured data is then loaded into a PostgreSQL database for a robust and queryable knowledge base.

Solution Summary
Approach
The pipeline follows a linear, batch-processing model. It starts with a seed CSV file, discovers company websites through automated Google searches, scrapes essential information, and enriches the data using a locally-hosted LLM. The final output is a populated relational database.

Flow
Seed CSV -> Google Search (Selenium) -> Website Scraping (Requests/BS4) -> LLM Enrichment (Ollama Mistral) -> DB Load (SQLAlchemy) -> PostgreSQL

Key Insights from Market Study
Web Presence: Most Singapore-registered companies have a .sg domain or a clear, locally-focused web presence. A simple name-token matching approach proves effective for discovering websites for many small and medium-sized enterprises (SMEs).

Contact Discoverability: Contact emails and phone numbers are frequently found on landing or dedicated "Contact Us" pages. Social media links, particularly to LinkedIn, are also common and easy to extract.

Industry Cues: Initial industry hints can be reliably inferred from a company's website meta description and first-paragraph text. However, a local LLM is invaluable for normalizing these descriptions into consistent industry verticals.

LLM Value-Add: The LLM is a powerful tool for deriving insights from unstructured text. It excels at normalizing industries, estimating company size, and extracting product/service descriptors with high accuracy.

Technology Stack
Web Discovery: Selenium WebDriver (with ChromeDriver): Handles dynamic web content, including cookie consent banners, and reliably interacts with Google search result pages.

Web Scraping: Requests and BeautifulSoup: A lightweight and efficient combination for parsing static HTML content and extracting specific data points like emails, phones, and social links.

LLM Integration: Ollama and the Mistral model: Chosen for its ability to provide private, predictable, and cost-effective local inference. The model's strong instruction-following capability is ideal for structured data extraction in JSON format.

Database: PostgreSQL: A robust, open-source relational database that ensures data integrity and supports complex queries.

ORM: SQLAlchemy: Provides a clean, Pythonic interface for interacting with the PostgreSQL database, simplifying entity modeling and ensuring idempotent data loads.

Orchestration: Python: The entire pipeline is orchestrated using a simple Python script, pipeline/main.py, which is well-suited for a linear batch process.

Architecture
The pipeline follows a staged architecture, with each step producing an intermediate CSV file that acts as a checkpoint.

data/input/rrr_data.csv -> rrr_data_with_websites.csv (after Google Search) -> output/rrr_data_enriched.csv (after Site Scraping) -> output/rrr_data_llm.csv (after LLM Enrichment) -> PostgreSQL company_db tables (after DB Load)

Configuration for the database connection and LLM model is managed in config/settings.py.

Data Model (Entity-Relationship)
The final data is loaded into four distinct tables to maintain a clean relational structure.

companies:

company_id (PK), uen, company_name, website, hq_country, industry, company_size, number_of_employees, is_it_delisted, stock_exchange_code, revenue, founding_year

company_contacts:

contact_id (PK), company_id (FK), contact_email, contact_phone, source_of_data

company_socials:

social_id (PK), company_id (FK), platform, url, source_of_data

company_keywords:

keyword_id (PK), company_id (FK), keyword, source_of_data

Brief Documentation
How to Run
Prerequisites:

Install ChromeDriver to match your Chrome browser version.

Set up a local PostgreSQL instance.

Install Ollama and download the Mistral model:

ollama run mistral

Ensure your config/settings.py file contains the correct DB_URI.

Place your seed data in data/input/rrr_data.csv.

Execution:

python pipeline/main.py

Data Quality and Extensibility
Data Quality: The pipeline includes defensive measures such as URL validation, timeouts, basic regex validation for contact information, and incremental CSV checkpoints to prevent progress loss.

Extensibility: The modular design allows for easy expansion:

Swap the LLM model by simply changing the OLLAMA_MODEL variable in config/settings.py.

Add new scraping logic to site_scraper.py to capture additional information (e.g., Twitter or YouTube links).

Enhance web discovery with retries and proxy rotation to mitigate rate-limiting.

Known Risks
Google Rate-Limiting: Automated Google search can lead to temporary IP blocks. This is mitigated by using randomized backoff and pacing.

LLM Output Parsing: As LLM output can be unpredictable, the pipeline includes defensive JSON parsing with robust error handling.

This project provides a powerful, automated solution for creating a structured and enriched database of company information from public web sources.
