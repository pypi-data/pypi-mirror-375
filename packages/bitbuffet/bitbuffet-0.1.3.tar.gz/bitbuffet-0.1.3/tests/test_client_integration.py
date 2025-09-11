"""
Test suite for the Python Structured Scraper Client SDK for Integration Tests
"""

import pytest

from bitbuffet import BitBuffet
from tests.schemas.recipe_schema import RecipeSchema
from tests.schemas.article_schema import ArticleSchema
import os

client = BitBuffet(os.getenv("TEST_API_KEY"))


class TestIntegration:
    """Integration tests for real API calls (optional - requires actual API)"""

    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires actual API endpoint and may be slow")
    def test_real_recipe_scraping(self):
        """Integration test with real recipe URL (skipped by default)"""
        url = "https://www.recipetineats.com/butter-chicken/"
        
        result = client.extract(url, RecipeSchema, reasoning_effort="medium")
        
        assert isinstance(result, RecipeSchema)
        assert result.title
        assert result.author
        assert len(result.steps) > 0
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires actual API endpoint and may be slow")
    def test_real_article_scraping(self):
        """Integration test with real article URL (skipped by default)"""
        url = "https://www.bbc.co.uk/news/articles/clyrev00lwno"
        
        result = client.extract(url, ArticleSchema)
        
        assert isinstance(result, ArticleSchema)
        assert result.title
        assert result.content
        assert result.author
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires actual API endpoint and may be slow")
    def test_real_recipe_scraping_with_all_params(self):
        """Integration test with all new parameters"""
        url = "https://www.recipetineats.com/butter-chicken/"
        
        result = client.extract(
            url, 
            RecipeSchema, 
            reasoning_effort="high",
            prompt="Focus on extracting detailed ingredient measurements and cooking times"
        )
        
        assert isinstance(result, RecipeSchema)
        assert result.title
        assert result.author
        assert len(result.steps) > 0
        assert result.time.total > 0
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires actual API endpoint and may be slow")
    def test_real_article_scraping_with_reasoning_effort(self):
        """Integration test with reasoning effort parameter"""
        url = "https://www.bbc.co.uk/news/articles/clyrev00lwno"
        
        result = client.extract(
            url, 
            ArticleSchema, 
            reasoning_effort="high",
            prompt="Extract the most important quotes and ensure accuracy"
        )
        
        assert isinstance(result, ArticleSchema)
        assert result.title
        assert result.content
        assert result.author
        assert len(result.important_quotes) >= 0
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires actual API endpoint and may be slow")
    def test_temperature_parameter_integration(self):
        """Integration test with different temperature values"""
        url = "https://www.recipetineats.com/butter-chicken/"
        
        # Test with low temperature (more deterministic)
        result_low = client.extract(
            url, 
            ArticleSchema, 
            temperature=0.1
        )
        
        # Test with high temperature (more creative)
        result_high = client.extract(
            url, 
            ArticleSchema, 
            temperature=1
        )
        
        assert isinstance(result_low, ArticleSchema)
        assert isinstance(result_high, ArticleSchema)
        assert result_low.title
        assert result_high.title
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires actual API endpoint and may be slow")
    def test_top_p_parameter_integration(self):
        """Integration test with top_p parameter"""
        url = "https://www.bbc.co.uk/news/articles/clyrev00lwno"
        
        result = client.extract(
            url, 
            ArticleSchema, 
            reasoning_effort="medium",
            top_p=0.8,
        )
        
        assert isinstance(result, ArticleSchema)
        assert result.title
        assert result.content
        assert result.author
