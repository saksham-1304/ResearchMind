# tools.py
from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs, and snippets."""
    try:
        # Increased to 7 results for a broader research base
        results = tavily.search(query=query, search_depth="advanced", max_results=7)
        out = []
        for r in results['results']:
            out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:400]}\n")
        return "\n----\n".join(out)
    except Exception as e:
        return f"Search API Error: {str(e)}"

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Remove noisy elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
            
        # Extract main text
        text = soup.get_text(separator="\n", strip=True)
        
        # Limit to 5000 characters to fit well within LLM context limits while retaining core info
        return f"Source URL: {url}\n\nContent:\n{text[:5000]}"
    except Exception as e:
        return f"Could not scrape URL {url}: {str(e)}"