from pydantic import BaseModel

class UserDTO(BaseModel):
    username: str
    email: str
    avatar_uri: str
