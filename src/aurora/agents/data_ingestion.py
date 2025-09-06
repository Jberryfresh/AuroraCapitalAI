"""Data ingestion agent for fetching and storing financial data."""
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
import yfinance as yf
from datetime import datetime, timedelta
import os

from sqlalchemy.orm import Session
from sqlalchemy import select

from aurora.agents.base import BaseAgent, DataFetchError
from aurora.models import Company, FinancialData, NewsSentiment
from aurora.database import SessionLocal
from aurora.config import DISCLAIMER

__all__ = ["DataIngestionAgent"]

class DataIngestionAgent(BaseAgent):
    """Agent responsible for fetching and storing financial data."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="DataIngestionAgent", config=config)
        self.session: Optional[Session] = None
        self.disclaimer = DISCLAIMER
        
        # Get Alpha Vantage API key from environment or config
        self.alpha_vantage_key = (
            (config or {}).get("alpha_vantage_key") 
            or os.getenv("ALPHA_VANTAGE_API_KEY")
        )
        if not self.alpha_vantage_key:
            self.log_activity(
                "Warning: No Alpha Vantage API key found. News fetching will be disabled.",
                level="WARN"
            )

    async def initialize(self) -> None:
        """Initialize database session."""
        self.session = SessionLocal()
        self.log_activity("Initialized database session")

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.session:
            self.session.close()
            self.log_activity("Closed database session")

    async def fetch_company_info(self, ticker: str) -> Dict[str, Any]:
        """Fetch basic company information."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "ticker": ticker,
                "name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "country": info.get("country", ""),
                "currency": info.get("currency", "USD")
            }
        except Exception as e:
            raise DataFetchError(f"Failed to fetch company info for {ticker}: {str(e)}")

    async def fetch_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch latest financial data."""
        try:
            stock = yf.Ticker(ticker)
            
            # Get quarterly financials
            financials = stock.quarterly_financials
            balance_sheet = stock.quarterly_balance_sheet
            cashflow = stock.quarterly_cashflow
            
            if financials.empty or balance_sheet.empty or cashflow.empty:
                raise DataFetchError(f"No financial data available for {ticker}")
            
            # Get the latest quarter data
            latest_quarter = financials.columns[0]
            
            # Helper to safely get value from DataFrame
            def safe_get(df, row_name, col):
                try:
                    return float(df.loc[row_name, col]) if row_name in df.index else None
                except:
                    return None

            return {
                "report_date": latest_quarter if isinstance(latest_quarter, datetime) else datetime.strptime(str(latest_quarter), "%Y-%m-%d").date(),
                "report_type": "10-Q",  # Assuming quarterly
                "revenue": safe_get(financials, "Total Revenue", latest_quarter),
                "operating_income": safe_get(financials, "Operating Income", latest_quarter),
                "net_income": safe_get(financials, "Net Income", latest_quarter),
                "total_assets": safe_get(balance_sheet, "Total Assets", latest_quarter),
                "total_liabilities": safe_get(balance_sheet, "Total Liabilities Net Minority Interest", latest_quarter),
                "total_equity": safe_get(balance_sheet, "Total Equity Gross Minority Interest", latest_quarter),
                "operating_cash_flow": safe_get(cashflow, "Operating Cash Flow", latest_quarter),
                "market_cap": stock.info.get("marketCap"),
                "source_name": "Yahoo Finance",
                "source_url": f"https://finance.yahoo.com/quote/{ticker}"
            }
        except Exception as e:
            raise DataFetchError(f"Failed to fetch financial data for {ticker}: {str(e)}")

    async def store_company_data(self, ticker: str) -> None:
        """Fetch and store company data."""
        if not self.session:
            raise RuntimeError("Database session not initialized")

        try:
            # Fetch company info
            company_info = await self.fetch_company_info(ticker)
            
            # Check if company exists
            stmt = select(Company).where(Company.ticker == ticker)
            company = self.session.execute(stmt).scalar_one_or_none()
            
            if company:
                # Update existing company
                for key, value in company_info.items():
                    setattr(company, key, value)
            else:
                # Create new company
                company = Company(**company_info)
                self.session.add(company)
            
            # Fetch and store financial data
            financial_data = await self.fetch_financial_data(ticker)
            financial_data["company_id"] = company.id
            
            # Check for existing financial data for this period
            stmt = select(FinancialData).where(
                FinancialData.company_id == company.id,
                FinancialData.report_date == financial_data["report_date"]
            )
            existing = self.session.execute(stmt).scalar_one_or_none()
            
            if existing:
                # Update existing record
                for key, value in financial_data.items():
                    setattr(existing, key, value)
            else:
                # Create new record
                new_financial = FinancialData(**financial_data)
                self.session.add(new_financial)
            
            # Fetch and store news data
            news_items = await self.fetch_news_sentiment(ticker)
            if news_items:
                # Flush to ensure company has an ID
                self.session.flush()
                if not isinstance(company.id, int):
                    raise DataFetchError("Could not get company ID")
                await self.store_news_data(int(company.id), news_items)
                self.log_activity(f"Stored {len(news_items)} news items for {ticker}")
            
            # Commit changes
            self.session.commit()
            self.log_activity(f"Successfully stored data for {ticker}")
            
        except Exception as e:
            self.session.rollback()
            raise DataFetchError(f"Failed to store data for {ticker}: {str(e)}")

    async def fetch_news_sentiment(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch news and sentiment data for a company."""
        if not self.alpha_vantage_key:
            self.log_activity(f"Skipping news fetch for {ticker} - no API key", level="WARN")
            return []
        
        try:
            # Initialize results list
            results = []
            
            # Use aiohttp to fetch news data from Alpha Vantage
            async with aiohttp.ClientSession() as session:
                url = "https://www.alphavantage.co/query"
                params = {
                    "function": "NEWS_SENTIMENT",
                    "tickers": ticker,
                    "apikey": self.alpha_vantage_key,
                    "sort": "RELEVANCE"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise DataFetchError(f"API returned status {response.status}")
                        
                    news_data = await response.json()
                    
                    if not news_data or "feed" not in news_data:
                        return []
                    
                    for item in news_data["feed"]:
                        try:
                            news_item = {
                                "title": item.get("title"),
                                "url": item.get("url"),
                                "source": item.get("source"),
                                "summary": item.get("summary"),
                                "published_at": datetime.fromisoformat(item.get("time_published", "")).date(),
                                "sentiment_score": float(item.get("overall_sentiment_score", 0)),
                                "sentiment_label": item.get("overall_sentiment_label")
                            }
                            results.append(news_item)
                        except (ValueError, TypeError) as e:
                            self.log_activity(f"Error processing news item: {str(e)}", level="WARN")
                            continue
                    
                    return results
                
        except Exception as e:
            self.log_activity(f"Error fetching news for {ticker}: {str(e)}", level="ERROR")
            return []

    async def store_news_data(self, company_id: int, news_items: List[Dict[str, Any]]) -> None:
        """Store news items in the database."""
        if not self.session:
            raise RuntimeError("Database session not initialized")
            
        try:
            for item in news_items:
                # Check for existing news item to avoid duplicates
                stmt = select(NewsSentiment).where(
                    NewsSentiment.company_id == company_id,
                    NewsSentiment.url == item["url"]
                )
                existing = self.session.execute(stmt).scalar_one_or_none()
                
                # Prepare news item data
                news_item = {
                    "title": item.get("title"),
                    "summary": item.get("summary"),
                    "source": item.get("source"),
                    "url": item.get("url"),
                    "published_at": item.get("published_at"),
                    "sentiment_score": item.get("sentiment_score"),
                    "sentiment_label": item.get("sentiment_label"),
                    "company_id": company_id
                }
                
                if existing:
                    # Update existing record
                    for key, value in news_item.items():
                        if value is not None:
                            setattr(existing, key, value)
                else:
                    # Create new record
                    news = NewsSentiment(**news_item)
                    self.session.add(news)
                    
            # Changes will be committed in store_company_data
            
        except Exception as e:
            raise DataFetchError(f"Failed to store news data: {str(e)}")

    async def run(self, tickers: List[str]) -> None:
        """Run data ingestion for multiple tickers."""
        try:
            await self.initialize()
            
            for ticker in tickers:
                try:
                    await self.store_company_data(ticker)
                except Exception as e:
                    self.log_activity(f"Error processing {ticker}: {str(e)}", level="ERROR")
                    continue
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(1)
            
        finally:
            await self.cleanup()
