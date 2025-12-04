import pandas as pd 
from ..core.config import USER_PATH, REVIEW_PATH, BUSINESS_PATH, PHOTO_PATH

def load_data():
    try:
        df_users = pd.read_parquet(USER_PATH)
        df_reviews = pd.read_parquet(REVIEW_PATH)
        df_restaurants = pd.read_json(BUSINESS_PATH)
        df_photos = pd.read_json(PHOTO_PATH)
    except FileNotFoundError as fe:
        print("ERROR - ", fe)
        return None 
    except Exception as e:
        print("ERROR - ", e)
        return None
    return df_users, df_restaurants, df_reviews, df_photos
        

