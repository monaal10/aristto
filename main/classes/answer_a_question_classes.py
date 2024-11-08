from typing import List
from pydantic import BaseModel, Field, ConfigDict
from classes.research_paper import ResearchPaper


class Answer(BaseModel):
    reference_ids: List[str] = Field(
        description="""List of reference_ids in the order that they appear in the answer. If there is a "[1]" in the answer, and that corresponds to first reference in the given list of references, extract the reference_id and add it here. """)
    answer: str = Field(description="""Answer to the user question with inline citations like [1], [2] etc.  When writing your answers, reference these quotes using inline citations in square brackets [1], [2], etc. Each 
                    statement in your answers should end with the relevant citation(s). Multiple citations can be used if needed [1,2].
                    \n \nIf there is no relevant reference, write "No relevant Info" instead. \n \n Do not include or reference 
                    quoted content verbatim in the answer. Make sure each statement in your answers includes at least one citation to the 
                    relevant quote number. Don\'t say "According to Quote [1]"  or " Based on the information provided" when answering. 
                    If the question cannot be answered by the document, say so.
                    Make references to quotes relevant to each section of the answer solely by adding their "
                     "bracketed ids at the end of relevant sentences. "
                     """)


class AnswerReference(BaseModel):
    reference_text: str
    chunk_id: str
    paper: ResearchPaper

    class Config:
        arbitrary_types_allowed = True
class AskQuestionOutput(BaseModel):
    references: List[AnswerReference] = Field(default_factory=List)
    answer: str = Field(default_factory=str)

    class Config:
        arbitrary_types_allowed = True
