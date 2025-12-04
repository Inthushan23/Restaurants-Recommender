from .src.core.data_app_state import data_app
from .src.api.routes import data_router
from .src.domain.preprocessing import preprocess_data


@data_app.get("/")
async def root():
    return {"status": "ok", "service": "data_app"}


@data_app.on_event("startup")
async def run_preprocessing() -> None:
    users_df = data_app.state.users_df
    restaurants_df = data_app.state.restaurants_df
    review_df = data_app.state.review_df

    # Ici on preprocess la data et derrière, on va save les nouveaux datasets
    # dans des app.state (voir dans la fonction).
    # Attention, cette fonction transforme les datasets en input en un subset.
    # Il faut retirer cette partie si besoin (c'est là où il y a .nlargest()
    # et head(5000)).
    preprocess_data(users_df, restaurants_df, review_df)


data_app.include_router(data_router)
