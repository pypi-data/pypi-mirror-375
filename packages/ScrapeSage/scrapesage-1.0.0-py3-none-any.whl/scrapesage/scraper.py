import requests
from duckduckgo_search import DDGS
from playwright.sync_api import sync_playwright
import google.generativeai as genai
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Union
from tenacity import retry, stop_after_attempt, wait_exponential
from concurrent.futures import ThreadPoolExecutor, as_completed


class ScrapeSageScraper:
    """
    ScrapeSage - A comprehensive web scraping and summarization library.
    
    This class provides functionality to search, scrape, and summarize web content
    using multiple search engines and AI-powered summarization.
    """
    
    def __init__(self, gemini_api_key: str, serper_api_key: str):
        """
        Initialize the ScrapeSage Scraper.
        
        Args:
            gemini_api_key (str): Google Gemini AI API key
            serper_api_key (str): Serper API key for Google search
            
        Raises:
            ValueError: If API keys are not provided
        """
        if not gemini_api_key or not serper_api_key:
            raise ValueError("Both gemini_api_key and serper_api_key are required")
        
        self.gemini_api_key = gemini_api_key
        self.serper_api_key = serper_api_key
        
        # Configure Gemini AI
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _search_serper(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Search using Serper API (Google Search).
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
            
        Returns:
            List[Dict]: Search results
        """
        url = "https://google.serper.dev/search"
        
        payload = {
            'q': query,
            'num': num_results,
            'gl': 'us',
            'hl': 'en'
        }
        
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extract organic results
            return data.get('organic', [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching with Serper: {e}")
            return []
    
    def _search_duckduckgo(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Search using DuckDuckGo.
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
            
        Returns:
            List[Dict]: Search results
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
                return results
        except Exception as e:
            print(f"Error searching with DuckDuckGo: {e}")
            return []
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _scrape_content(self, url: str) -> Optional[str]:
        """
        Scrape content from a URL using Playwright.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            Optional[str]: Scraped content or None if failed
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
                page = context.new_page()
                
                # Set a timeout and navigate
                page.set_default_timeout(30000)  # 30 seconds
                page.goto(url, wait_until="domcontentloaded")
                
                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)
                
                # Get page content
                content = page.content()
                browser.close()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text[:10000]  # Limit to 10k characters
                
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def _scrape_content_simple(self, url: str) -> Optional[str]:
        """
        Fallback method to scrape content using requests.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            Optional[str]: Scraped content or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:10000]  # Limit to 10k characters
            
        except Exception as e:
            print(f"Error scraping {url} with simple method: {e}")
            return None
    
    def _summarize_content(self, content: str, query: str) -> str:
        """
        Summarize content using Gemini AI.
        
        Args:
            content (str): Content to summarize
            query (str): Original search query for context
            
        Returns:
            str: Summary of the content
        """
        try:
            prompt = f"""
            Please provide a comprehensive summary of the following content in relation to the query: "{query}"
            
            Focus on:
            1. Key information relevant to the query
            2. Important facts and findings
            3. Main conclusions or insights
            4. Any actionable information
            
            Content:
            {content}
            
            Please provide a well-structured summary in 2-3 paragraphs:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error summarizing content: {e}")
            return "Summary not available due to AI processing error."
    
    def search_and_scrape(self, 
                         query: str, 
                         max_urls: int = 5,
                         search_engines: List[str] = ["serper", "duckduckgo"]) -> Dict:
        """
        Search for content and scrape the results.
        
        Args:
            query (str): Search query
            max_urls (int): Maximum number of URLs to process
            search_engines (List[str]): List of search engines to use
            
        Returns:
            Dict: Results containing summaries and sources
        """
        print(f"🔍 Searching for: {query}")
        
        all_results = []
        
        # Search with multiple engines
        for engine in search_engines:
            if engine == "serper":
                results = self._search_serper(query, max_urls)
                print(f"📊 Found {len(results)} results from Serper")
            elif engine == "duckduckgo":
                results = self._search_duckduckgo(query, max_urls)
                print(f"📊 Found {len(results)} results from DuckDuckGo")
            else:
                print(f"⚠️ Unknown search engine: {engine}")
                continue
            
            all_results.extend(results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get('link') or result.get('href')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        # Limit to max_urls
        unique_results = unique_results[:max_urls]
        
        print(f"🎯 Processing {len(unique_results)} unique URLs")
        
        # Scrape content from URLs with threading
        scraped_data = []
        
        def scrape_single_url(result):
            url = result.get('link') or result.get('href')
            title = result.get('title', 'No title')
            snippet = result.get('snippet') or result.get('body', 'No snippet')
            
            print(f"📄 Scraping: {title[:50]}...")
            
            # Try Playwright first, then fallback to simple requests
            content = self._scrape_content(url)
            if not content:
                content = self._scrape_content_simple(url)
            
            if content:
                summary = self._summarize_content(content, query)
                return {
                    'url': url,
                    'title': title,
                    'snippet': snippet,
                    'content_preview': content[:500] + "..." if len(content) > 500 else content,
                    'ai_summary': summary,
                    'scraped': True
                }
            else:
                return {
                    'url': url,
                    'title': title,
                    'snippet': snippet,
                    'content_preview': snippet,
                    'ai_summary': f"Could not scrape content. Based on snippet: {snippet}",
                    'scraped': False
                }
        
        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_result = {executor.submit(scrape_single_url, result): result for result in unique_results}
            
            for future in as_completed(future_to_result):
                scraped_data.append(future.result())
        
        # Generate overall summary
        print("🤖 Generating overall summary...")
        all_content = " ".join([item['ai_summary'] for item in scraped_data])
        
        overall_summary_prompt = f"""
        Based on the following individual summaries from multiple sources about "{query}", 
        please provide a comprehensive overview that synthesizes the key information:
        
        {all_content}
        
        Please provide:
        1. A consolidated summary of the main findings
        2. Key insights and trends
        3. Any contradictions or different perspectives found
        4. Actionable conclusions
        
        Format this as a well-structured response:
        """
        
        try:
            overall_summary = self.model.generate_content(overall_summary_prompt).text
        except Exception as e:
            print(f"Error generating overall summary: {e}")
            overall_summary = "Overall summary not available due to AI processing error."
        
        return {
            'query': query,
            'overall_summary': overall_summary,
            'sources': scraped_data,
            'total_sources': len(scraped_data),
            'successfully_scraped': len([item for item in scraped_data if item['scraped']])
        }
