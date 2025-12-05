import asyncio
from fastapi import APIRouter
from ..domain.recommender import get_recommendation
from ..domain.graphs_relations import add_user_relations
from ..core.app_state import rec_app
from ..input_models.recrequest import RecRequest 
from ....data_service.src.core.data_app_state import data_app
from .app_routes import add_relations

router = APIRouter(prefix="/recommender")

@router.post("/get_rec")
async def get_rec(input: RecRequest):
    model_linkpred = rec_app.state.link_pred
    model_labelpred = rec_app.state.edge_pred

    graph = rec_app.state.graph
    graph_with_labels = rec_app.state.graph_with_labels

    if not (model_labelpred and model_linkpred):
        return {"recommendation": []}
    rec = await asyncio.to_thread(
        get_recommendation,
        input.user_id,
        input.user_input,
        graph,
        graph_with_labels,
        model_linkpred,
        model_labelpred,
        input.top_k,
    )

    return {"recommendation": rec}

@router.post("/cold_start")
async def cold_start(user_id: str,cold_start_restaurants: list[str],label_tastes: list[int],):

    await asyncio.to_thread(add_user_relations, user_id, cold_start_restaurants, label_tastes)
    await asyncio.to_thread(add_relations, user_id, cold_start_restaurants, label_tastes)

    return {"status": "ok"}