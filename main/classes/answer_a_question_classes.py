from typing import List
from pydantic import BaseModel, Field, ConfigDict
from main.classes.research_paper import ResearchPaper


class Answer(BaseModel):
    reference_ids: List[str] = Field(
        description="""List of reference_ids used in the answer""")
    answer: str = Field(description="""Answer to the user question with inline citations like [271710510], 
    [266268949] etc.""")


class AnswerReference(BaseModel):
    reference_text: str
    reference_id: str
    paper: ResearchPaper

    class Config:
        arbitrary_types_allowed = True

class AskQuestionOutput(BaseModel):
    references: List[AnswerReference] = Field(default_factory=List)
    answer: str = Field(default_factory=str)
    relevant_papers: List[ResearchPaper] = Field(default_factory=List)

    class Config:
        arbitrary_types_allowed = True

class SearchableQueryAndTitle(BaseModel):
    title: str = Field(default_factory=str, description= "the title of the conversation with user")
    searchable_query: str = Field(default_factory=str, description= "The searchable query for hybrid search")
