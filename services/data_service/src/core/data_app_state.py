from fastapi import FastAPI
from contextlib import asynccontextmanager
from ..repository.load_data import load_data_from_supabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading Supabase data...")

    users_df, restaurants_df, review_df, photo_df = load_data_from_supabase()

    app.state.users_df = users_df
    app.state.restaurants_df = restaurants_df
    app.state.review_df = review_df
    app.state.photo_df = photo_df

    print("Data loaded from Supabase!")
    yield


data_app = FastAPI(lifespan=lifespan)
