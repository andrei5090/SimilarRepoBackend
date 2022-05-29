from pydantic import BaseModel
from typing import Optional, List


class CreateAndUpdateFeedback(BaseModel):
    githubLinks : dict
    ownLinks : dict
    githubPreferences : dict
    ownPreferences : dict
    extraInfo: dict

class Feedback(CreateAndUpdateFeedback):
    id: int
    class Config:
        orm_mode = True


class PaginatedFeedbackInfo(BaseModel):
    limit: int
    offset: int
    data: List[Feedback]