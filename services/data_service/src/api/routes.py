from fastapi import APIRouter
from ..core.data_app_state import data_app

data_router = APIRouter(prefix="/data")


@data_router.get("/check")
def get_check():
    return {"check": "ok"}

@data_router.get("/dataframes")
async def get_data():
    subset_users = data_app.state.subset_users
    subset_restaurants = data_app.state.subset_restaurants 
    subset_reviews = data_app.state.subset_reviews
    photo_df = data_app.state.photo_df 

    return {
        "user_df": subset_users.to_dict(orient="records"),
        "restaurants_df": subset_restaurants.to_dict(orient="records"),
        "review_df": subset_reviews.to_dict(orient="records"),
        "photo_df": photo_df.to_dict(orient="records")
    }
