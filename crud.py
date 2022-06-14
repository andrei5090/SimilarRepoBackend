# crud.py
from typing import List
from sqlalchemy.orm import Session
from models import FeedbackInfo
from schemas import CreateAndUpdateFeedback


def get_all_info(session: Session, limit: int, offset: int) -> List[FeedbackInfo]:
    return session.query(FeedbackInfo).offset(offset).limit(limit).all()


def get_feedback_info(session: Session, _id: int) -> FeedbackInfo:
    feedback_info = session.query(FeedbackInfo).get(_id)

    if feedback_info is None:
        raise Exception

    return feedback_info


def create_feedback(session: Session, feedback_info: CreateAndUpdateFeedback) -> FeedbackInfo:
    feedback_info = FeedbackInfo(**feedback_info.dict())
    session.add(feedback_info)
    session.commit()
    session.refresh(feedback_info)
    return feedback_info


def update_feedback(session: Session, _id: int, info_update: CreateAndUpdateFeedback) -> FeedbackInfo:
    feedback_info = get_feedback_info(session, _id)

    if feedback_info is None:
        raise Exception

    print("update_feedback", info_update.githubLinks)

    feedback_info.ownLinks = info_update.ownLinks
    feedback_info.githubPreferences = info_update.githubPreferences
    feedback_info.ownPreferences = info_update.ownPreferences
    feedback_info.githubLinks = info_update.githubLinks
    feedback_info.extraInfo = info_update.extraInfo
    session.commit()
    session.refresh(feedback_info)


    return feedback_info

def update_feedback_google_links(session: Session, _id: int, info_update: CreateAndUpdateFeedback) -> FeedbackInfo:
    feedback_info = get_feedback_info(session, _id)

    if feedback_info is None:
        raise Exception

    print("update_feedback", info_update.githubLinks)
    feedback_info.githubLinks = info_update.githubLinks
    session.commit()
    session.refresh(feedback_info)


    return feedback_info


def delete_feedback(session: Session, _id: int):
    feedback_info = get_feedback_info(session, _id)

    if feedback_info is None:
        raise Exception

    session.delete(feedback_info)
    session.commit()

    return
