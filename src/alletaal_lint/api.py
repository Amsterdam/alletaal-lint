"""
FastAPI server for LiNT readability assessment.

This module provides REST API endpoints for the LiNT readability scoring system.
"""

import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .core import Document, Sentence


class TextInput(BaseModel):
    """Input model for text to be analyzed."""
    text: str = Field(..., description="Text to analyze for readability")


class SentenceScoreResponse(BaseModel):
    """Response model for sentence scoring."""
    lint_score: float = Field(..., description="LiNT readability score (0-100)")
    difficulty_level: int = Field(..., description="Difficulty level (1-4)")


class DocumentScoreResponse(BaseModel):
    """Response model for document scoring."""
    lint_score: float = Field(..., description="Average LiNT readability score (0-100)")
    difficulty_level: int = Field(..., description="Overall difficulty level (1-4)")


class SentenceAnalysis(BaseModel):
    """Model for individual sentence analysis."""
    sentence: str = Field(..., description="The sentence text")
    lint_score: float = Field(..., description="LiNT readability score")
    difficulty_level: int = Field(..., description="Difficulty level")
    word_frequency_log: float = Field(..., description="Average log word frequency")
    max_dependency_length: int = Field(..., description="Maximum dependency length")
    content_words_proportion: float = Field(..., description="Proportion of content words")
    concrete_nouns_proportion: float = Field(..., description="Proportion of concrete nouns")


class DetailedDocumentResponse(BaseModel):
    """Response model for detailed document analysis."""
    document_score: float = Field(..., description="Overall document score")
    document_level: int = Field(..., description="Overall difficulty level")
    sentence_count: int = Field(..., description="Number of sentences")
    average_sentence_length: float = Field(..., description="Average words per sentence")
    sentences: List[SentenceAnalysis] = Field(..., description="Individual sentence analyses")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="alletaal-lint API",
        description="Dutch Text Readability Assessment using LiNT methodology",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def remove_markdown(text: str) -> str:
        """Remove common Markdown syntax from text."""
        patterns = [
            r'\*{1,3}',  # Bold/italic markers
            r'_+',       # Underscore emphasis
            r'~{2}',     # Strikethrough
            r'`{1,3}',   # Code markers
            r'#{1,6} ',  # Headers
            r'\[.*?\]\(.*?\)',  # Links
            r'!\[.*?\]\(.*?\)', # Images
            r'>-',       # Blockquotes
            r'--+',      # Horizontal lines
            r'\|',       # Table markers
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        
        return text.strip()

    @app.get("/")
    async def root():
        """Root endpoint with basic API information."""
        return {
            "name": "alletaal-lint API",
            "description": "Dutch Text Readability Assessment using LiNT methodology",
            "version": "1.0.0",
            "endpoints": {
                "score_sentence": "/score-sentence",
                "score_document": "/score-document", 
                "analyze_document": "/analyze-document",
                "health": "/health"
            }
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            # Test that spaCy model can be loaded
            test_sentence = Sentence("Test zin.")
            return {"status": "healthy", "spacy_model": "nl_core_news_sm loaded"}
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

    @app.post("/score-sentence", response_model=SentenceScoreResponse)
    async def score_sentence(input_data: TextInput):
        """Score a single sentence for readability."""
        try:
            clean_text = remove_markdown(input_data.text)
            sentence = Sentence(clean_text)
            
            return SentenceScoreResponse(
                lint_score=sentence.calculate_lint_score(),
                difficulty_level=sentence.get_difficulty_level()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error scoring sentence: {str(e)}")

    @app.post("/score-document", response_model=DocumentScoreResponse)
    async def score_document(input_data: TextInput):
        """Score a document for readability."""
        try:
            clean_text = remove_markdown(input_data.text)
            document = Document(clean_text)
            
            return DocumentScoreResponse(
                lint_score=document.calculate_lint_score(),
                difficulty_level=document.get_difficulty_level()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error scoring document: {str(e)}")

    @app.post("/analyze-document", response_model=DetailedDocumentResponse)
    async def analyze_document(input_data: TextInput):
        """Provide detailed analysis of document readability."""
        try:
            clean_text = remove_markdown(input_data.text)
            document = Document(clean_text)
            
            sentences = []
            for sentence in document.sentences:
                sentences.append(SentenceAnalysis(
                    sentence=sentence.text,
                    lint_score=sentence.calculate_lint_score(),
                    difficulty_level=sentence.get_difficulty_level(),
                    word_frequency_log=sentence.get_word_frequency_log(),
                    max_dependency_length=sentence.get_max_dependency_length(),
                    content_words_proportion=sentence.get_proportion_of_content_words_excluding_adverbs(),
                    concrete_nouns_proportion=sentence.get_proportion_of_broadly_concrete_nouns()
                ))
            
            analysis = document.get_detailed_analysis()
            
            return DetailedDocumentResponse(
                document_score=analysis['document_score'],
                document_level=analysis['document_level'],
                sentence_count=analysis['sentence_count'],
                average_sentence_length=analysis['average_sentence_length'],
                sentences=sentences
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")

    return app


# Create app instance
app = create_app()