from .src.core.app_state import rec_app
from .src.core.startup import load_models
from .src.api.routes import router

import pandas as pd
import numpy as np
import ast
from collections import Counter

import services.recommender_service.src.core.globals as g



df_reviews = pd.read_parquet(r'review1.parquet')
df_users = pd.read_parquet(r'user1.parquet')
df_restaurants = pd.read_json(r"business1.json")

def top_k_categories(k, subset_restaurants):
        all_categories = []
        for cats in subset_restaurants['categories'].dropna():
            if isinstance(cats, str):
                all_categories.extend([c.strip() for c in cats.split(',')])
        return [cat for cat, _ in Counter(all_categories).most_common(k)]


def preprocess_data(users_df, restaurants_df, reviews_df):

    reviews_df = reviews_df.drop(columns=['useful', 'funny', 'cool', 'date', 'text'])
    restaurants_df = restaurants_df.drop(columns=['name', 'address', 'city', 'state', 'postal_code',
       'latitude', 'longitude', 'is_open', 'HairSpecializesIn', 'AcceptsInsurance'])
    users_df = users_df.drop(columns=['compliment_hot', 'compliment_more', 'compliment_profile',
       'compliment_cute', 'compliment_list', 'compliment_note', 'compliment_plain',
       'compliment_cool', 'compliment_funny', 'compliment_writer', 'compliment_photos',
       'friends', 'name', 'fans', 'useful', 'funny', 'cool', 'elite', 'yelping_since'])

    top_users = users_df.nlargest(10000, 'review_count')['user_id'].values
    subset_reviews = reviews_df[reviews_df['user_id'].isin(top_users)].copy()
    top_restaurants = subset_reviews['business_id'].value_counts().head(5000).index.values
    subset_reviews = subset_reviews[subset_reviews['business_id'].isin(top_restaurants)].copy()

    subset_users = users_df[users_df['user_id'].isin(subset_reviews['user_id'].unique())].copy()
    subset_restaurants = restaurants_df[restaurants_df['business_id'].isin(top_restaurants)].copy()

    subset_users['review_count_log'] = np.log1p(subset_users['review_count'])
    subset_users['average_stars_norm'] = subset_users['average_stars'] / 5.0
    user_features_cols = ['review_count_log', 'average_stars_norm']

    col_to_dict = ["BusinessParking", "Ambience", "GoodForMeal"]
    for col in col_to_dict:
        subset_restaurants[col] = subset_restaurants[col].apply(lambda x: ast.literal_eval(x))

    subset_restaurants['stars_norm'] = subset_restaurants['stars'] / 5.0
    subset_restaurants['review_count_log'] = np.log1p(subset_restaurants['review_count'])
    subset_restaurants['RestaurantsPriceRange2'] = pd.to_numeric(subset_restaurants['RestaurantsPriceRange2'], errors='coerce').fillna(2.0)
    subset_restaurants['price_norm'] = subset_restaurants['RestaurantsPriceRange2'] / 4.0


    top_k_cat = top_k_categories(50, subset_restaurants)
    rmv_list = ['Food', 'Event Planning & Services', 'Venues & Event Spaces', 'Restaurants']
    top_k_cat = [i for i in top_k_cat if i not in rmv_list]

    for cat in top_k_cat:
        subset_restaurants[f'cat_{cat}'] = subset_restaurants['categories'].apply(
            lambda x: 1.0 if isinstance(x, str) and cat in x else 0.0
        )

    boolean_attrs = [
        'RestaurantsDelivery', 'OutdoorSeating', 'BusinessAcceptsCreditCards',
        'BikeParking', 'RestaurantsTakeOut', 'GoodForKids', 'Caters',
        'RestaurantsReservations', 'RestaurantsTableService', 'RestaurantsGoodForGroups',
        'WheelchairAccessible', 'HasTV', 'HappyHour', 'DriveThru',
        'BusinessAcceptsBitcoin', 'DogsAllowed', 'Open24Hours'
    ]

    def parse_boolean(val):
        if pd.isna(val) or val is None or val == 'None':
            return 0.0
        if isinstance(val, bool):
            return 1.0 if val else 0.0
        if isinstance(val, str):
            val = val.lower()
            if val in ['true', '1', 'yes']:
                return 1.0
            if val in ['false', '0', 'no']:
                return 0.0
        return 0.0

    for attr in boolean_attrs:
        if attr in subset_restaurants.columns:
            subset_restaurants[f'{attr}_bool'] = subset_restaurants[attr].apply(parse_boolean)

    categorical_attrs = {
        'WiFi': ['free', 'no', 'paid'],
        'Alcohol': ['full_bar', 'beer_and_wine', 'none'],
        'NoiseLevel': ['quiet', 'average', 'loud', 'very_loud'],
        'RestaurantsAttire': ['casual', 'dressy', 'formal'],
        'Smoking': ['no', 'yes', 'outdoor'],
        'BusinessParking': ['garage', 'lot', 'street', 'valet', 'validated'],
        'Ambience': ['casual', 'classy', 'divey', 'hipster', 'intimate', 'romantic', 'touristy', 'trendy','upscale'],
        'GoodForMeal': ['lunch', 'brunch', 'dessert', 'dinner', 'latenight', 'breakfast']
    }

    for attr, values in categorical_attrs.items():
        if attr in subset_restaurants.columns:
            for val in values:
                subset_restaurants[f'{attr}_{val}'] = subset_restaurants[attr].apply(
                    lambda x: 1.0 if isinstance(x, str) and val in x.lower() and x != "None" else 0.0
                )

    restaurant_features_cols = (
        ['stars_norm', 'review_count_log', 'price_norm']
        + [f'cat_{cat}' for cat in top_k_cat]
        + [f'{attr}_bool' for attr in boolean_attrs if attr in subset_restaurants.columns]
        + [f'{attr}_{val}' for attr, values in categorical_attrs.items()
           for val in values if attr in subset_restaurants.columns]
    )

    subset_restaurants_fillna = subset_restaurants[restaurant_features_cols].fillna(0)
    subset_users_fillna = subset_users[user_features_cols].fillna(0)

    return subset_users, subset_restaurants, subset_reviews, subset_users_fillna, subset_restaurants_fillna

subset_users, subset_restaurants, subset_reviews, subset_users_fillna, subset_restaurants_fillna = preprocess_data(df_users, df_restaurants, df_reviews)


g.user_features = g.scaler_user.fit_transform(subset_users_fillna)
g.restaurant_features = g.scaler_restaurant.fit_transform(subset_restaurants_fillna)


# graphs
from .src.domain.graphs.edge_pred_graph import build_graph_gnn_edge_predictor
from .src.domain.graphs.link_pred_graphs import build_graph_link_predictor

build_graph_link_predictor(subset_users, subset_restaurants, subset_reviews, rec_app)
build_graph_gnn_edge_predictor(subset_users, subset_restaurants, subset_reviews, rec_app)
load_models(rec_app)

rec_app.include_router(router)
