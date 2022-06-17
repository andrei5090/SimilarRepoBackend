from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session
from crud import *
from database import get_db
from schemas import Feedback, CreateAndUpdateFeedback, PaginatedFeedbackInfo
from util.statistics import buildStatistics, getNotValidGoogleSearches
import json

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
        except Exception as e:
            raise HTTPException(**e.__dict__)

    @router.get("/statistics")
    async def get_statistics(self):
        try:
            feedback_list = buildStatistics(get_all_info(self.session, 99999, 0))
            return feedback_list
        except Exception as e:
            raise HTTPException(**e.__dict__)

    # flag invalid google data -> google programmable search error
    # USE ONLY WHEN THE GOOGLE API FAILS, TO REVALIDATE THE DATA IN THE STATISTICS
    # @router.get("/flag")
    # async def flag_google_data(self):
    #     updateTotal = 0
    #     try:
    #         data = get_all_info(self.session, 99999, 0)
    #         wrongId = getNotValidGoogleSearches(data)
    #         for i in wrongId:
    #             for feedback in data:
    #                 if feedback.id == i:
    #                     if 'valid' in feedback.githubLinks['google'] and feedback.githubLinks['google'][
    #                         'valid'] == False:
    #                         continue
    #
    #                     feedback.githubLinks['google']['valid'] = False
    #                     a = FeedbackInfo()
    #                     a.githubLinks = feedback.githubLinks.copy()
    #                     b = FeedbackInfo()
    #                     b.githubLinks = ''
    #                     # feedback.githubLinks = feedback.githubLinks.copy
    #                     update_feedback_google_links(self.session, feedback.id, b)
    #                     update_feedback_google_links(self.session, feedback.id, a)
    #                     updateTotal += 1
    #
    #         return "A number of " + str(updateTotal) + "answers were flagged as invalid."
    #     except Exception as e:
    #         raise HTTPException(**e.__dict__)
