from fastapi import FastAPI

from contextlib import asynccontextmanager
import httpx
import asyncio
import services.recommender_service.src.core.globals as g


@asynccontextmanager
async def lifespan(app: FastAPI):

    url = "http://localhost:8001/data/check"
    ready = False
    async with httpx.AsyncClient() as client:
        while not ready:
            try:
                r = await client.get(url)
                if r.status_code == 200:
                    ready = True
            except:
                pass
            await asyncio.sleep(1)
    yield
    

rec_app = FastAPI(lifespan=lifespan)

