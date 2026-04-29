"""
ContentBoost AI — Competitor Scraper

Uses Firecrawl SDK to scrape competitor product pages and extract
structured product information. Falls back to fixture data in demo mode.
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Path to fixture data
FIXTURES_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "sample_products.json")


class CompetitorScraper:
    """Scrapes competitor product pages using Firecrawl and extracts structured data.
    
    When FIRECRAWL_API_KEY is not set, returns fixture data for demo mode.
    
    Attributes:
        client: Firecrawl client instance (None if API key not set).
        anthropic_client: Anthropic client for product extraction (optional).
    """
    
    def __init__(self) -> None:
        """Initialize the CompetitorScraper."""
        self.client = None
        self.anthropic_client = None
        self._init_clients()
    
    def _init_clients(self) -> None:
        """Initialize Firecrawl and Anthropic clients if API keys available."""
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        if firecrawl_key and firecrawl_key != "your-firecrawl-api-key":
            try:
                from firecrawl import Firecrawl
                self.client = Firecrawl(api_key=firecrawl_key)
            except Exception as e:
                print(f"Firecrawl initialization failed: {e}")
        
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your-anthropic-api-key":
            try:
                from anthropic import Anthropic
                self.anthropic_client = Anthropic(api_key=anthropic_key)
            except Exception as e:
                print(f"Anthropic initialization failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Firecrawl is configured and available.
        
        Returns:
            bool: True if Firecrawl client is initialized.
        """
        return self.client is not None
    
    def scrape_competitors(self, urls: list[str]) -> list[dict]:
        """Scrape multiple competitor product pages.
        
        Args:
            urls: List of competitor product page URLs (max 5).
            
        Returns:
            list[dict]: List of extracted product data dictionaries.
            
        Raises:
            Exception: If scraping fails entirely (individual URL failures are handled).
        """
        if not self.is_available():
            return self._get_demo_competitor_data()
        
        results = []
        urls = urls[:5]  # Cap at 5 URLs
        
        for url in urls:
            try:
                scrape_result = self.client.scrape(
                    url,
                    formats=["markdown"]
                )
                
                raw_content = ""
                if hasattr(scrape_result, "markdown"):
                    raw_content = scrape_result.markdown
                elif isinstance(scrape_result, dict):
                    raw_content = scrape_result.get("markdown", "")
                
                if raw_content:
                    product_info = self._extract_product_info(raw_content, url)
                    results.append(product_info)
                    
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                results.append({
                    "url": url,
                    "title": f"Failed to scrape",
                    "description": f"Error: {str(e)}",
                    "bullet_points": [],
                    "features": [],
                    "error": True
                })
        
        return results if results else self._get_demo_competitor_data()
    
    def _extract_product_info(self, raw_content: str, url: str) -> dict:
        """Extract structured product data from raw scraped content.
        
        Uses Claude API if available, otherwise falls back to regex extraction.
        
        Args:
            raw_content: Raw markdown content from scraping.
            url: Source URL for reference.
            
        Returns:
            dict: Structured product information.
        """
        # Try Claude extraction first
        if self.anthropic_client:
            try:
                from prompts import PRODUCT_EXTRACTION_PROMPT
                
                response = self.anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2048,
                    messages=[{
                        "role": "user",
                        "content": PRODUCT_EXTRACTION_PROMPT.format(
                            raw_content=raw_content[:5000]
                        )
                    }]
                )
                
                response_text = response.content[0].text
                # Extract JSON from response
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    product_data = json.loads(response_text[json_start:json_end])
                    product_data["url"] = url
                    return product_data
                    
            except Exception as e:
                print(f"Claude extraction failed, using regex: {e}")
        
        # Fallback: basic regex extraction
        return self._regex_extract(raw_content, url)
    
    def _regex_extract(self, content: str, url: str) -> dict:
        """Basic regex-based product info extraction fallback.
        
        Args:
            content: Raw text content.
            url: Source URL.
            
        Returns:
            dict: Extracted product data.
        """
        import re
        
        lines = content.split("\n")
        
        # Find title (usually first heading)
        title = "Unknown Product"
        for line in lines:
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break
        
        # Find bullet points
        bullet_points = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("- ", "* ", "• ")):
                bp = stripped.lstrip("-*• ").strip()
                if len(bp) > 10:
                    bullet_points.append(bp)
        
        # Description: first substantial paragraph
        description = ""
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 50 and not stripped.startswith(("#", "-", "*", "•", "|", "[")):
                description = stripped
                break
        
        return {
            "url": url,
            "title": title,
            "description": description or content[:300],
            "bullet_points": bullet_points[:8],
            "features": bullet_points[:6]
        }
    
    def _get_demo_competitor_data(self, product_index: int = 0) -> list[dict]:
        """Load competitor data from fixtures for demo mode.
        
        Args:
            product_index: Index of the sample product to use.
            
        Returns:
            list[dict]: Sample competitor data.
        """
        try:
            with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
                fixtures = json.load(f)
            if fixtures and len(fixtures) > product_index:
                return fixtures[product_index].get("competitor_data", [])
        except Exception as e:
            print(f"Failed to load fixtures: {e}")
        
        # Hardcoded minimal fallback
        return [{
            "url": "https://demo.example.com",
            "title": "Sample Competitor Product",
            "description": "A high-quality product with great features and excellent value.",
            "bullet_points": ["Premium quality materials", "Fast shipping", "30-day returns"],
            "features": ["Premium", "Fast", "Reliable"]
        }]
    
    def get_demo_analysis(self, product_index: int = 0) -> dict:
        """Load pre-built competitor analysis from fixtures for demo mode.
        
        Args:
            product_index: Index of the sample product.
            
        Returns:
            dict: Pre-built competitor analysis.
        """
        try:
            with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
                fixtures = json.load(f)
            if fixtures and len(fixtures) > product_index:
                return fixtures[product_index].get("demo_competitor_analysis", {})
        except Exception:
            pass
        
        return {
            "tone": "Professional and benefit-focused",
            "usps": ["Quality", "Value", "Service"],
            "keyword_patterns": ["premium", "best", "top-rated"],
            "gaps": ["No competitor mentions sustainability"]
        }
