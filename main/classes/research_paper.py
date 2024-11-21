from typing import List, Dict, Optional

from pydantic import BaseModel, Field


class ResearchPaper(BaseModel):
    open_alex_id: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    authors: Optional[List[str]] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    publication_year: Optional[int] = Field(default=None)
    publication_date: Optional[str] = Field(default=None)
    referenced_works_ids: Optional[List[str]] = Field(default=None)
    referenced_works_count: Optional[int] = Field(default=None)
    oa_url: Optional[str] = Field(default=None)
    concepts: Optional[List[str]] = Field(default=None)
    cited_by_count: Optional[int] = Field(default=None)
    cited_by_url: Optional[str] = Field(default=None)
    biblio: Optional[Dict] = Field(default=None)
    institutions: Optional[List[str]] = Field(default=None)
    key_words: Optional[List[str]] = Field(default=None)
    primary_topic: Optional[str] = Field(default=None)
    publication: Optional[str] = Field(default=None)
    extracted_figures: Optional[List[str]] = Field(default=None)
    referenced_papers: Optional[List[str]] = Field(default=None)
    embeddings: Optional[List] = Field(default=None)
    publication_id: Optional[str] = Field(default=None)
    publication_quartile: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    pdf_content: Optional[str] = Field(default=None)
    pdf_content_chunks: Optional[Dict[str, str]] = Field(default=None)
    extracted_info: Optional[Dict] = Field(default=None)
    methodology: Optional[Dict] = Field(default=None)
    datasets: Optional[Dict] = Field(default=None)
    contributions: Optional[Dict] = Field(default=None)
    results: Optional[Dict] = Field(default=None)
    limitations: Optional[Dict] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True
