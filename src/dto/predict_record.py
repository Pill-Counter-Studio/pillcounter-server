from pydantic import BaseModel
from uuid import UUID
from typing import List, Dict

class PredictRecordDTO(BaseModel):
    raw_img_id: UUID
    predict_img_id: UUID
    count: int
    boxes: List[Dict]
    user_id: str


class NoteDTO(BaseModel):
    note: str