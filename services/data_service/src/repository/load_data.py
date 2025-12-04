import os
from typing import Tuple
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client


def load_data_from_supabase() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load the four datasets (users, restaurants, reviews, photos) from Supabase.
    """

    # Load .env variables
    load_dotenv()

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Supabase credentials not found. Check your .env file.")

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def fetch_table(table_name: str) -> pd.DataFrame:
        response = supabase.table(table_name).select("*").execute()
        if response.data is None:
            raise RuntimeError(f"Could not fetch table '{table_name}' from Supabase.")
        return pd.DataFrame(response.data)

    # ⚠️ IMPORTANT → remplace ici par les VRAIS noms de tes tables dans Supabase
    users_df = fetch_table("users")
    restaurants_df = fetch_table("business")
    review_df = fetch_table("reviews")
    photo_df = fetch_table("photos")

    return users_df, restaurants_df, review_df, photo_df
