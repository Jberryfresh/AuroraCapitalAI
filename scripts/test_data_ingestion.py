#!/usr/bin/env python3
"""Test script for DataIngestionAgent."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from aurora.agents.data_ingestion import DataIngestionAgent

async def main():
    """Test data ingestion for sample tickers."""
    # Test tickers (major tech companies)
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    
    agent = DataIngestionAgent()
    
    try:
        print("Starting data ingestion test...")
        await agent.run(test_tickers)
        print("Data ingestion completed successfully!")
        
    except Exception as e:
        print(f"Error during data ingestion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
