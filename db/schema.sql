-- Companies Table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    uen VARCHAR(50) UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    hq_country VARCHAR(100),
    founding_year INT,
    is_it_delisted BOOLEAN DEFAULT FALSE,
    stock_exchange_code VARCHAR(20),
    revenue BIGINT,
    number_of_employees INT,
    company_size VARCHAR(50),
    industry VARCHAR(255),
    keywords TEXT,
    products_offered TEXT,
    services_offered TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contacts
CREATE TABLE company_contacts (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id) ON DELETE CASCADE,
    website VARCHAR(500),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    linkedin VARCHAR(500),
    facebook VARCHAR(500),
    instagram VARCHAR(500),
    source_of_data VARCHAR(255)
);

-- Locations
CREATE TABLE company_locations (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id) ON DELETE CASCADE,
    address TEXT,
    country VARCHAR(100),
    is_singapore BOOLEAN,
    source_of_data VARCHAR(255)
);

-- Enrichment Logs
CREATE TABLE enrichment_logs (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id) ON DELETE CASCADE,
    task VARCHAR(255),
    input_text TEXT,
    output_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_company_name ON companies(company_name);
CREATE INDEX idx_company_industry ON companies(industry);
CREATE INDEX idx_contacts_website ON company_contacts(website);
