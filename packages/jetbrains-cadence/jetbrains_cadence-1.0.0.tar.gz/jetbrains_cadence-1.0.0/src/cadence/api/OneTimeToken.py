from pydantic import BaseModel


class OneTimeToken(BaseModel):
    value: str