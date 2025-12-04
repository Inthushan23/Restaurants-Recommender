from .src.core.data_app_state import data_app
from .src.api.routes import data_router

data_app.include_router(data_router)

