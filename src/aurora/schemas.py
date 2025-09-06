from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

# Pydantic models for API/serialization

class CompanyBase(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FinancialDataBase(BaseModel):
    company_id: int
    report_date: date
    report_type: str
    revenue: Optional[Decimal] = None
    operating_income: Optional[Decimal] = None
    net_income: Optional[Decimal] = None
    eps_basic: Optional[Decimal] = None
    eps_diluted: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    total_liabilities: Optional[Decimal] = None
    total_equity: Optional[Decimal] = None
    cash_and_equivalents: Optional[Decimal] = None
    operating_cash_flow: Optional[Decimal] = None
    investing_cash_flow: Optional[Decimal] = None
    financing_cash_flow: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    price_to_book: Optional[Decimal] = None
    debt_to_equity: Optional[Decimal] = None
    current_ratio: Optional[Decimal] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None

class FinancialDataCreate(FinancialDataBase):
    pass

class FinancialData(FinancialDataBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class NewsSentimentBase(BaseModel):
    company_id: int
    published_at: datetime
    title: str
    summary: Optional[str] = None
    source_name: str
    source_url: str
    sentiment_score: Optional[float] = None
    sentiment_magnitude: Optional[float] = None

class NewsSentimentCreate(NewsSentimentBase):
    pass

class NewsSentiment(NewsSentimentBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ResearchReportBase(BaseModel):
    company_id: int
    report_type: str
    report_date: date
    content: str
    report_metadata: Dict[str, Any] = {}
    data_sources: Dict[str, Any] = {}
    agent_versions: Dict[str, Any] = {}

class ResearchReportCreate(ResearchReportBase):
    pass

class ResearchReport(ResearchReportBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
