from pydantic import BaseModel

class ImageDTO(BaseModel):
    uri: str
