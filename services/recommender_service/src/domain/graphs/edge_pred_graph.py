import torch
from torch_geometric.data import Data
import numpy as np
from fastapi import FastAPI

import services.recommender_service.src.core.globals as g




def build_graph_gnn_edge_predictor(subset_users, subset_restaurants, subset_reviews, app: FastAPI):

    g.user_to_idx_ep = {uid: i for i, uid in enumerate(subset_users['user_id'])}
    num_users = len(g.user_to_idx_ep)

    g.restaurant_to_idx_ep = {rid: i + num_users for i, rid in enumerate(subset_restaurants['business_id'])}
    g.restaurant_idx_id_ep = {i + num_users: rid for i, rid in enumerate(subset_restaurants['business_id'])}

    max_dim = max(g.user_features.shape[1], g.restaurant_features.shape[1])

    user_features_padded = np.pad(
        g.user_features,
        ((0, 0), (0, max_dim - g.user_features.shape[1])),
        mode='constant'
    )

    restaurant_features_padded = np.pad(
        g.restaurant_features,
        ((0, 0), (0, max_dim - g.restaurant_features.shape[1])),
        mode='constant'
    )

    all_features = np.vstack([user_features_padded, restaurant_features_padded])
    x = torch.FloatTensor(all_features)

    edge_list = []
    edge_labels = []

    likes = subset_reviews[subset_reviews['stars'] >= 3]
    for _, row in likes.iterrows():
        if row['user_id'] in g.user_to_idx_ep and row['business_id'] in g.restaurant_to_idx_ep:
            u = g.user_to_idx_ep[row['user_id']]
            r = g.restaurant_to_idx_ep[row['business_id']]
            edge_list.append([u, r])
            edge_list.append([r, u])
            edge_labels.extend([1.0, 1.0])

    dislikes = subset_reviews[subset_reviews['stars'] <= 2]
    for _, row in dislikes.iterrows():
        if row['user_id'] in g.user_to_idx_ep and row['business_id'] in g.restaurant_to_idx_ep:
            u = g.user_to_idx_ep[row['user_id']]
            r = g.restaurant_to_idx_ep[row['business_id']]
            edge_list.append([u, r])
            edge_list.append([r, u])
            edge_labels.extend([0.0, 0.0])

    edge_index = torch.LongTensor(edge_list).t().contiguous()
    edge_label = torch.FloatTensor(edge_labels)

    graph = Data(x=x, edge_index=edge_index, edge_label=edge_label)

    print(f"Edges: {edge_index.shape[1]:,}")
    print(f"Likes: {(edge_label == 1.0).sum().item():,}")
    print(f"Dislikes: {(edge_label == 0.0).sum().item():,}")

    app.state.graph_with_labels = graph

