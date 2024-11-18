from typing import List
from pydantic import BaseModel, Field, ConfigDict
from classes.research_paper import ResearchPaper


class Answer(BaseModel):
    reference_ids: List[str] = Field(
        description="""List of reference_ids used in the answer""")
    answer: str = Field(description="""Answer to the user question with inline citations like [W3155739706_32], 
    [W3155739706_31] etc.""")


class AnswerReference(BaseModel):
    reference_text: str
    reference_id: str
    paper: ResearchPaper

    class Config:
        arbitrary_types_allowed = True
class AskQuestionOutput(BaseModel):
    references: List[AnswerReference] = Field(default_factory=List)
    answer: str = Field(default_factory=str)

    class Config:
        arbitrary_types_allowed = True
