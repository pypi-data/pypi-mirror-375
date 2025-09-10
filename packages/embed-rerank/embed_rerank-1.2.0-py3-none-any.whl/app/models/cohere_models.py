"""
Pydantic models for Cohere API compatibility.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CohereDocument(BaseModel):
    """Document input for Cohere rerank API."""
    
    text: str = Field(..., description="The document text to rerank")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the document")


class CohereRerankRequest(BaseModel):
    """Request model for Cohere-compatible reranking."""

    query: str = Field(
        ...,
        description="The user query",
        min_length=1,
        max_length=2048,
        json_schema_extra={"example": "What is machine learning?"}
    )
    documents: List[str] = Field(
        ...,
        description="A list of documents to rerank",
        min_length=1,
        max_length=1000,
        json_schema_extra={
            "example": [
                "Machine learning is a subset of artificial intelligence.",
                "Deep learning uses neural networks with many layers.",
                "Natural language processing helps computers understand text."
            ]
        }
    )
    model: Optional[str] = Field(
        None,
        description="The Rerank model to use (e.g., 'rerank-v3.5')",
        json_schema_extra={"example": "rerank-v3.5"}
    )
    top_n: Optional[int] = Field(
        None,
        description="The number of top reranked documents to return",
        ge=1,
        le=100,
        json_schema_extra={"example": 5}
    )
    return_documents: Optional[bool] = Field(
        False,
        description="Whether to return the full document objects in the response",
        json_schema_extra={"example": False}
    )


class CohereRerankResult(BaseModel):
    """Individual result in Cohere rerank response."""
    
    index: int = Field(..., description="Original index of the document", ge=0)
    relevance_score: float = Field(..., description="Relevance score for the document")
    document: Optional[CohereDocument] = Field(None, description="Document object (if return_documents=True)")


class CohereRerankMeta(BaseModel):
    """Metadata for Cohere rerank response."""
    
    api_version: Dict[str, str] = Field(default={"version": "1"}, description="API version")
    billed_units: Dict[str, int] = Field(default={"search_units": 1}, description="Billing information")


class CohereRerankResponse(BaseModel):
    """Response model for Cohere-compatible reranking."""
    
    results: List[CohereRerankResult] = Field(..., description="Reranked results")
    meta: CohereRerankMeta = Field(default_factory=CohereRerankMeta, description="Response metadata")
