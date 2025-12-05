import torch
import numpy as np
import random

import services.recommender_service.src.core.globals as g
from ..core.app_state import rec_app


def create_user(user_id) -> str:

    graph_data = rec_app.state.graph
    graph_with_labels = rec_app.state.graph_with_labels

    user_id = user_id
    new_idx = max(
        max(g.user_to_idx_lp.values(), default=-1),
        max(g.restaurant_to_idx_lp.values(), default=-1),
        max(g.user_to_idx_ep.values(), default=-1),
        max(g.restaurant_to_idx_ep.values(), default=-1)
    ) + 1

    # [review_count, avg_stars_scaled]
    default_raw = np.array([[0.0, 0.7]])
    default_scaled = g.scaler_user.transform(default_raw)


    default_padded = np.pad(
        default_scaled,
        ((0, 0), (0, g.max_dim - default_scaled.shape[1])),
        mode='constant'
    )

    default_feat = torch.tensor(default_padded, dtype=torch.float32).squeeze(0)

    g.user_to_idx_lp[user_id] = new_idx
    graph_data.x = torch.cat([graph_data.x, default_feat.unsqueeze(0)], dim=0)

    
    g.user_to_idx_ep[user_id] = new_idx
    graph_with_labels.x = torch.cat([graph_with_labels.x, default_feat.unsqueeze(0)], dim=0)


def add_user_relations(user_id: str, rest_id_list: list[str], preference_list: list[int]):
    if len(rest_id_list) != len(preference_list):
        return False

    for r in rest_id_list:
        if r not in g.restaurant_to_idx_ep:
            return False

    if user_id not in g.user_to_idx_ep:
        new_user_idx_ep = max(max(g.user_to_idx_ep.values()), max(g.restaurant_to_idx_ep.values())) + 1
        g.user_to_idx_ep[user_id] = new_user_idx_ep
        user_vec = torch.zeros(g.max_dim)
        g.graph_with_labels.x = torch.cat([g.graph_with_labels.x, user_vec.unsqueeze(0)], dim=0)

    def _update_graph(graph, user_idx, rest_to_idx):
        edge_list = graph.edge_index.T.tolist()
        labels = graph.edge_label.cpu().tolist() if hasattr(graph, "edge_label") else [0] * len(edge_list)

        
        exist_edges = {r: lbl for (u, r), lbl in zip(edge_list, labels) if u == user_idx}

        rmv = []

        for i, (res, pref) in enumerate(zip(rest_id_list, preference_list)):
            ridx = rest_to_idx[res]
            if ridx in exist_edges:
                if pref == exist_edges[ridx]:
                    rmv.append(i)  
                else:
    
                    mask = (graph.edge_index[0] == user_idx) & (graph.edge_index[1] == ridx)
                    idx = mask.nonzero(as_tuple=True)[0].item()
                    graph.edge_label[idx] = float(pref)
                    
                    mask_inv = (graph.edge_index[0] == ridx) & (graph.edge_index[1] == user_idx)
                    idx_inv = mask_inv.nonzero(as_tuple=True)[0].item()
                    graph.edge_label[idx_inv] = float(pref)
                    rmv.append(i)

        
        new_rest = [rest_id_list[i] for i in range(len(rest_id_list)) if i not in rmv]
        new_pref = [preference_list[i] for i in range(len(preference_list)) if i not in rmv]


        new_edges = []
        new_labels = []
        for res, pref in zip(new_rest, new_pref):
            ridx = rest_to_idx[res]
            new_edges.extend([[user_idx, ridx], [ridx, user_idx]])
            new_labels.extend([float(pref), float(pref)])

        if new_edges:
            new_edge_index = torch.tensor(new_edges, dtype=torch.long).t().contiguous()
            new_edge_label = torch.tensor(new_labels, dtype=torch.float)
            graph.edge_index = torch.cat([graph.edge_index, new_edge_index], dim=1)
            if hasattr(graph, "edge_label"):
                graph.edge_label = torch.cat([graph.edge_label, new_edge_label])
            else:
                graph.edge_label = new_edge_label

    _update_graph(g.graph_with_labels, g.user_to_idx_ep[user_id], g.restaurant_to_idx_ep)