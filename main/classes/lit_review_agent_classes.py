from pydantic import BaseModel, Field
from typing import List, Dict
from classes.research_paper import ResearchPaper
from prompts.literature_review_prompts import PROMPT_FOR_CITATIONS


class PaperInformation(BaseModel):
    """Always use this tool to structure your response to the user."""
    references: Dict[str, str] = Field(
        description="List of references. The keys will be numbers like 1, 2, etc and the values will be the actual reference texts.")
    section: str = Field(description="Information extracted for the particular section.Make "
                                     "references to quotes relevant to each section of the answer solely by adding their "
                                     "bracketed numbers at the end of relevant sentences. "
                                     "\n \nThus, the format of your overall response for each of the section "
                                     "should look like what\'s shown between the <example></example> "
                                     "tags : <example>Almost 90% of revenue came from widget sales, with gadget sales making up the remaining 10%."
                                     "Company X earned \$12 million.[1] Almost 90% of it was from widget sales. [2]</example> "),
    """findings: str = Field(
        description=" major findings/contributions of the paper.Make "
                                         "references to quotes relevant to each section of the answer solely by adding their "
                                         "bracketed numbers at the end of relevant sentences. "
                                         "\n \nThus, the format of your overall response for each of the section "
                                         "should look like what\'s shown between the <example></example> "
                                         "tags : <example>Almost 90% of revenue came from widget sales, with gadget sales making up the remaining 10%."
                                         "Company X earned \$12 million.[1] Almost 90% of it was from widget sales. [2]</example> "),
    limitations: str = Field(
        description="limitations or drawbacks of the paper.Make "
                                         "references to quotes relevant to each section of the answer solely by adding their "
                                         "bracketed numbers at the end of relevant sentences. "
                                         "\n \nThus, the format of your overall response for each of the section "
                                         "should look like what\'s shown between the <example></example> "
                                         "tags : <example>Almost 90% of revenue came from widget sales, with gadget sales making up the remaining 10%."
                                         "Company X earned \$12 million.[1] Almost 90% of it was from widget sales. [2]</example> "),
    datasets: str = Field(
        description="datasets used in the paper if any.Make "
                                         "references to quotes relevant to each section of the answer solely by adding their "
                                         "bracketed numbers at the end of relevant sentences. "
                                         "\n \nThus, the format of your overall response for each of the section "
                                         "should look like what\'s shown between the <example></example> "
                                         "tags : <example>Almost 90% of revenue came from widget sales, with gadget sales making up the remaining 10%."
                                         "Company X earned \$12 million.[1] Almost 90% of it was from widget sales. [2]</example> "),
    results: str = Field(
        description="final results/conclusions of the paper.Make "
                                         "references to quotes relevant to each section of the answer solely by adding their "
                                         "bracketed numbers at the end of relevant sentences. "
                                         "\n \nThus, the format of your overall response for each of the section "
                                         "should look like what\'s shown between the <example></example> "
                                         "tags : <example>Almost 90% of revenue came from widget sales, with gadget sales making up the remaining 10%."
                                         "Company X earned \$12 million.[1] Almost 90% of it was from widget sales. [2]</example>")"""


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
    paper_id: str = Field(description="Id of the paper that the reference is from")
    reference_text: str = Field(description="Actual text that is used as the reference to form the answer")


class ReferenceWithMetdadata(BaseModel):
    reference: Reference
    reference_metadata: ResearchPaper

class InsightGeneration(BaseModel):
    references: Dict[str, Reference] = Field(
        description="List of references. The keys will be numbers like 1, 2, etc and the values will be the actual references with the paper_ids from where they were picked up.")
    research_evolution: str = Field(
        description=" A paragraph about the evolution of research in the field. Keep it verbose." + PROMPT_FOR_CITATIONS)
    methodology_analysis: str = Field(description="An in depth explaination of the different methodologies used in different papers and how they compare with one another." + PROMPT_FOR_CITATIONS)
    contradictions: str = Field(description="An in depth explaination Contradictions in different papers. They could be contradictions in results, approaches used or even opinions." +  PROMPT_FOR_CITATIONS)
    research_gaps: str = Field(description=" An in depth explaination of across the papers, the issues that have not yet been resolved and need more work" + PROMPT_FOR_CITATIONS)
    future_directions: str = Field(description="An in depth explaination of Where is this domain heading?" + PROMPT_FOR_CITATIONS)


class ThemeLiteratureReview(BaseModel):
    theme: str = Field(default_factory=str)
    references: List[ReferenceWithMetdadata] = Field(default_factory=list)
    insights: Dict = Field(default_factory=dict)
class AgentState(BaseModel):
    query: str
    start_year: int
    end_year: int
    citation_count: int
    published_in: List[str]
    authors: List[str]
    themes: List[str] = Field(default_factory=list)
    papers: Dict[str, List[str]] = Field(default_factory=dict)
    extracted_info: Dict[str, Dict] = Field(default_factory=dict)
    graph_data: List[Dict] = Field(default_factory=list)
    literature_review: List[ThemeLiteratureReview] = Field(default_factory=list)
    memory: Dict = Field(default_factory=dict)
    themes_with_papers: Dict[str, List[ResearchPaper]] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True