from fastapi import FastAPI
from ..repository.load_data import load_data
from ..domain.preprocessing import preprocess_data


users_df, restaurants_df, review_df, photo_df = load_data()

data_app = FastAPI()

data_app.state.users_df = users_df
data_app.state.restaurants_df = restaurants_df
data_app.state.review_df = review_df
data_app.state.photo_df = photo_df

preprocess_data(users_df, restaurants_df, review_df, data_app)