import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI

from config import HEALTH_ENDPOINT_URL


async def check_health_job():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_ENDPOINT_URL)
            print(f"[Scheduler] Health check: {response.status_code}")
        except Exception as e:
            print(f"[Scheduler] Error: {e}")


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(check_health_job, "interval", minutes=10)
    scheduler.start()
    print("Scheduler started.")

    yield

    scheduler.shutdown()
