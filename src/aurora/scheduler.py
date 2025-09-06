import asyncio
import logging
import os
from typing import List, Callable, Any

from aurora.agents.data_ingestion import DataIngestionAgent

logger = logging.getLogger("AuroraScheduler")


class AsyncScheduler:
    """A lightweight asyncio-based scheduler for periodic tasks.

    Usage:
        scheduler = AsyncScheduler()
        scheduler.add_periodic_task(func, seconds=300, *args, **kwargs)
        asyncio.run(scheduler.start())
    """

    def __init__(self):
        self._tasks: List[asyncio.Task] = []
        # Each runner is a callable that returns an awaitable (coroutine)
        # Use Any to avoid strict typing issues with different awaitable types
        self._runners: List[Callable[[], Any]] = []
        self._stop = False

    def add_periodic_task(self, coro_func: Callable[..., Any], seconds: int, *args, **kwargs):
        async def runner():
            while not self._stop:
                try:
                    await coro_func(*args, **kwargs)
                except Exception:
                    logger.exception("Scheduled task failed")
                await asyncio.sleep(seconds)

        # store the runner function (async function) directly
        self._runners.append(runner)

    async def start(self):
        logger.info("Starting AsyncScheduler with %d runners", len(self._runners))
        loop = asyncio.get_running_loop()
        for r in self._runners:
            # r() is a coroutine object which create_task can run
            t = loop.create_task(r())
            self._tasks.append(t)
        try:
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            logger.info("Scheduler stopped via CancelledError")

    def stop(self):
        logger.info("Stopping scheduler")
        self._stop = True
        for t in self._tasks:
            t.cancel()


async def run_ingestion_for_tickers(tickers: List[str]):
    """Wrapper to run DataIngestionAgent ingestion for a list of tickers once."""
    agent = DataIngestionAgent()
    try:
        logger.info("Scheduler: running ingestion for %s", tickers)
        await agent.initialize()
        await agent.run(tickers)
    finally:
        # ensure agent cleanup is called
        try:
            await agent.cleanup()
        except Exception:
            pass


def load_tickers_from_env() -> List[str]:
    raw = os.getenv("SCHEDULE_TICKERS", "AAPL,MSFT,GOOGL")
    return [t.strip().upper() for t in raw.split(",") if t.strip()]


async def main_loop():
    interval = int(os.getenv("SCHEDULE_INTERVAL_SECONDS", "3600"))
    tickers = load_tickers_from_env()

    scheduler = AsyncScheduler()
    # add ingestion runner
    scheduler.add_periodic_task(run_ingestion_for_tickers, seconds=interval, tickers=tickers)

    await scheduler.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user")
