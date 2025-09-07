from sqlalchemy import create_engine, Column, Integer, String, Boolean, Numeric, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
#from config.settings import DB_URI

Base = declarative_base()
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)

class Company(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, autoincrement=True)
    uen = Column(String(50), unique=True)
    company_name = Column(String(255), nullable=False)
    website = Column(String(500))
    hq_country = Column(String(100))
    industry = Column(String(255))
    company_size = Column(String(50))
    number_of_employees = Column(Integer)
    is_it_delisted = Column(Boolean, default=False)
    stock_exchange_code = Column(String(50))
    revenue = Column(Numeric(18,2))
    founding_year = Column(Integer)

    contacts = relationship("CompanyContact", back_populates="company")
    socials = relationship("CompanySocial", back_populates="company")
    keywords = relationship("CompanyKeyword", back_populates="company")

class CompanyContact(Base):
    __tablename__ = "company_contacts"
    contact_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    source_of_data = Column(String(255))

    company = relationship("Company", back_populates="contacts")

class CompanySocial(Base):
    __tablename__ = "company_socials"
    social_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    platform = Column(String(50))
    url = Column(String(500))
    source_of_data = Column(String(255))

    company = relationship("Company", back_populates="socials")

class CompanyKeyword(Base):
    __tablename__ = "company_keywords"
    keyword_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    keyword = Column(String(255))
    source_of_data = Column(String(255))

    company = relationship("Company", back_populates="keywords")
