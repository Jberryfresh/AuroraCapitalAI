from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Text, ForeignKey, CheckConstraint, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from aurora.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(50))
    currency = Column(String(3))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    financials = relationship("FinancialData", back_populates="company")
    news = relationship("NewsSentiment", back_populates="company")
    reports = relationship("ResearchReport", back_populates="company")

class FinancialData(Base):
    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    report_date = Column(Date, nullable=False)
    report_type = Column(String(10))
    
    # Income Statement
    revenue = Column(Numeric(20, 2))
    operating_income = Column(Numeric(20, 2))
    net_income = Column(Numeric(20, 2))
    eps_basic = Column(Numeric(10, 3))
    eps_diluted = Column(Numeric(10, 3))
    
    # Balance Sheet
    total_assets = Column(Numeric(20, 2))
    total_liabilities = Column(Numeric(20, 2))
    total_equity = Column(Numeric(20, 2))
    cash_and_equivalents = Column(Numeric(20, 2))
    
    # Cash Flow
    operating_cash_flow = Column(Numeric(20, 2))
    investing_cash_flow = Column(Numeric(20, 2))
    financing_cash_flow = Column(Numeric(20, 2))
    
    # Metrics
    market_cap = Column(Numeric(20, 2))
    pe_ratio = Column(Numeric(10, 3))
    price_to_book = Column(Numeric(10, 3))
    debt_to_equity = Column(Numeric(10, 3))
    current_ratio = Column(Numeric(10, 3))
    
    # Metadata
    source_url = Column(Text)
    source_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="financials")

    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'report_date', 'report_type'),
        CheckConstraint("report_type IN ('10-K', '10-Q')")
    )

class NewsSentiment(Base):
    __tablename__ = "news_sentiment"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    published_at = Column(DateTime(timezone=True), nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    source_name = Column(String(255), nullable=False)
    source_url = Column(Text, nullable=False)
    sentiment_score = Column(Numeric(4, 3))
    sentiment_magnitude = Column(Numeric(4, 3))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="news")

    # Constraints
    __table_args__ = (
        CheckConstraint('sentiment_score >= -1 AND sentiment_score <= 1'),
        CheckConstraint('sentiment_magnitude >= 0 AND sentiment_magnitude <= 1')
    )

class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    report_type = Column(String(50), nullable=False)
    report_date = Column(Date, nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=False, server_default='{}')
    data_sources = Column(JSON, nullable=False, server_default='{}')
    agent_versions = Column(JSON, nullable=False, server_default='{}')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="reports")

    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'report_type', 'report_date'),
    )
