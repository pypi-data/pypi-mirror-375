"""
Core functions for ScrapeSage - simplified interface for easy usage.

This module provides a simple function-based interface to the scraper functionality.
"""

from .scraper import ScrapeSageScraper
from typing import Dict, Union, List


def search_and_summarize(
    query: str, 
    gemini_api_key: str, 
    serper_api_key: str,
    max_urls: int = 5,
    use_both_engines: bool = True
) -> Dict[str, Union[List[Dict], List[str]]]:
    """
    Simple function to search, scrape, and summarize content.
    
    Args:
        query (str): The search query
        gemini_api_key (str): Google Gemini AI API key
        serper_api_key (str): Serper API key for Google search
        max_urls (int): Maximum number of URLs to scrape and summarize (default: 5)
        use_both_engines (bool): Whether to use both Google and DuckDuckGo (default: True)
        
    Returns:
        Dict containing:
            - summaries: List of dictionaries with title, url, and summary
            - sources: List of source URLs
            
    Example:
        >>> import scrapesage
        >>> results = scrapesage.search_and_summarize(
        ...     query="AI trends 2024",
        ...     gemini_api_key="your_gemini_key",
        ...     serper_api_key="your_serper_key",
        ...     max_urls=10  # Get up to 10 results
        ... )
        >>> print(f"Found {len(results['summaries'])} results")
    """
    scraper = ScrapeSageScraper(
        gemini_api_key=gemini_api_key,
        serper_api_key=serper_api_key
    )
    
    return scraper.search_and_scrape(
        query=query,
        max_urls=max_urls,
        search_engines=["serper", "duckduckgo"] if use_both_engines else ["serper"]
    )
