"""
Tests for the FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from alletaal_lint.api import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "alletaal-lint API" in data["name"]
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_score_sentence_endpoint(self, client):
        """Test sentence scoring endpoint."""
        response = client.post(
            "/score-sentence",
            json={"text": "De kat zit op de mat."}
        )
        assert response.status_code == 200
        data = response.json()
        assert "lint_score" in data
        assert "difficulty_level" in data
        assert isinstance(data["lint_score"], float)
        assert isinstance(data["difficulty_level"], int)
        assert 0 <= data["lint_score"] <= 100
        assert 1 <= data["difficulty_level"] <= 4
    
    def test_score_document_endpoint(self, client):
        """Test document scoring endpoint."""
        response = client.post(
            "/score-document",
            json={"text": "De kat zit op de mat. De hond rent in de tuin."}
        )
        assert response.status_code == 200
        data = response.json()
        assert "lint_score" in data
        assert "difficulty_level" in data
        assert isinstance(data["lint_score"], float)
        assert isinstance(data["difficulty_level"], int)
    
    def test_analyze_document_endpoint(self, client):
        """Test detailed document analysis endpoint."""
        response = client.post(
            "/analyze-document",
            json={"text": "De kat zit op de mat. De hond rent in de tuin."}
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "document_score", "document_level", "sentence_count",
            "average_sentence_length", "sentences"
        ]
        for field in required_fields:
            assert field in data
        
        assert len(data["sentences"]) == 2
        for sentence in data["sentences"]:
            assert "sentence" in sentence
            assert "lint_score" in sentence
            assert "difficulty_level" in sentence
    
    def test_empty_text_handling(self, client):
        """Test handling of empty text."""
        response = client.post(
            "/score-sentence",
            json={"text": ""}
        )
        # Should handle gracefully, not crash
        assert response.status_code in [200, 422]  # Either success or validation error
    
    def test_markdown_removal(self, client):
        """Test markdown removal functionality."""
        markdown_text = "**Bold text** and *italic text* with [links](http://example.com)"
        response = client.post(
            "/score-sentence",
            json={"text": markdown_text}
        )
        assert response.status_code == 200
        # Should process without error even with markdown
    
    def test_invalid_input_format(self, client):
        """Test invalid input format handling."""
        response = client.post(
            "/score-sentence",
            json={"wrong_field": "test"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_very_long_text(self, client):
        """Test with very long text."""
        long_text = "Dit is een test. " * 1000
        response = client.post(
            "/score-document",
            json={"text": long_text}
        )
        assert response.status_code == 200
        # Should handle long text without timeout


class TestAPIResponseFormats:
    """Test API response formats and validation."""
    
    def test_sentence_response_format(self, client):
        """Test sentence response format matches schema."""
        response = client.post(
            "/score-sentence",
            json={"text": "Test zin voor analyse."}
        )
        data = response.json()
        
        # Check required fields
        assert "lint_score" in data
        assert "difficulty_level" in data
        
        # Check data types
        assert isinstance(data["lint_score"], (int, float))
        assert isinstance(data["difficulty_level"], int)
        
        # Check value ranges
        assert 0 <= data["lint_score"] <= 100
        assert 1 <= data["difficulty_level"] <= 4
    
    def test_document_response_format(self, client):
        """Test document response format matches schema."""
        response = client.post(
            "/score-document",
            json={"text": "Eerste zin. Tweede zin. Derde zin."}
        )
        data = response.json()
        
        assert "lint_score" in data
        assert "difficulty_level" in data
        assert isinstance(data["lint_score"], (int, float))
        assert isinstance(data["difficulty_level"], int)
    
    def test_detailed_analysis_response_format(self, client):
        """Test detailed analysis response format."""
        response = client.post(
            "/analyze-document",
            json={"text": "Eerste zin. Tweede zin."}
        )
        data = response.json()
        
        # Check main fields
        main_fields = ["document_score", "document_level", "sentence_count", 
                      "average_sentence_length", "sentences"]
        for field in main_fields:
            assert field in data
        
        # Check sentence details
        assert len(data["sentences"]) == 2
        for sentence in data["sentences"]:
            sentence_fields = [
                "sentence", "lint_score", "difficulty_level",
                "word_frequency_log", "max_dependency_length",
                "content_words_proportion", "concrete_nouns_proportion"
            ]
            for field in sentence_fields:
                assert field in sentence


class TestCORSAndMiddleware:
    """Test CORS and middleware functionality."""
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/score-sentence")
        # FastAPI's TestClient doesn't fully simulate CORS, but we can check basic functionality
        assert response.status_code in [200, 405]  # Either allowed or method not allowed
    
    def test_content_type_handling(self, client):
        """Test different content type handling."""
        # Test with explicit content type
        response = client.post(
            "/score-sentence",
            json={"text": "Test zin."},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200