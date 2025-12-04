from .src.core.data_app_state import data_app
from .src.api.routes import data_router

from .src.domain.preprocessing import preprocess_data


users_df = data_app.state.users_df
restaurants_df = data_app.state.restaurants_df
review_df = data_app.state.review_df
    
# Ici on preprocess la data et derrière, on va save les nouveaux datasets dans des app.state (voir dans la fonction)
# Attention, cette fonction transforme les datasets en input en un subset. Il faut retirer cette partie ci besoin 
# (c'est là où il y a .nlargest() et head(5000))
preprocess_data(users_df, restaurants_df, review_df)


data_app.include_router(data_router)

