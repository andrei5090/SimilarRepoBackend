from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session
from crud import *
from database import get_db
from schemas import Feedback, CreateAndUpdateFeedback, PaginatedFeedbackInfo

router = APIRouter()


# Example of Class based view
@cbv(router)
class Feedback:
    session: Session = Depends(get_db)

    # API to get the list of feedback
    @router.get("/feedback", response_model=PaginatedFeedbackInfo)
    def list_feedback(self, limit: int = 10, offset: int = 0):

        feedback_list = get_all_info(self.session, limit, offset)
        response = {"limit": limit, "offset": offset, "data": feedback_list}

        return response

    @router.post("/feedback")
    def add_feedback(self, feedback_info: CreateAndUpdateFeedback):
        try:
            feedback_info = create_feedback(self.session, feedback_info)
            return feedback_info
        except Exception as cie:
            raise HTTPException(**cie.__dict__)

