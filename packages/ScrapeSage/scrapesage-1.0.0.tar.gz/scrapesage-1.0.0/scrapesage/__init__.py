"""
ScrapeSage - A comprehensive web scraping and summarization library.

This library provides functionality to:
- Search across multiple search engines (Google via Serper API and DuckDuckGo)
- Scrape content from web pages using Playwright
- Summarize content using Google's Gemini AI
- Return structured results with summaries and sources

Author: ScrapeSage
Version: 1.0.0
"""

from .scraper import ScrapeSageScraper
from .core import search_and_summarize

__version__ = "1.0.0"
__author__ = "ScrapeSage"
__email__ = "contact@scrapesage.com"

__all__ = ["ScrapeSageScraper", "search_and_summarize"]
