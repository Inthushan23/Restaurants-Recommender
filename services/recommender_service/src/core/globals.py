from sklearn.preprocessing import StandardScaler


# link graph
user_to_idx_lp = None
restaurant_to_idx_lp = None
restaurant_idx_id_lp = None

# edge graph
user_to_idx_ep = None
restaurant_to_idx_ep = None
restaurant_idx_id_ep = None

max_dim = None

scaler_user = StandardScaler()
scaler_restaurant = StandardScaler()

user_features = None
restaurant_features = None
