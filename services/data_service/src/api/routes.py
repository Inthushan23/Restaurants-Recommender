from fastapi import APIRouter

data_router = APIRouter(prefix="/data")


@data_router.get("/check")
def get_check():
    return {"check": "ok"}


