import asyncio
from fastapi import APIRouter
from ....data_service.src.domain.manage_user import create_user, check_mdp, create_mdp, add_or_update_review
from ..domain.graphs_relations import create_user as create_user_graph
from ....data_service.src.domain.update_df import add_user_df, add_review_df
from ..domain.graphs_relations import add_user_relations


app_router = APIRouter(prefix="/app")


@app_router.post("/create_user")
async def create_manage_user(user_id, name, mdp):
    print("Appel test")
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
    add_user_df(user_id, name)
    
    return {"create_user": True}

 


@app_router.post("/sign_in")
async def sign_in(user_id, mdp):
    result = await check_mdp(user_id, mdp) if callable(getattr(check_mdp, "__await__", None)) else check_mdp(user_id, mdp)
    return {"check_mdp": result}


@app_router.post("/add_review")
def add_relations(user_id: str, restaurants: list, labels:list): # True False
    num_lst = list(map(int, labels))
    add = add_user_relations(user_id, restaurants, num_lst)
    if add:
        for rest, lab in zip(restaurants, lab):
            add_or_update_review(user_id, rest, lab) 
            add_review_df(user_id, rest, lab)
        return {"add_review": True}
    else:
        return {"add_review": False}

