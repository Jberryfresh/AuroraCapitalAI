#!/usr/bin/env python3
"""Test script to verify SQLAlchemy models and database connection."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from datetime import date
from aurora.database import engine, Base, SessionLocal
from aurora.models import Company, FinancialData, NewsSentiment, ResearchReport

def main():
    """Create tables and test with sample data."""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Add test company
        company = Company(
            ticker="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics"
        )
        db.add(company)
        db.flush()  # Get ID without committing
        
        # Add test financial data
        financials = FinancialData(
            company_id=company.id,
            report_date=date(2025, 6, 30),
            report_type="10-Q",
            revenue=100000000000,
            net_income=25000000000,
            eps_basic=1.5,
            market_cap=3000000000000,
            source_name="Test Data"
        )
        db.add(financials)
        
        # Add test news
        news = NewsSentiment(
            company_id=company.id,
            title="Apple Announces Record Quarter",
            summary="Strong iPhone sales drive growth",
            source_name="Test News",
            source_url="https://example.com",
            published_at="2025-09-05T00:00:00+00:00",
            sentiment_score=0.8,
            sentiment_magnitude=0.9
        )
        db.add(news)
        
        # Add test report
        report = ResearchReport(
            company_id=company.id,
            report_type="quick_summary",
            report_date=date(2025, 9, 5),
            content="Test research report content",
            report_metadata={"analyst": "AI-1", "confidence": 0.9},
            data_sources={"financial": "10-Q", "news": "recent_articles"},
            agent_versions={"research": "v1.0"}
        )
        db.add(report)
        
        # Commit everything
        db.commit()
        print("Successfully added test data!")
        
        # Verify relationships
        db.refresh(company)
        print("\nVerifying relationships:")
        print(f"Company: {company.ticker}")
        print(f"Financial records: {len(company.financials)}")
        print(f"News items: {len(company.news)}")
        print(f"Research reports: {len(company.reports)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
