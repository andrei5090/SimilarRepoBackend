from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, JSON
from database import Base


class FeedbackInfo(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    githubLinks = Column(JSON, nullable=False)
    ownLinks = Column(JSON, nullable=False)
    githubPreferences = Column(JSON, nullable=False)
    ownPreferences = Column(JSON, nullable=False)
