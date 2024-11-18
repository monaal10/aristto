from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from classes.research_paper import ResearchPaper


class PaperInformation(BaseModel):
    "Extracted Information about the Paper"
    methodology: Dict[str, str] = Field(
        description="List of references that talk about the Methodology/Processes/Algorithms used to conduct the research"
                    "The keys will be numbers like 1, 2, etc and the values will be the actual reference texts.")
    contributions: Dict[str, str] = Field(
        description="List of references that talk about Major Findings/New Contributions of the paper."
                    "The keys will be numbers like 1, 2, etc and the values will be the actual reference texts.")
    datasets: Dict[str, str] = Field(
        description="List of references that talk about datasets used or referenced the paper."
                    "The keys will be numbers like 1, 2, etc and the values will be the actual reference texts.")
    limitations: Dict[str, str] = Field(
        description="List of references that talk about limitations or drawbacks of the paper."
                    "The keys will be numbers like 1, 2, etc and the values will be the actual reference texts.")
    results: Dict[str, str] = Field(
        description="List of references that talk about Results of the experiments in the paper."
                    "The keys will be numbers like 1, 2, etc and the values will be the actual reference texts.")



class ResearchEvolution(BaseModel):
    major_trends: str = Field(description="")
    turning_points: str = Field(description="")
    timeline: str = Field(description="")


class MethodologyAnalysis(BaseModel):
    dominant_approaches: str = Field(description="")
    effectiveness_comparison: str = Field(description="")
    common_limitations: str = Field(description="")


class Contradictions(BaseModel):
    major_debates: str = Field(description="")
    conflicting_results: str = Field(description="")
    potential_resolutions: str = Field(description="")


class ResearchGaps(BaseModel):
    underexplored_areas: str = Field(description="")
    common_limitations: str = Field(description="")
    missing_elements: str = Field(description="")


class FutureDirections(BaseModel):
    promising_areas: str = Field(description="")
    methodology_suggestions: str = Field(description="")
    new_questions: str = Field(description="")


class Reference(BaseModel):
    reference_id: str = Field(description="id of the reference")
    reference_text: str = Field(description="")



class ReferenceWithMetadata(BaseModel):
    reference_id: str = Field(description="id of the reference")
    paper_id: str = Field(description="id of the paper")
    reference_metadata: ResearchPaper
    reference_text: str = Field(description="Reference text")

    class Config:
        arbitrary_types_allowed = True

class InsightGeneration(BaseModel):
    references: List[str] = Field(
        description="List of reference_ids that have be used in different parts of the answer in square brackets")
    research_evolution: str = Field(
        description="An in depth explaination about the evolution of research in the field. Keep it verbose. Follow the instructions in the prompt for more details.")
    methodology_analysis: str = Field(description="An in depth explaination of the different methodologies used in different papers and how they compare with one another. Follow the instructions in the prompt for more details. " )
    contradictions: str = Field(description="An in depth explaination of contradictions in different papers. They could be contradictions in results, approaches used or even opinions. Follow the instructions in the prompt for more details.")
    research_gaps: str = Field(description=" An in depth explaination of across the papers, the issues that have not yet been resolved and need more work. Follow the instructions in the prompt for more details.")
    future_directions: str = Field(description="An in depth explaination of Where is this domain heading?. Follow the instructions in the prompt for more details.")

    class Config:
        arbitrary_types_allowed = True

class LiteratureReview(BaseModel):
    references: List[ReferenceWithMetadata] = Field(default_factory=list)
    insights: Dict[str, str] = Field(default_factory=Dict)

    class Config:
        arbitrary_types_allowed = True

class Themes(BaseModel):
    themes: List[str] = Field(description= "A list of phrases that can be directly used to search for papers on google "
                                           "scholar that are going to be relevant to the original query")
    class Config:
        arbitrary_types_allowed = True
class PaperValidation(BaseModel):
    answer: bool = Field(description="Answer in either true or false only. This is supposed to be used as a boolean")
    class Config:
        arbitrary_types_allowed = True

class AgentState(BaseModel):
    query: str
    start_year: Optional[int]
    end_year: Optional[int]
    citation_count: Optional[int]
    published_in: Optional[List[str]]
    authors: Optional[List[str]]
    themes: List[str] = Field(default_factory=list)
    papers: Dict[str, List[str]] = Field(default_factory=dict)
    extracted_info: Dict[str, Dict] = Field(default_factory=dict)
    graph_data: List[Dict] = Field(default_factory=list)
    literature_review: LiteratureReview = Field(default_factory=list)
    memory: Dict = Field(default_factory=dict)
    themes_with_papers: Dict[str, List[ResearchPaper]] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True