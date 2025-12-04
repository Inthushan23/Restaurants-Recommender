from  ..core.data_app_state import data_app
import pandas as pd
from ..core.config import USER_PATH, REVIEW_PATH
from datetime import datetime, timezone
import random



def add_user_df(user_id, name):
    df_users = data_app.state.users_df 
    default_values = {
    'user_id': user_id,
    'name': name,
    'review_count': 0,
    'yelping_since': pd.NaT,  #
    'useful': 0,
    'funny': 0,
    'cool': 0,
    'elite': "",  
    'friends': "",  
    'fans': 0,
    'average_stars': 0.0,
    'compliment_hot': 0,
    'compliment_more': 0,
    'compliment_profile': 0,
    'compliment_cute': 0,
    'compliment_list': 0,
    'compliment_note': 0,
    'compliment_plain': 0,
    'compliment_cool': 0,
    'compliment_funny': 0,
    'compliment_writer': 0,
    'compliment_photos': 0
    }

    df_users = pd.concat([df_users, pd.DataFrame([default_values])], ignore_index=True)
    df_users.to_parquet(USER_PATH)
    




def generate_id(existing_ids: list) -> str:
 
    rev_id = "".join([chr(random.randint(48, 125)) for _ in range(22)])
    if rev_id in existing_ids:
        return generate_id(existing_ids)
    return rev_id

def add_review_df(user_id: str, business_id: str, like: bool) -> bool:

    df_reviews = data_app.state.review_df
    now = datetime.now(timezone.utc).isoformat()


    
    existing = df_reviews[(df_reviews["user_id"] == user_id) & (df_reviews["business_id"] == business_id)]

    if not existing.empty:
        idx = existing.index[0]
        
        current_like = existing.iloc[0]["stars"] >= 3

        if current_like == like:
            print("Review already exists with the same like/dislike.")
            return True
        else:
            
            df_reviews.at[idx, "stars"] = 5 if like else 0
            df_reviews.at[idx, "date"] = now
            print(f"Review updated for user {user_id}, business {business_id}.")
            return True
    else:
        
        existing_ids = df_reviews["review_id"].tolist()
        review_id = generate_id(existing_ids)

        new_record = {
            "review_id": review_id,
            "user_id": user_id,
            "business_id": business_id,
            "stars": 5 if like else 0,
            "useful": 0,
            "funny": 0,
            "cool": 0,
            "text": "",
            "date": now
        }
        df_reviews.loc[len(df_reviews)] = new_record

    df_reviews.to_parquet(REVIEW_PATH, index = False)
