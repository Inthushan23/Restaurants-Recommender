from pydantic import BaseModel


class RecRequest(BaseModel):
    user_id: str
    user_input: str
    top_k: int = 50