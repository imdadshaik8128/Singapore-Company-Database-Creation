import pandas as pd
from sqlalchemy.orm import sessionmaker
from models import engine, Base, Company, CompanyContact, CompanySocial, CompanyKeyword

# ---------------------- Initialize DB ----------------------
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# ---------------------- CSV Setup ----------------------
INPUT_CSV = "data/output/rrr_data_llm.csv"

# Read CSV (Windows-safe encoding)
df = pd.read_csv(INPUT_CSV, encoding='utf-8', low_memory=False)

# Fill missing columns to avoid errors
for col in ["contact_email", "contact_phone", "linkedin", "facebook", "instagram", "keywords"]:
    if col not in df.columns:
        df[col] = None

# ---------------------- Processing CSV ----------------------
BATCH_SIZE = 50
counter = 0

for idx, row in df.iterrows():
    if pd.isna(row.get("entity_name")):
        continue

    # Check if company exists
    company = None
    if not pd.isna(row.get("uen")):
        company = session.query(Company).filter_by(uen=row["uen"]).first()
    if not company:
        company = session.query(Company).filter_by(company_name=row["entity_name"]).first()

    if not company:
        company = Company(
            uen=row.get("uen"),
            company_name=row.get("entity_name"),
            website=row.get("website"),
            hq_country=row.get("hq_country"),
            industry=row.get("industry"),
            company_size=row.get("company_size"),
            number_of_employees=row.get("number_of_employees"),
            is_it_delisted=row.get("is_it_delisted", False),
            stock_exchange_code=row.get("stock_exchange_code"),
            revenue=row.get("revenue"),
            founding_year=row.get("founding_year")
        )
        session.add(company)
        session.flush()  # get company_id

    # Contacts
    if row.get("contact_email") or row.get("contact_phone"):
        contact = CompanyContact(
            company_id=company.company_id,
            contact_email=row.get("contact_email"),
            contact_phone=row.get("contact_phone"),
            source_of_data="csv_import"
        )
        session.add(contact)

    # Socials
    for platform in ["linkedin", "facebook", "instagram"]:
        url = row.get(platform)
        if url and isinstance(url, str) and url.strip():
            social = CompanySocial(
                company_id=company.company_id,
                platform=platform.capitalize(),
                url=url.strip(),
                source_of_data="scraper"
            )
            session.add(social)

    # Keywords (comma-separated)
    if row.get("keywords") and isinstance(row["keywords"], str):
        keywords_list = [k.strip() for k in row["keywords"].split(",") if k.strip()]
        for k in keywords_list:
            keyword = CompanyKeyword(
                company_id=company.company_id,
                keyword=k,
                source_of_data="LLM"
            )
            session.add(keyword)

    counter += 1

    if counter % BATCH_SIZE == 0:
        session.commit()
        print(f" Committed {counter} rows...")

# Final commit
session.commit()
session.close()
print(f" Finished loading {counter} rows into database.")
