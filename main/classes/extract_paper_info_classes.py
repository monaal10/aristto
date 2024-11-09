from typing import Dict
from pydantic import BaseModel, Field


class ExtractedPaperInformation(BaseModel):
    methodology: str = Field(
        description=" What methods/algorithms/processes did the authors use to get the results in the paper"),
    contributions: str = Field(
        description=" major findings/contributions of the paper"),
    limitations: str = Field(
        description="limitations or drawbacks of the paper"),
    datasets: str = Field(
        description="datasets used in the paper if any."),
    results: str = Field(
        description="final results/conclusions of the paper.")
    summary: str = Field(description="2 line summary of the paper.")
