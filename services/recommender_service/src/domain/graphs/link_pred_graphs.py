import torch
from torch_geometric.data import Data
import numpy as np
from fastapi import FastAPI


import services.recommender_service.src.core.globals as g


def build_graph_link_predictor(subset_users, subset_restaurants, subset_reviews, app: FastAPI):

    
    g.user_to_idx_lp = {uid: i for i, uid in enumerate(subset_users['user_id'])}

    num_users = len(g.user_to_idx_lp)

    g.restaurant_to_idx_lp = {rid: i + num_users for i, rid in enumerate(subset_restaurants['business_id'])}
    g.restaurant_idx_id_lp = {i + num_users: rid for i, rid in enumerate(subset_restaurants['business_id'])}


    g.max_dim = max(g.user_features.shape[1], g.restaurant_features.shape[1])

    user_features_padded = np.pad(
        g.user_features,
        ((0, 0), (0, g.max_dim - g.user_features.shape[1])),
        mode='constant'
    )

    restaurant_features_padded = np.pad(
        g.restaurant_features,
        ((0, 0), (0, g.max_dim - g.restaurant_features.shape[1])),
        mode='constant'
    )

    all_features = np.vstack([user_features_padded, restaurant_features_padded])
    x = torch.FloatTensor(all_features)

    edge_list = []

    interactions = subset_reviews[
        subset_reviews['user_id'].isin(g.user_to_idx_lp)
        & subset_reviews['business_id'].isin(g.restaurant_to_idx_lp)
    ]

    for _, row in interactions.iterrows():
        u = g.user_to_idx_lp[row['user_id']]
        r = g.restaurant_to_idx_lp[row['business_id']]
        edge_list.append([u, r])
        edge_list.append([r, u])

    edge_index = torch.LongTensor(edge_list).t().contiguous()
    graph = Data(x=x, edge_index=edge_index)

    print(f"Number of nodes: {graph.num_nodes}")
    print(f"Number of edges: {graph.num_edges}")

    app.state.graph = graph
    