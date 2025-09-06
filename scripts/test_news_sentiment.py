"""Test script for news sentiment data ingestion."""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import select, func
from aurora.agents.data_ingestion import DataIngestionAgent
from aurora.database import Base, engine, SessionLocal
from aurora.models import Company, NewsSentiment

async def validate_data(session):
    """Validate the ingested news sentiment data."""
    # Get count of news items per company
    stmt = select(
        Company.ticker,
        func.count(NewsSentiment.id).label('news_count'),
        func.min(NewsSentiment.sentiment_score).label('min_score'),
        func.max(NewsSentiment.sentiment_score).label('max_score')
    ).join(NewsSentiment).group_by(Company.ticker)
    
    results = session.execute(stmt).all()
    
    print("\nValidation Results:")
    print("==================")
    for row in results:
        print(f"Ticker: {row.ticker}")
        print(f"News Items: {row.news_count}")
        print(f"Sentiment Range: {row.min_score:.3f} to {row.max_score:.3f}")
        print("------------------")

async def main():
    """Run test for news sentiment ingestion."""
    # Load environment variables
    load_dotenv()
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    # Initialize agent
    agent = DataIngestionAgent()
    
    # Test with a few well-known tickers
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    
    try:
        # Check Alpha Vantage API key
        if not os.getenv("ALPHA_VANTAGE_API_KEY"):
            raise ValueError("ALPHA_VANTAGE_API_KEY not found in environment")
            
        # Run ingestion
        print("Starting news sentiment ingestion test...")
        print(f"Testing with tickers: {', '.join(test_tickers)}")
        await agent.run(test_tickers)
        print("Successfully completed ingestion")
        
        # Validate results
        session = SessionLocal()
        try:
            await validate_data(session)
        finally:
            session.close()
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
