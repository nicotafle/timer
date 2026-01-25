from pydantic import BaseModel


class User(BaseModel):
    id : str | None = None
    name : str
    email : str
    lastname : str | None = None
    born_date : str | None = None