import torch
import json
import requests
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv(r"services\recommender_service\.env") 

api_key = os.getenv("OPENAI_API_KEY")

import services.recommender_service.src.core.globals as g



# Temporaire
import pandas as pd
from ....data_service.src.core.data_app_state import data_app

subset_restaurants = data_app.state.subset_restaurants


llm=ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.0,
    max_tokens=300
)


# graph: pour le link_pred
# graph_with_labels: pour le edge_pred
def get_top_k_rec(user_id, graph, graph_with_labels, top_k, model_linkpred, model_labelpred, device = 'cpu'):

    user_idx = g.user_to_idx_lp[user_id]
    with torch.no_grad():
        z_link = model_linkpred.encode(graph.x.to(device), graph.edge_index.to(device))
        
        # Tous les restaurants possibles pour cet utilisateur
        restaurant_indices = torch.tensor(list(g.restaurant_to_idx_lp.values()), device=device)
        user_indices = torch.full_like(restaurant_indices, user_idx, device=device)
        edge_candidates = torch.stack([user_indices, restaurant_indices], dim=0)
        
        # Score de relation
        scores = model_linkpred.decode(z_link, edge_candidates)
        probs_link = torch.sigmoid(scores)
        
        # Filtrer les arêtes les plus probables
        threshold = 0.5
        selected_edges = edge_candidates[:, probs_link > threshold]

    with torch.no_grad():
        z_label = model_labelpred.encode(graph_with_labels.x.to(device), graph_with_labels.edge_index.to(device))
        like_scores = model_labelpred.decode(z_label, selected_edges)
        like_probs = torch.sigmoid(like_scores)


    top_indices = torch.topk(like_probs, k=top_k).indices
    recommended_restaurants_idx = selected_edges[1, top_indices].cpu().numpy()
    recommended_restaurants = [g.restaurant_idx_id_ep[i] for i in recommended_restaurants_idx]


    return recommended_restaurants


# def get_recommendation(user_id, user_input, graph, graph_with_labels, model_linkpred, model_labelpred, top_k = 50):
    
#     prompt=f"""You are an information extraction model.\
# Given a user description of a restaurant,extract all relevant Yelp-style attributes from the list below.\
# If an attribute is not mentioned,set it to "unknown".\
# Output must be a valid JSON object.\
# Attributes to extract:\
# -RestaurantsTakeOut\
# -RestaurantsDelivery\
# -ByAppointmentOnly\
# -GoodForKids\
# -BusinessParking (garage,street,validated,lot,valet)\
# -BikeParking\
# -WheelchairAccessible\
# -OutdoorSeating\
# -WiFi\
# -NoiseLevel\
# -Alcohol\
# -HasTV\
# -GoodForMeal (breakfast,lunch,dinner,brunch,dessert)\
# -RestaurantsReservations\
# User input : {user_input}
# """
    
#     extract_feat=llm.invoke(prompt).content
#     data=json.loads(extract_feat)
#     recommended_restaurants = get_top_k_rec(user_id, graph, graph_with_labels, top_k, model_linkpred, model_labelpred)
#     print(f"Top recommendation for user {user_id}:")
#     recommanded=[]
#     return subset_restaurants[subset_restaurants["business_id"].isin(recommended_restaurants)]
#     # i=0
#     # for row in subset_restaurants[subset_restaurants["business_id"].isin(recommended_restaurants)].iterrows():
#     #     i+=1
#     #     tastes_fitted=True
#     #     for categorie in data:
#     #         if row[1][categorie] is not None:
#     #             if categorie=="GoodForMeal":
#     #                 mealType=False
#     #                 for sub in data[categorie]:
                        
#     #                     if data[categorie][sub]==row[1][categorie][sub]:
#     #                         mealType=True
#     #                 tastes_fitted=False if mealType==False else True
#     #             elif data[categorie]!="unknown" and data[categorie]!=row[1][categorie]:
#     #                 tastes_fitted=False

#     #     if tastes_fitted:
#     #         # Convert to dict instead of appending the row tuple
#     #         restaurant_dict = row[1].to_dict()
#     #         recommanded.append(restaurant_dict)
#     #         print(f"Restaurant ID: {row[1]['business_id']} | Stars: {row[1]['stars']} | Categories: {row[1]['categories']}")
    
#     # return recommanded

def get_recommendation(user_id, user_input, graph, graph_with_labels, model_linkpred, model_labelpred, top_k = 50):
    
    prompt=f"""You are an information extraction model.\
Given a user description of a restaurant,extract all relevant Yelp-style attributes from the list below.\
If an attribute is not mentioned,set it to "unknown".\
Output must be a valid JSON object.\
Attributes to extract:\
-RestaurantsTakeOut\
-RestaurantsDelivery\
-ByAppointmentOnly\
-GoodForKids\
-BusinessParking (garage,street,validated,lot,valet)\
-BikeParking\
-WheelchairAccessible\
-OutdoorSeating\
-WiFi\
-NoiseLevel\
-Alcohol\
-HasTV\
-GoodForMeal (breakfast,lunch,dinner,brunch,dessert)\
-RestaurantsReservations\
User input : {user_input}
"""
    
    RECOMMANDED_PROMPT="""
    
    Given a user query and a top recommendation list, you return the top 5 best restaurant based on the query criterias.\
You will follow this format :\
restaurant_id1 / restaurant_id2 / restaurant_id3 / restaurant_id4 / restaurant_id5\
You only provide the top restaurant IDs and you do not create any information, you only refer to the top recommendation list.\
User query : {userInput}\
top recommendation list : {recommendationList}
"""
    
    extract_feat=llm.invoke(prompt).content
    data=json.loads(extract_feat)
    
    recommended_restaurants = get_top_k_rec(user_id, graph, graph_with_labels, top_k, model_linkpred, model_labelpred)
    print(f"Top recommendation for user {user_id}:")
    recommanded=[]
    i=0
    for row in subset_restaurants[subset_restaurants["business_id"].isin(recommended_restaurants)].iterrows():
        i+=1
        tastes_fitted=True
        for categorie in data:
            if row[1][categorie] is not None:
                if data[categorie]!="unknown":
                    if categorie=="GoodForMeal" or categorie=="BusinessParking":
                        dictType=False
                        for sub in data[categorie]:
                            if data[categorie][sub]==row[1][categorie][sub]:
                                dictType=True
                        tastes_fitted=False if dictType==False else True
                    elif data[categorie]!= row[1][categorie]:
                        tastes_fitted=False

        if tastes_fitted:
            recommanded.append(row[1])

    recommandation_data=[{cat : dictio[cat] for cat in ["business_id","categories","hours"]} for dictio in recommanded]

    recommendation_choices=llm.invoke(RECOMMANDED_PROMPT.format(userInput=user_input,recommendationList=recommandation_data)).content.split(" / ")
    if len(recommendation_choices)!=1:
        choices=[]
        for recommend in recommanded:
            if recommend["business_id"] in recommendation_choices:
                choices.append(recommend)
    else:
        choices=recommanded[:5]
    for choice in choices:
        print(f"Restaurant ID: {choice['business_id']} | Stars: {choice['stars']} | Categories: {choice['categories']}")
    
    return choices