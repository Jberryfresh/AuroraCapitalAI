import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from aurora.scheduler import AsyncScheduler, run_ingestion_for_tickers

@pytest.fixture
def mock_agent(monkeypatch):
    """Mock the DataIngestionAgent."""
    mock = MagicMock()
    mock.initialize = AsyncMock()
    mock.run = AsyncMock()
    mock.cleanup = AsyncMock()
    monkeypatch.setattr("aurora.scheduler.DataIngestionAgent", lambda: mock)
    return mock

@pytest.mark.asyncio
async def test_scheduler_runs_task(mock_agent):
    """Test that the scheduler runs a task periodically."""
    scheduler = AsyncScheduler()
    scheduler.add_periodic_task(run_ingestion_for_tickers, seconds=0.1, tickers=["TEST"])
    
    # Run the scheduler for a short time
    task = asyncio.create_task(scheduler.start())
    await asyncio.sleep(0.25)
    scheduler.stop()
    await task

    # Check that the agent's methods were called
    assert mock_agent.initialize.call_count > 0
    assert mock_agent.run.call_count > 0
    assert mock_agent.cleanup.call_count > 0
    mock_agent.run.assert_called_with(["TEST"])

@pytest.mark.asyncio
async def test_scheduler_stops_cleanly():
    """Test that the scheduler stops cleanly."""
    scheduler = AsyncScheduler()
    mock_task = AsyncMock()
    scheduler.add_periodic_task(mock_task, seconds=1)
    
    task = asyncio.create_task(scheduler.start())
    await asyncio.sleep(0.1)
    scheduler.stop()
    await task
    
    # The task should be called once before stopping
    mock_task.assert_called_once()

@pytest.mark.asyncio
async def test_run_ingestion_for_tickers(mock_agent):
    """Test the run_ingestion_for_tickers wrapper function."""
    await run_ingestion_for_tickers(["AAPL", "GOOGL"])
    
    mock_agent.initialize.assert_called_once()
    mock_agent.run.assert_called_once_with(["AAPL", "GOOGL"])
    mock_agent.cleanup.assert_called_once()
