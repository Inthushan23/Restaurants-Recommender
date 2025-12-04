from fastapi import APIRouter
from ....data_service.src.domain.manage_user import create_user, check_mdp, create_mdp
from ..domain.graphs_relations import create_user as create_user_graph

app_router = APIRouter(prefix="/app")


@app_router.post("/create_user")
async def create_manage_user(user_id, name, mdp):
    cu = await create_user(user_id, name) if callable(getattr(create_user, "__await__", None)) else create_user(user_id, name)
    if not cu:
        return {"create_user": cu}
    if callable(getattr(create_mdp, "__await__", None)):
        await create_mdp(user_id, mdp)
    else:
        create_mdp(user_id, mdp)
    if callable(getattr(create_user_graph, "__await__", None)):
        await create_user_graph(user_id)
    else:
        create_user_graph(user_id)
    return {"create_user": True}


@app_router.post("/sign_in")
async def sign_in(user_id, mdp):
    result = await check_mdp(user_id, mdp) if callable(getattr(check_mdp, "__await__", None)) else check_mdp(user_id, mdp)
    return {"check_mdp": result}
