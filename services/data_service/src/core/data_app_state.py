from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading Supabase data…")

    #### A COMPLETER
    app.state.users_df = ...
    app.state.restaurants_df = ...
    app.state.review_df = ...
    app.state.photo_df = ...

    print("Data loaded!")

    yield 

data_app = FastAPI(lifespan=lifespan)