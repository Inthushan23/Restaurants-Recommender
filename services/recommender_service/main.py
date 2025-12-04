from .src.core.app_state import rec_app
from .src.core.startup import load_models
from .src.api.rec_routes import router

import services.recommender_service.src.core.globals as g

# graphs
from .src.domain.graphs.edge_pred_graph import build_graph_gnn_edge_predictor
from .src.domain.graphs.link_pred_graphs import build_graph_link_predictor

from ..data_service.src.core.data_app_state import data_app
subset_users = data_app.state.subset_users 
subset_restaurants = data_app.state.subset_restaurants
subset_reviews = data_app.state.subset_reviews 
subset_users_fillna = data_app.state.subset_users_fillna 
subset_restaurants_fillna = data_app.state.subset_restaurants_fillna


g.user_features = g.scaler_user.fit_transform(subset_users_fillna)
g.restaurant_features = g.scaler_restaurant.fit_transform(subset_restaurants_fillna)

build_graph_link_predictor(subset_users, subset_restaurants, subset_reviews, rec_app)
build_graph_gnn_edge_predictor(subset_users, subset_restaurants, subset_reviews, rec_app)

g.user_features = g.scaler_user.fit_transform(subset_users_fillna)
g.restaurant_features = g.scaler_restaurant.fit_transform(subset_restaurants_fillna)


load_models(rec_app)
rec_app.include_router(router)
